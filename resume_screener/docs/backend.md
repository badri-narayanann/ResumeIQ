# Backend API

The backend is now an API-only Flask service located in `backend/`.

## Endpoints

- `GET /api/` — service metadata
- `POST /api/screen` — upload resumes and job description, returns ranked results
- `GET /api/history` — recent screening summaries
- `GET /api/screening/<id>` — detailed results for a previous screening
- `GET /api/health` — service health check

## Architecture

- `backend/config.py` — environment-driven settings for uploads, database, and request limits
- `backend/db.py` — SQLite initialization and connection helpers
- `backend/extractors.py` — PDF/DOCX/TXT resume text extraction logic
- `backend/nlp.py` — NLP interface for scoring and keyword extraction
- `backend/routes.py` — API route definitions and error handling
- `backend/utils.py` — upload filename sanitization

## Deployment Notes

- The backend is built to run as a standalone service.
- It can be started with `python app.py` from the repository root.
- For development, the React frontend runs separately on its own development server.
- The backend sets permissive CORS headers to allow cross-origin requests from the frontend.

## Run locally (development)

These steps will get the backend running on your local machine for development and testing.

1. Create and activate a Python virtual environment, then install dependencies:

```powershell
cd resume_screener
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
pip install --upgrade pip
pip install -r requirements.txt
```

Or on macOS / Linux:

```bash
cd resume_screener
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Prepare runtime directories and environment variables:

```powershell
# ensure uploads folder exists
mkdir uploads
# copy environment template and edit as needed
copy .env.example .env
```

3. Initialize the SQLite database (uses `backend.config.DB_PATH`):

```powershell
python -c "from backend.db import init_db; init_db()"
```

4. Start the backend (recommended: stable WSGI runner)

Use the included WSGI runner to bind directly to a socket (avoids Flask reloader process issues):

```powershell
# defaults to PORT=5001
python run_server.py
# or set custom host/port before running
$env:PORT='5002'; python run_server.py
```

Alternatively start the Flask development server for quick iteration:

```powershell
python app.py
```

5. Verify the health endpoint:

```powershell
curl http://127.0.0.1:5001/api/health
```

Notes:

- To override the database location, set `DB_PATH` in your environment or `.env` before initializing the DB.
- Ensure the process has write permission for the `uploads/` folder and the directory containing the SQLite file.
- For production deployments use a proper WSGI server and a process manager; `run_server.py` is intended as a simple, stable runner for local testing only.
