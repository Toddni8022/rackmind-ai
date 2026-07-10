"""Deterministic parsing helpers for infrastructure log uploads."""

import re

TEMP_PATTERN = re.compile(
    r"(?:TEMP(?:ERATURE)?[^0-9]{0,12})?(\d+(?:\.\d+)?)\s*(?:°\s*)?F\b",
    re.IGNORECASE,
)
WARNING_PATTERN = re.compile(r"\b(WARN|WARNING|THRESHOLD|DEGRADED|HIGH|ELEVATED)\b", re.IGNORECASE)
ERROR_PATTERN = re.compile(r"\b(ERROR|ERR|CRITICAL|FATAL|FAIL(?:ED|URE)?|FAULT|ALARM)\b", re.IGNORECASE)
CRC_PATTERN = re.compile(r"\b(CRC|FCS|CHECKSUM|FRAME CHECK|INPUT ERROR|PHY ERROR)\b", re.IGNORECASE)
RESET_PATTERN = re.compile(r"\b(RESET|RESTART|REBOOT|LINK FLAP|FLAPPING|BOUNCE|BOUNCED)\b", re.IGNORECASE)


def _nonempty_lines(log_text: str) -> list[str]:
    return [line.strip() for line in log_text.splitlines() if line.strip()]


def parse_log(log_text: str) -> dict:
    """Summarize common switch, link, and environmental fault signals."""
    lines = _nonempty_lines(log_text)
    summary = {"events": len(lines), "warnings": 0, "errors": 0, "crc_errors": 0, "resets": 0, "max_temp": 0}

    for line in lines:
        summary["warnings"] += bool(WARNING_PATTERN.search(line))
        summary["errors"] += bool(ERROR_PATTERN.search(line))
        summary["crc_errors"] += bool(CRC_PATTERN.search(line))
        summary["resets"] += bool(RESET_PATTERN.search(line))
        temperatures = [float(match.group(1)) for match in TEMP_PATTERN.finditer(line)]
        summary["max_temp"] = max(summary["max_temp"], *temperatures) if temperatures else summary["max_temp"]

    return summary


def build_log_timeline(log_text: str, limit: int = 25) -> list[str]:
    """Return the first noteworthy events without flooding the UI or prompt."""
    patterns = (WARNING_PATTERN, ERROR_PATTERN, CRC_PATTERN, RESET_PATTERN)
    return [line for line in _nonempty_lines(log_text) if any(p.search(line) for p in patterns)][:limit]
