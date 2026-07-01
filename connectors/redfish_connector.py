"""
RackMind AI

Redfish Connector

Reads thermal and power telemetry from a BMC that implements the
DMTF Redfish API (iDRAC, iLO, XClarity, OpenBMC, ...).
"""

import base64
import json
import ssl
import urllib.error
import urllib.request

from connectors.base import ConnectorError, TelemetryConnector

CELSIUS_UNITS = ("cel", "celsius", "degc")


def celsius_to_fahrenheit(value: float) -> float:
    return round((value * 9 / 5) + 32, 1)


class RedfishConnector(TelemetryConnector):

    name = "redfish"
    description = "DMTF Redfish BMC thermal and power endpoints"

    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        chassis_id: str = "1",
        rack: str = None,
        verify_tls: bool = True,
        timeout: int = 10,
    ):
        self.base_url = str(base_url or "").rstrip("/")
        self.username = username
        self.password = password
        self.chassis_id = chassis_id
        self.rack = rack
        self.verify_tls = verify_tls
        self.timeout = timeout

    def _get(self, path: str) -> dict:
        url = f"{self.base_url}{path}"

        request = urllib.request.Request(url)

        if self.username:
            token = base64.b64encode(
                f"{self.username}:{self.password}".encode("utf-8")
            ).decode("ascii")
            request.add_header("Authorization", f"Basic {token}")

        context = None

        if not self.verify_tls:
            # Lab BMCs commonly run self-signed certs; the operator
            # explicitly opts out of verification in the UI.
            context = ssl._create_unverified_context()

        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout, context=context
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as ex:
            raise ConnectorError(
                f"Redfish request to {url} failed: {ex}"
            ) from ex

    def fetch(self) -> list[dict]:
        if not self.base_url:
            raise ConnectorError(
                "Redfish base URL is required, e.g. https://bmc.example.com"
            )

        chassis_path = f"/redfish/v1/Chassis/{self.chassis_id}"

        thermal = self._get(f"{chassis_path}/Thermal")
        power = self._get(f"{chassis_path}/Power")

        temperature = None

        for sensor in thermal.get("Temperatures", []):
            reading = sensor.get("ReadingCelsius")

            if reading is None:
                continue

            fahrenheit = celsius_to_fahrenheit(float(reading))

            if temperature is None or fahrenheit > temperature:
                temperature = fahrenheit

        power_kw = None

        for control in power.get("PowerControl", []):
            watts = control.get("PowerConsumedWatts")

            if watts is None:
                continue

            kw = round(float(watts) / 1000, 3)
            power_kw = kw if power_kw is None else power_kw + kw

        if temperature is None and power_kw is None:
            raise ConnectorError(
                "The Redfish chassis returned no temperature or power "
                "readings. Verify the chassis id."
            )

        rack = self.rack or f"Chassis-{self.chassis_id}"

        return [
            self.normalize(
                rack,
                temperature=temperature,
                power_kw=power_kw,
            )
        ]
