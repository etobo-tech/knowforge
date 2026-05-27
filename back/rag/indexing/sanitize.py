import re

# PostgreSQL text columns reject NUL (0x00); some PDF extractors emit them.
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def sanitize_extracted_text(text: str) -> str:
    return _CONTROL_CHARS.sub("", text)
