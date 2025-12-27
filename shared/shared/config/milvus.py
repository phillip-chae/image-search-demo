from .config import BaseComponent

class MilvusConfig(BaseComponent):
    host: str = 'localhost'
    port: int = 19530
    username: str = "root"
    password: str = "Milvus"