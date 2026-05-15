# ResumeIQ — AI-Powered Resume Screener

Built by **Badri Narayanan** | Python · Flask · NLTK · Scikit-learn · SQLite3

---

## What It Does
- Upload multiple resumes (PDF, DOCX, TXT)
- Paste a job description
- AI ranks candidates by match score using:
  - **TF-IDF Vectorization** — keyword importance scoring
  - **Cosine Similarity** — semantic matching between JD and resume
  - **Skill Gap Analysis** — matched vs missing skills
- Stores all screening history in SQLite3
- Clean dark-themed web UI built with Flask

---

## Setup & Run (Local)

### Step 1 — Make sure Python is installed
```
python --version   # should be 3.9+
```

### Step 2 — Open terminal in this folder
```
cd resume_screener
```

### Step 3 — Create virtual environment (recommended)
```
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 4 — Install dependencies
```
pip install -r requirements.txt
```

### Step 5 — Run the app
```
python app.py
```

### Step 6 — Open in browser
```
http://localhost:5000
```

---

## Project Structure
```
resume_screener/
├── app.py               ← Main Flask backend (NLP logic, routes, DB)
├── requirements.txt     ← Python dependencies
├── screener.db          ← SQLite3 database (auto-created on first run)
├── uploads/             ← Uploaded resumes stored here
└── templates/
    └── index.html       ← Full frontend (HTML + CSS + JS)
```

---

## Tech Stack (for resume)
| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Web Framework | Flask |
| NLP | NLTK (tokenization, lemmatization, stopwords) |
| ML Algorithm | Scikit-learn (TF-IDF, Cosine Similarity) |
| Database | SQLite3 |
| File Parsing | PyPDF2, docx2txt |
| Frontend | HTML5, CSS3, Vanilla JS |
| Data Processing | NumPy, Pandas |

---

## How the Scoring Works
```
Final Score = (TF-IDF Cosine Similarity × 0.6) + (Skill Overlap Score × 0.4)

Score ≥ 75  → Excellent Match  🟢
Score ≥ 55  → Good Match       🔵
Score ≥ 35  → Average Match    🟡
Score < 35  → Low Match        🔴
```

---

## GitHub Upload Steps
1. Create a new repo on github.com named `resume-screener-ai`
2. Run:
```
git init
git add .
git commit -m "Initial commit — AI Resume Screener"
git remote add origin https://github.com/YOUR_USERNAME/resume-screener-ai.git
git push -u origin main
```
3. Add this to your resume: `github.com/YOUR_USERNAME/resume-screener-ai`
