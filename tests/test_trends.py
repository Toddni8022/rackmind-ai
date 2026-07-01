"""
Tests for the telemetry store and trend/prediction service.
"""

from services.telemetry_store import (
    count_readings,
    get_history,
    list_racks,
    record_reading,
    record_readings,
)
from services.trend_service import (
    analyze_all_racks,
    analyze_rack,
    hours_until,
    linear_trend,
    seed_sample_telemetry,
)


def _record_series(rack, series, metric="temperature"):
    for hour, value in series:
        record_reading(
            rack=rack,
            recorded_at=f"2026-06-21 {hour:02d}:00:00",
            **{metric: value},
        )


class TestTelemetryStore:

    def test_record_and_fetch(self):
        record_reading(
            rack="Rack-22",
            recorded_at="2026-06-21 18:00:00",
            temperature=72,
            power_kw=4.1,
        )

        history = get_history(rack="Rack-22")

        assert len(history) == 1
        assert history[0]["temperature"] == 72
        assert history[0]["power_kw"] == 4.1

    def test_bulk_record_normalized_readings(self):
        saved = record_readings(
            [
                {"rack": "Rack-01", "timestamp": "2026-06-21 18:00:00",
                 "temperature": 70},
                {"rack": "Rack-02", "timestamp": "2026-06-21 18:00:00",
                 "temperature": 71},
            ]
        )

        assert saved == 2
        assert sorted(list_racks()) == ["Rack-01", "Rack-02"]

    def test_history_sorted_by_time(self):
        record_reading(rack="R", recorded_at="2026-06-21 19:00:00", temperature=80)
        record_reading(rack="R", recorded_at="2026-06-21 18:00:00", temperature=70)

        history = get_history(rack="R")

        assert [row["temperature"] for row in history] == [70, 80]


class TestLinearTrend:

    def test_fits_rising_line(self):
        slope, intercept = linear_trend([(0, 0), (1, 2), (2, 4)])

        assert round(slope, 6) == 2
        assert round(intercept, 6) == 0

    def test_flat_series(self):
        slope, _ = linear_trend([(0, 5), (1, 5), (2, 5)])

        assert slope == 0

    def test_single_point(self):
        slope, intercept = linear_trend([(0, 7)])

        assert slope == 0
        assert intercept == 7


class TestHoursUntil:

    def test_rising_series_predicts_crossing(self):
        # +2°F per hour starting at 80: hits 90 five hours after hour 2.
        points = [(0, 80), (1, 82), (2, 84)]

        assert hours_until(points, 90, rising=True) == 3.0

    def test_already_breached_returns_zero(self):
        assert hours_until([(0, 95)], 90, rising=True) == 0.0

    def test_cooling_series_never_crosses(self):
        points = [(0, 84), (1, 82), (2, 80)]

        assert hours_until(points, 90, rising=True) is None

    def test_falling_threshold_direction(self):
        # Health score dropping 10/hour from 100 crosses 70 at hour 3.
        points = [(0, 100), (1, 90), (2, 80)]

        assert hours_until(points, 70, rising=False) == 1.0

    def test_empty_series(self):
        assert hours_until([], 90) is None

    def test_min_slope_filters_noise(self):
        # A 0.17°F/h drift is noise, not a failure trend.
        points = [(0, 70), (12, 72)]

        assert hours_until(points, 90, rising=True, min_slope=0.5) is None
        assert hours_until(points, 90, rising=True) is not None


class TestRackAnalysis:

    def test_stable_rack(self):
        _record_series("Rack-OK", [(10, 70), (11, 70), (12, 70)])

        result = analyze_rack("Rack-OK")

        assert result["risk"] == "Stable"
        assert result["eta_hours"] is None
        assert result["reasons"] == []

    def test_rack_trending_to_critical_is_flagged(self):
        # +3°F per hour from 80 crosses 90 within ~4 hours.
        _record_series("Rack-HOT", [(10, 80), (11, 83), (12, 86)])

        result = analyze_rack("Rack-HOT")

        assert result["risk"] == "At Risk"
        assert 0 < result["eta_hours"] <= 24
        assert any("Temperature" in reason for reason in result["reasons"])

    def test_breached_rack_is_critical(self):
        _record_series("Rack-BAD", [(10, 88), (11, 91), (12, 93)])

        result = analyze_rack("Rack-BAD")

        assert result["risk"] == "Critical"
        assert result["eta_hours"] == 0.0

    def test_all_racks_sorted_riskiest_first(self):
        _record_series("Rack-OK", [(10, 70), (11, 70), (12, 70)])
        _record_series("Rack-BAD", [(10, 88), (11, 91), (12, 93)])

        results = analyze_all_racks()

        assert results[0]["rack"] == "Rack-BAD"
        assert results[-1]["rack"] == "Rack-OK"


class TestSeed:

    def test_seed_only_when_empty(self):
        first = seed_sample_telemetry()
        second = seed_sample_telemetry()

        assert first > 0
        assert second == 0
        assert count_readings() == first

    def test_seeded_data_produces_a_flagged_rack(self):
        seed_sample_telemetry()

        results = analyze_all_racks()

        assert any(r["risk"] != "Stable" for r in results)
