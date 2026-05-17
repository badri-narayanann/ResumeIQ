import sqlite3

import backend.config as config


def get_db_connection():
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS screenings (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   job_title TEXT,
                   job_description TEXT,
                   created_at TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS candidates (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   screening_id INTEGER,
                   filename TEXT,
                   raw_text TEXT,
                   match_score REAL,
                   matched_skills TEXT,
                   missing_skills TEXT,
                   word_count INTEGER,
                   created_at TEXT,
                   FOREIGN KEY(screening_id) REFERENCES screenings(id))"""
        )
        conn.commit()
