from pymilvus import MilvusClient, DataType

from shared.model.index import IndexItem
from shared.repo.milvus import AsyncMilvusRepository
from .import INGEST_DB

VECTOR_COLLECTION = "vector"

# Set collection schema
collection_schema = MilvusClient.create_schema(vector_field_name="vector")
collection_schema.add_field("id", DataType.VARCHAR, max_length=64, is_primary=True)
collection_schema.add_field("vector", DataType.FLOAT_VECTOR, dim=1152)
collection_schema.add_field("file_name", DataType.VARCHAR, max_length=255)

# Set index params
index_params = MilvusClient.prepare_index_params()
index_params.add_index("vector", "HNSW", "vector_index", 
    metric_type="COSINE", 
    params= {"M": 16, "efConstruction": 200}
)

class ImageRepository(AsyncMilvusRepository[IndexItem]):
    model = IndexItem
    collection_name = VECTOR_COLLECTION
    database_name = INGEST_DB
    collection_schema = collection_schema
    index_params = index_params
    
    async def search(self, embedding: list[float]) -> list[IndexItem]:
        results = await self.client.search(
            collection_name=self.collection_name,
            data=[embedding],
            anns_field="vector",
            param={
                "metric_type": "COSINE", 
                "params": {
                    "ef": 256
                }
            },
            limit=20,
            output_fields=["id", "file_name"],
        )
        hits = results[0] if results else []
        return [IndexItem(**hit) for hit in hits]