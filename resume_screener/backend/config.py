import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "screener.db"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = set(
        os.environ.get("ALLOWED_EXTENSIONS", "pdf,docx,txt").split(",")
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    PREFERRED_URL_SCHEME = "https"


UPLOAD_FOLDER = Config.UPLOAD_FOLDER
DB_PATH = Config.DB_PATH
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
MAX_CONTENT_LENGTH = Config.MAX_CONTENT_LENGTH
