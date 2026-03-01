import os
import dropbox
from dropbox.files import WriteMode
from dotenv import load_dotenv
from pathlib import Path

envpath = Path('.') / '.env'
load_dotenv(dotenv_path=envpath)

class DropboxStorage():
    def __init__(self):
        self.APP_KEY = os.getenv("DROPBOX_CLIENT_ID")
        self.APP_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
        self.REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
        self.FILEPATH_NAME = os.getenv("FILENAME")

        self.dbx = dropbox.Dropbox(
            app_key=self.APP_KEY,
            app_secret=self.APP_SECRET,
            oauth2_refresh_token=self.REFRESH_TOKEN
        )

    def upload_file(self, input_file, file_name):
        """
        input_file: expects a Python File that results from open(..., "r") as f:...
        file_name: expects a string object, that may be a path or a file basename
        """
        try:
            dropbox_path = f"/{os.path.basename(file_name)}"
            
            response = self.dbx.files_upload(
                input_file,
                dropbox_path, 
                mode=WriteMode('overwrite')
            )
                
            print(f"File uploaded successfully. Path: {response.path_display} at file ID: {response.id}")
            return str(response.id)

        except Exception as e:
            print(f"Dropbox Upload Error: {e}")

    def delete_file(self, file_id):
        """
        file_id: expects a string object denoting ID of the file we wish to delete
        """
        try:
            response = self.dbx.files_delete_v2(file_id)
            print(f"File {file_id} deleted successfully.")
            return response
            
        except Exception as e:
            print(f"Dropbox Delete Error: {e}")
    
    def get_file(self, file_id: str) -> bytes:
        try:
            metadata, response = self.dbx.files_download(file_id)
            
            print(f"Successfully downloaded {file_id}")
            return response.content
            
        except Exception as e:
            print(f"Dropbox Download Error: {e}")
            return None

if __name__ == "__main__":
    db = DropboxStorage()
