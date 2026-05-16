import functools
from typing import cast

import boto3
from types_boto3_s3 import S3Client

from db.models import Document
from rag.config import Config


@functools.cache
def get_s3_client() -> S3Client:
    return boto3.client(
        "s3",
        region_name=Config.S3_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )


def upload_document_to_s3(document: Document, content: bytes) -> None:
    s3 = get_s3_client()
    s3.put_object(
        Bucket=Config.S3_BUCKET,
        Key=document.s3_key,
        Body=content,
        ContentType=document.mime_type,
    )


def delete_object_from_s3(s3_key: str) -> None:
    s3 = get_s3_client()
    s3.delete_object(Bucket=Config.S3_BUCKET, Key=s3_key)


def _safe_attachment_filename(name: str) -> str:
    base = name.rsplit("/", maxsplit=1)[-1]
    return base.replace('"', "'")[:200]


def presigned_download_url(
    s3_key: str,
    download_filename: str,
    *,
    expires_in: int = 300,
) -> str:
    s3 = get_s3_client()
    disposition = f'attachment; filename="{_safe_attachment_filename(download_filename)}"'
    return cast(
        str,
        s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": Config.S3_BUCKET,
            "Key": s3_key,
            "ResponseContentDisposition": disposition,
        },
        ExpiresIn=expires_in,
        ),
    )
