from pydantic import BaseModel
from typing import List

class ChunkMetadata(BaseModel):
    chunk_index: int
    db_provider: str
    provider_id: str
    sha256: str

class FileMetadata(BaseModel):
    file_name: str
    file_size: int
    chunk_size: int
    chunks: List[ChunkMetadata] = []
