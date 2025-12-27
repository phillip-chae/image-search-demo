from shared.model.index import IndexItem, IndexResponse

from . import AsyncHttpClient

class AsyncHttpIndexClient(AsyncHttpClient):
    
    async def create_index(self, data: IndexItem) -> IndexResponse | None:
        endpoint = self.endpoint("/index")
        try:
            async with self.client as client:
                response = await client.post(
                    endpoint,
                    json=data.model_dump(),
                )
                response.raise_for_status()
                resp_data = response.json()
                return IndexResponse(**resp_data)
        except Exception as e:
            self.logger.error(f"Error creating index: {e}")
            return None