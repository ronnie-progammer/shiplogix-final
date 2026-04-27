"""ML engine: delay prediction (RandomForest) + anomaly detection (IsolationForest)."""
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
RF_PATH = os.path.join(ARTIFACTS_DIR, "delay_predictor.joblib")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.joblib")
ENCODERS_PATH = os.path.join(ARTIFACTS_DIR, "encoders.joblib")

CAT_COLS = ["carrier", "origin", "destination", "weather_region"]


class MLEngine:
    def __init__(self):
        self.rf_model = None
        self.scaler = None
        self.encoders: dict[str, LabelEncoder] = {}
        self.ready = False
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    def load_or_train(self, df: pd.DataFrame) -> None:
        if os.path.exists(RF_PATH):
            self.rf_model = joblib.load(RF_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            self.encoders = joblib.load(ENCODERS_PATH)
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
        cols = [f"{c}_enc" for c in CAT_COLS] + ["transit_days", "month"]
        return feat[cols].fillna(0).values.astype(float)

    def _train(self, df: pd.DataFrame) -> None:
        train_df = df[df["status"] == "delivered"].copy()
        if len(train_df) < 10:
            return

        self._fit_encoders(df)
        feat = self._encode(train_df)
        X_raw = self._build_X(feat)

        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(X_raw)

        y = (train_df["delay_hours"] > 4).astype(int).values
        self.rf_model = RandomForestClassifier(
            n_estimators=100, random_state=42, class_weight="balanced"
        )
        self.rf_model.fit(X, y)

        joblib.dump(self.rf_model, RF_PATH)
        joblib.dump(self.scaler, SCALER_PATH)
        joblib.dump(self.encoders, ENCODERS_PATH)
        self.ready = True

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        if not self.ready or self.rf_model is None:
            result["delay_risk_score"] = np.random.uniform(0, 1, len(df))
        else:
            feat = self._encode(df)
            X_raw = self._build_X(feat)
            X = self.scaler.transform(X_raw)
            result["delay_risk_score"] = self.rf_model.predict_proba(X)[:, 1]

        result["risk_label"] = result["delay_risk_score"].apply(
            lambda x: "High" if x > 0.65 else ("Medium" if x > 0.35 else "Low")
        )
        return result

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        feat = self._encode(df) if self.encoders else df.copy()
        num_cols = [f"{c}_enc" for c in CAT_COLS] + ["transit_days", "month"]
        available = [c for c in num_cols if c in feat.columns]
        X_raw = feat[available].fillna(0)
        delay_col = df["delay_hours"].fillna(0).reset_index(drop=True)
        X_combined = pd.concat([X_raw.reset_index(drop=True), delay_col], axis=1)

        scaler = StandardScaler()
        X = scaler.fit_transform(X_combined.values.astype(float))

        iso = IsolationForest(contamination=0.08, random_state=42)
        preds = iso.fit_predict(X)

        result = df.copy()
        result["is_anomaly"] = preds == -1
        return result


ml_engine = MLEngine()
