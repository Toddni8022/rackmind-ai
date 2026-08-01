from services.pdf_service import create_report, report_filename


def test_create_report_returns_pdf_bytes():
    pdf = create_report("# Executive Summary\n\nAll systems nominal.")
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF")


def test_create_report_survives_markup_characters():
    pdf = create_report("Temperature > 90°F & rising. <escalate> now.")
    assert pdf.startswith(b"%PDF")


def test_create_report_accepts_custom_title():
    pdf = create_report("All clear.", title="RackMind AI Log Analysis Report")
    assert pdf.startswith(b"%PDF")


def test_create_report_escapes_markup_in_custom_title():
    pdf = create_report("All clear.", title="Sensors & <Racks>")
    assert pdf.startswith(b"%PDF")


def test_report_filename_is_timestamped_pdf():
    from datetime import datetime

    name = report_filename(datetime(2026, 8, 1, 12, 30, 45))
    assert name == "Incident_Report_20260801_123045.pdf"
