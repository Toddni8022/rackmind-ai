"""
RackMind AI

Sensor Parser

Converts raw sensor CSV data into a structured summary
for the Sensor Agent.
"""

import pandas as pd


COLUMN_ALIASES = {
    "temperature": (
        "temperature",
        "temp",
        "temp_f",
        "rack_temp",
        "rack_temperature",
        "ambient_temp",
    ),
    "humidity": (
        "humidity",
        "relative_humidity",
        "humidity_percent",
        "rh",
    ),
    "power_kw": (
        "power_kw",
        "power",
        "kw",
        "load_kw",
        "rack_power",
    ),
}


def normalize_column_name(column: str) -> str:
    """
    Normalize CSV column names so uploaded files can use common variations.
    """

    return str(column).strip().lower().replace(" ", "_").replace("-", "_")


def normalize_sensor_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a copy of the dataframe with normalized column names.
    """

    normalized = df.copy()
    normalized.columns = [normalize_column_name(column) for column in normalized.columns]
    return normalized


def _find_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        if alias in df.columns:
            return alias

    return None


def _max_value(df: pd.DataFrame, column: str) -> float | None:
    values = pd.to_numeric(df[column], errors="coerce").dropna()

    if values.empty:
        return None

    return round(float(values.max()), 2)


def _mean_value(df: pd.DataFrame, column: str) -> float | None:
    values = pd.to_numeric(df[column], errors="coerce").dropna()

    if values.empty:
        return None

    return round(float(values.mean()), 2)


def parse_sensor_data(df: pd.DataFrame) -> dict:
    """
    Convert raw sensor data into the stable summary shape expected by agents.
    """

    normalized = normalize_sensor_dataframe(df)

    temperature_column = _find_column(normalized, COLUMN_ALIASES["temperature"])
    humidity_column = _find_column(normalized, COLUMN_ALIASES["humidity"])
    power_column = _find_column(normalized, COLUMN_ALIASES["power_kw"])

    return {
        "samples": len(normalized),
        "max_temp": _max_value(normalized, temperature_column) if temperature_column else None,
        "avg_temp": _mean_value(normalized, temperature_column) if temperature_column else None,
        "avg_humidity": _mean_value(normalized, humidity_column) if humidity_column else None,
        "peak_power": _max_value(normalized, power_column) if power_column else None,
        "observed_columns": list(normalized.columns),
    }
