import boto3
from rag.config import Config
import functools
from db.models import Document


@functools.cache
def get_s3_client():
    return boto3.client(
        "s3",
        region_name=Config.S3_REGION,
        endpoint_url=Config.S3_ENDPOINT_URL,
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
