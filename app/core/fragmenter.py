from pathlib import Path
import hashlib
import json
import re
from fastapi import UploadFile, HTTPException

from app.config.constants import DEFAULT_CHUNK_SIZE, READ_SIZE


def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _chunk_basename(idx: int) -> str:
    return f"chunk_{idx:06d}.bin"


def _normalize_file_name(upload_name: str | None) -> str:
    candidate = Path(upload_name or "").name.strip()
    if not candidate:
        candidate = "uploaded.bin"
    normalized = re.sub(r"[^A-Za-z0-9._-]", "_", candidate)
    normalized = normalized.strip("._-")
    return normalized or "uploaded.bin"


def _chunk_name(file_name: str, idx: int) -> str:
    return f"{file_name}\\{_chunk_basename(idx)}"


def _manifest_name(file_name: str) -> str:
    return f"{file_name}\\metadata.json"


def _chunk_source(idx: int) -> str:
    providers = ("gd", "box", "dropbox")
    return providers[idx % len(providers)]


async def fragment_upload(
    *,
    storage_root: Path,
    file: UploadFile,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    file_name = _normalize_file_name(file.filename)
    safe_mkdir(storage_root)
    manifest_path = storage_root / _manifest_name(file_name)
    if manifest_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"File '{file_name}' already exists. Duplicate uploads are not allowed.",
        )

    full_hasher = hashlib.sha256()

    chunks_meta = []
    idx = 0
    current_size = 0
    current_chunk_path = storage_root / _chunk_name(file_name, idx)
    current_chunk_file = open(current_chunk_path, "wb")
    current_chunk_hasher = hashlib.sha256()

    total_bytes = 0

    try:
        while True:
            buf = await file.read(READ_SIZE)
            if not buf:
                break

            total_bytes += len(buf)
            full_hasher.update(buf)

            offset = 0
            while offset < len(buf):
                space_left = chunk_size - current_size
                take = min(space_left, len(buf) - offset)
                part = buf[offset : offset + take]

                current_chunk_file.write(part)
                current_chunk_hasher.update(part)

                current_size += take
                offset += take

                if current_size == chunk_size:
                    current_chunk_file.close()
                    chunks_meta.append(
                        {
                            "index": idx,
                            "name": _chunk_name(file_name, idx),
                            "source": _chunk_source(idx),
                            "size": current_size,
                            "sha256": current_chunk_hasher.hexdigest(),
                        }
                    )

                    idx += 1
                    current_size = 0
                    current_chunk_path = storage_root / _chunk_name(file_name, idx)
                    current_chunk_file = open(current_chunk_path, "wb")
                    current_chunk_hasher = hashlib.sha256()

        if current_size > 0:
            current_chunk_file.close()
            chunks_meta.append(
                {
                    "index": idx,
                    "name": _chunk_name(file_name, idx),
                    "source": _chunk_source(idx),
                    "size": current_size,
                    "sha256": current_chunk_hasher.hexdigest(),
                }
            )
        else:
            current_chunk_file.close()
            if current_chunk_path.exists() and current_chunk_path.stat().st_size == 0:
                current_chunk_path.unlink()

    except Exception as e:
        try:
            current_chunk_file.close()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    manifest = {
        "file_name": file_name,
        "content_type": file.content_type,
        "file_size": total_bytes,
        "chunk_size": chunk_size,
        "total_chunks": len(chunks_meta),
        "file_sha256": full_hasher.hexdigest(),
        "chunks": chunks_meta,
        "status": "chunked",
    }

    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest
