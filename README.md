# Fullstack Foot-Traffic Starter (FastAPI + React)

**Goal:** ship a working dashboard in minutes during a timed assignment.

## Stack
- Backend: FastAPI + SQLite (seed data auto-created)
- Frontend: React + Vite + Recharts
- Proxy: Vite dev server → FastAPI

## Run locally

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
# http://localhost:5173  (calls /api/* proxied to :8000)
```

## Useful API endpoints
- `GET /api/pois`
- `GET /api/visits?poi=Gym%20C&date_from=2025-10-18&date_to=2025-10-20`
- `GET /api/summary?poi=Mall%20A`

## Notes
- DB is pre-seeded on first run; replace with your CSV by posting to `/api/ingest` or writing a quick loader.
- Keep scope small: 1 filter, 1 chart, 4 KPIs → iterate if time remains.