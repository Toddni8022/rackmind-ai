"""
RackMind AI

Health Scoring Service

Single source of truth for infrastructure health scoring so the
log page, trend dashboard, and tests all agree on thresholds.
"""

from config import POWER_WARNING, TEMP_CRITICAL, TEMP_WARNING

ERROR_PENALTY = 8
WARNING_PENALTY = 2
CRC_PENALTY = 3
RESET_PENALTY = 5
TEMP_WARNING_PENALTY = 10
TEMP_CRITICAL_PENALTY = 25
POWER_PENALTY = 5


def compute_health_score(summary: dict) -> int:
    """
    Convert a parsed log/sensor summary into a 0-100 health score.

    Accepts both parser shapes:
        services.log_parser.parse_log  -> errors/warnings/crc_errors/resets/max_temp
        tools.log_reader.analyze_log   -> errors/warnings/crc_errors/interface_resets/max_temperature
    """

    def _number(*keys, default=0):
        for key in keys:
            value = summary.get(key)

            if value in (None, ""):
                continue

            try:
                return float(value)
            except (TypeError, ValueError):
                continue

        return default

    score = 100.0

    score -= _number("errors") * ERROR_PENALTY
    score -= _number("warnings") * WARNING_PENALTY
    score -= _number("crc_errors") * CRC_PENALTY
    score -= _number("resets", "interface_resets") * RESET_PENALTY

    max_temp = _number("max_temp", "max_temperature")

    if max_temp >= TEMP_CRITICAL:
        score -= TEMP_CRITICAL_PENALTY
    elif max_temp >= TEMP_WARNING:
        score -= TEMP_WARNING_PENALTY

    peak_power = _number("peak_power")

    if peak_power >= POWER_WARNING:
        score -= POWER_PENALTY

    return int(max(0, min(100, round(score))))


def health_status(score: int) -> str:
    """
    Map a health score to an operator-facing status label.
    """

    if score >= 90:
        return "Healthy"

    if score >= 70:
        return "Warning"

    return "Critical"
