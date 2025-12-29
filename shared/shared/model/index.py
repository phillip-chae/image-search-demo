from pydantic import BaseModel, Field
from uuid_extensions import uuid7str

INDEX_BUCKET = "indexed-images"

class MilvusModel(BaseModel):
    pass

class IndexItem(MilvusModel):
    id: str = Field(default_factory=uuid7str, description="Unique identifier for the indexed item")
    file_name: str = Field(default="", description="Original file name of the indexed item")
    distance: float = Field(default=0.0, description="Distance score from the query",)
    vector: list[float] = Field(default_factory=list, description="Vector of the item")

class IndexRequest(BaseModel):
    idxs: list[IndexItem] = Field(default_factory=list, description="List of items to be indexed")

class IndexResponse(BaseModel):
    success: bool = Field(default=True, description="Indicates if the indexing was successful")
    detail: str = Field(default="", description="Additional details about the indexing process")
    elapsed_time: float = Field(default=0.0, description="Time taken to complete the indexing in seconds")