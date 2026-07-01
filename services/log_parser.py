"""
RackMind AI

Log Parser

Converts raw switch logs into a structured summary
for the Log Agent.
"""

import re

# Uppercase level tokens as emitted by syslog-style network gear.
# Severity is taken from these tokens, never from words inside the
# message text, so "WARNING CRC error detected" is one warning and
# zero errors.
ERROR_TOKENS = re.compile(r"\b(?:ERROR|ERR|CRITICAL|CRIT|ALERT|FATAL|EMERG)\b")

WARNING_TOKENS = re.compile(r"\b(?:WARNING|WARN)\b")


def line_severity(line: str) -> str | None:
    """
    Classify a log line as "error", "warning", or None using its
    uppercase severity token.
    """

    if ERROR_TOKENS.search(line):
        return "error"

    if WARNING_TOKENS.search(line):
        return "warning"

    return None


def parse_log(log_text: str) -> dict:

    lines = log_text.splitlines()

    summary = {
        "events": len(lines),
        "warnings": 0,
        "errors": 0,
        "crc_errors": 0,
        "resets": 0,
        "max_temp": 0,
    }

    temp_pattern = re.compile(r"(\d+)F")

    for line in lines:

        severity = line_severity(line)

        if severity == "warning":
            summary["warnings"] += 1
        elif severity == "error":
            summary["errors"] += 1

        upper = line.upper()

        if "CRC" in upper:
            summary["crc_errors"] += 1

        # Only count actual reset events, not the recovery
        # messages ("reset complete") that follow them.
        if "RESET INITIATED" in upper:
            summary["resets"] += 1

        match = temp_pattern.search(line)

        if match:

            temp = int(match.group(1))

            if temp > summary["max_temp"]:
                summary["max_temp"] = temp

    return summary
