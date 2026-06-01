import pytest

from rag.indexing.extract import extract_text
from tests.helpers.files import docx_bytes, markdown_bytes, pdf_bytes, plain_text_bytes


def test_extract_text_from_plain_and_markdown() -> None:
    plain = extract_text(plain_text_bytes("Hello plain"), "text/plain")
    markdown = extract_text(markdown_bytes("# Hi"), "text/markdown")

    assert "Hello plain" in plain
    assert "# Hi" in markdown


def test_extract_text_from_pdf_and_docx() -> None:
    pdf = extract_text(pdf_bytes(), "application/pdf")
    docx = extract_text(
        docx_bytes("Hello DOCX"),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    assert isinstance(pdf, str)
    assert "Hello DOCX" in docx


def test_extract_text_rejects_unknown_mime() -> None:
    with pytest.raises(ValueError, match="No text extractor"):
        extract_text(b"data", "application/zip")


def test_extract_text_from_pdf_rejects_encrypted_pdf() -> None:
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.encrypt("secret")
    buffer = __import__("io").BytesIO()
    writer.write(buffer)

    with pytest.raises(ValueError, match="password-protected"):
        extract_text(buffer.getvalue(), "application/pdf")
