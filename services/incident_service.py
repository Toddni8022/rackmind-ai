"""
RackMind AI

Incident Service

Coordinates all AI agents and produces
a single executive incident report.
"""

from agents.log_agent import analyze_log_summary
from agents.sensor_agent import analyze_sensor_data
from agents.report_agent import generate_incident_report


class IncidentService:

    def analyze(
        self,
        log_summary=None,
        sensor_summary=None,
        runbook_context="",
    ):

        log_report = ""
        sensor_report = ""

        if log_summary:

            log_report = analyze_log_summary(
                log_summary
            )

        if sensor_summary:

            sensor_report = analyze_sensor_data(
                sensor_summary
            )

        report = generate_incident_report(
            log_report=log_report,
            runbook_report=runbook_context,
            sensor_report=sensor_report,
            log_summary=log_summary,
            sensor_summary=sensor_summary,
        )

        return report


incident_service = IncidentService()