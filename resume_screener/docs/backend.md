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
