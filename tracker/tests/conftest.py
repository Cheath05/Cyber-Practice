import os
import sys
from pathlib import Path

import pytest

TRACKER = Path(__file__).resolve().parent.parent
REPO = TRACKER.parent
sys.path.insert(0, str(TRACKER))


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Keep the module-level default app from touching the real home directory
    monkeypatch.setenv("CT_DB", str(tmp_path / "default.db"))
    monkeypatch.setenv("CT_TODAY", "2026-11-20")
    monkeypatch.delenv("CT_ALLOWED_LOGINS", raising=False)
    from fastapi.testclient import TestClient
    from cyber_tracker.main import create_app
    app = create_app(repo=REPO, db_path=tmp_path / "test.db")
    return TestClient(app)


HDR = {"X-Requested-With": "cyber-tracker"}
