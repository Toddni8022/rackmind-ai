from pypdf import PdfReader


def extract_pdf_text(uploaded_file):
    """
    Extract all text from an uploaded PDF.
    """

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text