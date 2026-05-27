from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from rag.indexing.sanitize import sanitize_extracted_text


def _extract_text_from_plain_text(content: bytes) -> str:
    return sanitize_extracted_text(content.decode("utf-8", errors="replace"))


def _extract_text_from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
    except PdfReadError as exc:
        raise ValueError("PDF could not be read") from exc

    if reader.is_encrypted:
        raise ValueError("PDF is password-protected and cannot be indexed")

    parts = [page.extract_text() or "" for page in reader.pages]
    return sanitize_extracted_text("\n".join(parts))


def _extract_text_from_docx(content: bytes) -> str:
    doc = DocxDocument(BytesIO(content))
    text = "\n".join(p.text for p in doc.paragraphs if p.text)
    return sanitize_extracted_text(text)


def extract_text(content: bytes, mime_type: str) -> str:
    match mime_type:
        case "text/plain":
            return _extract_text_from_plain_text(content)
        case "text/markdown":
            return _extract_text_from_plain_text(content)
        case "application/pdf":
            return _extract_text_from_pdf(content)
        case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return _extract_text_from_docx(content)
        case _:
            raise ValueError(f"No text extractor for mime type: {mime_type}")
