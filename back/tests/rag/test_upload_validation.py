import pytest

from rag.config import Config
from rag.upload import _check_content_type, _check_file_size


def test_check_content_type_accepts_allowed_mime() -> None:
    _check_content_type("text/plain")


def test_check_content_type_rejects_unknown_mime() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        _check_content_type("application/zip")


def test_check_file_size_accepts_within_limit() -> None:
    _check_file_size(Config.MAX_FILE_SIZE)


def test_check_file_size_rejects_oversized_file() -> None:
    with pytest.raises(ValueError, match="File too large"):
        _check_file_size(Config.MAX_FILE_SIZE + 1)
