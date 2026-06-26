"""
Executive Summary Agent

Creates a concise AI-generated summary of the
overall infrastructure condition.
"""


def generate_executive_summary(
    metric_name,
    mean_value,
    std_value,
    anomaly_count,
    health_score,
    risk_score,
):

    if health_score >= 90:
        status = "Healthy"
    elif health_score >= 70:
        status = "Monitor"
    else:
        status = "Critical"

    if risk_score < 20:
        risk = "Low"
    elif risk_score < 50:
        risk = "Moderate"
    elif risk_score < 75:
        risk = "High"
    else:
        risk = "Critical"

    summary = f"""
## Executive Summary

**Overall Status:** {status}

The selected metric **{metric_name}** has an average value of
**{mean_value:.2f}** with a standard deviation of
**{std_value:.2f}**.

A total of **{anomaly_count} anomalies** were detected.

Infrastructure Health Score: **{health_score}/100**

Predicted Failure Risk: **{risk} ({risk_score}%)**

### AI Recommendation

"""

    if health_score >= 90:

        summary += """
System performance appears stable.

Continue normal monitoring and scheduled maintenance.
"""

    elif health_score >= 70:

        summary += """
The infrastructure is operating normally but developing
patterns should be monitored.

Review HVAC performance and continue trend analysis.
"""

    else:

        summary += """
Infrastructure conditions indicate elevated operational risk.

Immediate inspection of environmental systems and rack
conditions is recommended.
"""

    return summary