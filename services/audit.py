"""Append-only local audit events, suitable for a mounted deployment volume."""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from config import LOG_DIR

_logger = logging.getLogger("rackmind.audit")
_path = Path(LOG_DIR) / "audit.jsonl"


def record(event, actor="anonymous", details=None):
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "actor": actor, "details": details or {}}
    try:
        _path.parent.mkdir(exist_ok=True)
        with _path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
    except OSError:
        _logger.exception("Unable to write audit event")
