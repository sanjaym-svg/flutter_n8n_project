from uuid import uuid4

import boto3
from botocore.client import Config

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
        self.client = boto3.client(
            's3',
            endpoint_url=f"http{'s' if settings.minio_secure else ''}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1',
        )

    def ensure_bucket(self) -> None:
        buckets = [b['Name'] for b in self.client.list_buckets().get('Buckets', [])]
        if settings.bucket_name not in buckets:
            self.client.create_bucket(Bucket=settings.bucket_name)

    def upload_resume(self, filename: str, content: bytes) -> str:
        object_name = f"resumes/{uuid4()}-{filename}"
        self.client.put_object(Bucket=settings.bucket_name, Key=object_name, Body=content)
        return f's3://{settings.bucket_name}/{object_name}'
