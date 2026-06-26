"""
RackMind AI

Sensor Parser

Converts raw sensor CSV data into a structured summary
for the Sensor Agent.
"""

import pandas as pd


def parse_sensor_data(df: pd.DataFrame) -> dict:
    """
    Convert raw sensor data into a summary.
    """

    summary = {
        "samples": len(df),
        "max_temp": 0,
        "avg_temp": 0,
        "avg_humidity": 0,
        "peak_power": 0,
    }

    if "temperature" in df.columns:

        summary["max_temp"] = float(df["temperature"].max())

        summary["avg_temp"] = round(
            float(df["temperature"].mean()),
            1,
        )

    if "humidity" in df.columns:

        summary["avg_humidity"] = round(
            float(df["humidity"].mean()),
            1,
        )

    if "power_kw" in df.columns:

        summary["peak_power"] = float(
            df["power_kw"].max()
        )

    return summary