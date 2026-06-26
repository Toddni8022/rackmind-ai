"""
RackMind AI

Sensor Analysis Agent
"""


def analyze_sensor_data(summary: dict) -> str:
    """
    Returns sensor observations without using Gemini.
    """

    temperature = summary.get("temperature", {})
    humidity = summary.get("humidity", {})
    power = summary.get("power_kw", {})

    max_temp = summary.get("max_temp", temperature.get("max", 0))
    avg_temp = summary.get("avg_temp", temperature.get("mean", 0))
    avg_humidity = summary.get("avg_humidity", humidity.get("mean", 0))
    peak_power = summary.get("peak_power", power.get("max", 0))

    report = []

    report.append("### Sensor Analysis\n")

    report.append(
        f"- Maximum Temperature: {max_temp}°F"
    )

    report.append(
        f"- Average Temperature: {avg_temp}°F"
    )

    report.append(
        f"- Average Humidity: {avg_humidity}%"
    )

    report.append(
        f"- Peak Power: {peak_power} kW"
    )

    if max_temp >= 90:

        report.append(
            "\nCritical temperature threshold exceeded."
        )

    elif max_temp >= 80:

        report.append(
            "\nElevated rack temperature detected."
        )

    else:

        report.append(
            "\nRack temperatures are within expected limits."
        )

    return "\n".join(report)