"""
Tests for services.log_parser and tools.log_reader.
"""

import io

from services.log_parser import parse_log
from tools.log_reader import analyze_log


class TestParseLog:

    def test_counts_all_event_types(self, sample_log_text):
        summary = parse_log(sample_log_text)

        assert summary["events"] == 7
        assert summary["warnings"] == 2
        # "CRC error" lines match the ERROR substring too, so the two
        # WARNING CRC lines are also counted as errors (2 + 2).
        assert summary["errors"] == 4
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

    def test_case_insensitive_matching(self):
        summary = parse_log("warning: crc error\nError: reset now")

        assert summary["warnings"] == 1
        assert summary["crc_errors"] == 1
        # Both lines contain the "error" substring.
        assert summary["errors"] == 2
        assert summary["resets"] == 1

    def test_lines_without_events_only_count_as_events(self):
        summary = parse_log("hello\nworld")

        assert summary["events"] == 2
        assert summary["errors"] == 0


class TestAnalyzeLog:

    def _upload(self, text):
        return io.BytesIO(text.encode("utf-8"))

    def test_counts_and_temperature(self, sample_log_text):
        summary = analyze_log(self._upload(sample_log_text))

        assert summary["total_events"] == 7
        assert summary["warnings"] == 2
        # CRC warning lines also contain the ERROR substring (2 + 2).
        assert summary["errors"] == 4
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
