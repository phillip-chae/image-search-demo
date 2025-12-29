from typing import Generic, Type, TypeVar
from pymilvus import AsyncMilvusClient, CollectionSchema, MilvusClient
from pymilvus.milvus_client.index import IndexParams

from shared.config import MilvusConfig
from shared.model.index import MilvusModel

T = TypeVar("T", bound=MilvusModel)

class MilvusRepository(Generic[T]):
    model: Type[T]
    collection_name: str
    database_name: str
    index_params: IndexParams
    collection_schema: CollectionSchema

    def __init__(self, cfg: MilvusConfig):
        self.client = MilvusClient(
            uri=f"http://{cfg.host}:{cfg.port}",
            username=cfg.username,
            password=cfg.password,
            db_name=self.database_name,
        )
        
    @classmethod
    def init(cls, cfg: MilvusConfig):
        client: MilvusClient = MilvusClient(
            uri=f"http://{cfg.host}:{cfg.port}",
            username=cfg.username,
            password=cfg.password,
        )

        if not cls.database_name in client.list_databases():
            client.create_database(cls.database_name)
        client.use_database(cls.database_name)

        if cls.collection_name in client.list_collections(): #type: ignore
            client.drop_collection(cls.collection_name)
        client.create_collection(
            cls.collection_name, 
            schema=cls.collection_schema, 
            index_params=cls.index_params
        )
        client.load_collection(collection_name=cls.collection_name)
        client.close()

    def create(self, items: list[T]) -> list[str]:
        """Create new entries in the Milvus collection."""
        data = [item.model_dump(exclude_unset=True, exclude_defaults=True) for item in items]
        results = self.client.insert(self.collection_name, data)
        return [str(id) for id in results["ids"]]
    
    def read_by_id(self, ids: list) -> list[T]:
        """Read entries from the Milvus collection by their IDs."""
        return [
            self.model(**hit)
            for hit in self.client.query(
                self.collection_name,
                expr=f'id in {ids}',
                output_fields=["*"]
            )
        ]
    
    def delete_by_id(self, ids: list) -> int:
        try:
            self.client.delete(self.collection_name, ids)
            return len(ids) if isinstance(ids, list) else 1
        except Exception as e:
            print(f"Error deleting ids {ids}: {e}")
            return 0

class AsyncMilvusRepository(Generic[T]):
    model: Type[T]
    collection_name: str
    database_name: str
    index_params: IndexParams
    collection_schema: CollectionSchema

    def __init__(self, cfg: MilvusConfig):
        self.client = AsyncMilvusClient(
            uri=f"http://{cfg.host}:{cfg.port}",
            username=cfg.username,
            password=cfg.password,
            db_name=self.database_name,
        )
        
    @classmethod
    async def init(cls, cfg: MilvusConfig):
        client = AsyncMilvusClient(
            uri=f"http://{cfg.host}:{cfg.port}",
            username=cfg.username,
            password=cfg.password,
        )

        if not cls.database_name in await client.list_databases():
            await client.create_database(cls.database_name)
        client.use_database(cls.database_name)

        if not cls.collection_name in await client.list_collections():
            await client.create_collection(
                cls.collection_name, 
                schema=cls.collection_schema, 
                index_params=cls.index_params
            )
        await client.load_collection(collection_name=cls.collection_name)
        await client.close()

    async def create(self, items: list[T]) -> list[str]:
        """Create new entries in the Milvus collection."""
        data = [item.model_dump() for item in items]
        results = await self.client.insert(self.collection_name, data)
        return [str(id) for id in results["ids"]]
    
    async def read_by_id(self, ids: list) -> list[T]:
        """Read entries from the Milvus collection by their IDs."""
        return [
            self.model(**hit)
            for hit in await self.client.query(
                self.collection_name,
                expr=f'id in {ids}',
                output_fields=["*"]
            )
        ]
    
    async def delete_by_id(self, ids: list) -> int:
        try:
            await self.client.delete(self.collection_name, ids)
            return len(ids) if isinstance(ids, list) else 1
        except Exception as e:
            print(f"Error deleting ids {ids}: {e}")
            return 0
        
    