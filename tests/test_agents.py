from agents.log_agent import analyze_log_summary
from agents.sensor_agent import analyze_sensor_data


def test_log_agent_reports_counts_and_flags_faults():
    report = analyze_log_summary(
        {
            "events": 12,
            "errors": 6,
            "warnings": 3,
            "crc_errors": 2,
            "resets": 1,
            "max_temp": 95,
        }
    )

    assert "- Events: 12" in report
    assert "CRC errors indicate possible physical layer issues" in report
    assert "Interface resets were detected" in report
    assert "Multiple switch errors detected" in report
    assert "Critical temperature readings" in report


def test_log_agent_tolerates_missing_and_bad_values():
    report = analyze_log_summary({"events": "not-a-number", "max_temp": None})
    assert "- Events: 0" in report
    assert "CRC errors indicate" not in report


def test_sensor_agent_flags_critical_temperature_and_power():
    report = analyze_sensor_data(
        {
            "samples": 10,
            "max_temp": 95,
            "avg_temp": 82.5,
            "avg_humidity": 45,
            "peak_power": 4.8,
        }
    )

    assert "Maximum Temperature: 95°F" in report
    assert "Critical temperature threshold exceeded" in report
    assert "Power draw is elevated" in report


def test_sensor_agent_handles_missing_telemetry():
    report = analyze_sensor_data({"samples": 0})
    assert "Maximum Temperature: N/A" in report
    assert "Temperature data was not found" in report
