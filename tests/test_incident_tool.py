import adk.incident_tool as incident_tool


def test_investigate_incident_builds_prompt_from_logs_sensors_and_runbook(monkeypatch):
    monkeypatch.setattr(
        incident_tool,
        "search_runbooks",
        lambda query: ["Inspect CRAC units when temperatures spike."],
    )

    captured = {}

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return "FULL INCIDENT REPORT"

    monkeypatch.setattr(incident_tool, "generate", fake_generate)

    log_text = "WARNING CRC error detected on Gi1/0/12\nERROR Temperature 95F"
    sensor_data = [
        {"timestamp": "18:00", "temperature": 95, "humidity": 48, "power_kw": 4.9},
        {"timestamp": "18:05", "temperature": 97, "humidity": 49, "power_kw": 5.1},
    ]

    result = incident_tool.investigate_incident(log_text, sensor_data)

    assert result == "FULL INCIDENT REPORT"
    prompt = captured["prompt"]
    assert "LOG SUMMARY" in prompt
    assert "SENSOR SUMMARY" in prompt
    assert "Inspect CRAC units when temperatures spike." in prompt
    assert "Executive Summary" in prompt


def test_investigate_incident_falls_back_when_no_runbook_match(monkeypatch):
    monkeypatch.setattr(incident_tool, "search_runbooks", lambda query: [])

    captured = {}

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return "REPORT"

    monkeypatch.setattr(incident_tool, "generate", fake_generate)

    incident_tool.investigate_incident("INFO ok", [{"temperature": 72}])

    assert "No matching runbook guidance was found." in captured["prompt"]
