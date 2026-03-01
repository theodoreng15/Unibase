from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
import mimetypes

from app.config.constants import STORAGE_ROOT, DEFAULT_CHUNK_SIZE, DEFAULT_CONTENT_TYPE
from app.core.fragmenter import fragment_upload
from app.core.assembler import load_manifest, chunk_stream

app = FastAPI()


@app.post("/upload")
async def upload(file: UploadFile = File(...), chunk_size: int = DEFAULT_CHUNK_SIZE):
    manifest = await fragment_upload(
        storage_root=STORAGE_ROOT,
        file=file,
        chunk_size=chunk_size,
    )
    return JSONResponse(
        {
            "file_id": manifest["file_id"],
            "original_name": manifest["original_name"],
            "file_size": manifest["file_size"],
            "total_chunks": manifest["total_chunks"],
            "chunk_size": manifest["chunk_size"],
        }
    )


@app.get("/meta/{file_id}")
def meta(file_id: str):
    return load_manifest(STORAGE_ROOT, file_id)


@app.get("/download/{file_id}")
def download(file_id: str):
    manifest = load_manifest(STORAGE_ROOT, file_id)

    filename = manifest.get("original_name") or f"{file_id}.bin"
    content_type = manifest.get("content_type")
    if not content_type:
        guessed, _ = mimetypes.guess_type(filename)
        content_type = guessed or DEFAULT_CONTENT_TYPE

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        chunk_stream(STORAGE_ROOT, file_id),
        media_type=content_type,
        headers=headers,
    )