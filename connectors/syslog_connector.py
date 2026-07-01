"""
RackMind AI

Syslog Connector

Tails a syslog file (local file, mounted share, or one produced
by rsyslog/syslog-ng forwarding) and converts switch events into
telemetry readings using the same parsing rules as the log agent.
"""

import re
from pathlib import Path

from connectors.base import ConnectorError, TelemetryConnector

TIMESTAMP_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
)

TEMPERATURE_PATTERN = re.compile(r"(\d+)\s*F\b", re.IGNORECASE)

POWER_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*KW\b", re.IGNORECASE)

RACK_PATTERN = re.compile(r"\b(Rack[-_ ]?\w+)\b", re.IGNORECASE)


class SyslogConnector(TelemetryConnector):

    name = "syslog"
    description = "Syslog file tail (rsyslog / syslog-ng forwarding)"

    def __init__(self, path: str, rack: str = None, max_lines: int = 5000):
        self.path = Path(str(path or "").strip())
        self.rack = rack
        self.max_lines = max_lines

    def fetch(self) -> list[dict]:
        if not str(self.path):
            raise ConnectorError("Syslog file path is required.")

        if not self.path.exists():
            raise ConnectorError(
                f"Syslog file not found: {self.path}. Point rsyslog or "
                "syslog-ng at a file RackMind can read."
            )

        try:
            lines = self.path.read_text(
                encoding="utf-8", errors="ignore"
            ).splitlines()[-self.max_lines:]
        except OSError as ex:
            raise ConnectorError(
                f"Unable to read syslog file {self.path}: {ex}"
            ) from ex

        if not lines:
            raise ConnectorError(
                f"Syslog file {self.path} is empty."
            )

        readings = []
        crc_total = 0
        reset_total = 0

        for line in lines:
            upper = line.upper()

            if "CRC" in upper:
                crc_total += 1

            if "RESET" in upper:
                reset_total += 1

            temp_match = TEMPERATURE_PATTERN.search(line)
            power_match = POWER_PATTERN.search(line)

            if not temp_match and not power_match:
                continue

            timestamp_match = TIMESTAMP_PATTERN.search(line)
            rack_match = RACK_PATTERN.search(line)

            rack = self.rack or (
                rack_match.group(1).replace("_", "-").replace(" ", "-")
                if rack_match
                else "Unknown"
            )

            readings.append(
                self.normalize(
                    rack,
                    timestamp=(
                        timestamp_match.group(1) if timestamp_match else None
                    ),
                    temperature=(
                        float(temp_match.group(1)) if temp_match else None
                    ),
                    power_kw=(
                        float(power_match.group(1)) if power_match else None
                    ),
                    crc_errors=crc_total,
                    resets=reset_total,
                )
            )

        if not readings:
            raise ConnectorError(
                "No temperature or power events were found in "
                f"{self.path}. The file was read but contained no "
                "parseable telemetry."
            )

        return readings
