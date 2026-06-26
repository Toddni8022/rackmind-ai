"""
AI Root Cause Agent

This agent reviews sensor statistics and generates a
human-readable infrastructure analysis.
"""


def analyze_root_cause(
    metric_name,
    mean_value,
    std_value,
    anomaly_count,
    health_score,
):
    summary = []

    summary.append(
        f"The selected metric is '{metric_name}'."
    )

    summary.append(
        f"The average reading is {mean_value:.2f} with a standard deviation of {std_value:.2f}."
    )

    if anomaly_count == 0:

        summary.append(
            "No abnormal behavior was detected."
        )

        summary.append(
            "Sensor values remain stable and within expected operating ranges."
        )

    elif anomaly_count < 5:

        summary.append(
            "A small number of anomalies were detected."
        )

        summary.append(
            "This could indicate temporary environmental fluctuations or isolated sensor events."
        )

    elif anomaly_count < 15:

        summary.append(
            "Multiple anomalies were detected."
        )

        summary.append(
            "This pattern may indicate developing infrastructure issues such as cooling inefficiency, airflow restrictions, or increasing workload."
        )

    else:

        summary.append(
            "A significant number of anomalies were detected."
        )

        summary.append(
            "Immediate investigation is recommended because persistent abnormal readings may lead to equipment failures or service interruptions."
        )

    if health_score >= 90:

        recommendation = """
Recommended Actions

• Continue normal monitoring

• No immediate maintenance required

• Review trends during routine inspections
"""

    elif health_score >= 70:

        recommendation = """
Recommended Actions

• Verify HVAC performance

• Inspect airflow around equipment

• Monitor sensor values for continued degradation

• Review recent infrastructure changes
"""

    else:

        recommendation = """
Recommended Actions

• Escalate to Infrastructure Operations

• Verify cooling systems immediately

• Inspect rack power utilization

• Review environmental alarms

• Schedule maintenance as soon as possible
"""

    return "\n\n".join(summary) + "\n\n" + recommendation