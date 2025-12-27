from .config import BaseComponent
from pydantic import Field
from enum import Enum

class S3Config(BaseComponent):
    region: str = Field(default="", description="Region of the storage service")
    host: str = Field(default="", description="Host address of the storage service")
    port: int = Field(default=0, description="Port number of the storage service")
    access_key: str = Field(default="", description="Access key for authentication")
    secret_key: str = Field(default="", description="Secret key for authentication")
    ssl: bool = Field(default=False, description="Whether to use SSL for the connection")