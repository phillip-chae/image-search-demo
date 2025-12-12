from abc import ABC, abstractmethod
from typing import Any
from shared.config import StorageConfig, StorageType

class Storage(ABC):

    client: Any

    @abstractmethod
    def __init__(self, cfg: StorageConfig):
        """
        Initializes the storage with the given configuration.
        :param cfg: Configuration for the storage
        """
        scheme = "https" if cfg.ssl else "http"
        host = cfg.host if not "://" in cfg.host else cfg.host.split("://")[1]
        port = f":{cfg.port}" if cfg.port else ""
        self.endpoint = f"{scheme}://{host}{port}"
        self.cfg = cfg
        pass

    @abstractmethod
    def check_connection(self, bucket_name: str) -> bool:
        """
        Checks if the connection to the storage is valid.
        """
        pass

    @abstractmethod
    def create_bucket(self, bucket_name: str) -> bool:
        """
        Creates a bucket in the storage.
        :param bucket_name: Name of the bucket to create
        :return: True if the bucket was created successfully, False otherwise
        """
        pass

    @abstractmethod
    def exists(self, bucket_name: str, key: str) -> bool:
        """
        Checks if a file exists in the specified bucket.
        :param bucket_name: Name of the bucket
        :param key: Key of the file
        :return: True if the file exists, False otherwise
        """
        pass

    @abstractmethod
    def upload(self, bucket_name: str, file_content: bytes, key: str, extra_args: dict = {}) -> str:
        pass

    @abstractmethod
    def download(self, bucket_name: str, key: str, extra_args: dict = {}) -> bytes:
        pass

    @abstractmethod
    def delete(self, bucket_name: str, key: str, extra_args: dict = {}) -> bool:
        pass

def new_storage(cfg: StorageConfig) -> Storage:

    """
    Factory method to create a storage instance based on the configuration.
    :param cfg: Configuration for the storage
    :return: An instance of a storage class
    """
    match StorageType(cfg.type):
        case StorageType.S3:
            from .s3 import S3Storage
            return S3Storage(cfg)
        case StorageType.MINIO:
            from .s3 import S3Storage
            return S3Storage(cfg)
        case _:
            raise ValueError(f"Unknown storage type: {cfg.type}")