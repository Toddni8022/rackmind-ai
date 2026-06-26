"""
RackMind AI

Application Configuration
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_secret(name: str, default=None):
    """
    Read config from environment variables first, then Streamlit Cloud secrets.
    This keeps local development and Streamlit deployment working the same way.
    """
    value = os.getenv(name)

    if value:
        return value

    try:
        import streamlit as st

        return st.secrets.get(name, default)
    except Exception:
        return default


# --------------------------------------------------
# Application
# --------------------------------------------------

APP_NAME = "RackMind AI"

APP_VERSION = "1.0.0"

# --------------------------------------------------
# Gemini
# --------------------------------------------------

GEMINI_MODEL = _get_secret(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

GEMINI_API_KEY = _get_secret("GOOGLE_API_KEY")

# --------------------------------------------------
# Google ADK
# --------------------------------------------------

ADK_APP_NAME = "rackmind-ai"

ADK_USER = "streamlit"

ADK_SESSION = "default"

# --------------------------------------------------
# Directories
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).parent

DATA_DIR = PROJECT_ROOT / "data"

SAMPLE_DIR = PROJECT_ROOT / "sample_data"

LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# AI Thresholds
# --------------------------------------------------

TEMP_WARNING = 80

TEMP_CRITICAL = 90

POWER_WARNING = 4.5

CRC_WARNING = 5
