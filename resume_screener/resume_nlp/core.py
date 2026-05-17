import logging
import re

logger = logging.getLogger(__name__)

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    NLTK_OK = True
except Exception as exc:
    NLTK_OK = False
    logger.warning('NLTK unavailable: %s', exc)

try:
    import numpy as np
    import pandas as pd
    PANDAS_OK = True
except Exception as exc:
    np = None
    pd = None
    PANDAS_OK = False
    logger.warning('Pandas/NumPy unavailable: %s', exc)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_OK = True
except Exception as exc:
    SKLEARN_OK = False
    logger.warning('scikit-learn unavailable: %s', exc)

SKILL_KEYWORDS = [
    'python', 'sql', 'java', 'javascript', 'html', 'css', 'react', 'flask', 'django',
    'machine learning', 'deep learning', 'nlp', 'data analysis', 'power bi',
    'tableau', 'excel', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
    'git', 'github', 'docker', 'aws', 'azure', 'mysql', 'postgresql', 'mongodb',
    'sqlite', 'rest api', 'linux', 'data visualization', 'statistics', 'regression',
    'classification', 'neural network', 'computer vision', 'langchain', 'openai',
    'llm', 'spark', 'hadoop', 'etl', 'agile', 'scrum', 'communication',
    'problem solving', 'teamwork', 'leadership', 'c++', 'r programming',
    'opencv', 'matplotlib', 'seaborn', 'jupyter', 'colab', 'vscode'
]


def clean_text(text: str) -> str:
    if not text:
        return ''

    normalized = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    if NLTK_OK:
        try:
            lemmatizer = WordNetLemmatizer()
            stop_words = set(stopwords.words('english'))
            tokens = [tok for tok in re.split(r'\s+', normalized) if tok and len(tok) > 2]
            return ' '.join(
                lemmatizer.lemmatize(token)
                for token in tokens
                if token not in stop_words
            )
        except Exception as exc:
            logger.warning('NLTK text cleaning failed: %s', exc)

    return ' '.join(token for token in normalized.split() if len(token) > 2)


def extract_skills(text: str) -> list[str]:
    normalized = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    detected = []
    for skill in SKILL_KEYWORDS:
        pattern = rf'\b{re.escape(skill)}\b'
        if re.search(pattern, normalized):
            detected.append(skill)
    return detected


def extract_experience_years(text: str) -> float:
    normalized = text.lower()
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*\+?\s*years?', normalized)
    if matches:
        return max(float(value) for value in matches)
    if re.search(r'\bsenior\b', normalized):
        return 6.0
    if re.search(r'\b(mid[- ]level|lead)\b', normalized):
        return 4.0
    if re.search(r'\b(junior|entry|associate)\b', normalized):
        return 1.0
    return 0.0


def get_experience_level(years: float) -> str:
    if years >= 8:
        return 'Senior'
    if years >= 4:
        return 'Mid-level'
    if years >= 1:
        return 'Junior'
    return 'Unknown'


def compute_keyword_density(jd_text: str, resume_text: str) -> float:
    keywords = [word for word in re.findall(r'\w+', jd_text.lower()) if len(word) > 3]
    if not keywords:
        return 0.0

    resume_tokens = re.findall(r'\w+', resume_text.lower())
    if not resume_tokens:
        return 0.0

    matched = sum(1 for token in resume_tokens if token in keywords)
    density = matched / len(resume_tokens)
    return min(density, 1.0)


def compute_match(jd_text: str, resume_text: str) -> tuple[float, list[str], list[str], float, str]:
    jd_clean = clean_text(jd_text)
    resume_clean = clean_text(resume_text)
    similarity = 0.0

    if SKLEARN_OK and jd_clean and resume_clean:
        try:
            tfidf = TfidfVectorizer()
            matrix = tfidf.fit_transform([jd_clean, resume_clean])
            similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        except Exception as exc:
            logger.warning('TF-IDF similarity failed: %s', exc)

    jd_skills = set(extract_skills(jd_text))
    resume_skills = set(extract_skills(resume_text))
    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)
    skill_score = len(matched) / len(jd_skills) if jd_skills else 0.0
    experience_years = extract_experience_years(resume_text)
    experience_score = min(experience_years / 10.0, 1.0)
    keyword_density = compute_keyword_density(jd_text, resume_text)

    score = 0.0
    if PANDAS_OK:
        try:
            df = pd.DataFrame([
                {
                    'similarity': similarity,
                    'skill_score': skill_score,
                    'experience_score': experience_score,
                    'keyword_density': keyword_density,
                }
            ])
            base_weights = np.array([0.5, 0.5, 0.0, 0.0])
            base_score = float((df[['similarity', 'skill_score', 'experience_score', 'keyword_density']].to_numpy() * base_weights).sum(axis=1)[0] * 100)
            score = float(base_score + experience_score * 5 + keyword_density * 5)
        except Exception as exc:
            logger.warning('Pandas scoring fallback: %s', exc)
            score = (similarity * 0.5 + skill_score * 0.5) * 100 + experience_score * 5 + keyword_density * 5
    else:
        score = (similarity * 0.5 + skill_score * 0.5) * 100 + experience_score * 5 + keyword_density * 5

    score = round(max(0.0, min(score, 100.0)), 1)
    return score, matched, missing, experience_years, get_experience_level(experience_years)


def get_grade(score: float) -> dict[str, str]:
    if score >= 75:
        return {'label': 'Excellent', 'color': '#10b981'}
    if score >= 55:
        return {'label': 'Good', 'color': '#3b82f6'}
    if score >= 35:
        return {'label': 'Average', 'color': '#f59e0b'}
    return {'label': 'Low Match', 'color': '#ef4444'}
