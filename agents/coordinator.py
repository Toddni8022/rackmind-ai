import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_issue(issue: str) -> str:
    """
    RackMind AI Coordinator Agent

    This agent performs the initial infrastructure analysis.
    Future versions will coordinate specialized Runbook,
    Log, Sensor, and Report agents.
    """

    prompt = f"""
You are a Senior Data Center Infrastructure Engineer.

Analyze the following issue.

Return your answer using this format:

# Root Cause

# Likely Impact

# Recommended Actions

- item 1
- item 2
- item 3

# Priority

# Confidence Score

Issue:

{issue}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text