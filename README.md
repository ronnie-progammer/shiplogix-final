# ShipLogiz

AI-powered supply chain visibility platform. Real-time shipment tracking, carrier scorecards, route analytics, and ML-driven delay prediction + anomaly detection.

**Stack:** FastAPI · SQLAlchemy · SQLite → Postgres · RandomForest · IsolationForest · React 18 · Vite · Tailwind 3 · Recharts  
**Deploy:** Railway (backend) · Vercel (frontend)

---

## Quickstart

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py          # generates 800 shipments, trains ML, seeds DB
uvicorn main:app --reload
```

API runs at `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI runs at `http://localhost:5173`

---

## API Endpoints

| Route | Description |
|---|---|
| `GET /api/dashboard/stats` | KPIs: volume, on-time rate, risk breakdown |
| `GET /api/shipments/` | List shipments (filter: status, carrier, risk_label, date range) |
| `GET /api/shipments/{id}` | Single shipment detail |
| `GET /api/carriers/` | Carrier scorecards with on-time rates |
| `GET /api/routes/` | Route stats: volume, avg delay, on-time rate |
| `GET /api/deliveries/` | Delivered shipments — planned vs actual |
| `GET /api/anomalies/` | IsolationForest-flagged shipments |
| `GET /api/predictions/` | RandomForest delay risk scores |

---

## ML Models

| Model | Purpose | Algorithm |
|---|---|---|
| Delay Predictor | P(delay > 4h) per shipment | RandomForestClassifier (100 trees) |
| Anomaly Detector | Flag unusual patterns | IsolationForest (contamination=0.08) |

Models train on first `seed.py` run, then load from `backend/ml/artifacts/*.joblib`.  
Features: carrier, origin, destination, weather region, transit days, month.

---

## Deploy

### Railway (backend)

1. Create Railway project → link this repo → set root to `backend/`
2. Set env var: `CORS_ORIGINS=https://your-app.vercel.app`
3. Railway auto-detects `railway.json` — deploys on push

### Vercel (frontend)

1. Import repo → set root to `frontend/`
2. Set env var: `VITE_API_URL=https://your-backend.railway.app`
3. Vercel auto-detects Vite — deploys on push

---

## Phase 2 Roadmap

- [ ] Supabase auth + multi-tenancy (stub in `Navbar.jsx`)
- [ ] Stripe subscriptions (Free / Pro / Business)
- [ ] Resend anomaly alert emails
- [ ] Postgres swap (change `SQLALCHEMY_DATABASE_URL` in `database.py`)
- [ ] Live carrier API integrations (FedEx, UPS, project44)

---

*ShipLogiz — $30B+ logistics SaaS space. Built for supply chain teams who need answers, not dashboards.*
