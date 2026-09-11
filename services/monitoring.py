"""Structured operational monitoring hooks without requiring a third-party service."""
import logging
import traceback

logger = logging.getLogger("rackmind.monitoring")


def initialize():
    """Enable Sentry only when a DSN is supplied; never block local/demo startup."""
    dsn = __import__("os").getenv("SENTRY_DSN")
    if not dsn:
        return False
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.0, send_default_pii=False)
        return True
    except Exception as exc:
        logger.warning("monitoring_initialization_failed: %s", exc)
        return False


def capture_exception(exc, context=None):
    logger.error("application_exception", extra={"context": context or {}, "error": str(exc), "trace": traceback.format_exc()})
