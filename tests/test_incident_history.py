from services.incident_history import parse_incident_history, search_incident_history

SAMPLE = """Incident 001

Rack: Rack18

Symptoms:
CRC errors
High temperature
Packet loss

Resolution:
Replace cooling fan
Reseat SFP module

Status:
Resolved

----------------------------------------

Incident 002

Rack: Rack31

Symptoms:
Interface resets
Power fluctuations

Resolution:
Replace PDU

Status:
Resolved
"""


def test_parse_incident_history_extracts_all_records():
    records = parse_incident_history(SAMPLE)

    assert len(records) == 2
    assert records[0]["id"] == "Incident 001"
    assert records[0]["rack"] == "Rack18"
    assert records[0]["symptoms"] == ["CRC errors", "High temperature", "Packet loss"]
    assert records[0]["resolution"] == ["Replace cooling fan", "Reseat SFP module"]
    assert records[0]["status"] == "Resolved"


def test_parse_incident_history_handles_empty_text():
    assert parse_incident_history("") == []
    assert parse_incident_history("   \n\n  ") == []


def test_search_incident_history_matches_symptom_keyword():
    records = parse_incident_history(SAMPLE)

    results = search_incident_history("interface resets", records)

    assert len(results) == 1
    assert results[0]["id"] == "Incident 002"


def test_search_incident_history_matches_rack_name():
    records = parse_incident_history(SAMPLE)

    results = search_incident_history("Rack18", records)

    assert len(results) == 1
    assert results[0]["rack"] == "Rack18"


def test_search_incident_history_returns_all_on_empty_query():
    records = parse_incident_history(SAMPLE)

    assert search_incident_history("", records) == records


def test_search_incident_history_returns_empty_for_no_match():
    records = parse_incident_history(SAMPLE)

    assert search_incident_history("kubernetes ingress", records) == []
