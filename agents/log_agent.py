"""
RackMind AI

Log Analysis Agent
"""


def _number(summary: dict, *keys: str) -> int:
    for key in keys:
        value = summary.get(key)

        if value in (None, ""):
            continue

        try:
            return int(value)
        except (TypeError, ValueError):
            continue

    return 0


def analyze_log_summary(summary: dict) -> str:
    """
    Returns a structured log analysis without calling Gemini.
    """

    events = _number(summary, "events", "total_events")
    errors = _number(summary, "errors")
    warnings = _number(summary, "warnings")
    crc_errors = _number(summary, "crc_errors")
    resets = _number(summary, "resets", "interface_resets")
    max_temp = _number(summary, "max_temp", "max_temperature")

    report = [
        "### Log Analysis\n",
        f"- Events: {events}",
        f"- Errors: {errors}",
        f"- Warnings: {warnings}",
        f"- CRC Errors: {crc_errors}",
        f"- Interface Resets: {resets}",
        f"- Max Temperature: {max_temp}°F",
    ]

    if crc_errors > 0:
        report.append(
            "\nCRC errors indicate possible physical layer issues such as cabling, optics, ports, or patching."
        )

    if resets > 0:
        report.append(
            "Interface resets were detected and should be correlated with CRC errors and temperature events."
        )

    if errors > 5:
        report.append(
            "Multiple switch errors detected. Escalation or deeper review may be needed."
        )

    if max_temp >= 90:
        report.append(
            "Critical temperature readings appeared in the log data."
        )

    return "\n".join(report)
