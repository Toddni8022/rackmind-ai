"""
RackMind AI

Report Agent
"""

from services.assessment_service import build_executive_report
from services.gemini_service import generate


def _needs_fallback(response: str) -> bool:

    if not response:
        return True

    fallback_headers = (
        "# AI Service Offline",
        "# AI Service Error",
        "# Gemini Service Busy",
    )

    return response.strip().startswith(fallback_headers)


def generate_incident_report(
    log_report="",
    runbook_report="",
    sensor_report="",
    log_summary=None,
    sensor_summary=None,
):

    prompt = f"""
You are an Incident Manager.

Merge these infrastructure reports into one concise executive report.
Use clear evidence, operational risk, and action-oriented recommendations.

Log Report

{log_report}

Runbook Report

{runbook_report}

Sensor Report

{sensor_report}

Return:

# Executive Summary

# Root Cause

# Business Impact

# Recommended Actions

# Evidence

# Priority

# Confidence
"""

    response = generate(prompt)

    if _needs_fallback(response):
        return build_executive_report(
            log_summary=log_summary,
            sensor_summary=sensor_summary,
            runbook_context=runbook_report,
        )

    return response