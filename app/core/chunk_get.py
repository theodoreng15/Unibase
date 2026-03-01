from fastapi import HTTPException

from app.storages.box import BoxStorage
from app.storages.dbx import DropboxStorage
from app.storages.gd import GoogleDriveStorage


class ChunkCloudGetter:
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

    def get_manifest_chunks(
        self,
        *,
        manifest: dict,
        persist_manifest=None,
    ) -> dict:
        """
        Takes a manifest, iterates through its chunks, and gets them from the cloud providers.
        Updates the manifest to remove cloud file IDs as they are deleted.
        """
        
        get_chunk_dict = dict()        

        for chunk in sorted(manifest.get("chunks", []), key=lambda c: c.get("index", 0)):
            file_id = chunk.get("cloud_file_id")
            if not file_id:
                # Chunk wasn't uploaded or already deleted
                continue
                
            source = chunk.get("source")
            if not source:
                continue

            client = self._client_for(source)
            try:
                # Call the delete_file method on the respective storage client
                result = client.get_file(file_id)
                # If the method doesn't throw an error, we assume success
                print(f"SUCCESSFULLY got chunk {chunk['name']} from {source} (ID: {file_id})")
                
                get_chunk_dict[chunk['name']] = result
                
                # Update the manifest file if a save callback was provided
                if persist_manifest:
                    persist_manifest(manifest)
                    
            except Exception as e:
                provider_error = getattr(client, "last_error", "") or str(e)
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"Failed getting chunk {chunk['name']} from {source}: "
                        f"{provider_error}"
                    ),
                )

        return get_chunk_dict
