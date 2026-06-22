import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_incident_report(log_report="", runbook_report="", sensor_report=""):

    prompt = f"""
You are a Senior Data Center Incident Manager.

Combine the information from multiple AI agents into one professional report.

Log Agent Output

{log_report}

Runbook Agent Output

{runbook_report}

Sensor Agent Output

{sensor_report}

Return your response using this format.

# Executive Summary

# Root Cause

# Business Impact

# Recommended Actions

- Action 1
- Action 2
- Action 3

# Priority

# Confidence
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text