from google.adk.agents import Agent

from agents.log_agent import analyze_log_summary
from agents.report_agent import generate_incident_report


class RackMindCoordinator:

    def __init__(self):

        self.agent = Agent(
            name="rackmind_coordinator",
            model="gemini-2.5-flash",
            description="Coordinates infrastructure AI agents."
        )

    def run(
        self,
        log_summary=None,
        runbook_context="",
        sensor_context=""
    ):

        log_output = ""

        if log_summary is not None:

            log_output = analyze_log_summary(
                log_summary
            )

        report = generate_incident_report(
            log_report=log_output,
            runbook_report=runbook_context,
            sensor_report=sensor_context
        )

        return report


rackmind = RackMindCoordinator()