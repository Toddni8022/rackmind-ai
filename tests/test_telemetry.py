import json
import pandas as pd
import pytest
from services.telemetry_service import assess_telemetry, prepare_telemetry


def test_multi_rack_priorities_and_power_status():
    df = prepare_telemetry(pd.DataFrame({"rack": ["A", "B", "C"], "temp_f": [90, 72, 80], "rh": [45, 50, 40], "load_kw": [3, 4.5, 3]}))
    result = assess_telemetry(df)
    assert result["status"] == "Critical"
    assert [r["Status"] for r in result["racks"]] == ["Critical", "Warning", "Warning"]
    assert result["alerts"][0]["severity"] == "Critical"
    assert assess_telemetry(df[df.rack == "B"])["status"] == "Warning"


def test_invalid_values_never_look_normal_or_export_nan():
    df = prepare_telemetry(pd.DataFrame({"temperature": ["bad", float("inf")], "humidity": [-1, 101], "power_kw": [-2, float("-inf")]}))
    result = assess_telemetry(df)
    assert result["status"] == "Incomplete"
    assert result["racks"][0]["Missing / invalid readings"] == 6
    assert result["racks"][0]["Peak temperature (°F)"] is None
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("data", [{"x": [1]}, {"Temp": [70], " temp ": [80]}, {"temperature": [70], "temp_f": [80]}, {"temperature": []}])
def test_ambiguous_empty_and_unsupported_uploads(data):
    with pytest.raises(ValueError):
        prepare_telemetry(pd.DataFrame(data))


def test_partial_coverage_preserves_critical_alert():
    result = assess_telemetry(prepare_telemetry(pd.DataFrame({"temperature": [92, "bad"]})))
    assert result["status"] == "Critical"
    assert result["racks"][0]["Missing / invalid readings"] == 5
    assert [a["severity"] for a in result["alerts"]] == ["Critical", "Data quality"]


def test_normal_readings_and_unknown_racks():
    raw = pd.DataFrame({"rack": [None, "  "], "temperature": [72, 73], "humidity": [0, 100], "power_kw": [0, 4.4]})
    result = assess_telemetry(prepare_telemetry(raw))
    assert result["status"] == "Normal"
    assert result["alerts"] == []
    assert len(result["racks"]) == 1
    assert result["racks"][0]["Samples"] == 2
    assert raw["rack"].isna().sum() == 1
