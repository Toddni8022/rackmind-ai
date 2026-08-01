"""
RackMind AI

PDF Report Service

Renders an incident report to PDF bytes in memory so the
Streamlit download button can serve it without touching disk.
"""

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def report_filename(now: datetime | None = None) -> str:
    """Return a timestamped filename for the downloaded report."""

    stamp = now or datetime.now()
    return f"Incident_Report_{stamp:%Y%m%d_%H%M%S}.pdf"


def create_report(report: str) -> bytes:
    """
    Render the report text as PDF bytes.

    The text is XML-escaped first because ReportLab paragraphs
    parse inline markup, and raw '&' or '<' characters from an
    AI-generated report would otherwise crash the build.
    """

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = [
        Paragraph(
            "RackMind AI Executive Incident Report",
            styles["Heading1"],
        ),
        Paragraph(
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            styles["Normal"],
        ),
        Spacer(1, 12),
        Paragraph(
            escape(report).replace("\n", "<br/>"),
            styles["BodyText"],
        ),
    ]

    pdf.build(story)

    return buffer.getvalue()
