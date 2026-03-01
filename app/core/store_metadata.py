import asyncio
import os
from dotenv import load_dotenv
from app.core.file_format import ChunkMetadata, FileMetadata
from pymongo import AsyncMongoClient

_uri = os.getenv("MONGO_URI")
client = AsyncMongoClient(_uri)

async def record_chunk_metadata(file_meta: FileMetadata, chunk_meta: ChunkMetadata) -> None:
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
    

async def get_chunk_metadata(file_name: str) -> list[str]:
    try:
        database = client.get_database("unibase")
        unibase = database.get_collection("unibase_collection")
        query = { "_id": file_name }

        # Fetch the document based on file_name
        doc = await unibase.find_one(query)
        if not doc: return []

        # Extract the chunks and order by chunk_id
        chunk_dict = doc.get("chunk_list", {})
        raw_chunks = list(chunk_dict.values())
        sorted_chunks = sorted(raw_chunks, key=lambda x: x["chunk_index"])

        # List of chunk_id only
        chunk_id_list = []
        for chunk in sorted_chunks:
            chunk_id_list.append(chunk["provider_id"])
        
        return chunk_id_list
    except Exception as e:
            raise Exception("Unable to find the document due to the following error: ", e)

