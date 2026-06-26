from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def create_report(report: str):

    filename = (
        f"Incident_Report_"
        f"{datetime.now():%Y%m%d_%H%M%S}.pdf"
    )

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "RackMind AI Executive Incident Report",
            styles["Heading1"],
        )
    )

    story.append(
        Paragraph(
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(report.replace("\n", "<br/>"), styles["BodyText"])
    )

    pdf.build(story)

    return filename