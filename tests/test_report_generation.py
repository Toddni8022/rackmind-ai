"""
Tests for the deterministic (non-LLM) report generators.
"""

from agents.executive_summary_agent import generate_executive_summary
from agents.incident_report_agent import generate_incident_report
from agents.log_agent import analyze_log_summary
from agents.root_cause_agent import analyze_root_cause
from agents.sensor_agent import analyze_sensor_data


class TestLogAgent:

    def test_reports_all_metrics(self):
        report = analyze_log_summary(
            {
                "events": 10,
                "errors": 2,
                "warnings": 3,
                "crc_errors": 4,
                "resets": 1,
                "max_temp": 91,
            }
        )

        assert "Events: 10" in report
        assert "Errors: 2" in report
        assert "CRC Errors: 4" in report
        assert "91°F" in report
        assert "physical layer" in report
        assert "Critical temperature" in report

    def test_accepts_log_reader_key_names(self):
        report = analyze_log_summary(
            {
                "total_events": 5,
                "interface_resets": 2,
                "max_temperature": 75,
            }
        )

        assert "Events: 5" in report
        assert "Interface Resets: 2" in report
        assert "75°F" in report

    def test_handles_empty_summary(self):
        report = analyze_log_summary({})

        assert "Events: 0" in report


class TestSensorAgent:

    def test_critical_temperature_message(self):
        report = analyze_sensor_data({"max_temp": 95, "samples": 9})

        assert "Critical temperature threshold exceeded" in report

    def test_warning_temperature_message(self):
        report = analyze_sensor_data({"max_temp": 85})

        assert "Elevated rack temperature" in report

    def test_normal_temperature_message(self):
        report = analyze_sensor_data({"max_temp": 70})

        assert "within expected limits" in report

    def test_missing_temperature_message(self):
        report = analyze_sensor_data({})

        assert "Temperature data was not found" in report
        assert "N/A" in report

    def test_power_warning(self):
        report = analyze_sensor_data({"max_temp": 70, "peak_power": 4.9})

        assert "Power draw is elevated" in report


class TestIncidentReport:

    def test_severity_bands(self):
        low = generate_incident_report("temp", 0, 95, "analysis")
        medium = generate_incident_report("temp", 3, 75, "analysis")
        high = generate_incident_report("temp", 9, 40, "analysis")

        assert "Severity:\nLow" in low
        assert "Severity:\nMedium" in medium
        assert "Severity:\nHigh" in high

    def test_includes_analysis_and_metrics(self):
        report = generate_incident_report(
            "temperature", 4, 62, "cooling failure suspected"
        )

        assert "cooling failure suspected" in report
        assert "62/100" in report
        assert "temperature" in report


class TestExecutiveSummary:

    def test_status_and_risk_labels(self):
        summary = generate_executive_summary(
            "temperature", 80.0, 5.0, 3, 65, 80
        )

        assert "Critical" in summary
        assert "Critical (80%)" in summary

    def test_healthy_summary(self):
        summary = generate_executive_summary(
            "temperature", 70.0, 1.0, 0, 95, 10
        )

        assert "Healthy" in summary
        assert "Low (10%)" in summary
        assert "stable" in summary.lower()


class TestRootCauseAgent:

    def test_no_anomalies(self):
        analysis = analyze_root_cause("temp", 70.0, 1.0, 0, 95)

        assert "No abnormal behavior" in analysis
        assert "Continue normal monitoring" in analysis

    def test_many_anomalies_escalates(self):
        analysis = analyze_root_cause("temp", 88.0, 9.0, 20, 40)

        assert "significant number of anomalies" in analysis
        assert "Escalate to Infrastructure Operations" in analysis
