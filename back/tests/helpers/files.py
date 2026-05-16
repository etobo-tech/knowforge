from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfWriter


def plain_text_bytes(text: str = "Knowforge sample document for tests.") -> bytes:
    return text.encode("utf-8")


def markdown_bytes(text: str = "# Title\n\nParagraph for indexing.") -> bytes:
    return text.encode("utf-8")


def pdf_bytes() -> bytes:
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(buffer)
    return buffer.getvalue()


def docx_bytes(text: str = "DOCX extractable text for tests.") -> bytes:
    buffer = BytesIO()
    document = DocxDocument()
    document.add_paragraph(text)
    document.save(buffer)
    return buffer.getvalue()
