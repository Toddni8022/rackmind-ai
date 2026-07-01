"""
RackMind AI

SNMP Connector

Polls temperature / power OIDs from switches, PDUs, or
environment sensors. Requires the optional pysnmp package; a
clear message is raised when it is not installed so the rest of
the app keeps working.
"""

from connectors.base import ConnectorError, TelemetryConnector

# Sensible defaults: ENTITY-SENSOR-MIB style gauges. Sites override
# these in the UI with their vendor OIDs.
DEFAULT_OIDS = {
    "temperature": "1.3.6.1.4.1.9.9.13.1.3.1.3.1",
    "power_kw": "",
    "humidity": "",
}


class SNMPConnector(TelemetryConnector):

    name = "snmp"
    description = "SNMP v2c polling of sensor OIDs"

    def __init__(
        self,
        host: str,
        community: str = "public",
        port: int = 161,
        rack: str = None,
        oids: dict = None,
        timeout: int = 5,
    ):
        self.host = str(host or "").strip()
        self.community = community
        self.port = int(port)
        self.rack = rack or self.host
        self.oids = {k: v for k, v in (oids or DEFAULT_OIDS).items() if v}
        self.timeout = timeout

    def _snmp_get(self, oid: str):
        try:
            from pysnmp.hlapi import (
                CommunityData,
                ContextData,
                ObjectIdentity,
                ObjectType,
                SnmpEngine,
                UdpTransportTarget,
                getCmd,
            )
        except ImportError as ex:
            raise ConnectorError(
                "SNMP support requires the pysnmp package. "
                "Install it with: pip install pysnmp"
            ) from ex

        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=1),
            UdpTransportTarget(
                (self.host, self.port),
                timeout=self.timeout,
                retries=1,
            ),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        error_indication, error_status, _, var_binds = next(iterator)

        if error_indication:
            raise ConnectorError(
                f"SNMP request to {self.host}:{self.port} failed: "
                f"{error_indication}"
            )

        if error_status:
            raise ConnectorError(
                f"SNMP error from {self.host}: {error_status.prettyPrint()}"
            )

        for _, value in var_binds:
            try:
                return float(value)
            except (TypeError, ValueError):
                raise ConnectorError(
                    f"SNMP OID {oid} returned a non-numeric value: {value}"
                )

        return None

    def fetch(self) -> list[dict]:
        if not self.host:
            raise ConnectorError("SNMP host is required.")

        if not self.oids:
            raise ConnectorError(
                "At least one SNMP OID must be configured."
            )

        metrics = {}

        for metric, oid in self.oids.items():
            value = self._snmp_get(oid)

            if value is not None:
                metrics[metric] = value

        if not metrics:
            raise ConnectorError(
                f"No SNMP values returned from {self.host}."
            )

        return [self.normalize(self.rack, **metrics)]
