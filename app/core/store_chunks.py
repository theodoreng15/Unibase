import asyncio
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from security import encrypt_key, decrypt_token
from pymongo import AsyncMongoClient

async def record_chunk_metadata(filename: str, filesize: int, 
                                chunk_idx: int, chunk_size: int,
                                db_provider: str, provider_id: str):
    uri = os.getenv("MONGO_URI")
    client = AsyncMongoClient(uri)

    new_chunk = {
        "chunk_index" : chunk_idx,
        "db_provider" : db_provider,
        "provider_id" : provider_id,
        "chunk_size" : chunk_size
    }

    update_operation = {
        "$set": {
            f"chunk_list.{str(chunk_idx)}" : new_chunk
        },
        "$setOnInsert": {
            "filename": filename,
            "filesize": filesize,
        }
    }

    try:
        database = client.get_database("unibase")
        unibase = database.get_collection("unibase_collection")
        query = { "_id": filename }

        # Add document if it doesn't exist
        res = await unibase.update_one(query, update_operation, upsert=True)
        await client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)

load_dotenv()
asyncio.run(record_chunk_metadata("test.txt", 1, 0, 100, "S3", "s3.key"))

