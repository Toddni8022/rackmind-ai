"""
RackMind AI

Central AI Service
"""

from google import genai
from google.genai.errors import ServerError
from dotenv import load_dotenv

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

from services.logger import (
    info,
    warning,
    error,
)

import time

load_dotenv()

client = genai.Client(
    api_key=GEMINI_API_KEY
)


class AIService:
    """
    Centralized Gemini service used by
    all RackMind agents.
    """

    def __init__(self):

        self.model = GEMINI_MODEL

    def generate(
        self,
        prompt: str,
        retries: int = 3,
    ) -> str:

        info(f"Gemini request using {self.model}")

        for attempt in range(retries):

            try:

                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                info("Gemini request completed successfully.")

                return response.text

            except ServerError as ex:

                warning(
                    f"Gemini unavailable. Retry {attempt + 1}/{retries}"
                )

                if attempt == retries - 1:

                    error(str(ex))

                    return f"""
# Gemini Service Busy

The Gemini API is temporarily unavailable.

Model:
{self.model}

Reason:

{str(ex)}

Please try again shortly.
"""

                time.sleep(2)

            except Exception as ex:

                error(str(ex))

                return f"""
# AI Service Error

{str(ex)}
"""

        return "No response returned."


ai = AIService()


def generate(prompt: str) -> str:
    """
    Backwards-compatible helper.

    Existing agents can continue calling:

        generate(prompt)

    without modification.
    """

    return ai.generate(prompt)