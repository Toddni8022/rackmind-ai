"""
Tests for health scoring and predictive risk thresholds.
"""

from agents.predictive_risk_agent import predict_failure_risk
from services.scoring import compute_health_score, health_status


class TestHealthScore:

    def test_clean_summary_is_perfect(self):
        assert compute_health_score({}) == 100
        assert compute_health_score(
            {"errors": 0, "warnings": 0, "crc_errors": 0, "resets": 0}
        ) == 100

    def test_error_and_warning_penalties(self):
        assert compute_health_score({"errors": 1}) == 92
        assert compute_health_score({"warnings": 1}) == 98
        assert compute_health_score({"crc_errors": 1}) == 97
        assert compute_health_score({"resets": 1}) == 95

    def test_supports_both_parser_shapes(self):
        log_parser_shape = {"resets": 2, "max_temp": 85}
        log_reader_shape = {"interface_resets": 2, "max_temperature": 85}

        assert compute_health_score(log_parser_shape) == compute_health_score(
            log_reader_shape
        )

    def test_temperature_thresholds(self):
        assert compute_health_score({"max_temp": 79}) == 100
        assert compute_health_score({"max_temp": 80}) == 90
        assert compute_health_score({"max_temp": 90}) == 75

    def test_power_threshold(self):
        assert compute_health_score({"peak_power": 4.4}) == 100
        assert compute_health_score({"peak_power": 4.5}) == 95

    def test_score_never_negative(self):
        summary = {"errors": 50, "warnings": 50, "crc_errors": 50}

        assert compute_health_score(summary) == 0

    def test_ignores_junk_values(self):
        assert compute_health_score(
            {"errors": "bad", "warnings": None, "crc_errors": ""}
        ) == 100

    def test_status_bands(self):
        assert health_status(95) == "Healthy"
        assert health_status(90) == "Healthy"
        assert health_status(89) == "Warning"
        assert health_status(70) == "Warning"
        assert health_status(69) == "Critical"


class TestPredictiveRisk:

    def test_low_risk_band(self):
        prediction, score = predict_failure_risk(0, 95)

        assert score == 5
        assert "LOW FAILURE RISK" in prediction

    def test_moderate_risk_band(self):
        prediction, score = predict_failure_risk(4, 90)

        assert score == 30
        assert "MODERATE FAILURE RISK" in prediction

    def test_high_risk_band(self):
        prediction, score = predict_failure_risk(8, 70)

        assert score == 70
        assert "HIGH FAILURE RISK" in prediction

    def test_critical_risk_band(self):
        prediction, score = predict_failure_risk(20, 40)

        assert score == 100
        assert "CRITICAL FAILURE RISK" in prediction

    def test_risk_score_capped_at_100(self):
        _, score = predict_failure_risk(1000, 0)

        assert score == 100

    def test_band_boundaries(self):
        _, score_19 = predict_failure_risk(0, 81)
        prediction_20, _ = predict_failure_risk(4, 100)

        assert score_19 == 19
        assert "MODERATE" in prediction_20
