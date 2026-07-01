"""
RackMind AI

Trend + Prediction Service

Analyzes telemetry history per rack, fits simple linear trends,
and flags racks that are likely to reach critical temperature,
power, or health thresholds soon.
"""

from datetime import datetime, timedelta

from config import POWER_WARNING, TEMP_CRITICAL, TEMP_WARNING
from services.telemetry_store import get_history, list_racks

HEALTH_CRITICAL = 70

# A rack predicted to go critical inside this window is flagged.
PREDICTION_WINDOW_HOURS = 24


def _parse_timestamp(value) -> datetime | None:
    if isinstance(value, datetime):
        return value

    text = str(value or "").strip()

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%H:%M",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def linear_trend(points: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Least-squares fit over (x, y) points. Returns (slope, intercept).
    A flat line is returned when there are fewer than two points.
    """

    if len(points) < 2:
        y = points[0][1] if points else 0.0
        return 0.0, float(y)

    n = len(points)
    sum_x = sum(x for x, _ in points)
    sum_y = sum(y for _, y in points)
    sum_xy = sum(x * y for x, y in points)
    sum_x2 = sum(x * x for x, _ in points)

    denominator = (n * sum_x2) - (sum_x * sum_x)

    if denominator == 0:
        return 0.0, sum_y / n

    slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator
    intercept = (sum_y - slope * sum_x) / n

    return slope, intercept


def hours_until(
    points: list[tuple[float, float]],
    threshold: float,
    rising: bool = True,
    min_slope: float = 0.0,
) -> float | None:
    """
    Given (hours, value) points, estimate hours from the latest
    sample until the fitted line crosses the threshold.

    Returns None when the trend never reaches the threshold, and
    0.0 when the threshold is already breached. Slopes flatter
    than min_slope are treated as noise, not a trend.
    """

    if not points:
        return None

    latest_x, latest_y = points[-1]

    if (rising and latest_y >= threshold) or (
        not rising and latest_y <= threshold
    ):
        return 0.0

    slope, intercept = linear_trend(points)

    if rising and slope <= 0:
        return None

    if not rising and slope >= 0:
        return None

    if abs(slope) < min_slope:
        return None

    crossing_x = (threshold - intercept) / slope

    remaining = crossing_x - latest_x

    return max(0.0, round(remaining, 1))


def _metric_points(history: list[dict], metric: str) -> list[tuple[float, float]]:
    """
    Convert history rows into (hours since first sample, value)
    points for one metric, skipping missing values.
    """

    points = []
    first_ts = None

    for index, row in enumerate(history):
        value = row.get(metric)

        if value is None:
            continue

        ts = _parse_timestamp(row.get("recorded_at"))

        if ts is None:
            # Fall back to sample index spacing (assume 5 minutes).
            x_hours = index * (5 / 60)
        else:
            if first_ts is None:
                first_ts = ts

            x_hours = (ts - first_ts).total_seconds() / 3600

        points.append((float(x_hours), float(value)))

    return points


def analyze_rack(rack: str, history: list[dict] = None) -> dict:
    """
    Build a trend + prediction summary for one rack.
    """

    if history is None:
        history = get_history(rack=rack)

    temp_points = _metric_points(history, "temperature")
    power_points = _metric_points(history, "power_kw")
    health_points = _metric_points(history, "health_score")

    # Minimum slopes filter out sensor noise so a flat rack with a
    # tiny wobble is not extrapolated into a failure.
    temp_hours = hours_until(
        temp_points, TEMP_CRITICAL, rising=True, min_slope=0.5
    )
    power_hours = hours_until(
        power_points, POWER_WARNING, rising=True, min_slope=0.02
    )
    health_hours = hours_until(
        health_points, HEALTH_CRITICAL, rising=False, min_slope=0.5
    )

    reasons = []

    def _describe(label, hours, unit=""):
        if hours is None:
            return

        if hours == 0:
            reasons.append(f"{label} threshold already breached{unit}")
        elif hours <= PREDICTION_WINDOW_HOURS:
            reasons.append(
                f"{label} projected to go critical in ~{hours} h{unit}"
            )

    _describe("Temperature", temp_hours)
    _describe("Power", power_hours)
    _describe("Health score", health_hours)

    breached = [h for h in (temp_hours, power_hours, health_hours) if h == 0]
    imminent = [
        h
        for h in (temp_hours, power_hours, health_hours)
        if h is not None and 0 < h <= PREDICTION_WINDOW_HOURS
    ]

    if breached:
        risk = "Critical"
        eta_hours = 0.0
    elif imminent:
        risk = "At Risk"
        eta_hours = min(imminent)
    else:
        risk = "Stable"
        eta_hours = None

    latest = history[-1] if history else {}

    return {
        "rack": rack,
        "samples": len(history),
        "risk": risk,
        "eta_hours": eta_hours,
        "reasons": reasons,
        "latest_temperature": latest.get("temperature"),
        "latest_power_kw": latest.get("power_kw"),
        "latest_health_score": latest.get("health_score"),
        "temp_slope_per_hour": round(linear_trend(temp_points)[0], 3)
        if temp_points
        else None,
        "hours_to_temp_critical": temp_hours,
        "hours_to_power_warning": power_hours,
        "hours_to_health_critical": health_hours,
    }


def analyze_all_racks() -> list[dict]:
    """
    Trend summary for every rack with telemetry, riskiest first.
    """

    order = {"Critical": 0, "At Risk": 1, "Stable": 2}

    results = [analyze_rack(rack) for rack in list_racks()]

    results.sort(
        key=lambda item: (
            order.get(item["risk"], 3),
            item["eta_hours"] if item["eta_hours"] is not None else float("inf"),
        )
    )

    return results


def seed_sample_telemetry() -> int:
    """
    Load demo telemetry from the bundled sample data so the trend
    dashboard renders before any live connector is configured.
    """

    from services.telemetry_store import count_readings, record_reading

    if count_readings() > 0:
        return 0

    base = datetime(2026, 6, 21, 6, 0)

    # (hours offset, temp, humidity, power, crc, resets, health)
    rack22 = [
        (0, 72, 44, 4.1, 0, 0, 96),
        (2, 73, 44, 4.2, 0, 0, 95),
        (4, 75, 45, 4.2, 1, 0, 92),
        (6, 77, 46, 4.3, 2, 0, 88),
        (8, 82, 47, 4.4, 3, 0, 82),
        (10, 87, 48, 4.6, 4, 1, 71),
        (11, 91, 49, 4.8, 5, 1, 58),
        (12, 92, 50, 4.9, 6, 2, 49),
        (13, 90, 50, 4.8, 6, 2, 51),
    ]

    rack7 = [
        (0, 68, 41, 3.1, 0, 0, 99),
        (3, 69, 41, 3.2, 0, 0, 99),
        (6, 69, 42, 3.1, 1, 0, 96),
        (9, 70, 42, 3.2, 1, 0, 96),
        (12, 70, 42, 3.2, 1, 0, 96),
    ]

    count = 0

    for hours, temp, humidity, power, crc, resets, health in rack22:
        record_reading(
            rack="Rack-22",
            recorded_at=(base + timedelta(hours=hours)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            temperature=temp,
            humidity=humidity,
            power_kw=power,
            crc_errors=crc,
            resets=resets,
            health_score=health,
            source="seed",
        )
        count += 1

    for hours, temp, humidity, power, crc, resets, health in rack7:
        record_reading(
            rack="Rack-07",
            recorded_at=(base + timedelta(hours=hours)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            temperature=temp,
            humidity=humidity,
            power_kw=power,
            crc_errors=crc,
            resets=resets,
            health_score=health,
            source="seed",
        )
        count += 1

    return count
