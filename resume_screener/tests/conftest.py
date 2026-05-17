import os
from pathlib import Path

import pytest

import backend.config as backend_config
import backend.db as backend_db
from backend import create_app


@pytest.fixture(autouse=True)
def app(tmp_path, monkeypatch):
    db_path = tmp_path / "test_screener.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    monkeypatch.setattr(backend_config, "DB_PATH", str(db_path))
    monkeypatch.setattr(backend_config, "UPLOAD_FOLDER", str(upload_dir))

    backend_db.init_db()
    application = create_app()
    application.testing = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
