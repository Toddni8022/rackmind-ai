"""
RackMind AI

Live Telemetry Connectors

Registry of connectors that pull telemetry from real sources
(SNMP, Redfish, Prometheus, syslog, CloudWatch) plus a built-in
simulator for demos.
"""

from connectors.base import ConnectorError, TelemetryConnector
from connectors.cloudwatch_connector import CloudWatchConnector
from connectors.prometheus_connector import PrometheusConnector
from connectors.redfish_connector import RedfishConnector
from connectors.simulator import SimulatorConnector
from connectors.snmp_connector import SNMPConnector
from connectors.syslog_connector import SyslogConnector

CONNECTORS = {
    SimulatorConnector.name: SimulatorConnector,
    PrometheusConnector.name: PrometheusConnector,
    RedfishConnector.name: RedfishConnector,
    SNMPConnector.name: SNMPConnector,
    SyslogConnector.name: SyslogConnector,
    CloudWatchConnector.name: CloudWatchConnector,
}

__all__ = [
    "CONNECTORS",
    "ConnectorError",
    "TelemetryConnector",
    "CloudWatchConnector",
    "PrometheusConnector",
    "RedfishConnector",
    "SimulatorConnector",
    "SNMPConnector",
    "SyslogConnector",
]
