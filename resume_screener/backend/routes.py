import json
import os
from datetime import datetime, timezone

from flask import Blueprint, Flask, current_app, jsonify, request

from backend import config
from backend.db import get_db_connection, init_db
from backend.extractors import allowed_file, extract_text
from backend.nlp import compute_match, get_grade
from backend.utils import safe_filename

bp = Blueprint("main", __name__, url_prefix="/api")


@bp.route("/")
def index():
    return jsonify(
        {
            "service": "ResumeIQ API",
            "endpoints": ["/api/screen", "/api/history", "/api/screening/<id>", "/api/health"],
            "status": "ok",
        }
    )


@bp.route("/screen", methods=["POST"])
def screen():
    job_title = (request.form.get("job_title") or "Untitled Role").strip()
    job_description = (request.form.get("job_description") or "").strip()
    files = request.files.getlist("resumes")

    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    if not files or all(upload.filename == "" for upload in files):
        return jsonify({"error": "Please upload at least one resume."}), 400

    results = []
    skipped = []

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO screenings (job_title, job_description, created_at) VALUES (?, ?, ?)",
            (job_title, job_description, datetime.now(timezone.utc).isoformat()),
        )
        screening_id = cursor.lastrowid

        for uploaded_file in files:
            if not uploaded_file or not uploaded_file.filename:
                continue

            if not allowed_file(uploaded_file.filename):
                skipped.append(uploaded_file.filename)
                continue

            filename = safe_filename(uploaded_file.filename)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

            try:
                uploaded_file.save(filepath)
            except Exception:
                skipped.append(uploaded_file.filename)
                continue

            raw_text = extract_text(filepath)
            if len(raw_text) < 20:
                skipped.append(f"{uploaded_file.filename} (unreadable)")
                continue

            score, matched, missing, experience_years, experience_level = compute_match(
                job_description, raw_text
            )
            word_count = len(raw_text.split())

            cursor.execute(
                """INSERT INTO candidates
                   (screening_id, filename, raw_text, match_score, matched_skills, missing_skills, word_count, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    screening_id,
                    uploaded_file.filename,
                    raw_text[:5000],
                    score,
                    json.dumps(matched, ensure_ascii=False),
                    json.dumps(missing, ensure_ascii=False),
                    word_count,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            results.append(
                {
                    "filename": uploaded_file.filename,
                    "score": score,
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "word_count": word_count,
                    "experience_years": experience_years,
                    "experience_level": experience_level,
                    "grade": get_grade(score),
                }
            )

        if not results:
            message = "No readable resumes were found."
            if skipped:
                message += f' Files skipped: {", ".join(skipped)}. Ensure files are valid PDF/DOCX/TXT.'
            return jsonify({"error": message}), 400

        results.sort(key=lambda item: item["score"], reverse=True)
        for index, item in enumerate(results, start=1):
            item["rank"] = index

        conn.commit()

    return jsonify(
        {
            "results": results,
            "screening_id": screening_id,
            "job_title": job_title,
            "skipped": skipped,
        }
    )


@bp.route("/history")
def history():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.id, s.job_title, s.created_at,
                      COUNT(c.id) AS total,
                      MAX(c.match_score) AS top_score
               FROM screenings s
               LEFT JOIN candidates c ON s.id = c.screening_id
               GROUP BY s.id
               ORDER BY s.created_at DESC
               LIMIT 10"""
        )
        rows = cursor.fetchall()

    return jsonify(
        [
            {
                "id": row["id"],
                "job_title": row["job_title"],
                "created_at": row["created_at"][:10],
                "total": row["total"],
                "top_score": round(row["top_score"] or 0.0, 1),
            }
            for row in rows
        ]
    )


@bp.route("/screening/<int:screening_id>")
def screening_detail(screening_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, job_title, job_description, created_at FROM screenings WHERE id = ?",
            (screening_id,),
        )
        screening = cursor.fetchone()
        if not screening:
            return jsonify({"error": "Screening not found."}), 404

        cursor.execute(
            """SELECT filename, match_score, matched_skills, missing_skills, word_count
               FROM candidates
               WHERE screening_id = ?
               ORDER BY match_score DESC""",
            (screening_id,),
        )
        candidates = cursor.fetchall()

    return jsonify(
        {
            "screening_id": screening["id"],
            "job_title": screening["job_title"],
            "job_description": screening["job_description"],
            "created_at": screening["created_at"],
            "results": [
                {
                    "filename": candidate["filename"],
                    "score": round(candidate["match_score"] or 0.0, 1),
                    "matched_skills": json.loads(candidate["matched_skills"] or "[]"),
                    "missing_skills": json.loads(candidate["missing_skills"] or "[]"),
                    "word_count": candidate["word_count"],
                    "grade": get_grade(round(candidate["match_score"] or 0.0, 1)),
                }
                for candidate in candidates
            ],
        }
    )


@bp.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "uploads_folder_exists": os.path.exists(
                current_app.config["UPLOAD_FOLDER"]
            ),
            "db_exists": os.path.exists(current_app.config["DB_PATH"]),
            "active_env": os.environ.get("FLASK_ENV", "production"),
        }
    )


def create_app(test_config: dict | None = None):
    app = Flask(__name__)
    app.config.from_object(config.Config)
    app.config["DB_PATH"] = config.DB_PATH
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
    app.config["ALLOWED_EXTENSIONS"] = config.ALLOWED_EXTENSIONS
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    init_db()

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Content-Type,Authorization"
        return response

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return (
            jsonify(
                {"error": "One or more uploaded files exceed the maximum allowed size."}
            ),
            413,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        current_app.logger.exception("Unhandled exception occurred")
        return jsonify({"error": "An internal server error occurred."}), 500

    app.register_blueprint(bp)
    return app
