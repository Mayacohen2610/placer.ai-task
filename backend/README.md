# Backend (FastAPI)

## Quick start
```bash
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000
```

## API
- `GET /api/pois` → list of POIs
- `GET /api/visits?poi=Mall%20A&date_from=2025-10-18&date_to=2025-10-20`
- `GET /api/summary?poi=Cafe%20B`
- `POST /api/ingest` → JSON array of rows