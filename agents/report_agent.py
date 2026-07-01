"""
RackMind AI

Report Agent
"""

from services.gemini_service import generate

GROUND_RULES = """
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
  With missing sections, Confidence must not be High.
- In the report, cite only numbers and events that appear verbatim
  in the data below.
"""


def _section(title: str, content: str) -> str:

    body = (content or "").strip() or "NOT PROVIDED"

    return f"{title}\n\n{body}"


def generate_incident_report(
    log_report="",
    runbook_report="",
    sensor_report="",
):

    prompt = f"""
You are an Incident Manager.

Merge the analysis below into one executive report.

{GROUND_RULES}

{_section("LOG ANALYSIS", log_report)}

{_section("RUNBOOK GUIDANCE", runbook_report)}

{_section("SENSOR ANALYSIS", sensor_report)}

Return:

# Executive Summary

# Root Cause

# Business Impact

# Recommended Actions

# Priority

# Confidence
"""

    return generate(prompt)
