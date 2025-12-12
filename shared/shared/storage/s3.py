import boto3
from botocore.exceptions import ClientError
from botocore.client import BaseClient
from base64 import b64decode

from shared.config import StorageConfig
from . import Storage

MB = 1024 * 1024
chunk_size = 8 * MB  # 8MB

class S3Storage(Storage):
    def __init__(self, cfg: StorageConfig):
        super().__init__(cfg)
        self.client: BaseClient = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            region_name=cfg.region,
            aws_access_key_id=cfg.access_key,
            aws_secret_access_key=cfg.secret_key
        )
        
    def check_connection(self, bucket_name: str) -> bool:
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False
        
    def create_bucket(self, bucket_name: str) -> bool:
        try:
            self.client.create_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            print(f"Create bucket failed: {e}")
            return False

    def exists(self, bucket_name: str, key: str) -> bool:
        try:
            self.client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError:
            return False
        
    def upload(self, bucket_name: str, file_content: bytes, key: str, extra_args: dict | None = None) -> str:
        if extra_args is None:
            extra_args = {}
        try:
            self.client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_content,
                **extra_args
            )
            return key
        except ClientError as e:
            print(f"Upload failed: {e}")
            print("Seeing if the bucket exists...")
            if not self.check_connection(bucket_name):
                print("Either the bucket does not exist or cannot establish a connection. Making a new bucket...")
                if self.create_bucket(bucket_name):
                    print(f"Bucket {bucket_name} created successfully. Retrying upload...")
                    return self.upload(bucket_name, file_content, key, extra_args)
            return ""

    def download(self, bucket_name: str, key: str, extra_args: dict = {}) -> bytes:
        try:
            response = self.client.get_object(
                Bucket=bucket_name, 
                Key=key, 
                **extra_args
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Download failed: {e}")
            print("Seeing if the bucket exists...")
            if not self.check_connection(bucket_name):
                print("Either the bucket does not exist or cannot establish a connection. Making a new bucket...")
                if self.create_bucket(bucket_name):
                    print(f"Bucket {bucket_name} created successfully. Retrying download...")
                    return self.download(bucket_name, key, extra_args)
            return b""
        
    def delete(self, bucket_name: str, key: str, extra_args: dict = {}) -> bool:
        try:
            self.client.delete_object(
                Bucket=bucket_name, 
                Key=key, 
                **extra_args
            )
            return True
        except ClientError as e:
            print(f"Delete failed: {e}")
            return False