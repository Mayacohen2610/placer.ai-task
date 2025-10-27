# Developer Quick Start

Short, copyable commands to get the project running locally for the interview.

Backend (Bash):
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000
```

Backend (Windows cmd):
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

Quick checks:
- `curl http://localhost:8000/api/pois`
- `curl http://localhost:8000/api/summary`

Useful helpers added in this repo:
- `backend/load_csv.py` — CSV -> POST `/api/ingest` (supports `--dry-run`).
- `backend/tests/test_api.py` — minimal pytest smoke tests for the API.

If you want, run these before the interview to ensure everything is installed and working.
