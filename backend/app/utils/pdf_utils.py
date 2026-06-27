"""
app/utils/pdf_utils.py
======================
PDF text extraction utility using pypdf.

pypdf is a pure-Python library — it requires no system dependencies like
Poppler or Ghostscript, which makes it easy to install in Docker containers.

Limitation: pypdf can only extract text from text-based PDFs.  Scanned PDFs
(which are images of pages) will return empty text.  For scanned documents,
an OCR library like pytesseract or AWS Textract would be needed instead.
"""

from pathlib import Path

from pypdf import PdfReader


class PdfExtractionError(Exception):
    """
    Raised when we cannot extract text from a PDF file.

    Wraps the underlying pypdf exception so callers don't need to import
    pypdf directly — they just catch PdfExtractionError.
    """
    pass


def extract_text_pages(file_path: Path) -> list[tuple[int, str]]:
    """
    Extract plain text from every page of a PDF file.

    Pages are returned in reading order (page 1 first).  Empty pages
    (e.g., intentional blank pages) are included as empty strings so that
    page numbers in the returned list always match the real PDF page numbers.

    Args:
        file_path: Absolute path to the PDF file on disk.

    Returns:
        A list of (page_number, page_text) tuples.
        page_number is 1-indexed (first page = 1, not 0).
        page_text is a stripped string; may be empty for blank or image pages.

    Raises:
        PdfExtractionError: If the file cannot be opened or parsed.
    """
    try:
        reader = PdfReader(file_path)
        pages: list[tuple[int, str]] = []

        for idx, page in enumerate(reader.pages, start=1):
            # extract_text() returns None for image-only pages; default to ""
            raw_text = page.extract_text() or ""
            pages.append((idx, raw_text.strip()))

        return pages

    except Exception as exc:
        raise PdfExtractionError(
            f"Unable to extract text from PDF: {file_path.name}"
        ) from exc
