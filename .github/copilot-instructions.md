## Quick orientation

This repository is a minimal fullstack demo: a FastAPI backend (SQLite) and a Vite + React frontend (Recharts). The frontend fetches data from `/api/*` which is proxied to the backend during development.

Keep answers tightly scoped to discoverable code. Reference the exact files listed below when suggesting edits or implementing features.

### Key files
This repo is a small fullstack demo: a FastAPI backend (SQLite) and a Vite + React frontend (Recharts). The frontend fetches data from `/api/*` which the Vite dev server proxies to the backend.
Keep fixes and feature work tightly scoped to the files below — the project intentionally keeps most server logic in a single backend file to make changes easy to find.
- `frontend/src/App.jsx` — main UI, data fetching and state.
- `frontend/src/components/Filters.jsx` and `VisitsChart.jsx` — UI patterns and data shapes.
`backend/src/app.py` — full backend: DB schema, seeding (init_db), and API endpoints; edit this file for server behavior.
`backend/load_csv.py` & `backend/sample.csv` — quick CSV ingestion helpers and examples.
`backend/src/data.db` — SQLite DB file created at runtime.
`frontend/src/App.jsx`, `frontend/src/main.jsx` — app entry and top-level data fetching/state.
`frontend/src/components/Filters.jsx`, `frontend/src/components/VisitsChart.jsx` — UI patterns and expected data shapes.
`tests/test_api.py` — lightweight API tests (pytest).
- Data flow: UI builds query params (poi, date_from, date_to) and calls `/api/summary` and `/api/visits`; backend runs SQL against `visits` table and returns JSON.

Backend: a single FastAPI app that seeds and queries `backend/src/data.db` on startup (see `init_db()` in `backend/src/app.py`). Keep startup light.
Frontend: Vite + React, runs on port 5173 and proxies `/api/*` to `http://localhost:8000` during development.
Data flow: UI builds query params (snake_case: `poi`, `date_from`, `date_to`) and calls `/api/pois`, `/api/visits`, and `/api/summary`. The backend translates those into parameterized SQL queries against `visits`.
  - Run: `uvicorn src.app:app --reload --port 8000` — backend listens on port 8000 and seeds DB on startup.
- Frontend (from `frontend/`):
Backend (from `backend/`):
  - Create venv and install deps:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

  - Run dev server (auto-seeds DB):

```bash
uvicorn src.app:app --reload --port 8000
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Tests (repo root):

```bash
pytest -q
```
- Date format: `YYYY-MM-DD` (validated by `datetime.strptime` in `/api/ingest` and used in queries).
- Ingest shape: POST `/api/ingest` expects a JSON array of rows like: `{ "poi": "Mall A", "date": "2025-10-18", "visitors": 120, "cbg": "...", "dma": "...", "dwell": 23.5 }`.
Single-file backend: most changes to API behavior happen in `backend/src/app.py` — search there first.
API params use snake_case. The frontend sends `poi=All` to mean no filtering; the backend checks `poi.lower() != 'all'`.
Date format: `YYYY-MM-DD` (validated in `/api/ingest`). Keep UI and API consistent.
SQL conventions: use parameterized `?` placeholders (see `backend/src/app.py`) to avoid injection and to match current code style.
Response shapes are relied upon by the frontend — `visitors` is an integer, `dwell` is numeric, and endpoints return arrays. Keep responses backward-compatible.
- Third-party libs in use:
  - Backend: FastAPI, uvicorn.
SQLite DB: `backend/src/data.db` (created/seeded by `init_db()` on server start).
Vite proxy: frontend dev server proxies `/api/*` to `http://localhost:8000` so frontend can call `/api/` paths directly in dev.
Ingest shape example (POST `/api/ingest`):

```json
[{ "poi": "Mall A", "date": "2025-10-18", "visitors": 120, "cbg": "...", "dma": "...", "dwell": 23.5 }]
```

## What to watch for when editing
Server logic and DB interactions: `backend/src/app.py` (single source of truth).
Add/adjust UI components: `frontend/src/components/*` and `frontend/src/App.jsx`.
Sample data and CSV loaders: `backend/sample.csv` and `backend/load_csv.py`.
Tests: `tests/test_api.py` — small, fast checks you can run after changes.

## Where to look to extend or debug
Avoid heavy startup tasks in the backend; the app seeds the DB at startup which is intended for dev convenience.
SQLite concurrency: opened with `check_same_thread=False` — OK for single-process dev but don't assume production-grade concurrency.
Keep changes small and preserve response shapes; the frontend parsing expects exact field types.

---
If anything above is unclear or you'd like a different structure (e.g., split backend into multiple files or expanded test coverage), tell me which parts you want expanded and I'll iterate.
