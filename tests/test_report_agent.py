import agents.report_agent as report_agent


def test_generate_incident_report_includes_all_three_sub_reports(monkeypatch):
    captured = {}

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return "EXECUTIVE REPORT"

    monkeypatch.setattr(report_agent, "generate", fake_generate)

    result = report_agent.generate_incident_report(
        log_report="### Log Analysis\n- Errors: 3",
        runbook_report="Replace faulty optics.",
        sensor_report="### Sensor Analysis\n- Max Temp: 95F",
    )

    assert result == "EXECUTIVE REPORT"
    assert "### Log Analysis" in captured["prompt"]
    assert "Replace faulty optics." in captured["prompt"]
    assert "### Sensor Analysis" in captured["prompt"]
    assert "Executive Summary" in captured["prompt"]


def test_generate_incident_report_handles_missing_sub_reports(monkeypatch):
    captured = {}

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return "REPORT"

    monkeypatch.setattr(report_agent, "generate", fake_generate)

    result = report_agent.generate_incident_report()

    assert result == "REPORT"
    assert "prompt" in captured
