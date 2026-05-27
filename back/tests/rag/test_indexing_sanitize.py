from rag.indexing.extract import extract_text
from rag.indexing.sanitize import sanitize_extracted_text


def test_sanitize_extracted_text_strips_nul_bytes() -> None:
    assert sanitize_extracted_text("hello\x00world") == "helloworld"


def test_extract_text_strips_nul_from_plain() -> None:
    text = extract_text(b"line one\x00line two", "text/plain")
    assert "\x00" not in text
    assert "line one" in text
    assert "line two" in text
