"""Shared test fixtures: point SQLite at a throwaway file before app.db loads."""
import os
import tempfile
from pathlib import Path

_tmp = Path(tempfile.gettempdir()) / "triage_test.db"
if _tmp.exists():
    try:
        _tmp.unlink()
    except OSError:
        pass
os.environ["APP_DB_PATH"] = str(_tmp)
