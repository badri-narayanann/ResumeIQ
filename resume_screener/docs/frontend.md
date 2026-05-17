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

## Troubleshooting

If the `npm` command is not recognized (for example you see "'npm' is not recognized as an internal or external command" on Windows or "npm: command not found" on Linux/macOS), Node.js is not installed or not available on your `PATH`.

Quick fixes:

- **Windows**
	- Install Node.js (LTS) from https://nodejs.org/en/download/ or use `winget`:

```powershell
winget install --id OpenJS.NodeJS.LTS -e
```

	- Alternatively use Chocolatey (requires admin):

```powershell
choco install nodejs-lts
```

	- If you prefer version managers, use nvm-windows: https://github.com/coreybutler/nvm-windows

- **macOS**

```bash
brew install node
```

- **Linux (Debian/Ubuntu)**

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

After installing, restart your terminal and verify with `node -v` and `npm -v`.

Then from the `frontend/` folder run:

```bash
npm install
npm run dev
```

If you cannot install Node system-wide, consider using a version manager like `nvm` or a portable Node binary. This repository ignores local Node runtimes under `.local/` (see `.gitignore`) so a locally-extracted Node can be used for development without committing it to Git.
