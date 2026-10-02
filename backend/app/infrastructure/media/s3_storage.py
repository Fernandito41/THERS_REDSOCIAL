# Adaptador S3-compatible del puerto MediaStorage (ADR-015): Supabase
# Storage, Cloudflare R2, AWS S3 o MinIO -- solo cambian endpoint y
# credenciales. Única pieza que importa boto3.

import boto3
from botocore.config import Config as BotoConfig

from app.domain.media.storage import MediaStorage


class S3MediaStorage(MediaStorage):
    def __init__(self, bucket, endpoint_url, access_key_id, secret_access_key, region):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or None,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region or "auto",
            config=BotoConfig(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

    def save(self, key, data, content_type):
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
        )

    def delete(self, key):
        self.client.delete_object(Bucket=self.bucket, Key=key)
