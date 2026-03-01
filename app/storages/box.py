from box_sdk_gen import BoxClient, AccessToken, PreflightFileUploadCheckParent, BoxOAuth, OAuthConfig
import os
from dotenv import load_dotenv
from pathlib import Path
import io

envpath = Path('../..') / '.env'
load_dotenv(dotenv_path=envpath)

class BoxStorage():
    def __init__(self):
        CLIENT_ID = os.getenv("BOX_CLIENT_ID")
        CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET")
        ACCESS_TOKEN = os.getenv("BOX_ACCESS_TOKEN")
        REFRESH_TOKEN = os.getenv("BOX_REFRESH_TOKEN")

        auth = BoxOAuth(
            OAuthConfig(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        )
        access_token = AccessToken(access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
        auth.token_storage.store(access_token)
        self.client = BoxClient(auth=auth)
    
    def upload_file(self, input_file, file_name):
        """
        input_file: expects a Python File that results from open(..., "r") as f:...
        file_name: expects a string object, that may be a path or a file basename
        """
        try:
            file_basename = os.path.basename(file_name)
            
            msg = self.client.uploads.upload_file(
                attributes={
                    "name": file_basename, # should replace with filename in future
                    "parent": {"id": "0"}
                },
                file=input_file
            )
            print(f"Successfully uploaded {file_basename} at file ID: {msg.entries[0].id}") # TODO: what if msg.entries more than 1 item?
            return str(msg.entries[0].id)

        except Exception as e:
            self.last_error = str(e)
            print(f"Box: Encountered error {e}")
        
    def delete_file(self, file_id):
        """
        file_id: expects a string object denoting ID of the file we wish to delete
        """
        try:
            self.client.files.delete_file_by_id(file_id=file_id)
            print(f"Successfully deleted Box file with ID: {file_id}")
            return True
        except Exception as e:
            print(f"Failed to delete file {file_id}: {e}")
            return False
    
    def get_file(self, file_id: str) -> bytes:
        try:
            file_stream = io.BytesIO()
            
            self.client.downloads.download_file(file_id=file_id, byte_stream=file_stream)
            
            file_stream.seek(0)
            print(f"Successfully downloaded {file_id}")
            return file_stream.read()
            
        except Exception as e:
            print(f"Box Download Error: {e}")
            return None
        
if __name__ == "__main__":
    b = BoxStorage()
    
    with open("example_lol.txt", "r") as f:
        b.upload_file(f, "example_lol.txt")
