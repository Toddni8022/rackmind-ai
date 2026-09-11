"""Local telemetry review; no provider calls or live infrastructure access."""
import math
import pandas as pd
from services.sensor_parser import COLUMN_ALIASES, normalize_sensor_dataframe


def prepare_telemetry(df):
    """Canonicalize known metrics and exclude invalid readings."""
    result = normalize_sensor_dataframe(df)
    if result.columns.duplicated().any():
        raise ValueError("Column names must be unique after normalization.")
    if result.empty:
        raise ValueError("The CSV contains no sensor readings.")
    found = False
    for metric, aliases in COLUMN_ALIASES.items():
        matches = [name for name in aliases if name in result.columns]
        if len(matches) > 1:
            raise ValueError(f"Multiple columns describe {metric}; keep one: {', '.join(matches)}.")
        if matches:
            found = True
            values = pd.to_numeric(result[matches[0]], errors="coerce")
            values = values.where(values.map(lambda v: pd.notna(v) and math.isfinite(v)))
            if metric == "humidity":
                values = values.where(values.between(0, 100))
            elif metric == "power_kw":
                values = values.where(values >= 0)
            result[metric] = values
        else:
            result[metric] = float("nan")
    if not found:
        raise ValueError("No supported readings found. Include temperature (°F), humidity (%), or power_kw.")
    if "rack" not in result.columns:
        result["rack"] = "Unspecified rack"
    else:
        result["rack"] = result["rack"].astype("string").str.strip().fillna("Unspecified rack")
        result.loc[result["rack"] == "", "rack"] = "Unspecified rack"
    return result


def assess_telemetry(df, temp_warning=80, temp_critical=90, power_warning=4.5):
    """Assess the selected upload window, preserving unknown coverage."""
    alerts, racks = [], []
    for rack, readings in df.groupby("rack", sort=True):
        temperature = readings["temperature"].max()
        power = readings["power_kw"].max()
        missing = int(readings[list(COLUMN_ALIASES)].isna().sum().sum())
        status = "Incomplete" if missing else "Normal"
        if pd.notna(power) and power >= power_warning:
            status = "Warning"
            alerts.append({"severity": "Warning", "rack": rack, "signal": "Power",
                           "detail": f"Peak {power:.2f} kW ≥ {power_warning:g} kW",
                           "action": "Check load against the rack's approved power budget."})
        if pd.notna(temperature) and temperature >= temp_warning:
            severity = "Critical" if temperature >= temp_critical else "Warning"
            status = severity
            alerts.append({"severity": severity, "rack": rack, "signal": "Temperature",
                           "detail": f"Peak {temperature:.1f} °F",
                           "action": "Verify the reading and inspect cooling and airflow; follow the facility escalation runbook."})
        if missing:
            alerts.append({"severity": "Data quality", "rack": rack, "signal": "Coverage",
                           "detail": f"{missing} missing or invalid metric readings",
                           "action": "Check temperature, humidity, and power coverage before concluding the rack is healthy."})
        racks.append({"Rack": rack, "Status": status, "Samples": len(readings),
                      "Peak temperature (°F)": None if pd.isna(temperature) else round(float(temperature), 2),
                      "Peak power (kW)": None if pd.isna(power) else round(float(power), 2),
                      "Missing / invalid readings": missing})
    order = {"Critical": 0, "Warning": 1, "Data quality": 2}
    alerts.sort(key=lambda a: (order[a["severity"]], a["rack"]))
    statuses = {rack["Status"] for rack in racks}
    status = next((v for v in ("Critical", "Warning", "Incomplete", "Normal") if v in statuses), "Incomplete")
    return {"status": status, "alerts": alerts, "racks": racks, "samples": len(df)}
