## Quick orientation

This repository is a minimal fullstack demo: a FastAPI backend (SQLite) and a Vite + React frontend (Recharts). The frontend fetches data from `/api/*` which is proxied to the backend during development.

Keep answers tightly scoped to discoverable code. Reference the exact files listed below when suggesting edits or implementing features.

### Key files
- `backend/src/app.py` — entire backend (FastAPI) and DB initialization.
- `backend/README.md` — backend run instructions.
- `frontend/src/App.jsx` — main UI, data fetching and state.
- `frontend/src/components/Filters.jsx` and `VisitsChart.jsx` — UI patterns and data shapes.
- `frontend/package.json` & `README.md` — frontend dev scripts and stack.

## Big-picture architecture (what to know)
- Backend: single FastAPI app that creates/uses `backend/src/data.db` (SQLite). DB is seeded on startup in `init_db()`.
- Frontend: Vite + React using built-in proxy to forward `/api/*` to the backend. UI fetches `/api/pois`, `/api/visits`, and `/api/summary`.
- Data flow: UI builds query params (poi, date_from, date_to) and calls `/api/summary` and `/api/visits`; backend runs SQL against `visits` table and returns JSON.

## Developer workflows / commands
- Backend (from `backend/`):
  - Create venv and install: `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`) then `pip install -r requirements.txt`.
  - Run: `uvicorn src.app:app --reload --port 8000` — backend listens on port 8000 and seeds DB on startup.
- Frontend (from `frontend/`):
  - `npm install`
  - `npm run dev` — Vite dev server (default port 5173). It proxies `/api/*` to the backend so UI fetches use `/api/` paths directly.

## Important patterns & conventions (project-specific)
- Single-file backend: most logic (DB schema, seed data, endpoints) is in `backend/src/app.py`. When modifying API behavior, edit this file directly.
- API query params use snake_case names: `date_from`, `date_to`, `poi`. The frontend sends `poi=All` to mean no filter; the backend checks `poi.lower() != "all"` to filter.
- Date format: `YYYY-MM-DD` (validated by `datetime.strptime` in `/api/ingest` and used in queries).
- Ingest shape: POST `/api/ingest` expects a JSON array of rows like: `{ "poi": "Mall A", "date": "2025-10-18", "visitors": 120, "cbg": "...", "dma": "...", "dwell": 23.5 }`.
- DB concurrency: SQLite is opened with `check_same_thread=False` which lowers thread restrictions but still treat SQLite as a local file DB (no cross-process concurrency expectations).

## Integration points & externals
- SQLite file: `backend/src/data.db` (auto-created).
- Vite proxy: frontend expects `/api/*` to be proxied to `http://localhost:8000` when running `npm run dev`.
- Third-party libs in use:
  - Backend: FastAPI, uvicorn.
  - Frontend: React, Vite, Recharts.

## Concrete examples from the codebase (copy/paste-ready)
- Fetch POIs (frontend): `fetch('/api/pois').then(r => r.json())` — use this path as-is when adding features.
- SQL pattern (backend): parameterized queries using `?` placeholders. Example: `cur.execute("SELECT poi, date, visitors, cbg, dma, dwell FROM visits WHERE poi = ? AND date >= ?", params)` — follow this style for safety.

## What to watch for when editing
- Because backend is single-file and seeds DB on startup, avoid adding heavy startup work that slows development cycles.
- Frontend assumes the backend returns arrays and numeric fields exactly as seeded (e.g., `visitors` is an integer). Keep the response shape backward-compatible when changing endpoints.

## Where to look to extend or debug
- Backend errors surface in the uvicorn logs. For bad ingest rows the endpoint returns HTTP 400 with `detail` containing the row and error.
- UI network issues: open browser DevTools network tab; Vite will proxy `/api/*` calls — CORS is wide-open in backend so CORS is not a blocker.

---
If you want, I can (1) merge this with an existing `.github/copilot-instructions.md` if you have one, (2) inject short examples into `backend/README.md`, or (3) expand the instructions to include small preferred PR/commit conventions for this project. What would you like next?
