"""User-safe messages for indexing failures (API / upload UI)."""


def public_indexing_error_message(raw: str | None) -> str:
    if not raw:
        return (
            "This document could not be processed. Try saving a new copy "
            "or exporting to PDF."
        )

    text = raw.strip()
    lower = text.lower()

    if "\0" in text or "nul" in lower or "0x00" in lower:
        return (
            "This document could not be processed because it contains invalid "
            "or unsupported content. Try saving a new copy or exporting to PDF."
        )

    if "no extractable text" in lower or "password-protected" in lower:
        return (
            "This document has no readable text (it may be scanned or "
            "password-protected). Try OCR or remove the password and upload again."
        )

    if "pdf could not be read" in lower:
        return "This PDF could not be read. Try re-exporting it or use another format."

    if len(text) > 200:
        return (
            "This document could not be processed. Try saving a new copy "
            "or exporting to PDF."
        )

    return text
