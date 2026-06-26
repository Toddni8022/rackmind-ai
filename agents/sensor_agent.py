"""
RackMind AI

Sensor Analysis Agent
"""


def analyze_sensor_data(summary: dict) -> str:
    """
    Returns sensor observations without using Gemini.
    """

    report = []

    report.append("### Sensor Analysis\n")

    report.append(
        f"- Maximum Temperature: {summary['max_temp']}°F"
    )

    report.append(
        f"- Average Temperature: {summary['avg_temp']}°F"
    )

    report.append(
        f"- Average Humidity: {summary['avg_humidity']}%"
    )

    report.append(
        f"- Peak Power: {summary['peak_power']} kW"
    )

    if summary["max_temp"] >= 90:

        report.append(
            "\nCritical temperature threshold exceeded."
        )

    elif summary["max_temp"] >= 80:

        report.append(
            "\nElevated rack temperature detected."
        )

    else:

        report.append(
            "\nRack temperatures are within expected limits."
        )

    return "\n".join(report)