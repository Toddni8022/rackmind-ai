from agents.log_agent import analyze_log_summary
from agents.report_agent import generate_incident_report


class CoordinatorAgent:

    def __init__(self):

        self.name = "RackMind Coordinator"

    def analyze(
        self,
        log_summary=None,
        runbook_context="",
        sensor_context="",
    ):

        log_report = ""

        if log_summary:

            log_report = analyze_log_summary(log_summary)

        final_report = generate_incident_report(
            log_report=log_report,
            runbook_report=runbook_context,
            sensor_report=sensor_context,
        )

        return final_report


coordinator = CoordinatorAgent()


def coordinate_log_workflow(summary):

    return coordinator.analyze(
        log_summary=summary
    )