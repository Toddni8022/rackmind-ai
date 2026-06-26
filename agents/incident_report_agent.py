"""
AI Incident Report Generator

Creates a professional incident report from the
results of the infrastructure analysis.
"""

from datetime import datetime


def generate_incident_report(
    metric_name,
    anomaly_count,
    health_score,
    root_cause_analysis,
):

    if health_score >= 90:
        severity = "Low"
    elif health_score >= 70:
        severity = "Medium"
    else:
        severity = "High"

    report = f"""
===========================================
AI INFRASTRUCTURE INCIDENT REPORT
===========================================

Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Severity:
{severity}

Metric Analyzed:
{metric_name}

Health Score:
{health_score}/100

Anomalies Detected:
{anomaly_count}

-------------------------------------------
AI ROOT CAUSE ANALYSIS
-------------------------------------------

{root_cause_analysis}

-------------------------------------------
RECOMMENDED NEXT STEPS
-------------------------------------------

1. Review environmental sensors.

2. Verify cooling systems.

3. Check rack power utilization.

4. Review infrastructure logs.

5. Continue monitoring for additional anomalies.

===========================================
End of Report
===========================================
"""

    return report