"""
Tests for services.log_parser and tools.log_reader.
"""

import io
from pathlib import Path

from services.log_parser import line_severity, parse_log
from tools.log_reader import analyze_log

SAMPLE_SWITCH_LOG = (
    Path(__file__).resolve().parent.parent / "data" / "switch.log"
)


class TestLineSeverity:

    def test_severity_comes_from_level_token(self):
        assert line_severity("2026-06-21 ERROR Interface reset") == "error"
        assert line_severity("2026-06-21 WARNING Fan speed low") == "warning"
        assert line_severity("2026-06-21 INFO Boot complete") is None

    def test_message_text_does_not_set_severity(self):
        # "error" inside the message is not a severity token.
        assert line_severity(
            "WARNING CRC error detected on Gi1/0/12"
        ) == "warning"

        assert line_severity("An error occurred somewhere") is None

    def test_critical_variants_count_as_errors(self):
        assert line_severity("CRITICAL temperature exceeded") == "error"
        assert line_severity("switch01 CRIT fan failure") == "error"
        assert line_severity("kernel: FATAL power loss") == "error"


class TestParseLog:

    def test_counts_all_event_types(self, sample_log_text):
        summary = parse_log(sample_log_text)

        assert summary["events"] == 7
        assert summary["warnings"] == 2
        # Only the two ERROR-level lines count as errors; the two
        # "WARNING CRC error" lines are warnings + CRC events.
        assert summary["errors"] == 2
        assert summary["crc_errors"] == 2
        assert summary["resets"] == 1

    def test_tracks_max_temperature(self, sample_log_text):
        summary = parse_log(sample_log_text)

        assert summary["max_temp"] == 91

    def test_empty_log_returns_zeroed_summary(self):
        summary = parse_log("")

        assert summary["events"] == 0
        assert summary["warnings"] == 0
        assert summary["errors"] == 0
        assert summary["crc_errors"] == 0
        assert summary["resets"] == 0
        assert summary["max_temp"] == 0

    def test_crc_warnings_are_not_double_counted_as_errors(self):
        summary = parse_log(
            "WARNING CRC error detected on Gi1/0/12\n"
            "WARNING CRC error detected on Gi1/0/12"
        )

        assert summary["warnings"] == 2
        assert summary["crc_errors"] == 2
        assert summary["errors"] == 0

    def test_reset_recovery_messages_are_not_counted_as_resets(self):
        summary = parse_log(
            "ERROR Interface Gi1/0/12 reset initiated\n"
            "INFO Interface reset complete\n"
            "INFO Interface recovered"
        )

        assert summary["resets"] == 1

    def test_lines_without_events_only_count_as_events(self):
        summary = parse_log("hello\nworld")

        assert summary["events"] == 2
        assert summary["errors"] == 0

    def test_bundled_sample_switch_log(self):
        summary = parse_log(SAMPLE_SWITCH_LOG.read_text(encoding="utf-8"))

        assert summary["events"] == 25
        assert summary["warnings"] == 10
        assert summary["errors"] == 4
        assert summary["crc_errors"] == 5
        assert summary["resets"] == 2
        assert summary["max_temp"] == 91


class TestAnalyzeLog:

    def _upload(self, text):
        return io.BytesIO(text.encode("utf-8"))

    def test_counts_and_temperature(self, sample_log_text):
        summary = analyze_log(self._upload(sample_log_text))

        assert summary["total_events"] == 7
        assert summary["warnings"] == 2
        # Severity comes from the level token, so the two WARNING CRC
        # lines are not also counted as errors.
        assert summary["errors"] == 2
        assert summary["crc_errors"] == 2
        assert summary["interface_resets"] == 1
        assert summary["max_temperature"] == 91

    def test_timeline_contains_significant_events(self, sample_log_text):
        summary = analyze_log(self._upload(sample_log_text))

        assert len(summary["timeline"]) == 4
        assert any("CRC" in event for event in summary["timeline"])
        assert any("reset initiated" in event for event in summary["timeline"])

    def test_handles_malformed_temperature_tokens(self):
        summary = analyze_log(
            self._upload("INFO Temperature spike FF n/aF 88F")
        )

        assert summary["max_temperature"] == 88

    def test_empty_file(self):
        summary = analyze_log(self._upload(""))

        assert summary["total_events"] == 0
        assert summary["timeline"] == []
        assert summary["max_temperature"] == 0

    def test_bundled_sample_switch_log(self):
        summary = analyze_log(
            self._upload(SAMPLE_SWITCH_LOG.read_text(encoding="utf-8"))
        )

        assert summary["total_events"] == 25
        assert summary["warnings"] == 10
        assert summary["errors"] == 4
        assert summary["crc_errors"] == 5
        assert summary["interface_resets"] == 2
        assert summary["max_temperature"] == 91
