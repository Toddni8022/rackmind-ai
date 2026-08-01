"""
RackMind AI

Application Logger
"""

import logging

from config import LOG_DIR

LOG_FILE = LOG_DIR / "rackmind.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("rackmind")


def info(message: str):
    logger.info(message)


def warning(message: str):
    logger.warning(message)


def error(message: str):
    logger.error(message)


def exception(message: str):
    logger.exception(message)
