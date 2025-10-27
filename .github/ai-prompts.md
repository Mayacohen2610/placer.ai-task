# AI / Coding Agent Prompts (copyable)

Below are short, reusable prompts you can paste into your coding agent during the interview. Keep them focused — ask for a single small change per prompt.

1) Project summary (6 bullets)
```
You are my coding assistant. I'm working on a small FastAPI + React repo (backend: `backend/src/app.py`, frontend: `frontend/src`). Summarize endpoints, data model, and where the frontend fetches data (file: `frontend/src/App.jsx`) in 6 bullet points.
```

2) Add endpoint: POI totals
```
Add GET `/api/poi_totals` to `backend/src/app.py` returning [{"poi":..., "total_visitors":...}] per POI. Support optional `date_from` and `date_to` query params (YYYY-MM-DD). Use parameterized SQL (`?`) and match existing connection handling. Provide a minimal patch.
```

3) CSV loader helper
```
Create `backend/load_csv.py` that reads a CSV (headers: poi,date,visitors,cbg,dma,dwell) and POSTs JSON to `/api/ingest`. Support `--dry-run` to validate rows without posting. Use standard library only.
```

4) Frontend tweak: last 7 days
```
Modify `frontend/src/components/Filters.jsx` to add a "Last 7 days" button that sets `dateFrom` and `dateTo` appropriately. Keep styles consistent and return only the patch.
```

5) Quick tests
```
Add `backend/tests/test_api.py` using FastAPI TestClient with smoke tests for `/api/pois` and `/api/summary`. Keep tests minimal and runnable with `pytest -q` from `backend/`.
```

6) Validation / run step
```
After making code changes, run these commands locally and report any errors: `cd backend && source .venv/bin/activate && uvicorn src.app:app --reload --port 8000` and `curl http://localhost:8000/api/pois`.
```

---
Tip: ask for diffs/patches rather than full-file rewrites to avoid accidental broad edits.
