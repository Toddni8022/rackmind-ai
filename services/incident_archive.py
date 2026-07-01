"""
RackMind AI

Historical Incident Archive

Stores every generated incident report so operators can search
past incidents by rack, severity, timestamp, root cause, and
recommended fix.
"""

import re
from datetime import datetime

from services.db import get_connection

SEVERITIES = ("Low", "Medium", "High", "Critical")


def _ensure_schema(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            rack TEXT NOT NULL DEFAULT 'Unknown',
            severity TEXT NOT NULL DEFAULT 'Medium',
            root_cause TEXT NOT NULL DEFAULT '',
            recommended_fix TEXT NOT NULL DEFAULT '',
            report TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual'
        )
        """
    )
    connection.commit()


def _extract_section(report: str, heading: str) -> str:
    """
    Pull the text under a markdown heading such as '# Root Cause'
    out of a generated executive report.
    """

    pattern = re.compile(
        rf"^#+\s*{re.escape(heading)}\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    match = pattern.search(report)

    if not match:
        return ""

    rest = report[match.end():]

    next_heading = re.search(r"^#+\s+\S", rest, re.MULTILINE)

    if next_heading:
        rest = rest[: next_heading.start()]

    return rest.strip()


def extract_incident_fields(report: str) -> dict:
    """
    Best-effort extraction of rack, severity, root cause, and the
    recommended fix from a generated executive report.
    """

    root_cause = _extract_section(report, "Root Cause")

    recommended_fix = (
        _extract_section(report, "Recommended Actions")
        or _extract_section(report, "Recommended Next Steps")
        or _extract_section(report, "Recommended Fix")
    )

    severity = "Medium"

    priority = _extract_section(report, "Priority") or report

    for level in ("Critical", "High", "Medium", "Low"):
        if re.search(rf"\b{level}\b", priority, re.IGNORECASE):
            severity = level
            break

    rack_match = re.search(r"\bRack[-_ ]?(\w+)\b", report, re.IGNORECASE)

    rack = f"Rack-{rack_match.group(1)}" if rack_match else "Unknown"

    return {
        "rack": rack,
        "severity": severity,
        "root_cause": root_cause,
        "recommended_fix": recommended_fix,
    }


def save_incident(
    report: str,
    rack: str = None,
    severity: str = None,
    root_cause: str = None,
    recommended_fix: str = None,
    source: str = "manual",
    created_at: str = None,
) -> int:
    """
    Persist an incident. Fields not supplied are extracted from
    the report text. Returns the new incident id.
    """

    extracted = extract_incident_fields(report or "")

    row = {
        "created_at": created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rack": rack or extracted["rack"],
        "severity": severity or extracted["severity"],
        "root_cause": root_cause if root_cause is not None else extracted["root_cause"],
        "recommended_fix": (
            recommended_fix
            if recommended_fix is not None
            else extracted["recommended_fix"]
        ),
        "report": report or "",
        "source": source,
    }

    if row["severity"] not in SEVERITIES:
        row["severity"] = "Medium"

    with get_connection() as connection:
        _ensure_schema(connection)

        cursor = connection.execute(
            """
            INSERT INTO incidents
                (created_at, rack, severity, root_cause,
                 recommended_fix, report, source)
            VALUES
                (:created_at, :rack, :severity, :root_cause,
                 :recommended_fix, :report, :source)
            """,
            row,
        )

        connection.commit()

        return cursor.lastrowid


def search_incidents(
    rack: str = None,
    severity: str = None,
    start: str = None,
    end: str = None,
    root_cause_contains: str = None,
    fix_contains: str = None,
    text: str = None,
    limit: int = 200,
) -> list[dict]:
    """
    Search the archive. All filters are optional and combined
    with AND. Text filters are case-insensitive substrings.
    """

    query = "SELECT * FROM incidents WHERE 1=1"
    params = []

    if rack:
        query += " AND LOWER(rack) LIKE ?"
        params.append(f"%{rack.lower()}%")

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if start:
        query += " AND created_at >= ?"
        params.append(start)

    if end:
        query += " AND created_at <= ?"
        params.append(end)

    if root_cause_contains:
        query += " AND LOWER(root_cause) LIKE ?"
        params.append(f"%{root_cause_contains.lower()}%")

    if fix_contains:
        query += " AND LOWER(recommended_fix) LIKE ?"
        params.append(f"%{fix_contains.lower()}%")

    if text:
        query += " AND LOWER(report) LIKE ?"
        params.append(f"%{text.lower()}%")

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection() as connection:
        _ensure_schema(connection)

        rows = connection.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def get_incident(incident_id: int) -> dict | None:
    with get_connection() as connection:
        _ensure_schema(connection)

        row = connection.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident_id,),
        ).fetchone()

    return dict(row) if row else None


def delete_incident(incident_id: int) -> bool:
    with get_connection() as connection:
        _ensure_schema(connection)

        cursor = connection.execute(
            "DELETE FROM incidents WHERE id = ?",
            (incident_id,),
        )

        connection.commit()

        return cursor.rowcount > 0


def count_incidents() -> int:
    with get_connection() as connection:
        _ensure_schema(connection)

        row = connection.execute(
            "SELECT COUNT(*) AS total FROM incidents"
        ).fetchone()

    return row["total"]


def seed_sample_incidents() -> int:
    """
    Load a few demo incidents so the archive is useful before the
    first real report is generated. Returns how many were added.
    """

    if count_incidents() > 0:
        return 0

    samples = [
        {
            "created_at": "2026-06-21 18:15:00",
            "rack": "Rack-22",
            "severity": "Critical",
            "root_cause": (
                "Cooling degradation drove rack temperature past 90F, "
                "causing CRC errors and an interface reset on Gi1/0/12."
            ),
            "recommended_fix": (
                "Restore HVAC capacity, verify airflow at Rack-22, and "
                "replace the patch cable on Gi1/0/12."
            ),
            "report": (
                "# Executive Summary\nRack-22 overheated to 91F with "
                "correlated CRC errors and an interface reset.\n"
                "# Root Cause\nCooling degradation.\n"
                "# Recommended Actions\nRestore HVAC capacity.\n"
                "# Priority\nCritical"
            ),
            "source": "seed",
        },
        {
            "created_at": "2026-06-14 09:40:00",
            "rack": "Rack-07",
            "severity": "Medium",
            "root_cause": (
                "Intermittent CRC errors from a marginal optic on the "
                "uplink port."
            ),
            "recommended_fix": (
                "Swap the SFP optic and clean fiber connectors during "
                "the next maintenance window."
            ),
            "report": (
                "# Executive Summary\nRack-07 uplink logged intermittent "
                "CRC errors.\n# Root Cause\nMarginal optic.\n"
                "# Recommended Actions\nSwap the SFP optic.\n"
                "# Priority\nMedium"
            ),
            "source": "seed",
        },
        {
            "created_at": "2026-06-02 22:05:00",
            "rack": "Rack-14",
            "severity": "High",
            "root_cause": (
                "Power draw exceeded 4.5 kW after new servers were "
                "installed without capacity review."
            ),
            "recommended_fix": (
                "Rebalance load across feeds and update rack capacity "
                "records before further installs."
            ),
            "report": (
                "# Executive Summary\nRack-14 exceeded its power "
                "budget.\n# Root Cause\nUnreviewed capacity change.\n"
                "# Recommended Actions\nRebalance load across feeds.\n"
                "# Priority\nHigh"
            ),
            "source": "seed",
        },
    ]

    for sample in samples:
        save_incident(**sample)

    return len(samples)
