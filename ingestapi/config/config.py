from pathlib import Path
from pydantic import Field

from shared.config import BaseConfig, S3Config, RedisConfig

service_name = "ingestapi"
conf_path = Path(__file__).parent.parent.parent / "conf" / f"{service_name}.yaml"

class Config(BaseConfig):
    redis: RedisConfig = Field(default_factory=RedisConfig)
    storage: S3Config = Field(default_factory=S3Config)