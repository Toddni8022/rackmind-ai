"""
RackMind AI

Prometheus Connector

Pulls rack telemetry from a Prometheus HTTP API using instant
queries. Metric names are configurable so it adapts to whatever
exporters the site runs (node_exporter, snmp_exporter, ipmi, ...).
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from connectors.base import ConnectorError, TelemetryConnector

DEFAULT_METRIC_QUERIES = {
    "temperature": "rack_temperature_fahrenheit",
    "humidity": "rack_humidity_percent",
    "power_kw": "rack_power_kw",
    "crc_errors": "rack_interface_crc_errors_total",
    "resets": "rack_interface_resets_total",
}

RACK_LABELS = ("rack", "rack_id", "instance", "node")


class PrometheusConnector(TelemetryConnector):

    name = "prometheus"
    description = "Prometheus HTTP API instant queries"

    def __init__(self, base_url: str, metric_queries: dict = None, timeout: int = 10):
        self.base_url = str(base_url or "").rstrip("/")
        self.metric_queries = metric_queries or dict(DEFAULT_METRIC_QUERIES)
        self.timeout = timeout

    def _query(self, promql: str) -> list[dict]:
        url = (
            f"{self.base_url}/api/v1/query?"
            + urllib.parse.urlencode({"query": promql})
        )

        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as ex:
            raise ConnectorError(
                f"Prometheus query failed against {self.base_url}: {ex}"
            ) from ex

        if payload.get("status") != "success":
            raise ConnectorError(
                f"Prometheus returned an error for query '{promql}': "
                f"{payload.get('error', 'unknown error')}"
            )

        return payload.get("data", {}).get("result", [])

    @staticmethod
    def _rack_label(metric_labels: dict) -> str:
        for label in RACK_LABELS:
            if metric_labels.get(label):
                return str(metric_labels[label])

        return "Unknown"

    def fetch(self) -> list[dict]:
        if not self.base_url:
            raise ConnectorError(
                "Prometheus URL is required, e.g. http://prometheus:9090"
            )

        racks: dict[str, dict] = {}

        for metric, promql in self.metric_queries.items():
            if not promql:
                continue

            for result in self._query(promql):
                rack = self._rack_label(result.get("metric", {}))
                value = result.get("value", [None, None])[1]

                racks.setdefault(rack, {})[metric] = value

        if not racks:
            raise ConnectorError(
                "Prometheus returned no samples for the configured "
                "metric queries. Check the metric names."
            )

        return [
            self.normalize(rack, **metrics)
            for rack, metrics in racks.items()
        ]
