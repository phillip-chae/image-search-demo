from .config import BaseComponent
from pydantic import Field

class RedisConfig(BaseComponent):
    host: str = Field(default='localhost', description="Redis server host")
    port: int = Field(default=6379, description="Redis server port")
    db: int = Field(default=0, description="Redis database number")
    username: str = Field(default="", description="Username for Redis server")
    password: str = Field(default="", description="Password for Redis server")
    ssl: bool = Field(default=False, description="Use SSL for Redis connection")

    @property
    def url(self) -> str:
        scheme = "rediss" if self.ssl else "redis"
        auth_part = f"{self.username}:{self.password}@" if self.password else ""
        return f"{scheme}://{auth_part}{self.host}:{self.port}/{self.db}"
