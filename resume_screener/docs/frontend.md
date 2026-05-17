# React Frontend

The React frontend is located in `frontend/` and communicates with the Flask API via `/api/*` endpoints.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

By default, Vite runs on `http://localhost:5173`.

## Configuration

- `VITE_API_BASE` — optional base URL for the backend API.

Example `.env` file in `frontend/`:

```env
VITE_API_BASE=http://localhost:5000
```

## Features

- upload PDF, DOCX, and TXT resumes
- paste job description text
- review candidate ranking, matched skills, and missing skill gaps
- inspect prior screenings
