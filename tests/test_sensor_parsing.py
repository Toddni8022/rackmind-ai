"""
Tests for services.sensor_parser, including column-alias handling
and defensive behavior on malformed CSVs.
"""

import pandas as pd

from services.sensor_parser import (
    normalize_column_name,
    normalize_sensor_dataframe,
    parse_sensor_data,
)


class TestNormalization:

    def test_normalize_column_name(self):
        assert normalize_column_name("  Rack Temp ") == "rack_temp"
        assert normalize_column_name("POWER-KW") == "power_kw"

    def test_normalize_dataframe_does_not_mutate_original(self):
        df = pd.DataFrame({" Temperature ": [70]})

        normalized = normalize_sensor_dataframe(df)

        assert "temperature" in normalized.columns
        assert " Temperature " in df.columns


class TestParseSensorData:

    def test_standard_columns(self):
        df = pd.DataFrame(
            {
                "temperature": [72, 84, 91],
                "humidity": [44, 47, 49],
                "power_kw": [3.9, 4.2, 4.8],
            }
        )

        summary = parse_sensor_data(df)

        assert summary["samples"] == 3
        assert summary["max_temp"] == 91
        assert summary["avg_temp"] == round((72 + 84 + 91) / 3, 2)
        assert summary["avg_humidity"] == round((44 + 47 + 49) / 3, 2)
        assert summary["peak_power"] == 4.8

    def test_alias_columns(self):
        df = pd.DataFrame(
            {
                "Temp_F": [70, 75],
                "Relative_Humidity": [40, 42],
                "Load_KW": [3.0, 3.5],
            }
        )

        summary = parse_sensor_data(df)

        assert summary["max_temp"] == 75
        assert summary["avg_humidity"] == 41
        assert summary["peak_power"] == 3.5

    def test_missing_columns_return_none_instead_of_crashing(self):
        df = pd.DataFrame({"voltage": [220, 221]})

        summary = parse_sensor_data(df)

        assert summary["max_temp"] is None
        assert summary["avg_temp"] is None
        assert summary["avg_humidity"] is None
        assert summary["peak_power"] is None
        assert summary["samples"] == 2

    def test_non_numeric_values_are_skipped(self):
        df = pd.DataFrame(
            {"temperature": ["hot", "72", None, "88"]}
        )

        summary = parse_sensor_data(df)

        assert summary["max_temp"] == 88
        assert summary["avg_temp"] == 80

    def test_all_non_numeric_column_returns_none(self):
        df = pd.DataFrame({"temperature": ["a", "b"]})

        summary = parse_sensor_data(df)

        assert summary["max_temp"] is None

    def test_observed_columns_reported(self):
        df = pd.DataFrame({"Rack Temp": [70], "Extra": [1]})

        summary = parse_sensor_data(df)

        assert "rack_temp" in summary["observed_columns"]
        assert "extra" in summary["observed_columns"]
