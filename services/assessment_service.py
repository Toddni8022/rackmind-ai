"""
RackMind AI

Deterministic infrastructure assessment helpers.

These functions keep the app useful even when an LLM provider is
not configured or temporarily unavailable.
"""

from __future__ import annotations


def normalize_log_summary(summary: dict | None) -> dict:
    summary = summary or {}

    return {
        "events": int(summary.get("events", summary.get("total_events", 0)) or 0),
        "warnings": int(summary.get("warnings", 0) or 0),
        "errors": int(summary.get("errors", 0) or 0),
        "crc_errors": int(summary.get("crc_errors", 0) or 0),
        "resets": int(summary.get("resets", summary.get("interface_resets", 0)) or 0),
        "max_temp": float(summary.get("max_temp", summary.get("max_temperature", 0)) or 0),
        "timeline": summary.get("timeline", []) or [],
    }


def normalize_sensor_summary(summary: dict | None) -> dict:
    summary = summary or {}
    temperature = summary.get("temperature", {}) or {}
    humidity = summary.get("humidity", {}) or {}
    power = summary.get("power_kw", {}) or {}

    return {
        "samples": int(summary.get("samples", 0) or 0),
        "max_temp": float(summary.get("max_temp", temperature.get("max", 0)) or 0),
        "avg_temp": float(summary.get("avg_temp", temperature.get("mean", 0)) or 0),
        "avg_humidity": float(summary.get("avg_humidity", humidity.get("mean", 0)) or 0),
        "peak_power": float(summary.get("peak_power", power.get("max", 0)) or 0),
    }


def score_log_summary(summary: dict | None) -> dict:
    log = normalize_log_summary(summary)
    score = 100
    score -= log["errors"] * 8
    score -= log["warnings"] * 2
    score -= log["crc_errors"] * 4
    score -= log["resets"] * 5

    if log["max_temp"] >= 90:
        score -= 18
    elif log["max_temp"] >= 80:
        score -= 8

    return build_scorecard(score)


def score_sensor_summary(summary: dict | None) -> dict:
    sensor = normalize_sensor_summary(summary)
    score = 100

    if sensor["max_temp"] >= 90:
        score -= 30
    elif sensor["max_temp"] >= 80:
        score -= 14

    if sensor["peak_power"] >= 4.5:
        score -= 15
    elif sensor["peak_power"] >= 4.0:
        score -= 6

    if sensor["avg_humidity"] and not 35 <= sensor["avg_humidity"] <= 60:
        score -= 8

    return build_scorecard(score)


def build_scorecard(score: float) -> dict:
    score = max(0, min(100, round(score)))

    if score >= 90:
        return {"score": score, "status": "Healthy", "severity": "Low"}
    if score >= 75:
        return {"score": score, "status": "Monitor", "severity": "Medium"}
    if score >= 55:
        return {"score": score, "status": "Degraded", "severity": "High"}

    return {"score": score, "status": "Critical", "severity": "Critical"}


def build_alerts(log_summary=None, sensor_summary=None, runbooks: int | None = None) -> list[str]:
    log = normalize_log_summary(log_summary)
    sensor = normalize_sensor_summary(sensor_summary)
    alerts = []

    if sensor["max_temp"] >= 90 or log["max_temp"] >= 90:
        alerts.append("Critical rack temperature threshold exceeded.")
    elif sensor["max_temp"] >= 80 or log["max_temp"] >= 80:
        alerts.append("Rack temperature is elevated and should be watched.")

    if sensor["peak_power"] >= 4.5:
        alerts.append("Power draw is above the expected operating envelope.")

    if log["crc_errors"]:
        alerts.append("CRC errors point to a possible cable, optic, or switch port issue.")

    if log["resets"]:
        alerts.append("Interface resets were detected and may indicate instability.")

    if runbooks == 0:
        alerts.append("No runbooks are indexed, reducing guided-response quality.")

    return alerts


def build_recommendations(log_summary=None, sensor_summary=None, runbooks: int | None = None) -> list[str]:
    log = normalize_log_summary(log_summary)
    sensor = normalize_sensor_summary(sensor_summary)
    recommendations = []

    if sensor["max_temp"] >= 80 or log["max_temp"] >= 80:
        recommendations.append("Inspect airflow, blanking panels, CRAC output, and rack intake temperature.")

    if log["crc_errors"]:
        recommendations.append("Reseat or replace suspect cables and optics, then clear counters and watch recurrence.")

    if log["resets"]:
        recommendations.append("Check switch interface logs around reset timestamps and validate firmware stability.")

    if sensor["peak_power"] >= 4.5:
        recommendations.append("Review rack power distribution and move noncritical load if redundancy is constrained.")

    if runbooks == 0:
        recommendations.append("Index at least one runbook so investigations can cite operational procedures.")

    if not recommendations:
        recommendations.append("Continue monitoring; no immediate corrective action is required.")

    return recommendations


def build_executive_report(
    log_summary=None,
    sensor_summary=None,
    runbook_context: str = "",
) -> str:
    log = normalize_log_summary(log_summary)
    sensor = normalize_sensor_summary(sensor_summary)
    log_score = score_log_summary(log)
    sensor_score = score_sensor_summary(sensor)
    overall = build_scorecard(min(log_score["score"], sensor_score["score"]))
    alerts = build_alerts(log, sensor)
    recommendations = build_recommendations(log, sensor)

    if alerts:
        root_cause = alerts[0]
    else:
        root_cause = "No active fault pattern was detected in the supplied telemetry."

    report = [
        "# Executive Summary",
        f"RackMind rates this incident as **{overall['severity']}** severity with an operational health score of **{overall['score']}/100**.",
        "",
        "# Root Cause",
        root_cause,
        "",
        "# Business Impact",
        "Potential impact is bounded while services remain online, but unresolved thermal, CRC, or reset patterns can increase outage risk.",
        "",
        "# Recommended Actions",
    ]

    report.extend(f"- {item}" for item in recommendations)
    report.extend([
        "",
        "# Evidence",
        f"- Log events: {log['events']}",
        f"- Errors: {log['errors']}",
        f"- Warnings: {log['warnings']}",
        f"- CRC errors: {log['crc_errors']}",
        f"- Interface resets: {log['resets']}",
        f"- Max temperature: {max(log['max_temp'], sensor['max_temp'])}°F",
        f"- Peak power: {sensor['peak_power']} kW",
        "",
        "# Priority",
        overall["severity"],
        "",
        "# Confidence",
        "Medium. This report is based on deterministic telemetry scoring and should be reviewed with live device state.",
    ])

    if runbook_context:
        report.extend(["", "# Runbook Context", runbook_context[:1200]])

    return "\n".join(report)
