"""
RackMind AI

Google ADK Tools
"""

from agents.log_agent import analyze_log_summary
from agents.runbook_agent import answer_question
from agents.sensor_agent import analyze_sensor_data


def analyze_logs(log_summary: dict) -> str:
    """
    Analyze switch logs.
    """
    return analyze_log_summary(log_summary)


def analyze_sensors(sensor_summary: dict) -> str:
    """
    Analyze environmental telemetry.
    """
    return analyze_sensor_data(sensor_summary)


def search_runbooks(question: str) -> str:
    """
    Search indexed runbooks.
    """
    return answer_question(question)