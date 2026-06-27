"""
RackMind AI

Log Parser

Converts raw switch logs into a structured summary
for the Log Agent.
"""

import re


TEMP_PATTERN = re.compile(
    r"(?:TEMP(?:ERATURE)?[^0-9]{0,12})?(\d+(?:\.\d+)?)\s*(?:°\s*)?F\b",
    re.IGNORECASE,
)

WARNING_PATTERN = re.compile(
    r"\b(WARN|WARNING|THRESHOLD|DEGRADED|HIGH|ELEVATED)\b",
    re.IGNORECASE,
)

ERROR_PATTERN = re.compile(
    r"\b(ERROR|ERR|CRITICAL|FATAL|FAIL(?:ED|URE)?|FAULT|ALARM)\b",
    re.IGNORECASE,
)

CRC_PATTERN = re.compile(
    r"\b(CRC|FCS|CHECKSUM|FRAME CHECK|INPUT ERROR|PHY ERROR)\b",
    re.IGNORECASE,
)

RESET_PATTERN = re.compile(
    r"\b(RESET|RESTART|REBOOT|LINK FLAP|FLAPPING|BOUNCE|BOUNCED)\b",
    re.IGNORECASE,
)


def _nonempty_lines(log_text: str) -> list[str]:
    return [
        line.strip()
        for line in log_text.splitlines()
        if line.strip()
    ]


def _extract_max_temperature(line: str) -> float:
    values = []

    for match in TEMP_PATTERN.finditer(line):
        try:
            values.append(float(match.group(1)))
        except ValueError:
            pass

    return max(values, default=0)


def is_noteworthy_log_line(line: str) -> bool:
    return any(
        pattern.search(line)
        for pattern in (
            WARNING_PATTERN,
            ERROR_PATTERN,
            CRC_PATTERN,
            RESET_PATTERN,
        )
    )


def parse_log(log_text: str) -> dict:

    lines = _nonempty_lines(log_text)

    summary = {
        "events": len(lines),
        "warnings": 0,
        "errors": 0,
        "crc_errors": 0,
        "resets": 0,
        "max_temp": 0,
    }

    for line in lines:

        if WARNING_PATTERN.search(line):
            summary["warnings"] += 1

        if ERROR_PATTERN.search(line):
            summary["errors"] += 1

        if CRC_PATTERN.search(line):
            summary["crc_errors"] += 1

        if RESET_PATTERN.search(line):
            summary["resets"] += 1

        temp = _extract_max_temperature(line)

        if temp > summary["max_temp"]:
            summary["max_temp"] = temp

    return summary


def build_log_timeline(log_text: str, limit: int = 25) -> list[str]:
    timeline = []

    for line in _nonempty_lines(log_text):
        if is_noteworthy_log_line(line):
            timeline.append(line)

        if len(timeline) >= limit:
            break

    return timeline
