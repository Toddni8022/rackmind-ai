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

Analyze the following infrastructure log summary.

{summary}

Return your answer in this format:

# Executive Summary

# Root Cause

# Recommended Actions

- item 1
- item 2
- item 3

# Priority

# Confidence
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text