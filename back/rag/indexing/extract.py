from io import BytesIO

from pypdf import PdfReader
from docx import Document as DocxDocument


def _extract_text_from_plain_text(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def _extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(parts)


def _extract_text_from_docx(content: bytes) -> str:
    doc = DocxDocument(BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text)


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
