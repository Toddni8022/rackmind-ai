"""
RackMind AI

Telemetry History Store

Keeps a rolling history of rack readings (temperature, humidity,
power, CRC errors, resets, health score) so the trend dashboard
can chart behavior over time and predict failures.
"""

from datetime import datetime

from services.db import get_connection

METRICS = (
    "temperature",
    "humidity",
    "power_kw",
    "crc_errors",
    "resets",
    "health_score",
)


def _ensure_schema(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at TEXT NOT NULL,
            rack TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            power_kw REAL,
            crc_errors REAL,
            resets REAL,
            health_score REAL,
            source TEXT NOT NULL DEFAULT 'upload'
        )
        """
    )
    connection.commit()


def record_reading(
    rack: str,
    recorded_at: str = None,
    temperature: float = None,
    humidity: float = None,
    power_kw: float = None,
    crc_errors: float = None,
    resets: float = None,
    health_score: float = None,
    source: str = "upload",
) -> int:
    with get_connection() as connection:
        _ensure_schema(connection)

        cursor = connection.execute(
            """
            INSERT INTO telemetry
                (recorded_at, rack, temperature, humidity, power_kw,
                 crc_errors, resets, health_score, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recorded_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                rack or "Unknown",
                temperature,
                humidity,
                power_kw,
                crc_errors,
                resets,
                health_score,
                source,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def record_readings(readings: list[dict]) -> int:
    """
    Bulk insert normalized connector readings.
    """

    count = 0

    for reading in readings:
        record_reading(
            rack=reading.get("rack", "Unknown"),
            recorded_at=reading.get("timestamp"),
            temperature=reading.get("temperature"),
            humidity=reading.get("humidity"),
            power_kw=reading.get("power_kw"),
            crc_errors=reading.get("crc_errors"),
            resets=reading.get("resets"),
            health_score=reading.get("health_score"),
            source=reading.get("source", "connector"),
        )

        count += 1

    return count


def get_history(rack: str = None, limit: int = 2000) -> list[dict]:
    query = "SELECT * FROM telemetry"
    params = []

    if rack:
        query += " WHERE rack = ?"
        params.append(rack)

    query += " ORDER BY recorded_at ASC"

    if limit:
        query = (
            f"SELECT * FROM ({query.replace('ASC', 'DESC')} LIMIT ?) "
            "ORDER BY recorded_at ASC"
        )
        params.append(limit)

    with get_connection() as connection:
        _ensure_schema(connection)

        rows = connection.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def list_racks() -> list[str]:
    with get_connection() as connection:
        _ensure_schema(connection)

        rows = connection.execute(
            "SELECT DISTINCT rack FROM telemetry ORDER BY rack"
        ).fetchall()

    return [row["rack"] for row in rows]


def count_readings() -> int:
    with get_connection() as connection:
        _ensure_schema(connection)

        row = connection.execute(
            "SELECT COUNT(*) AS total FROM telemetry"
        ).fetchone()

    return row["total"]
