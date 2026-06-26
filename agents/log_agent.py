"""
RackMind AI

Log Analysis Agent
"""


def analyze_log_summary(summary: dict) -> str:
    """
    Returns a structured log analysis without calling Gemini.
    """

    report = []

    report.append("### Log Analysis\n")

    report.append(f"- Events: {summary['events']}")
    report.append(f"- Errors: {summary['errors']}")
    report.append(f"- Warnings: {summary['warnings']}")
    report.append(f"- CRC Errors: {summary['crc_errors']}")
    report.append(f"- Interface Resets: {summary['resets']}")

    if summary["crc_errors"] > 0:
        report.append(
            "\nCRC errors indicate possible physical layer issues."
        )

    if summary["errors"] > 5:
        report.append(
            "Multiple switch errors detected."
        )

    return "\n".join(report)