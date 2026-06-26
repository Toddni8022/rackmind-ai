"""
RackMind AI

Report Agent
"""

from services.gemini_service import generate


def generate_incident_report(
    log_report="",
    runbook_report="",
    sensor_report="",
):

    prompt = f"""
You are an Incident Manager.

Merge these AI reports into one executive report.

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

# Priority

# Confidence
"""

    return generate(prompt)