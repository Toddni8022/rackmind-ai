"""
RackMind AI

Single-Prompt Incident Investigation
"""

import pandas as pd

from services.assessment_service import build_executive_report
from services.log_parser import parse_log
from services.sensor_parser import parse_sensor_data
from services.vector_service import search_runbooks
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


def investigate_incident(
    log: str,
    sensor_data: list,
) -> str:
    """
    Performs a complete investigation using one Gemini request,
    with a deterministic local report as the fallback path.
    """

    log_summary = parse_log(log)
    sensor_df = pd.DataFrame(sensor_data)
    sensor_summary = parse_sensor_data(sensor_df)

    docs = search_runbooks(
        "CRC high temperature cooling"
    )

    runbook_context = "\n\n".join(docs)

    prompt = f"""
You are a senior data center engineer.

Analyze the incident using the evidence below. Write a concise,
professional executive report with practical next actions.

=========================
LOG SUMMARY
=========================

{log_summary}

=========================
SENSOR SUMMARY
=========================

{sensor_summary}

=========================
RUNBOOK
=========================

{runbook_context}

=========================

Include:

1. Executive Summary

2. Root Cause

3. Business Impact

4. Recommended Actions

5. Evidence

6. Priority

7. Confidence
"""

    response = generate(prompt)

    if _needs_fallback(response):
        return build_executive_report(
            log_summary=log_summary,
            sensor_summary=sensor_summary,
            runbook_context=runbook_context,
        )

    return response
