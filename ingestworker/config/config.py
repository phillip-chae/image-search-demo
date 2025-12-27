from pathlib import Path
from pydantic import Field
from dotenv import load_dotenv

from shared.config import BaseConfig, S3Config, MilvusConfig, RedisConfig
from ingestworker import project_root

service_name = "ingestworker"
conf_path = project_root / "conf" / f"{service_name}.yaml"

class Config(BaseConfig):
    redis: RedisConfig = Field(default_factory=RedisConfig)
    s3: S3Config = Field(default_factory=S3Config)
    milvus_db: MilvusConfig = Field(default_factory=MilvusConfig)

load_dotenv(project_root / ".env")

cfg = Config.from_yaml(conf_path)
print(cfg)