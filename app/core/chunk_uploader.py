from pathlib import Path
import re

from fastapi import HTTPException

from app.storages.box import BoxStorage
from app.storages.dbx import DropboxStorage
from app.storages.gd import GoogleDriveStorage
from app.core.file_format import FileMetadata


class ChunkCloudUploader:
    def __init__(self):
        self._clients = {}

    def _client_for(self, source: str):
        if source == "gd":
            if "gd" not in self._clients:
                self._clients["gd"] = GoogleDriveStorage()
            return self._clients["gd"]
        if source == "box":
            if "box" not in self._clients:
                self._clients["box"] = BoxStorage()
            return self._clients["box"]
        if source == "dropbox":
            if "dropbox" not in self._clients:
                self._clients["dropbox"] = DropboxStorage()
            return self._clients["dropbox"]
        raise HTTPException(status_code=500, detail=f"Unsupported chunk source '{source}'")

    def upload_manifest_chunks(
        self,
        *,
        storage_root: Path,
        manifest: FileMetadata,
        persist_manifest=None,
    ) -> dict:
        for chunk in sorted(manifest.chunks, key=lambda c: c.chunk_index):
            if chunk.provider_id:
                continue
            source = chunk.db_provider
            chunk_path = storage_root / chunk.chunk_name
            if not chunk_path.exists():
                raise HTTPException(
                    status_code=500,
                    detail=f"Missing chunk before cloud upload: {chunk.chunk_name}",
                )

            client = self._client_for(source)
            file_id = client.upload_file(chunk_path, chunk.chunk_name)
            if not file_id:
                provider_error = getattr(client, "last_error", "") or "unknown provider error"
                provider_error = self._redact(provider_error)
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"Failed uploading chunk {chunk.chunk_name} to {source}: "
                        f"{provider_error}"
                    ),
                )
            print(f"SUCCESSFULLY uploaded chunk {chunk.chunk_name} to {source}: ")
            chunk.provider_id = str(file_id)
            if persist_manifest:
                persist_manifest(manifest)

        return manifest

    @staticmethod
    def _redact(msg: str) -> str:
        # Box SDK exceptions can include the full oauth request body never echo secrets.
        patterns = [
            r"(client_secret=)[^&\s]+",
            r"(refresh_token=)[^&\s]+",
            r"(access_token=)[^&\s]+",
            r"('client_secret':\s*)'[^']+'",
            r"('refresh_token':\s*)'[^']+'",
            r"('access_token':\s*)'[^']+'",
            r"(\"client_secret\"\s*:\s*)\"[^\"]+\"",
            r"(\"refresh_token\"\s*:\s*)\"[^\"]+\"",
            r"(\"access_token\"\s*:\s*)\"[^\"]+\"",
        ]
        out = msg
        for pat in patterns:
            out = re.sub(pat, r"\1<redacted>", out)
        # Keep responses readable and avoid dumping huge request/response blobs.
        out = out.strip()
        if len(out) > 400:
            out = out[:400] + "…"
        return out
