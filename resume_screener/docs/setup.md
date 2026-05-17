# Setup and Development

## Backend

1. Create and activate a Python virtual environment:

```powershell
cd resume_screener
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install backend dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3. Start the backend API:

```powershell
python app.py
```

The Flask API will listen on `http://127.0.0.1:5000`.

### Stable dev server (recommended when testing from external processes)

If you need the running process to bind a predictable socket (for example to avoid the Flask reloader creating a separate process that can cause external 404s), use the included WSGI runner:

```powershell
cd resume_screener
python run_server.py
# To change host/port: set HOST and PORT environment variables
```

The `run_server.py` script uses `wsgiref.simple_server` and defaults to port `5001` to avoid interfering with other local services.

## Frontend

1. Change into the frontend folder:

```bash
cd frontend
```

2. Install Node dependencies:

```bash
npm install
```

3. Start the React development server:

```bash
npm run dev
```

If you do not have Node installed system-wide, do not commit any locally downloaded Node runtime or `node_modules` into Git — the repository ignores `.local/` and `frontend/node_modules/` via `.gitignore`.

## Notes

- The backend exposes `/api` endpoints.
- The React frontend can be configured with `VITE_API_BASE` when accessing a backend on another host or port.
