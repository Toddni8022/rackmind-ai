"""Optional live telemetry adapters. The demo remains fully offline by default."""
import json
import os
from urllib.request import Request, urlopen


class IntegrationError(RuntimeError):
    pass


def fetch_json(url=None, token=None, timeout=5):
    endpoint = url or os.getenv("RACKMIND_TELEMETRY_URL")
    if not endpoint:
        raise IntegrationError("RACKMIND_TELEMETRY_URL is not configured.")
    headers = {"Accept": "application/json"}
    if token or os.getenv("RACKMIND_TELEMETRY_TOKEN"):
        headers["Authorization"] = f"Bearer {token or os.getenv('RACKMIND_TELEMETRY_TOKEN')}"
    try:
        with urlopen(Request(endpoint, headers=headers), timeout=timeout) as response:
            if response.status != 200:
                raise IntegrationError(f"Telemetry source returned HTTP {response.status}.")
            payload = json.loads(response.read())
    except (OSError, ValueError) as exc:
        raise IntegrationError(f"Unable to read telemetry source: {exc}") from exc
    if not isinstance(payload, (list, dict)):
        raise IntegrationError("Telemetry source must return a JSON object or array.")
    return payload
