from rag.indexing.errors import public_indexing_error_message


def test_public_indexing_error_message_uses_generic_fallback_for_empty() -> None:
    message = public_indexing_error_message(None)

    assert "could not be processed" in message


def test_public_indexing_error_message_hides_nul_byte_errors() -> None:
    message = public_indexing_error_message("PostgreSQL rejected NUL byte 0x00")

    assert "invalid or unsupported content" in message


def test_public_indexing_error_message_explains_unreadable_text() -> None:
    message = public_indexing_error_message("Document has no extractable text")

    assert "no readable text" in message


def test_public_indexing_error_message_explains_unreadable_pdf() -> None:
    message = public_indexing_error_message("PDF could not be read")

    assert "PDF could not be read" in message


def test_public_indexing_error_message_hides_long_internal_errors() -> None:
    message = public_indexing_error_message("x" * 201)

    assert "could not be processed" in message


def test_public_indexing_error_message_preserves_short_safe_errors() -> None:
    assert (
        public_indexing_error_message("Unsupported file type")
        == "Unsupported file type"
    )
