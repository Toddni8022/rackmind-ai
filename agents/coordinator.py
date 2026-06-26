"""
RackMind AI

Coordinator Agent

Routes work between specialized agents.
"""

from services.incident_service import incident_service


def coordinate_log_workflow(summary):

    return incident_service.analyze(
        log_summary=summary
    )


def coordinate_sensor_workflow(summary):

    return incident_service.analyze(
        sensor_summary=summary
    )


def coordinate_full_workflow(

    log_summary,
    sensor_summary,
    runbook_context,

):

    return incident_service.analyze(
        log_summary=log_summary,
        sensor_summary=sensor_summary,
        runbook_context=runbook_context,
    )