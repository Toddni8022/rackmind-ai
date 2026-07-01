"""
Tests for the historical incident archive.
"""

from services.incident_archive import (
    count_incidents,
    delete_incident,
    extract_incident_fields,
    get_incident,
    save_incident,
    search_incidents,
    seed_sample_incidents,
)

SAMPLE_REPORT = """
# Executive Summary
Rack-22 overheated and dropped packets.

# Root Cause
Cooling degradation raised rack temperature above 90F.

# Recommended Actions
Restore HVAC capacity and replace the Gi1/0/12 patch cable.

# Priority
Critical
"""


class TestExtraction:

    def test_extracts_all_fields(self):
        fields = extract_incident_fields(SAMPLE_REPORT)

        assert fields["rack"] == "Rack-22"
        assert fields["severity"] == "Critical"
        assert "Cooling degradation" in fields["root_cause"]
        assert "Restore HVAC capacity" in fields["recommended_fix"]

    def test_defaults_for_unstructured_text(self):
        fields = extract_incident_fields("something broke")

        assert fields["rack"] == "Unknown"
        assert fields["severity"] == "Medium"
        assert fields["root_cause"] == ""


class TestSaveAndSearch:

    def test_save_and_get(self):
        incident_id = save_incident(SAMPLE_REPORT, source="test")

        incident = get_incident(incident_id)

        assert incident["rack"] == "Rack-22"
        assert incident["severity"] == "Critical"
        assert incident["source"] == "test"

    def test_explicit_fields_override_extraction(self):
        incident_id = save_incident(
            SAMPLE_REPORT,
            rack="Rack-99",
            severity="Low",
        )

        incident = get_incident(incident_id)

        assert incident["rack"] == "Rack-99"
        assert incident["severity"] == "Low"

    def test_invalid_severity_normalized(self):
        incident_id = save_incident("report", severity="Apocalyptic")

        assert get_incident(incident_id)["severity"] == "Medium"

    def test_filter_by_rack(self):
        save_incident("r1", rack="Rack-01", severity="Low")
        save_incident("r2", rack="Rack-02", severity="Low")

        results = search_incidents(rack="rack-01")

        assert len(results) == 1
        assert results[0]["rack"] == "Rack-01"

    def test_filter_by_severity(self):
        save_incident("a", severity="Critical")
        save_incident("b", severity="Low")

        results = search_incidents(severity="Critical")

        assert len(results) == 1
        assert results[0]["severity"] == "Critical"

    def test_filter_by_time_range(self):
        save_incident("old", created_at="2026-01-01 10:00:00")
        save_incident("new", created_at="2026-06-15 10:00:00")

        results = search_incidents(
            start="2026-06-01 00:00:00",
            end="2026-06-30 23:59:59",
        )

        assert len(results) == 1
        assert results[0]["report"] == "new"

    def test_filter_by_root_cause_and_fix(self):
        save_incident(
            "x",
            root_cause="Cooling failure",
            recommended_fix="Fix HVAC",
        )
        save_incident(
            "y",
            root_cause="Bad optic",
            recommended_fix="Swap SFP",
        )

        assert len(search_incidents(root_cause_contains="cooling")) == 1
        assert len(search_incidents(fix_contains="sfp")) == 1

    def test_full_text_filter(self):
        save_incident("The uplink flapped repeatedly")
        save_incident("Power feed imbalance")

        results = search_incidents(text="uplink")

        assert len(results) == 1

    def test_filters_combine_with_and(self):
        save_incident("a", rack="Rack-01", severity="Critical")
        save_incident("b", rack="Rack-01", severity="Low")

        results = search_incidents(rack="Rack-01", severity="Low")

        assert len(results) == 1

    def test_results_sorted_newest_first(self):
        save_incident("older", created_at="2026-01-01 00:00:00")
        save_incident("newer", created_at="2026-06-01 00:00:00")

        results = search_incidents()

        assert results[0]["report"] == "newer"


class TestDeleteAndSeed:

    def test_delete(self):
        incident_id = save_incident("to delete")

        assert delete_incident(incident_id) is True
        assert get_incident(incident_id) is None
        assert delete_incident(incident_id) is False

    def test_seed_only_when_empty(self):
        first = seed_sample_incidents()
        second = seed_sample_incidents()

        assert first == 3
        assert second == 0
        assert count_incidents() == 3
