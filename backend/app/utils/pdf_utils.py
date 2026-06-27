from pathlib import Path
from typing import Iterable
from pypdf import PdfReader

class PdfExtractionError(Exception):
    pass


def extract_text_pages(file_path: Path) -> list[tuple[int, str]]:
    try:
        reader = PdfReader(file_path)
        pages = []
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append((idx, text.strip()))
        return pages
    except Exception as exc:
        raise PdfExtractionError("Unable to extract text from PDF document") from exc
