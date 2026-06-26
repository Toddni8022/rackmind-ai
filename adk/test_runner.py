"""
RackMind AI

ADK Runner Test
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from google.genai import types

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from adk.root_agent import root_agent


APP_NAME = "rackmind-ai"
USER_ID = "todd"
SESSION_ID = "demo"


async def main():

    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="What causes CRC errors?"
            )
        ],
    )

    print("\nRunning ADK...\n")

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message,
    ):

        if event.is_final_response():

            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())