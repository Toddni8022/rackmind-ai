"""
Tests for the live telemetry connectors, focused on normalization
and graceful failure — no network access required.
"""

import pytest

from connectors import CONNECTORS, ConnectorError
from connectors.prometheus_connector import PrometheusConnector
from connectors.redfish_connector import (
    RedfishConnector,
    celsius_to_fahrenheit,
)
from connectors.simulator import SimulatorConnector
from connectors.snmp_connector import SNMPConnector
from connectors.syslog_connector import SyslogConnector

READING_KEYS = {"timestamp", "rack", "source"}


class TestRegistry:

    def test_all_expected_connectors_registered(self):
        assert set(CONNECTORS) == {
            "simulator",
            "prometheus",
            "redfish",
            "snmp",
            "syslog",
            "cloudwatch",
        }


class TestSimulator:

    def test_generates_normalized_readings(self):
        connector = SimulatorConnector(
            racks=["Rack-A", "Rack-B"], samples=6, seed=42
        )

        readings = connector.fetch()

        assert len(readings) == 12

        for reading in readings:
            assert READING_KEYS <= set(reading)
            assert "temperature" in reading

    def test_failing_rack_trends_hotter(self):
        connector = SimulatorConnector(
            racks=["Rack-A", "Rack-B"],
            samples=10,
            seed=1,
            failing_rack="Rack-A",
        )

        readings = connector.fetch()

        failing = [r["temperature"] for r in readings if r["rack"] == "Rack-A"]
        healthy = [r["temperature"] for r in readings if r["rack"] == "Rack-B"]

        assert max(failing) > max(healthy)
        assert failing[-1] > failing[0]


class TestSyslogConnector:

    def test_parses_temperature_power_crc_and_resets(
        self, tmp_path, sample_log_text
    ):
        log_file = tmp_path / "switch.log"
        log_file.write_text(
            sample_log_text + "2026-06-21 18:12:30 INFO Rack22 Power draw 4.8kW\n"
        )

        readings = SyslogConnector(path=str(log_file)).fetch()

        assert readings

        temperatures = [
            r["temperature"] for r in readings if "temperature" in r
        ]

        assert 91.0 in temperatures

        last = readings[-1]

        assert last["power_kw"] == 4.8
        assert last["crc_errors"] == 2
        assert last["resets"] == 1
        assert last["rack"] == "Rack22"
        assert last["timestamp"] == "2026-06-21 18:12:30"

    def test_missing_file_raises_connector_error(self, tmp_path):
        connector = SyslogConnector(path=str(tmp_path / "nope.log"))

        with pytest.raises(ConnectorError, match="not found"):
            connector.fetch()

    def test_file_without_telemetry_raises_connector_error(self, tmp_path):
        log_file = tmp_path / "empty.log"
        log_file.write_text("INFO nothing interesting here\n")

        with pytest.raises(ConnectorError, match="No temperature or power"):
            SyslogConnector(path=str(log_file)).fetch()

    def test_explicit_rack_override(self, tmp_path):
        log_file = tmp_path / "s.log"
        log_file.write_text("INFO Temperature 75F\n")

        readings = SyslogConnector(
            path=str(log_file), rack="Rack-99"
        ).fetch()

        assert readings[0]["rack"] == "Rack-99"


class TestPrometheusConnector:

    def _payload(self, results):
        return {
            "status": "success",
            "data": {"result": results},
        }

    def test_groups_metrics_by_rack(self, monkeypatch):
        connector = PrometheusConnector(
            base_url="http://prom:9090",
            metric_queries={
                "temperature": "temp_query",
                "power_kw": "power_query",
            },
        )

        responses = {
            "temp_query": [
                {"metric": {"rack": "Rack-22"}, "value": [0, "88"]},
                {"metric": {"rack": "Rack-07"}, "value": [0, "70"]},
            ],
            "power_query": [
                {"metric": {"rack": "Rack-22"}, "value": [0, "4.6"]},
            ],
        }

        monkeypatch.setattr(
            connector,
            "_query",
            lambda promql: responses[promql],
        )

        readings = connector.fetch()

        by_rack = {r["rack"]: r for r in readings}

        assert by_rack["Rack-22"]["temperature"] == 88.0
        assert by_rack["Rack-22"]["power_kw"] == 4.6
        assert by_rack["Rack-07"]["temperature"] == 70.0
        assert "power_kw" not in by_rack["Rack-07"]

    def test_missing_url_raises(self):
        with pytest.raises(ConnectorError, match="URL is required"):
            PrometheusConnector(base_url="").fetch()

    def test_no_samples_raises(self, monkeypatch):
        connector = PrometheusConnector(base_url="http://prom:9090")

        monkeypatch.setattr(connector, "_query", lambda promql: [])

        with pytest.raises(ConnectorError, match="no samples"):
            connector.fetch()

    def test_error_status_raises(self, monkeypatch):
        connector = PrometheusConnector(base_url="http://prom:9090")

        def fake_urlopen(url, timeout=None):
            raise OSError("connection refused")

        monkeypatch.setattr(
            "urllib.request.urlopen",
            fake_urlopen,
        )

        with pytest.raises(ConnectorError, match="query failed"):
            connector.fetch()


class TestRedfishConnector:

    def test_celsius_conversion(self):
        assert celsius_to_fahrenheit(0) == 32
        assert celsius_to_fahrenheit(100) == 212

    def test_reads_hottest_sensor_and_total_power(self, monkeypatch):
        connector = RedfishConnector(
            base_url="https://bmc", rack="Rack-22"
        )

        payloads = {
            "/redfish/v1/Chassis/1/Thermal": {
                "Temperatures": [
                    {"ReadingCelsius": 25},
                    {"ReadingCelsius": 32},
                    {"ReadingCelsius": None},
                ]
            },
            "/redfish/v1/Chassis/1/Power": {
                "PowerControl": [
                    {"PowerConsumedWatts": 2400},
                    {"PowerConsumedWatts": 1800},
                ]
            },
        }

        monkeypatch.setattr(connector, "_get", lambda path: payloads[path])

        readings = connector.fetch()

        assert len(readings) == 1
        assert readings[0]["rack"] == "Rack-22"
        assert readings[0]["temperature"] == celsius_to_fahrenheit(32)
        assert readings[0]["power_kw"] == 4.2

    def test_empty_chassis_raises(self, monkeypatch):
        connector = RedfishConnector(base_url="https://bmc")

        monkeypatch.setattr(
            connector,
            "_get",
            lambda path: {"Temperatures": [], "PowerControl": []},
        )

        with pytest.raises(ConnectorError, match="no temperature or power"):
            connector.fetch()

    def test_missing_url_raises(self):
        with pytest.raises(ConnectorError, match="URL is required"):
            RedfishConnector(base_url="").fetch()


class TestSNMPConnector:

    def test_missing_host_raises(self):
        with pytest.raises(ConnectorError, match="host is required"):
            SNMPConnector(host="").fetch()

    def test_missing_oids_raises(self):
        connector = SNMPConnector(host="10.0.0.5", oids={"temperature": ""})

        with pytest.raises(ConnectorError, match="OID must be configured"):
            connector.fetch()

    def test_normalizes_polled_values(self, monkeypatch):
        connector = SNMPConnector(
            host="10.0.0.5",
            rack="Rack-22",
            oids={"temperature": "1.2.3", "power_kw": "4.5.6"},
        )

        values = {"1.2.3": 86.0, "4.5.6": 4.4}

        monkeypatch.setattr(
            connector, "_snmp_get", lambda oid: values[oid]
        )

        readings = connector.fetch()

        assert len(readings) == 1
        assert readings[0]["rack"] == "Rack-22"
        assert readings[0]["temperature"] == 86.0
        assert readings[0]["power_kw"] == 4.4


class TestNormalization:

    def test_non_numeric_metrics_dropped(self):
        connector = SimulatorConnector()

        reading = connector.normalize(
            "Rack-1", temperature="not-a-number", power_kw=4.2
        )

        assert "temperature" not in reading
        assert reading["power_kw"] == 4.2
        assert reading["rack"] == "Rack-1"

    def test_missing_rack_defaults_to_unknown(self):
        reading = SimulatorConnector().normalize(None, temperature=70)

        assert reading["rack"] == "Unknown"
