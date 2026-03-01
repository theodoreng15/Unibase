from box_sdk_gen import BoxClient, AccessToken, PreflightFileUploadCheckParent, BoxOAuth, OAuthConfig
import os
from dotenv import load_dotenv
from pathlib import Path

envpath = Path('.') / '.env'
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
            
            self.client.uploads.preflight_file_upload_check(
                name=file_basename, size=21474836480, parent=PreflightFileUploadCheckParent(id="0") # roughly 20GB
            )
            
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
        
if __name__ == "__main__":
    b = BoxStorage()
    # b.upload_file("C:\\Users\\steve\\Downloads\\Unibase\\test_files\\lab05.pdf")
    # b.delete_file("2150167600272")