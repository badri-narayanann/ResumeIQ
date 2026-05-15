import os
import re
import sqlite3
import json
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# ── SAFE IMPORTS ──────────────────────────────────────────────────────────────
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    NLTK_OK = True
except Exception as e:
    NLTK_OK = False
    print(f"[WARN] NLTK not available: {e}")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_OK = True
except Exception as e:
    SKLEARN_OK = False
    print(f"[WARN] Scikit-learn not available: {e}")

try:
    import PyPDF2
    PYPDF2_OK = True
except Exception as e:
    PYPDF2_OK = False
    print(f"[WARN] PyPDF2 not available: {e}")

try:
    import docx2txt
    DOCX_OK = True
except Exception as e:
    DOCX_OK = False
    print(f"[WARN] docx2txt not available: {e}")

app = Flask(__name__)

# ── UPLOADS FOLDER (auto-create) ──────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screener.db')

# ── DATABASE ──────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT, job_description TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        screening_id INTEGER, filename TEXT, raw_text TEXT,
        match_score REAL, matched_skills TEXT, missing_skills TEXT,
        word_count INTEGER, created_at TEXT,
        FOREIGN KEY(screening_id) REFERENCES screenings(id))''')
    conn.commit()
    conn.close()

init_db()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""
    try:
        if ext == 'pdf' and PYPDF2_OK:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + " "
        elif ext == 'docx' and DOCX_OK:
            text = docx2txt.process(filepath) or ""
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
    except Exception as e:
        print(f"[ERROR] extract_text {filepath}: {e}")
    return text.strip()

def clean_text(text):
    if not text:
        return ""
    try:
        if NLTK_OK:
            lemmatizer = WordNetLemmatizer()
            stop_words = set(stopwords.words('english'))
            text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
            tokens = word_tokenize(text)
            return ' '.join([lemmatizer.lemmatize(t) for t in tokens
                             if t not in stop_words and len(t) > 2])
        else:
            return re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    except Exception as e:
        print(f"[ERROR] clean_text: {e}")
        return text.lower()

SKILL_KEYWORDS = [
    'python','sql','java','javascript','html','css','react','flask','django',
    'machine learning','deep learning','nlp','data analysis','power bi',
    'tableau','excel','pandas','numpy','scikit-learn','tensorflow','pytorch',
    'git','github','docker','aws','azure','mysql','postgresql','mongodb',
    'sqlite','rest api','linux','data visualization','statistics','regression',
    'classification','neural network','computer vision','langchain','openai',
    'llm','spark','hadoop','etl','agile','scrum','communication',
    'problem solving','teamwork','leadership','c++','r programming',
    'opencv','matplotlib','seaborn','jupyter','colab','vscode'
]

def extract_skills(text):
    t = text.lower()
    return [s for s in SKILL_KEYWORDS if s in t]

def compute_match(jd_text, resume_text):
    jd_clean = clean_text(jd_text)
    resume_clean = clean_text(resume_text)
    similarity = 0.0
    if SKLEARN_OK and jd_clean and resume_clean:
        try:
            tfidf = TfidfVectorizer()
            mat = tfidf.fit_transform([jd_clean, resume_clean])
            similarity = float(cosine_similarity(mat[0:1], mat[1:2])[0][0])
        except Exception as e:
            print(f"[ERROR] TF-IDF: {e}")
    jd_skills = set(extract_skills(jd_text))
    resume_skills = set(extract_skills(resume_text))
    matched = jd_skills & resume_skills
    missing = jd_skills - resume_skills
    skill_score = len(matched) / len(jd_skills) if jd_skills else 0
    score = min(round((similarity * 0.6 + skill_score * 0.4) * 100, 1), 99.0)
    return score, list(matched), list(missing)

def get_grade(score):
    if score >= 75: return {'label': 'Excellent', 'color': '#10b981'}
    if score >= 55: return {'label': 'Good',      'color': '#3b82f6'}
    if score >= 35: return {'label': 'Average',   'color': '#f59e0b'}
    return           {'label': 'Low Match',       'color': '#ef4444'}

# ── ROUTES ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screen', methods=['POST'])
def screen():
    try:
        job_title = (request.form.get('job_title') or 'Untitled Role').strip()
        job_description = (request.form.get('job_description') or '').strip()
        files = request.files.getlist('resumes')

        if not job_description:
            return jsonify({'error': 'Job description is required.'}), 400
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'Please upload at least one resume.'}), 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO screenings (job_title,job_description,created_at) VALUES (?,?,?)',
                  (job_title, job_description, datetime.now().isoformat()))
        screening_id = c.lastrowid

        results, skipped = [], []

        for f in files:
            if not f or not f.filename:
                continue
            if not allowed_file(f.filename):
                skipped.append(f.filename)
                continue
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                f.save(filepath)
            except Exception as e:
                print(f"[ERROR] save {filename}: {e}")
                skipped.append(filename)
                continue

            raw_text = extract_text(filepath)
            if not raw_text or len(raw_text) < 20:
                skipped.append(filename + " (unreadable)")
                continue

            score, matched, missing = compute_match(job_description, raw_text)
            word_count = len(raw_text.split())
            c.execute('''INSERT INTO candidates
                (screening_id,filename,raw_text,match_score,
                 matched_skills,missing_skills,word_count,created_at)
                VALUES (?,?,?,?,?,?,?,?)''',
                (screening_id, filename, raw_text[:5000], score,
                 json.dumps(matched), json.dumps(missing),
                 word_count, datetime.now().isoformat()))
            results.append({
                'filename': filename, 'score': score,
                'matched_skills': matched, 'missing_skills': missing,
                'word_count': word_count, 'grade': get_grade(score)
            })

        conn.commit()
        conn.close()

        if not results:
            msg = "No readable resumes found."
            if skipped:
                msg += f" Files skipped: {', '.join(skipped)}. Ensure files are valid PDF/DOCX/TXT."
            return jsonify({'error': msg}), 400

        results.sort(key=lambda x: x['score'], reverse=True)
        for i, r in enumerate(results):
            r['rank'] = i + 1

        return jsonify({'results': results, 'screening_id': screening_id,
                        'job_title': job_title, 'skipped': skipped})

    except Exception as e:
        print(f"[ERROR] /screen: {traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/history')
def history():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT s.id, s.job_title, s.created_at,
                     COUNT(c.id), MAX(c.match_score)
                     FROM screenings s LEFT JOIN candidates c ON s.id=c.screening_id
                     GROUP BY s.id ORDER BY s.created_at DESC LIMIT 10''')
        rows = c.fetchall()
        conn.close()
        return jsonify([{'id':r[0],'job_title':r[1],'created_at':r[2][:10],
                         'total':r[3],'top_score':round(r[4] or 0,1)} for r in rows])
    except:
        return jsonify([])

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'nltk': NLTK_OK, 'sklearn': SKLEARN_OK,
        'pypdf2': PYPDF2_OK, 'docx2txt': DOCX_OK,
        'uploads_folder_exists': os.path.exists(UPLOAD_FOLDER),
        'db_exists': os.path.exists(DB_PATH)
    })

if __name__ == '__main__':
    print("\n✅ ResumeIQ starting...")
    print(f"   NLTK:      {'✓' if NLTK_OK     else '✗  pip install nltk'}")
    print(f"   Sklearn:   {'✓' if SKLEARN_OK  else '✗  pip install scikit-learn'}")
    print(f"   PyPDF2:    {'✓' if PYPDF2_OK   else '✗  pip install PyPDF2'}")
    print(f"   docx2txt:  {'✓' if DOCX_OK     else '✗  pip install docx2txt'}")
    print(f"   Uploads:   {UPLOAD_FOLDER}")
    print(f"\n🌐 Open http://localhost:5000\n")
    app.run(debug=True, port=5000)
