from httpx import AsyncClient
from logging import Logger, getLogger

class AsyncHttpClient:

    def __init__(
            self, 
            base_url: str, 
            logger: Logger = getLogger(__name__), 
            version: str = "v1",
            *args, **kwargs
        ):
        self.client = AsyncClient(
            base_url=base_url,
            *args, **kwargs
        )
        self.logger = logger
        self.version = version

    def endpoint(self, path: str) -> str:
        return f"/api/{self.version}/{path.lstrip('/')}"
        
    async def close(self):
        await self.client.aclose()
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()