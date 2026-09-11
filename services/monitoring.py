"""Structured operational monitoring hooks without requiring a third-party service."""
import logging
import traceback

logger = logging.getLogger("rackmind.monitoring")


def capture_exception(exc, context=None):
    logger.error("application_exception", extra={"context": context or {}, "error": str(exc), "trace": traceback.format_exc()})
