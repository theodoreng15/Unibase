import os
from app.core.file_format import ChunkMetadata, FileMetadata
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from pathlib import Path

envpath = Path('.') / '.env'
load_dotenv(dotenv_path=envpath)

_uri = os.getenv("MONGO_URI")
client = AsyncMongoClient(_uri)
database = client.get_database("unibase")
unibase = database.get_collection("unibase_collection")

async def record_chunk_metadata(file_meta: FileMetadata, chunk_meta: ChunkMetadata) -> None:
    new_chunk_dict = chunk_meta.model_dump()
    file_base_dict = file_meta.model_dump(exclude={"chunks"}) # Exclude the empty list

    # Add document if it doesn't exist
    update_operation = {
        "$set": {
            f"chunk_list.{str(chunk_meta.chunk_index)}" : new_chunk_dict
        },
        "$setOnInsert": file_base_dict
    }
    try:
        query = { "_id": file_meta.file_name }
        await unibase.update_one(query, update_operation, upsert=True)
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)

async def get_chunk_metadata(file_name: str) -> list[str]:
    try:
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

async def delete_chunk_metadata(file_name: str) -> bool:
    try:
        query = { "_id": file_name }

        # Delete the doc based on file_name
        res = await unibase.delete_one(query)

        if res.deleted_count > 0:
             return True
        return False

    except Exception as e:
            raise Exception("Unable to find the document due to the following error: ", e)

async def get_full_manifest(file_name: str) -> dict:
    try:
        query = { "_id": file_name }
        doc = await unibase.find_one(query)
        if not doc: 
            return None
            
        # Format the document to match what ChunkCloudDeleter expects
        # This should've been FileMetadata, todo fix
        manifest = {
            "file_name": doc["_id"],
            "file_size": doc.get("file_size"),
            "chunk_size": doc.get("chunk_size"),
            "chunks": []
        }
        
        chunk_dict = doc.get("chunk_list", {})
        for idx_str, chunk_data in chunk_dict.items():
            manifest["chunks"].append({
                "index": int(idx_str),
                "source": chunk_data.get("db_provider"),
                "cloud_file_id": chunk_data.get("provider_id"),
                "name": f"{file_name}.part{idx_str}",
                "sha256": chunk_data.get("sha256")
            })
            
        return manifest
    except Exception as e:
        raise Exception("Unable to get manifest due to the following error: ", e)

async def get_total_storage_used() -> int:
    try:
        pipeline = [
            {"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}
        ]
        cursor = await unibase.aggregate(pipeline)
        result = [doc async for doc in cursor]
        if result:
            return result[0].get("total_size", 0)
        return 0
    except Exception as e:
        print(f"Failed to calculate total storage: {e}")
        return 0

"""
async def list_files() -> list[dict]:
    try:
        # Include chunk_list to extract provider information
        cursor = unibase.find({}, {"_id": 1, "file_size": 1, "chunk_size": 1, "chunk_list": 1})
        files = []
        async for doc in cursor:
            # Extract unique providers from the chunk_list dictionary
            chunk_dict = doc.get("chunk_list", {})
            providers = set()
            for chunk_meta in chunk_dict.values():
                if "db_provider" in chunk_meta:
                    providers.add(chunk_meta["db_provider"])
            
            files.append({
                "file_name": doc["_id"],
                "file_size": doc.get("file_size", 0),
                "chunk_size": doc.get("chunk_size", 0),
                "providers": list(providers)
            })
        return files
    except Exception as e:
        raise Exception("Unable to list files due to the following error: ", e)
"""
