import os

from dotenv import load_dotenv

load_dotenv()


def _get_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    return value


class Config:
    S3_BUCKET = "knowforge-documents-bucket"
    S3_REGION = "us-east-1"
    AWS_ACCESS_KEY_ID = _get_env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = _get_env("AWS_SECRET_ACCESS_KEY")

    OPENAI_API_KEY = _get_env("OPENAI_API_KEY")
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 200

    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
    }

    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
