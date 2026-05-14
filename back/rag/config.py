import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    S3_BUCKET = "knowforge-documents"
    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
    S3_REGION = "us-east-1"
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
    }

    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
