"""
RackMind AI

Sensor Analysis Agent
"""

from config import POWER_WARNING, TEMP_CRITICAL, TEMP_WARNING


def _number(summary: dict, key: str) -> float | None:
    value = summary.get(key)

    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _display(value: float | None, suffix: str = "") -> str:
    if value is None:
        return "N/A"

    if value.is_integer():
        return f"{int(value)}{suffix}"

    return f"{value}{suffix}"


def analyze_sensor_data(summary: dict) -> str:
    """
    Returns sensor observations without using Gemini.
    """

    max_temp = _number(summary, "max_temp")
    avg_temp = _number(summary, "avg_temp")
    avg_humidity = _number(summary, "avg_humidity")
    peak_power = _number(summary, "peak_power")
    samples = summary.get("samples", "N/A")

    report = [
        "### Sensor Analysis\n",
        f"- Samples Reviewed: {samples}",
        f"- Maximum Temperature: {_display(max_temp, '°F')}",
        f"- Average Temperature: {_display(avg_temp, '°F')}",
        f"- Average Humidity: {_display(avg_humidity, '%')}",
        f"- Peak Power: {_display(peak_power, ' kW')}",
    ]

    if max_temp is None:
        report.append(
            "\nTemperature data was not found in the uploaded sensor CSV."
        )
    elif max_temp >= TEMP_CRITICAL:
        report.append(
            "\nCritical temperature threshold exceeded. Immediate review is recommended."
        )
    elif max_temp >= TEMP_WARNING:
        report.append(
            "\nElevated rack temperature detected. Continue monitoring airflow and load."
        )
    else:
        report.append(
            "\nRack temperatures are within expected limits."
        )

    if peak_power is not None and peak_power >= POWER_WARNING:
        report.append(
            "Power draw is elevated and should be checked against rack capacity."
        )

    return "\n".join(report)
