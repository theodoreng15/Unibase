import asyncio
import os
from dotenv import load_dotenv
from app.core.file_format import ChunkMetadata, FileMetadata
from pymongo import AsyncMongoClient


async def record_chunk_metadata(file_meta: FileMetadata, chunk_meta: ChunkMetadata):
    new_chunk_dict = chunk_meta.model_dump()
    file_base_dict = file_meta.model_dump(exclude={"chunks"}) # Exclude the empty list

    update_operation = {
        "$set": {
            f"chunk_list.{str(chunk_meta.chunk_index)}" : new_chunk_dict
        },
        "$setOnInsert": file_base_dict
    }

    try:
        database = client.get_database("unibase")
        unibase = database.get_collection("unibase_collection")
        query = { "_id": file_meta.file_name }

        # Add document if it doesn't exist
        await unibase.update_one(query, update_operation, upsert=True)
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)
    


load_dotenv()
_uri = os.getenv("MONGO_URI")
client = AsyncMongoClient(_uri)
test_file = FileMetadata(
    file_name="test1.txt",
    file_size=1,
    chunk_size=20,
)
current_chunk = ChunkMetadata(
    chunk_index=0,
    db_provider="gd",
    provider_id="gd_id_fake",
    sha256="checksum"
)
asyncio.run(record_chunk_metadata(test_file, current_chunk))
