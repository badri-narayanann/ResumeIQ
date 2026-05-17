import importlib
from pathlib import Path

import pytest

import backend.config as backend_config
import backend.routes as backend_routes
import config as config_module
import routes as routes_module


def test_config_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("UPLOAD_FOLDER", str(tmp_path / "uploads"))
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test_screener.db"))
    monkeypatch.setenv("MAX_CONTENT_LENGTH", "5242880")

    importlib.reload(backend_config)
    importlib.reload(backend_routes)
    importlib.reload(config_module)
    importlib.reload(routes_module)

    app = routes_module.create_app()

    assert app.config["UPLOAD_FOLDER"] == str(tmp_path / "uploads")
    assert app.config["DB_PATH"] == str(tmp_path / "test_screener.db")
    assert app.config["MAX_CONTENT_LENGTH"] == 5_242_880
    assert Path(app.config["UPLOAD_FOLDER"]).exists()
    assert Path(app.config["DB_PATH"]).parent.exists()
