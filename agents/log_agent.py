import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_log_summary(summary):

    prompt = f"""
You are a Senior Network Operations Engineer.

Analyze this structured log summary.

Log Summary

{summary}

Provide:

# Executive Summary

# Likely Root Cause

# Recommended Actions

# Priority

# Confidence
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text