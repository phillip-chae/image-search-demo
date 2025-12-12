from pydantic import Field

from .config import BaseComponent

class LoggerConfig(BaseComponent):
    formatter:str = Field(default="")
    filename: str = Field(default="", description="Log file name, if empty logs to console")
    level: str = Field(default="INFO", description="Logging level")
    fmt: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log message format")