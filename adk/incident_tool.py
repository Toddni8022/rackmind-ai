"""
RackMind AI

Single-Prompt Incident Investigation
"""

import pandas as pd

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

    log_summary = parse_log(log)

    # -----------------------------
    # Parse sensors
    # -----------------------------

    sensor_df = pd.DataFrame(sensor_data)

    sensor_summary = parse_sensor_data(sensor_df)

    # -----------------------------
    # Retrieve runbook context
    # -----------------------------

    docs = search_runbooks(
        "CRC high temperature cooling"
    )

    runbook_context = "\n\n".join(docs).strip() or "NOT PROVIDED"

    # -----------------------------
    # Build ONE prompt
    # -----------------------------

    prompt = f"""
You are a senior data center engineer.

Analyze the incident.

Ground rules — follow these strictly:

- Use ONLY the data provided below. Do not invent metrics, interface
  names, port numbers, sensor readings, runbook titles, versions, or
  troubleshooting steps that were already performed.
- Sections marked NOT PROVIDED contain no data. State "No data
  provided" for them. Never infer or fabricate their contents.
- If the provided data points to environmental problems (temperature,
  cooling, fans, power), address them; do not rule out causes the
  data supports.
- Base your Confidence level on how much data was actually provided.
- Cite only numbers and events that appear verbatim in the data below.

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