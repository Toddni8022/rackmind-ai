"""
RackMind AI

Central AI Service

Supports Google Gemini and OpenAI behind one generate() helper.
"""

import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

from config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

from services.logger import (
    error,
    info,
    warning,
)

load_dotenv()


class AIService:
    """
    Centralized AI service used by all RackMind agents.

    Provider options:
        AI_PROVIDER="auto"   -> OpenAI if OPENAI_API_KEY exists, otherwise Gemini
        AI_PROVIDER="gemini" -> Google Gemini only
        AI_PROVIDER="openai" -> OpenAI only
    """

    def __init__(self):

        self.gemini_model = GEMINI_MODEL
        self.openai_model = OPENAI_MODEL
        self._gemini_client = None
        self._openai_client = None

    def _provider(self) -> str:

        provider = str(AI_PROVIDER or "auto").strip().lower()

        if provider in ("google", "gemini"):
            return "gemini"

        if provider in ("openai", "open_ai", "gpt"):
            return "openai"

        if provider == "auto":
            if OPENAI_API_KEY:
                return "openai"

            if GEMINI_API_KEY:
                return "gemini"

            return "gemini"

        raise RuntimeError(
            "AI_PROVIDER must be 'auto', 'gemini', or 'openai'."
        )

    def _get_gemini_client(self):

        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GOOGLE_API_KEY is not configured. "
                "Add it to your local .env file or Streamlit Cloud secrets."
            )

        if str(GEMINI_API_KEY).startswith("sk-"):
            raise RuntimeError(
                "The configured Google key looks like an OpenAI key. "
                "Move it to OPENAI_API_KEY and set AI_PROVIDER='openai', "
                "or use a Google AI Studio key that usually starts with AIza."
            )

        if self._gemini_client is None:
            self._gemini_client = genai.Client(
                api_key=GEMINI_API_KEY
            )

        return self._gemini_client

    def _get_openai_client(self):

        if not OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. "
                "Add it to your local .env file or Streamlit Cloud secrets."
            )

        if str(OPENAI_API_KEY).startswith("AIza"):
            raise RuntimeError(
                "The configured OpenAI key looks like a Google Gemini key. "
                "Move it to GOOGLE_API_KEY and set AI_PROVIDER='gemini', "
                "or use an OpenAI key that starts with sk-."
            )

        if self._openai_client is None:
            try:
                from openai import OpenAI
            except ImportError as ex:
                raise RuntimeError(
                    "The openai package is not installed. Run: pip install openai"
                ) from ex

            self._openai_client = OpenAI(
                api_key=OPENAI_API_KEY
            )

        return self._openai_client

    def generate(
        self,
        prompt: str,
        retries: int = 3,
    ) -> str:

        provider = self._provider()
        info(f"AI request using provider={provider}")

        if provider == "openai":
            return self._generate_openai(prompt, retries)

        return self._generate_gemini(prompt, retries)

    def _generate_gemini(
        self,
        prompt: str,
        retries: int,
    ) -> str:

        info(f"Gemini request using {self.gemini_model}")

        try:
            client = self._get_gemini_client()
        except Exception as ex:
            warning(str(ex))

            return f"""
# AI Service Not Configured

{str(ex)}

The demo dashboard can still run, but Gemini-powered responses require a valid Google API key.
"""

        for attempt in range(retries):

            try:

                response = client.models.generate_content(
                    model=self.gemini_model,
                    contents=prompt,
                )

                info("Gemini request completed successfully.")

                if not response.text:
                    return "Gemini returned an empty response. Try again."

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
{self.gemini_model}

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

    def _generate_openai(
        self,
        prompt: str,
        retries: int,
    ) -> str:

        info(f"OpenAI request using {self.openai_model}")

        try:
            client = self._get_openai_client()
        except Exception as ex:
            warning(str(ex))

            return f"""
# AI Service Not Configured

{str(ex)}

The demo dashboard can still run, but OpenAI-powered responses require a valid OpenAI API key.
"""

        for attempt in range(retries):

            try:

                response = client.responses.create(
                    model=self.openai_model,
                    input=prompt,
                )

                info("OpenAI request completed successfully.")

                text = getattr(response, "output_text", None)

                if text:
                    return text

                return self._extract_openai_text(response)

            except Exception as ex:

                warning(
                    f"OpenAI request failed. Retry {attempt + 1}/{retries}"
                )

                if attempt == retries - 1:
                    error(str(ex))

                    return f"""
# OpenAI Service Error

Model:
{self.openai_model}

Reason:

{str(ex)}
"""

                time.sleep(2)

        return "No response returned."

    @staticmethod
    def _extract_openai_text(response) -> str:
        """
        Fallback parser for OpenAI SDK response objects.
        """

        parts = []

        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)

                if text:
                    parts.append(text)

        if parts:
            return "\n".join(parts)

        return "OpenAI returned an empty response. Try again."


ai = AIService()


def generate(prompt: str) -> str:
    """
    Backwards-compatible helper.

    Existing agents can continue calling:

        generate(prompt)

    without modification.
    """

    return ai.generate(prompt)
