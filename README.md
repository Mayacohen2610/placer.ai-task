# Placer.ai task

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

### Quick run (windows only)
- `start-dev.bat`

## Useful API endpoints

