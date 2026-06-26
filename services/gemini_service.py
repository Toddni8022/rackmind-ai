"""
RackMind AI

Central AI Service
"""

import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

from services.logger import (
    info,
    warning,
    error,
)

load_dotenv()


class AIService:
    """
    Centralized Gemini service used by
    all RackMind agents.
    """

    def __init__(self):

        self.model = GEMINI_MODEL
        self._client = None

    def _get_client(self):

        if not GEMINI_API_KEY:
            return None

        if self._client is None:
            self._client = genai.Client(
                api_key=GEMINI_API_KEY
            )

        return self._client

    def generate(
        self,
        prompt: str,
        retries: int = 3,
    ) -> str:

        client = self._get_client()

        if client is None:
            warning("Gemini API key is not configured.")

            return """
# AI Service Offline

Gemini is not configured. RackMind generated a local deterministic assessment instead.
"""

        info(f"Gemini request using {self.model}")

        for attempt in range(retries):

            try:

                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                info("Gemini request completed successfully.")

                return response.text or ""

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
"""

                time.sleep(2)

            except Exception as ex:

                error(str(ex))

                return f"""
# AI Service Error

{str(ex)}
"""

        return ""


ai = AIService()


def generate(prompt: str) -> str:
    """
    Backwards-compatible helper.

    Existing agents can continue calling:

        generate(prompt)

    without modification.
    """

    return ai.generate(prompt)
