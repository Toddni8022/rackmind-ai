"""
RackMind AI

Historical Incident Parser

Parses the dashed-delimited historical incident log into structured
records and provides keyword search over them.
"""

import re
from pathlib import Path

HISTORY_FILE = Path("data/incident_history.txt")

_DELIMITER = re.compile(r"-{3,}")


def _clean_lines(block: str) -> list[str]:
    return [line.strip() for line in block.splitlines() if line.strip()]


def _parse_record(block: str) -> dict | None:
    lines = _clean_lines(block)

    if not lines:
        return None

    record = {
        "id": lines[0],
        "rack": "",
        "symptoms": [],
        "resolution": [],
        "status": "",
    }

    section = None

    for line in lines[1:]:
        lower = line.lower()

        if lower.startswith("rack:"):
            record["rack"] = line.split(":", 1)[1].strip()
            section = None
        elif lower == "symptoms:":
            section = "symptoms"
        elif lower == "resolution:":
            section = "resolution"
        elif lower == "status:":
            section = "status"
        elif section == "status":
            record["status"] = line
        elif section in ("symptoms", "resolution"):
            record[section].append(line)

    return record


def parse_incident_history(text: str) -> list[dict]:
    """Parse the dashed-delimited incident history format into records."""

    records = []

    for block in _DELIMITER.split(text):
        record = _parse_record(block)

        if record:
            records.append(record)

    return records


def load_incident_history() -> list[dict]:
    """Load and parse data/incident_history.txt, if present."""

    if not HISTORY_FILE.exists():
        return []

    return parse_incident_history(
        HISTORY_FILE.read_text(encoding="utf-8", errors="ignore")
    )


def search_incident_history(
    query: str,
    records: list[dict] | None = None,
) -> list[dict]:
    """Keyword search over historical incidents by rack, symptom, or resolution."""

    records = load_incident_history() if records is None else records

    terms = {term.lower() for term in query.split() if len(term) >= 3}

    if not terms:
        return records

    scored = []

    for record in records:
        haystack = " ".join(
            [record["id"], record["rack"], record["status"]]
            + record["symptoms"]
            + record["resolution"]
        ).lower()

        score = sum(1 for term in terms if term in haystack)

        if score > 0:
            scored.append((score, record))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [record for _, record in scored]
