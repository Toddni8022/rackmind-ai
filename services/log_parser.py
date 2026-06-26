"""
RackMind AI

Log Parser

Converts raw switch logs into a structured summary
for the Log Agent.
"""

import re


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

        upper = line.upper()

        if "WARNING" in upper:
            summary["warnings"] += 1

        if "ERROR" in upper:
            summary["errors"] += 1

        if "CRC" in upper:
            summary["crc_errors"] += 1

        if "RESET" in upper:
            summary["resets"] += 1

        match = temp_pattern.search(line)

        if match:

            temp = int(match.group(1))

            if temp > summary["max_temp"]:
                summary["max_temp"] = temp

    return summary