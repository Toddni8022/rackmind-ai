"""
Predictive Risk Agent

Predicts infrastructure failure risk based on
anomaly counts and infrastructure health score.
"""


def predict_failure_risk(
    anomaly_count,
    health_score,
):
    """
    Returns:
        prediction_text (str)
        risk_score (int)
    """

    risk_score = min(
        100,
        (anomaly_count * 5) + (100 - health_score)
    )

    if risk_score < 20:

        prediction = """
🟢 LOW FAILURE RISK

Infrastructure appears stable.

Recommendations
---------------
• Continue normal monitoring
• No immediate maintenance required
• Review during scheduled inspections

Estimated Time Before Critical Event
------------------------------------
Greater than 48 hours
"""

    elif risk_score < 50:

        prediction = """
🟡 MODERATE FAILURE RISK

Sensor behavior indicates developing issues.

Recommendations
---------------
• Verify HVAC performance
• Inspect airflow around racks
• Monitor sensor trends closely

Estimated Time Before Critical Event
------------------------------------
12 to 24 hours
"""

    elif risk_score < 75:

        prediction = """
🟠 HIGH FAILURE RISK

Environmental trends suggest possible cooling
or power distribution problems.

Recommendations
---------------
• Begin infrastructure investigation
• Review power utilization
• Inspect environmental alarms

Estimated Time Before Critical Event
------------------------------------
4 to 12 hours
"""

    else:

        prediction = """
🔴 CRITICAL FAILURE RISK

Multiple abnormal sensor readings detected.

Recommendations
---------------
• Escalate immediately
• Verify cooling systems
• Inspect affected racks
• Notify infrastructure operations

Estimated Time Before Critical Event
------------------------------------
Less than 4 hours
"""

    return prediction, risk_score