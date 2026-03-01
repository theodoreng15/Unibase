from pathlib import Path
import hashlib
import json
from fastapi import HTTPException

from app.config.constants import READ_SIZE


def load_manifest(storage_root: Path, file_id: str) -> dict:
    manifest_path = storage_root / file_id / "metadata.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="File id not found")
    return json.loads(manifest_path.read_text())


def chunk_stream(storage_root: Path, file_id: str):
    manifest = load_manifest(storage_root, file_id)
    base = storage_root / file_id

    for c in sorted(manifest["chunks"], key=lambda x: x["index"]):
        p = base / c["name"]
        if not p.exists():
            raise HTTPException(status_code=500, detail=f"Missing chunk {c['name']}")

        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while True:
                b = f.read(READ_SIZE)
                if not b:
                    break
                hasher.update(b)
                yield b

        if hasher.hexdigest() != c["sha256"]:
            raise HTTPException(status_code=500, detail=f"Corrupt chunk {c['name']}")