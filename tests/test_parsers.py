import pandas as pd

from services.log_parser import build_log_timeline, parse_log
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
