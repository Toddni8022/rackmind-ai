"""
RackMind AI

Application Configuration
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# Application
# --------------------------------------------------

APP_NAME = "RackMind AI"

APP_VERSION = "1.0.0"

# --------------------------------------------------
# Gemini
# --------------------------------------------------

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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