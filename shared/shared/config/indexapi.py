from pydantic import Field

from .config import BaseComponent

class IndexApiConfig(BaseComponent):
    protocol: str = Field(default="http", description="Protocol to use for connecting to the Index API")
    host: str = Field(default="indexapi", description="Host address of the Index API service")
    port: int = Field(default=8080, description="Port number of the Index API service")

    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"