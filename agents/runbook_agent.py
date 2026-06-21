import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def search_runbook(question, runbook_text):

    prompt = f"""
You are a senior data center engineer.

Use ONLY the supplied documentation.

Documentation:

{runbook_text[:15000]}

Question:

{question}

Provide a concise answer with:

- Explanation
- Recommended actions
- Confidence
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text