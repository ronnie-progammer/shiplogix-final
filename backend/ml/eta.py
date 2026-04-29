"""ETA predictor: predicts arrival timestamp + 95% confidence interval.

Trains a RandomForestRegressor on delivered shipments to predict actual
transit hours. Per-tree predictions give us a non-parametric distribution
that we summarize as mean ± 1.96 * std for a 95% CI band.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
ETA_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "eta_predictor.joblib")
ETA_SCALER_PATH = os.path.join(ARTIFACTS_DIR, "eta_scaler.joblib")
ETA_ENCODERS_PATH = os.path.join(ARTIFACTS_DIR, "eta_encoders.joblib")

CAT_COLS = ["carrier", "origin", "destination", "weather_region"]
NUM_COLS = ["transit_days", "month"]


class ETAPredictor:
    """Regresses actual transit hours from shipment features.

    The output of `predict` is hours offset from `ship_date`. Callers add
    that offset to ship_date to get a calendar timestamp. Confidence is
    derived from the variance across the forest's individual trees.
    """

    def __init__(self) -> None:
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.encoders: dict[str, LabelEncoder] = {}
        self.ready = False
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    def load_or_train(self, df: pd.DataFrame) -> None:
        if os.path.exists(ETA_MODEL_PATH):
            self.model = joblib.load(ETA_MODEL_PATH)
            self.scaler = joblib.load(ETA_SCALER_PATH)
            self.encoders = joblib.load(ETA_ENCODERS_PATH)
            self.ready = True
            return
        self._train(df)

    def _fit_encoders(self, df: pd.DataFrame) -> None:
        for col in CAT_COLS:
            le = LabelEncoder()
            le.fit(df[col].astype(str))
            self.encoders[col] = le

    def _encode(self, df: pd.DataFrame) -> pd.DataFrame:
        feat = df.copy()
        for col in CAT_COLS:
            le = self.encoders.get(col)
            if le is None:
                feat[f"{col}_enc"] = 0
                continue
            known = set(le.classes_)
            feat[f"{col}_enc"] = feat[col].astype(str).apply(
                lambda x, _le=le, _k=known: int(_le.transform([x])[0]) if x in _k else 0
            )
        return feat

    def _build_X(self, feat: pd.DataFrame) -> np.ndarray:
        cols = [f"{c}_enc" for c in CAT_COLS] + NUM_COLS
        return feat[cols].fillna(0).values.astype(float)

    def _actual_transit_hours(self, df: pd.DataFrame) -> np.ndarray:
        # Ground truth = transit_days * 24 + delay_hours for delivered rows
        return (df["transit_days"].values * 24.0 + df["delay_hours"].values).astype(float)

    def _train(self, df: pd.DataFrame) -> None:
        train_df = df[df["status"] == "delivered"].copy()
        if len(train_df) < 20:
            return

        self._fit_encoders(df)
        feat = self._encode(train_df)
        X_raw = self._build_X(feat)

        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(X_raw)
        y = self._actual_transit_hours(train_df)

        self.model = RandomForestRegressor(
            n_estimators=120,
            max_depth=14,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X, y)

        joblib.dump(self.model, ETA_MODEL_PATH)
        joblib.dump(self.scaler, ETA_SCALER_PATH)
        joblib.dump(self.encoders, ETA_ENCODERS_PATH)
        self.ready = True

    def _predict_hours(self, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """Returns (mean_hours, std_hours) per row."""
        if not self.ready or self.model is None or self.scaler is None:
            mean = (df["transit_days"].values * 24.0).astype(float)
            return mean, np.full_like(mean, 12.0)

        feat = self._encode(df)
        X = self.scaler.transform(self._build_X(feat))
        per_tree = np.array([t.predict(X) for t in self.model.estimators_])
        mean = per_tree.mean(axis=0)
        std = per_tree.std(axis=0)
        # Floor std so degenerate forests still produce a sensible band.
        std = np.maximum(std, 1.0)
        return mean, std

    @staticmethod
    def _parse_ship_date(value: str) -> Optional[datetime]:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    def predict_eta(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds predicted_eta, predicted_eta_lower, predicted_eta_upper, and
        eta_confidence_hours columns (ISO-formatted timestamps + numeric band).
        """
        result = df.copy()
        mean, std = self._predict_hours(result)
        # 95% CI ≈ 1.96σ; clamp lower bound to ship_date (no negative transit).
        lower = np.maximum(mean - 1.96 * std, 0.0)
        upper = mean + 1.96 * std

        eta, eta_lo, eta_hi = [], [], []
        for ship_date_str, m, lo, hi in zip(
            result["ship_date"].astype(str).values, mean, lower, upper
        ):
            base = self._parse_ship_date(ship_date_str)
            if base is None:
                eta.append(None)
                eta_lo.append(None)
                eta_hi.append(None)
                continue
            eta.append((base + timedelta(hours=float(m))).strftime("%Y-%m-%d %H:%M"))
            eta_lo.append((base + timedelta(hours=float(lo))).strftime("%Y-%m-%d %H:%M"))
            eta_hi.append((base + timedelta(hours=float(hi))).strftime("%Y-%m-%d %H:%M"))

        result["predicted_transit_hours"] = np.round(mean, 1)
        result["predicted_eta"] = eta
        result["predicted_eta_lower"] = eta_lo
        result["predicted_eta_upper"] = eta_hi
        result["eta_confidence_hours"] = np.round(1.96 * std, 1)
        return result


eta_predictor = ETAPredictor()
