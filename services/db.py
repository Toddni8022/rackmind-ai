"""
RackMind AI

Shared SQLite Database Helper

All persistent features (incident archive, telemetry history,
users) share one SQLite database file so deployment stays simple.
"""

import os
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """
    Resolve the database location.

    RACKMIND_DB can override the default so tests and
    multi-instance deployments can isolate their data.
    """

    override = os.getenv("RACKMIND_DB")

    if override:
        return Path(override)

    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    return data_dir / "rackmind.db"


def get_connection() -> sqlite3.Connection:
    """
    Open a connection with row access by column name.
    """

    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row

    return connection
