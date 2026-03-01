from pydantic import BaseModel
from typing import List

class ChunkMetadata(BaseModel):
    chunk_index: int
    chunk_name: str
    db_provider: str
    provider_id: str
    sha256: str

class FileMetadata(BaseModel):
    file_name: str
    content_type: str
    file_size: int
    chunk_size: int
    num_chunks: int
    file_sha256: str
    chunks: List[ChunkMetadata] = []
