from pathlib import Path
import hashlib
import json
from fastapi import HTTPException

from app.config.constants import READ_SIZE


def load_manifest(storage_root: Path, file_name: str) -> dict:
    manifest_path = storage_root / f"{file_name}\\metadata.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return json.loads(manifest_path.read_text())


def chunk_stream(storage_root: Path, file_name: str):
    manifest = load_manifest(storage_root, file_name)

    for c in sorted(manifest["chunks"], key=lambda x: x["index"]):
        p = storage_root / c["name"]
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
