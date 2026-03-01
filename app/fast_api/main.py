from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import mimetypes
import json
import time
from pathlib import Path

from app.config.constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CONTENT_TYPE,
    STORAGE_ROOT,
)
from app.core.fragmenter import fragment_upload
from app.core.store_metadata import record_chunk_metadata
from app.core.file_format import FileMetadata, ChunkMetadata
from app.core.chunk_uploader import ChunkCloudUploader

app = FastAPI()
chunk_uploader = ChunkCloudUploader()


@app.post("/upload")
async def upload(file: UploadFile = File(...), chunk_size: int = DEFAULT_CHUNK_SIZE):
    start_time = time.time()
    manifest = await fragment_upload(storage_root=STORAGE_ROOT, file=file, chunk_size=chunk_size)

    # Persist cloud data for each chunk
    manifest = chunk_uploader.upload_manifest_chunks(
        storage_root=STORAGE_ROOT, manifest=manifest
    )

    # Persist metadata for each chunk
    file_meta = FileMetadata(
        file_name=manifest.file_name,
        content_type=manifest.content_type,
        file_size=manifest.file_size,
        chunk_size=manifest.chunk_size,
        num_chunks=manifest.num_chunks,
        file_sha256=manifest.file_sha256,
        chunks=[],
    )
    for ch in manifest.chunks:
        await record_chunk_metadata(file_meta=file_meta, chunk_meta=ch)

    from app.core.store_metadata import get_total_storage_used
    
    total_used = await get_total_storage_used()
    TOTAL_CAPACITY = 15 * 1024 * 1024 * 1024 # Assumed 15GB capacity across free tiers
    percent_used = round((total_used / TOTAL_CAPACITY) * 100, 4) if TOTAL_CAPACITY else 0
    
    distribution = {}
    for ch in manifest.chunks:
        dist_key = ch.db_provider
        distribution[dist_key] = distribution.get(dist_key, 0) + 1
        
    processing_time_ms = int((time.time() - start_time) * 1000)

    return JSONResponse(
        {
            "file_name": manifest.file_name,
            "file_size": manifest.file_size,
            "total_chunks": manifest.num_chunks,
            "chunk_size": manifest.chunk_size,
            "status": getattr(manifest, "status", "complete"),
            "storage_distribution": distribution,
            "metrics": {
                "processing_time_ms": processing_time_ms,
                "total_storage_used_bytes": total_used,
                "total_storage_capacity_bytes": TOTAL_CAPACITY,
                "storage_used_percentage": percent_used
            }
        }
    )


@app.get("/meta/{file_name}")
def meta(file_name: str):
    storage_provider = None
    return storage_provider.get_manifest(file_name)


@app.post("/retry/{file_name}")
def retry(file_name: str):
    storage_provider = None
    if not chunk_uploader:
        return JSONResponse({"detail": "Cloud uploader unavailable"}, status_code=500)
    manifest = storage_provider.get_manifest(file_name)
    manifest_path = None
    try:
        # Local storage layout only; in Mongo mode this endpoint is not supported.
        from app.config.constants import STORAGE_ROOT, STORAGE_PROVIDER

        if STORAGE_PROVIDER.strip().lower() != "local":
            return JSONResponse({"detail": "Retry supported only in local mode"}, status_code=400)
        manifest_path = STORAGE_ROOT / f"{file_name}\\metadata.json"

        def persist(m: dict) -> None:
            manifest_path.write_text(__import__("json").dumps(m, indent=2))

        manifest["status"] = "uploading"
        persist(manifest)
        manifest = chunk_uploader.upload_manifest_chunks(
            storage_root=STORAGE_ROOT,
            manifest=manifest,
            persist_manifest=persist,
        )
        manifest["status"] = "complete"
        persist(manifest)
        return JSONResponse({"file_name": manifest["file_name"], "status": manifest["status"]})
    except Exception as exc:
        if isinstance(manifest, dict):
            manifest["status"] = "failed"
            manifest["error"] = str(exc)
            if manifest_path:
                try:
                    manifest_path.write_text(__import__("json").dumps(manifest, indent=2))
                except Exception:
                    pass
        raise


@app.get("/download/{file_name}")
def download(file_name: str):
    storage_provider = None
    manifest = storage_provider.get_manifest(file_name)

    filename = manifest.get("file_name") or f"{file_name}.bin"
    content_type = manifest.get("content_type")
    if not content_type:
        guessed, _ = mimetypes.guess_type(filename)
        content_type = guessed or DEFAULT_CONTENT_TYPE

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        storage_provider.stream_chunks(file_name),
        media_type=content_type,
        headers=headers,
    )

"""
@app.get("/files")
async def list_all_files():
    from app.core.store_metadata import list_files
    try:
        files = await list_files()
        return JSONResponse({"files": files})
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)
"""

@app.delete("/files/{file_name}")
async def delete_file(file_name: str):
    start_time = time.time()
    from app.core.store_metadata import get_full_manifest, delete_chunk_metadata, get_total_storage_used
    from app.core.chunk_deleter import ChunkCloudDeleter
    try:
        manifest = await get_full_manifest(file_name)
        if not manifest:
            return JSONResponse({"detail": "File not found"}, status_code=404)
        
        deleter = ChunkCloudDeleter()
        # Step 1: Delete physical chunks from cloud
        deleter.delete_manifest_chunks(manifest=manifest)
        
        # Step 2: Delete logical file record from database
        success = await delete_chunk_metadata(file_name)
        
        total_used = await get_total_storage_used()
        TOTAL_CAPACITY = 15 * 1024 * 1024 * 1024
        percent_used = round((total_used / TOTAL_CAPACITY) * 100, 4) if TOTAL_CAPACITY else 0
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        if success:
            return JSONResponse({
                "detail": "File deleted successfully", 
                "file_name": file_name,
                "metrics": {
                    "processing_time_ms": processing_time_ms,
                    "total_storage_used_bytes": total_used,
                    "total_storage_capacity_bytes": TOTAL_CAPACITY,
                    "storage_used_percentage": percent_used
                }
            })
        else:
            return JSONResponse({"detail": "Failed to selectively delete metadata from database"}, status_code=500)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)

@app.get("/files/{file_name}")
async def get_file(file_name: str):
    from app.core.store_metadata import get_full_manifest, get_chunk_metadata
    from app.core.chunk_get import ChunkCloudGetter
    try:
        manifest = await get_full_manifest(file_name)
        if not manifest:
            return JSONResponse({"detail": "File not found"}, status_code=404)
        
        getr = ChunkCloudGetter()

        resulting_chunks_dict = getr.get_manifest_chunks(manifest=manifest)
        ordered_keys = sorted(resulting_chunks_dict.keys())

        with open("combined_file.bin", "wb") as output_file:
            for blob_name in ordered_keys:
                chunk_data = resulting_chunks_dict.get(blob_name)
                if chunk_data:
                    output_file.write(chunk_data)
        
        success = await get_chunk_metadata(file_name)
        
        if success:
            return JSONResponse({"detail": "File get successfully", "file_name": file_name})
        else:
            return JSONResponse({"detail": "Failed to selectively get metadata from database"}, status_code=500)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)