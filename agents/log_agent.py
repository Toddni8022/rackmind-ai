"""
RackMind AI

Log Analysis Agent
"""


def analyze_log_summary(summary: dict) -> str:
    """
    Returns a structured log analysis without calling Gemini.
    """

    events = summary.get("events", summary.get("total_events", 0))
    errors = summary.get("errors", 0)
    warnings = summary.get("warnings", 0)
    crc_errors = summary.get("crc_errors", 0)
    resets = summary.get("resets", summary.get("interface_resets", 0))
    max_temp = summary.get("max_temp", summary.get("max_temperature", 0))

    report = []

    report.append("### Log Analysis\n")

    report.append(f"- Events: {events}")
    report.append(f"- Errors: {errors}")
    report.append(f"- Warnings: {warnings}")
    report.append(f"- CRC Errors: {crc_errors}")
    report.append(f"- Interface Resets: {resets}")

    if max_temp:
        report.append(f"- Max Temperature: {max_temp}°F")

    if crc_errors > 0:
        report.append(
            "\nCRC errors indicate possible physical layer issues."
        )

    if errors > 5:
        report.append(
            "Multiple switch errors detected."
        )

    return "\n".join(report)