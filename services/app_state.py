"""
RackMind AI

Small persistent state store for the latest analyzed telemetry.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import DATA_DIR


STATE_FILE = DATA_DIR / "runtime_state.json"


def load_runtime_state() -> dict:
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_runtime_state(**updates) -> dict:
    state = load_runtime_state()
    state.update(updates)
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8",
    )

    return state


def replace_runtime_state(**updates) -> dict:
    state = {
        **updates,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8",
    )

    return state


def clear_runtime_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    safe_df = df.copy()

    for column in safe_df.columns:
        if pd.api.types.is_datetime64_any_dtype(safe_df[column]):
            safe_df[column] = safe_df[column].astype(str)

    return safe_df.to_dict(orient="records")


def records_to_dataframe(records: list[dict] | None) -> pd.DataFrame | None:
    if not records:
        return None

    return pd.DataFrame(records)
