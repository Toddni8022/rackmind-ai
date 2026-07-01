"""
RackMind AI

Telemetry Connector Base

Every connector fetches readings from a live source (SNMP,
Redfish, Prometheus, syslog, cloud monitoring) and returns them
in one normalized shape:

    {
        "timestamp": "2026-06-21 18:05:00",
        "rack": "Rack-22",
        "temperature": 87.0,   # optional, °F
        "humidity": 48.0,      # optional, %
        "power_kw": 4.6,       # optional
        "crc_errors": 3,       # optional, cumulative count
        "resets": 1,           # optional, cumulative count
        "source": "prometheus",
    }

Connectors must never raise for unreachable endpoints or missing
optional client libraries; they raise ConnectorError with a clear,
operator-facing message instead.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class ConnectorError(RuntimeError):
    """
    Raised when a connector cannot fetch telemetry. The message is
    shown directly to the operator, so keep it actionable.
    """


class TelemetryConnector(ABC):

    name = "base"
    description = "Abstract telemetry connector"

    @abstractmethod
    def fetch(self) -> list[dict]:
        """
        Fetch current readings from the source.

        Returns a list of normalized reading dicts (see module
        docstring). Raises ConnectorError when the source cannot
        be reached or is misconfigured.
        """

    @staticmethod
    def now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def normalize(self, rack: str, **metrics) -> dict:
        """
        Build one normalized reading, dropping unknown metrics.
        """

        reading = {
            "timestamp": metrics.pop("timestamp", None) or self.now(),
            "rack": rack or "Unknown",
            "source": self.name,
        }

        for key in ("temperature", "humidity", "power_kw", "crc_errors", "resets"):
            value = metrics.get(key)

            if value is None:
                continue

            try:
                reading[key] = float(value)
            except (TypeError, ValueError):
                continue

        return reading
