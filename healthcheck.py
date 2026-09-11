"""Dependency-light readiness check for local and hosted deployments."""
import json
from config import SAMPLE_DIR


def check():
    sample = SAMPLE_DIR / "sensors" / "rack22.csv"
    return {"status": "ok" if sample.is_file() else "degraded", "sample_telemetry": sample.is_file()}


if __name__ == "__main__":
    print(json.dumps(check()))
