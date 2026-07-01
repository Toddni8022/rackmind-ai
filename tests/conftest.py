"""
RackMind AI test fixtures.

Every test gets an isolated SQLite database via RACKMIND_DB so
tests never touch real archive/user/telemetry data.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("RACKMIND_DB", str(tmp_path / "test.db"))
    yield


@pytest.fixture
def sample_log_text():
    return (
        "2026-06-21 18:00:01 INFO Switch01 Boot complete\n"
        "2026-06-21 18:03:40 INFO Rack22 Temperature 72F\n"
        "2026-06-21 18:05:11 WARNING CRC error detected on Gi1/0/12\n"
        "2026-06-21 18:05:13 WARNING CRC error detected on Gi1/0/12\n"
        "2026-06-21 18:09:00 ERROR Temperature threshold exceeded (87F)\n"
        "2026-06-21 18:09:15 ERROR Interface Gi1/0/12 reset initiated\n"
        "2026-06-21 18:11:00 INFO Rack22 Temperature 91F\n"
    )
