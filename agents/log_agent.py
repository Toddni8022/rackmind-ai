import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_log_summary(summary):

    severity = "LOW"

    if summary["errors"] >= 2:
        severity = "MEDIUM"

    if (
        summary["crc_errors"] >= 3
        or summary["max_temperature"] >= 90
    ):
        severity = "HIGH"

    prompt = f"""
You are a Senior Network Operations Engineer.

Infrastructure Summary

{summary}

Generate a professional incident report.

Use this exact format.

# Executive Summary

# Root Cause

# Business Impact

# Recommended Actions

- Action 1
- Action 2
- Action 3

# Priority

{severity}

# Confidence
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text