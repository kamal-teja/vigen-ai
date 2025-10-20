import json
import uuid
from pathlib import Path
from typing import Dict

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.config import settings


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def generate_presigned_url(
        self,
        object_key: str,
        content_type: str,
        expiration: int = 3600
    ) -> str:
        """Generate a presigned URL for uploading a file to S3"""
        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Error generating presigned URL: {str(e)}")
    
    def generate_presigned_download_url(
        self,
        object_key: str,
        expiration: int = 3600
    ) -> str:
        """Generate a presigned URL for downloading/viewing a file from S3"""
        # Additional security: Validate object key format
        if not object_key or ".." in object_key or object_key.startswith("/"):
            raise Exception("Invalid object key format")
        
        # Security: Check if object exists before generating URL
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise Exception("Object not found")
            else:
                raise Exception(f"Error checking object existence: {str(e)}")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Error generating presigned download URL: {str(e)}")
    
    def get_s3_uri(self, object_key: str) -> str:
        """Get S3 URI for an object"""
        return f"s3://{self.bucket_name}/{object_key}"
    
    def generate_product_image_key(self, adv_id: uuid.UUID, filename: str) -> str:
        """Generate S3 key for a product image asset."""
        sanitized = Path(filename).name.strip().replace(" ", "-")
        return f"{adv_id}/assets/images/{sanitized}"

    def generate_ad_details_key(self, adv_id: uuid.UUID) -> str:
        """Generate S3 key for the advertisement details JSON."""
        return f"{adv_id}/assets/json/details.json"

    def generate_ad_asset_key(self, adv_id: uuid.UUID, filename: str) -> str:
        """Generate S3 key for generic ad input assets."""
        sanitized = Path(filename).name.strip().replace(" ", "-")
        return f"{adv_id}/assets/inputs/{sanitized}"

    def get_content_type(self, ext: str) -> str:
        """Get content type based on file extension."""
        content_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'mp4': 'video/mp4',
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'json': 'application/json'
        }
        return content_types.get(ext.lower(), 'application/octet-stream')

    def get_content_type_by_filename(self, filename: str) -> str:
        """Infer content type from a filename."""
        ext = Path(filename).suffix.lstrip('.')
        return self.get_content_type(ext) if ext else 'application/octet-stream'

    def upload_json(self, object_key: str, payload: Dict) -> str:
        """Upload JSON payload to S3 and return its URI."""
        try:
            body = json.dumps(payload, default=str)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=body.encode('utf-8'),
                ContentType='application/json'
            )
            return self.get_s3_uri(object_key)
        except ClientError as e:
            raise Exception(f"Error uploading JSON to S3: {str(e)}")


s3_service = S3Service()
