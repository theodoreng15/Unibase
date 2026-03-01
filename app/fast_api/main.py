from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import mimetypes
import json
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
    manifest = await fragment_upload(storage_root=STORAGE_ROOT, file=file, chunk_size=chunk_size)
    
    chunk_uploader()


    file_meta = FileMetadata(
        file_name=manifest["file_name"],
        file_size=manifest["file_size"],
        chunk_size=manifest["chunk_size"],
        chunks=[],
    )

    for ch in manifest.get("chunks", []):
        chunk_meta = ChunkMetadata(
            chunk_index=ch["index"],
            db_provider=ch.get("source", ""),
            provider_id=ch.get("name", ""),
            sha256=ch.get("sha256", ""),
        )
        await record_chunk_metadata(file_meta=file_meta, chunk_meta=chunk_meta)

    return JSONResponse(
        {
            "file_name": manifest["file_name"],
            "file_size": manifest["file_size"],
            "total_chunks": manifest["total_chunks"],
            "chunk_size": manifest["chunk_size"],
            "status": manifest.get("status"),
        }
    )


@app.get("/meta/{file_name}")
def meta(file_name: str):
    return storage_provider.get_manifest(file_name)


@app.post("/retry/{file_name}")
def retry(file_name: str):
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
