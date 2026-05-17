# ResumeIQ — API Backend + React Frontend

ResumeIQ is now split into a backend API and a React frontend.

- Backend: `backend/` contains the Flask API service.
- Frontend: `frontend/` contains the React UI built with Vite.
- Docs: `docs/` explains setup, API design, and development workflow.

## Repository Structure

```text
resume_screener/
├── backend/                # Flask API package
├── frontend/               # React frontend project
├── docs/                   # developer documentation and setup guides
├── README.md               # repository overview
├── requirements.txt        # backend Python dependencies
├── pyproject.toml          # packaging metadata
├── Dockerfile              # backend container build instructions
├── docker-compose.yml      # local backend deployment
├── .env.example            # environment variable template
├── tests/                  # backend pytest cases
└── app.py                  # root backend entrypoint
```

## Getting Started

### Backend

```powershell
cd resume_screener
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

The backend API will listen on `http://localhost:5000`.

### Frontend

```bash
cd resume_screener/frontend
npm install
npm run dev
```

The React app runs on `http://localhost:5173` by default.

## Development Notes

- Run a stable WSGI-backed server (avoids Flask auto-reloader spawning a separate process):

```powershell
cd resume_screener
# uses wsgiref to serve the application (default PORT=5001)
python run_server.py
```

- Alternatively continue using the Flask development server for quick iteration:

```powershell
python app.py
```

- Frontend dev server (Vite):

```powershell
cd resume_screener\frontend
npm install
npm run dev
```

- If you see unexpected 404s for `/api/health` when using the Flask dev server, try `run_server.py` which binds directly to the socket and avoids reloader process confusion.

- The legacy templates and static assets were archived to `resume_screener/legacy_frontend/` during the React migration.

## API Endpoints

The backend now exposes a dedicated `/api` prefix:

- `GET /api/` — service metadata
- `POST /api/screen` — submit resumes and a job description for scoring
- `GET /api/history` — recent screening summaries
- `GET /api/screening/<id>` — detailed screening results
- `GET /api/health` — health status

## Environment Variables

Use the `.env.example` template at the repository root.

- `HOST` — host to bind (default: `127.0.0.1`)
- `PORT` — port to listen on (default: `5000`)
- `FLASK_DEBUG` — enable debug mode with `1`
- `SECRET_KEY` — Flask secret key
- `UPLOAD_FOLDER` — custom upload directory
- `DB_PATH` — custom SQLite database path
- `MAX_CONTENT_LENGTH` — upload size limit in bytes
- `SESSION_COOKIE_SECURE` — enable secure cookies with `1`
- `VITE_API_BASE` — optional frontend API base URL

## Documentation

See the `docs/` folder for more detailed guides:

- `docs/setup.md` — local installation and development
- `docs/backend.md` — API backend architecture
- `docs/frontend.md` — React frontend setup
- `docs/testing.md` — automated testing

## Testing

Run the backend tests from the repository root:

```powershell
python -m pytest -q
```

## Docker

Build and run the backend container:

```bash
docker build -t resumeiq .
docker run -p 5000:5000 resumeiq
```

## Notes

- The backend is API-only and designed to serve React or other remote clients.
- CORS is enabled for frontend development.
- The React frontend is separate from the Flask backend and uses `/api/*` routes.
