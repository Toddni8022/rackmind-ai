"""
RackMind AI

Google ADK Chat Service
"""

import asyncio
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from adk.root_agent import root_agent
from adk.incident_tool import investigate_incident
from agents.runbook_agent import answer_question_local

from services.logger import info, error

APP_NAME = "rackmind-ai"
USER_ID = "streamlit"
SESSION_ID = "default"

session_service = InMemorySessionService()


def _is_quota_error(message: str) -> bool:
    markers = (
        "RESOURCE_EXHAUSTED",
        "prepayment credits are depleted",
        "429",
        "quota",
    )

    return any(marker.lower() in message.lower() for marker in markers)


async def ask_adk(question: str) -> str:

    info("Starting ADK request.")

    try:

        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

    except Exception:
        pass

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=question)],
    )

    answer = ""

    try:

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=message,
        ):

            if event.content is None:
                continue

            if not hasattr(event.content, "parts"):
                continue

            if not event.content.parts:
                continue

            for part in event.content.parts:

                if hasattr(part, "text") and part.text:
                    answer = part.text

    except Exception as ex:

        message = str(ex)
        error(message)

        if _is_quota_error(message):
            return answer_question_local(question)

        return """
### AI Service Error

RackMind could not reach the cloud reasoning service for this request.

Try again later, or use the Log Agent, Sensor Agent, and Incident Commander tabs for local deterministic analysis.
"""

    info("ADK request completed.")

    if not answer:
        return "No response returned."

    return answer


def ask(question: str) -> str:
    return asyncio.run(ask_adk(question))


def investigate(
    log_text: str,
    sensor_df: pd.DataFrame,
) -> str:

    info("Starting incident investigation.")

    result = investigate_incident(
        log=log_text,
        sensor_data=sensor_df.to_dict(orient="records"),
    )

    info("Incident investigation completed.")

    return result
