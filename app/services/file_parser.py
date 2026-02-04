"""
File parsing service - PDF and DOCX.
"""

import io
import logging
import pdfplumber
from docx import Document
from app.utils.helpers import get_file_extension

logger = logging.getLogger(__name__)


async def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or DOCX file."""
    ext = get_file_extension(filename)

    if ext == ".pdf":
        return _parse_pdf(file_bytes)
    elif ext == ".docx":
        return _parse_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def _parse_pdf(data: bytes) -> str:
    """Extract text from PDF."""
    text_pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
    
    full_text = "\n\n".join(text_pages).strip()
    if not full_text:
        logger.warning("PDF extraction returned empty text.")
    return full_text


def _parse_docx(data: bytes) -> str:
    """Extract text from DOCX."""
    doc = Document(io.BytesIO(data))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs).strip()
    if not full_text:
        logger.warning("DOCX extraction returned empty text.")
    return full_text
