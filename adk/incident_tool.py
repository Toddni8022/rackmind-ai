"""
RackMind AI

Single-Prompt Incident Investigation
"""

import pandas as pd
import os

from services.log_parser import parse_log
from services.sensor_parser import parse_sensor_data
from services.vector_service import search_runbooks
from services.gemini_service import generate


def investigate_incident(
    log: str,
    sensor_data: list,
) -> str:
    """
    Performs a complete investigation using
    ONE Gemini request.
    """

    # -----------------------------
    # Parse logs
    # -----------------------------

    use_mcp = os.getenv("RACKMIND_USE_MCP", "0").lower() in ("1", "true", "yes")
    if use_mcp:
        from rackmind_mcp.integration import analyze_incident
        mcp_logs, mcp_sensors = analyze_incident(
            log, pd.DataFrame(sensor_data).to_csv(index=False)
        )
        log_summary = mcp_logs["summary"]
        sensor_summary = mcp_sensors["summary"]
    else:
        log_summary = parse_log(log)

    # -----------------------------
    # Parse sensors
    # -----------------------------

    sensor_df = pd.DataFrame(sensor_data)

    if not use_mcp:
        sensor_summary = parse_sensor_data(sensor_df)

    # -----------------------------
    # Retrieve runbook context
    # -----------------------------

    docs = search_runbooks(
        "CRC high temperature cooling"
    )

    runbook_context = "\n\n".join(docs)

    # -----------------------------
    # Build ONE prompt
    # -----------------------------

    prompt = f"""
You are a senior data center engineer.

Analyze the incident.\n\nData source: {"MCP tools over stdio" if use_mcp else "local Python parsers"}.

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

Write a professional executive report.

Include:

1. Executive Summary

2. Root Cause

3. Business Impact

4. Recommended Actions

5. Priority

6. Confidence
"""

    return generate(prompt)