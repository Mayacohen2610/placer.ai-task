.PHONY: backend run-backend run-frontend install-frontend test

backend:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run-backend:
	cd backend && . .venv/bin/activate && uvicorn src.app:app --reload --port 8000

run-frontend:
	cd frontend && npm install && npm run dev

test:
	cd backend && . .venv/bin/activate && pytest -q
