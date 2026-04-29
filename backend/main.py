import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import Base
from routers import anomalies, billing, carriers, dashboard, deliveries, eta, notifications, predictions, routes, shipments, tracking

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShipLogiz API",
    description="Logistics Tracking SaaS — AI-powered delay prediction & anomaly detection",
    version="1.0.0",
)

_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
_cors_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(shipments.router)
app.include_router(carriers.router)
app.include_router(routes.router)
app.include_router(deliveries.router)
app.include_router(anomalies.router)
app.include_router(predictions.router)
app.include_router(eta.router)
app.include_router(tracking.router)
app.include_router(billing.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"name": "ShipLogiz API", "version": "1.0.0", "status": "operational"}


@app.get("/health")
def health():
    return {"status": "ok"}
