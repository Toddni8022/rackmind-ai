import pandas as pd

from services.log_parser import build_log_timeline, compute_health_score, parse_log
from services.sensor_parser import parse_sensor_data


def test_log_parser_handles_realistic_variants_and_blank_lines():
    summary = parse_log(
        "\nWARNING temp 91.5 F\nERR FCS failure Ethernet1/4\nlink flap detected\n"
    )
    assert summary == {
        "events": 3,
        "warnings": 1,
        "errors": 1,
        "crc_errors": 1,
        "resets": 1,
        "max_temp": 91.5,
    }
    assert len(build_log_timeline("INFO ok\nERROR failed\nWARN hot")) == 2


def test_log_parser_handles_empty_input():
    assert parse_log("") == {
        "events": 0,
        "warnings": 0,
        "errors": 0,
        "crc_errors": 0,
        "resets": 0,
        "max_temp": 0,
    }
    assert build_log_timeline("") == []


def test_log_timeline_respects_limit():
    log_text = "\n".join(f"ERROR event {i}" for i in range(50))
    assert len(build_log_timeline(log_text, limit=10)) == 10


def test_health_score_penalizes_faults_and_never_goes_negative():
    assert compute_health_score({}) == 100
    assert compute_health_score({"errors": 1, "warnings": 2, "crc_errors": 3, "resets": 1}) == 74
    assert compute_health_score({"errors": 100}) == 0


def test_sensor_parser_normalizes_columns_and_bad_values():
    result = parse_sensor_data(
        pd.DataFrame(
            {
                "Rack Temp": ["72", "bad", "91"],
                "Relative Humidity": [40, 44, 48],
                "Load-kW": [3.0, 3.5, 4.8],
            }
        )
    )
    assert result["samples"] == 3
    assert result["max_temp"] == 91.0
    assert result["avg_humidity"] == 44.0
    assert result["peak_power"] == 4.8


def test_sensor_parser_returns_none_for_missing_columns():
    result = parse_sensor_data(pd.DataFrame({"voltage": [120, 121]}))
    assert result["samples"] == 2
    assert result["max_temp"] is None
    assert result["avg_temp"] is None
    assert result["avg_humidity"] is None
    assert result["peak_power"] is None
    assert result["observed_columns"] == ["voltage"]


def test_sensor_parser_handles_empty_dataframe():
    result = parse_sensor_data(pd.DataFrame())
    assert result["samples"] == 0
    assert result["max_temp"] is None
