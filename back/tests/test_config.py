import pytest

from rag.config import Config, _get_env


def test_get_env_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_ENV_KEY", "value")
    assert _get_env("TEST_ENV_KEY") == "value"


def test_get_env_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_ENV_KEY", raising=False)
    with pytest.raises(ValueError, match="TEST_ENV_KEY"):
        _get_env("TEST_ENV_KEY")


def test_config_exposes_expected_defaults() -> None:
    assert Config.S3_BUCKET == "knowforge-documents-bucket"
    assert Config.EMBEDDING_MODEL == "text-embedding-3-small"
    assert "application/pdf" in Config.ALLOWED_MIME_TYPES
    assert Config.MAX_FILE_SIZE == 25 * 1024 * 1024
