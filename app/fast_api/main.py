from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
import mimetypes

from app.config.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CONTENT_TYPE
from app.core.providers import create_storage_provider

app = FastAPI()
storage_provider = create_storage_provider()


@app.post("/upload")
async def upload(file: UploadFile = File(...), chunk_size: int = DEFAULT_CHUNK_SIZE):
    manifest = await storage_provider.save_upload(file=file, chunk_size=chunk_size)
    return JSONResponse(
        {
            "file_name": manifest["file_name"],
            "file_size": manifest["file_size"],
            "total_chunks": manifest["total_chunks"],
            "chunk_size": manifest["chunk_size"],
        }
    )


@app.get("/meta/{file_name}")
def meta(file_name: str):
    return storage_provider.get_manifest(file_name)


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
