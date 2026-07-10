import pandas as pd

from services.assessment_service import build_alerts, score_operations
from services.log_parser import build_log_timeline, parse_log
from services.sensor_parser import parse_sensor_data


def test_log_parser_extracts_operational_signals():
    text = "\n".join(
        [
            "10:00 WARNING interface temperature 91 F",
            "10:01 ERROR CRC failure on Ethernet1/4",
            "10:02 link reset completed",
        ]
    )
    summary = parse_log(text)

    assert summary == {
        "events": 3,
        "warnings": 1,
        "errors": 1,
        "crc_errors": 1,
        "resets": 1,
        "max_temp": 91.0,
    }
    assert len(build_log_timeline(text)) == 3


def test_sensor_parser_and_score_flag_critical_conditions():
    summary = parse_sensor_data(
        pd.DataFrame(
            {
                "temperature": [78, 92],
                "humidity": [44, 48],
                "power_kw": [3.2, 4.8],
            }
        )
    )
    score = score_operations(sensor_summary=summary)

    assert summary["max_temp"] == 92.0
    assert summary["peak_power"] == 4.8
    assert score["status"] == "Critical"
    assert len(build_alerts(sensor_summary=summary)) == 2


def test_healthy_inputs_remain_healthy():
    score = score_operations(
        {"events": 10, "warnings": 0, "errors": 0},
        {"max_temp": 72, "avg_humidity": 45, "peak_power": 3.0},
    )
    assert score == {"score": 100, "status": "Healthy", "severity": "Low"}
