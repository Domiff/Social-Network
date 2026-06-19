import io
import uuid
from contextlib import asynccontextmanager

import aioboto3

from src.core.config import settings
from src.core.exceptions import S3Error


class S3Client:
    def __init__(
        self,
        s3_endpoint_url,
        s3_access_key,
        s3_secret_key,
        s3_region,
        s3_bucket,
    ):
        self.s3_endpoint_url = s3_endpoint_url
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key
        self.s3_region = s3_region
        self.s3_bucket = s3_bucket
        self.session = None
        self.client = None

    def _get_client(self):
        self.session = aioboto3.Session(
            aws_access_key_id=self.s3_access_key,
            aws_secret_access_key=self.s3_secret_key,
            region_name=self.s3_region,
        )
        return self.session.client(
            "s3",
            endpoint_url=self.s3_endpoint_url,
        )

    async def upload(self, content: bytes, filename: str, content_type: str, username: str):
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        async with self._get_client() as s3:
            try:
                await s3.upload_fileobj(
                    io.BytesIO(content),
                    settings.s3.S3_BUCKET,
                    f"{username}/{unique_filename}",
                )

                file_url = f"{settings.s3.S3_ENDPOINT_URL}/{settings.s3.S3_BUCKET}/{username}/{unique_filename}"

                return {
                    "filename": unique_filename,
                    "content_type": content_type,
                    "file_size": len(content),
                    "file_url": file_url,
                }
            except Exception as e:
                raise S3Error(
                    status_code=500, detail=f"Error uploading file: {str(e)}"
                ) from e

    async def delete(self, key: str) -> dict:
        async with self._get_client() as s3:
            try:
                await s3.delete_object(
                    Bucket=settings.s3.S3_BUCKET,
                    Key=key
                )
                return {"message": "File successfully deleted", "key": key}
            except Exception as e:
                raise S3Error(status_code=500, detail=f"Error deleting file: {str(e)}")


s3_client = S3Client(
    s3_endpoint_url=settings.s3.S3_ENDPOINT_URL,
    s3_access_key=settings.s3.S3_ACCESS_KEY,
    s3_secret_key=settings.s3.S3_SECRET_KEY,
    s3_region=settings.s3.S3_REGION,
    s3_bucket=settings.s3.S3_BUCKET,
)
