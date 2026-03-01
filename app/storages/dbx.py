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

    def upload_file(self, file_name):
        try:
            dropbox_path = f"/{os.path.basename(file_name)}"
            
            with open(self.FILEPATH_NAME, "rb") as f:
                response = self.dbx.files_upload(
                    f.read(), 
                    dropbox_path, 
                    mode=WriteMode('overwrite')
                )
                
            print(f"File uploaded successfully. Path: {response.path_display} at file ID: {response.id}")
            return str(response.id)

        except Exception as e:
            print(f"Dropbox Upload Error: {e}")

    def delete_file(self, file_path_or_id):
        try:
            response = self.dbx.files_delete_v2(file_path_or_id)
            print(f"File {file_path_or_id} deleted successfully.")
            return response
            
        except Exception as e:
            print(f"Dropbox Delete Error: {e}")

if __name__ == "__main__":
    db = DropboxStorage()
    
    # To upload the file specified in your .env
    # db.upload_file("lab05.pdf")
    
    # To delete (Dropbox usually deletes by path)
    db.delete_file("id:KbksDpmCpUAAAAAAAAAABw")