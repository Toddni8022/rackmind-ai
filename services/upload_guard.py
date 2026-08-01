"""
RackMind AI

Upload Size Guard

Rejects file uploads larger than MAX_UPLOAD_MB before they are
parsed, so an oversized file can't stall the app.
"""

from config import MAX_UPLOAD_MB

MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def exceeds_upload_limit(uploaded_file) -> bool:
    """Return True if the uploaded file is larger than MAX_UPLOAD_MB."""

    return uploaded_file.size > MAX_UPLOAD_BYTES


def upload_limit_message(uploaded_file) -> str:
    """A friendly error message naming the file, its size, and the limit."""

    size_mb = uploaded_file.size / (1024 * 1024)

    return (
        f"'{uploaded_file.name}' is {size_mb:.1f} MB, which exceeds the "
        f"{MAX_UPLOAD_MB:.0f} MB upload limit. Please upload a smaller file."
    )
