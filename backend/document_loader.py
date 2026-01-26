import io
import os
from typing import Optional

import fitz  # PyMuPDF
from docx import Document


class DocumentLoadError(RuntimeError):
    pass


def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower().strip(".")


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    ext = _get_extension(filename)
    if ext == "pdf":
        return _extract_pdf_text(file_bytes)
    if ext == "docx":
        return _extract_docx_text(file_bytes)
    if ext == "txt":
        return _extract_txt_text(file_bytes)
    raise DocumentLoadError(f"Unsupported document type: {ext}")


def _extract_pdf_text(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        return "\n".join(text_parts).strip()
    except Exception as exc:
        raise DocumentLoadError(f"Failed to read PDF: {exc}") from exc


def _extract_docx_text(file_bytes: bytes) -> str:
    try:
        with io.BytesIO(file_bytes) as file_like:
            doc = Document(file_like)
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs).strip()
    except Exception as exc:
        raise DocumentLoadError(f"Failed to read DOCX: {exc}") from exc


def _extract_txt_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8", errors="ignore").strip()
    except Exception as exc:
        raise DocumentLoadError(f"Failed to read TXT: {exc}") from exc
