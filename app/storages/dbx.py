import os
import dropbox
from dropbox.files import WriteMode
from dotenv import load_dotenv
from pathlib import Path

envpath = Path('.') / '.env'
load_dotenv(dotenv_path=envpath, override=True)


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip().strip("'").strip('"')


def _cloud_name(file_name: str) -> str:
    return file_name.replace("\\", "__")


class DropboxStorage:
    def __init__(self):
        self.APP_KEY = _env("DROPBOX_CLIENT_ID")
        self.APP_SECRET = _env("DROPBOX_CLIENT_SECRET")
        self.REFRESH_TOKEN = _env("DROPBOX_REFRESH_TOKEN")
        self.last_error = ""
        self.dbx = dropbox.Dropbox(
            app_key=self.APP_KEY,
            app_secret=self.APP_SECRET,
            oauth2_refresh_token=self.REFRESH_TOKEN
        )

    def upload_file(self, input_file: Path, file_name: str):
        """
        input_file: local path to chunk file
        file_name: expects a string object, that may be a path or a file basename
        """
        try:
            dropbox_path = f"/{_cloud_name(file_name)}"
            content = Path(input_file).read_bytes()
            
            response = self.dbx.files_upload(
                content,
                dropbox_path, 
                mode=WriteMode('overwrite')
            )
                
            print(f"File uploaded successfully. Path: {response.path_display} at file ID: {response.id}")
            return str(response.id)

        except Exception as e:
            self.last_error = str(e)
            print(f"Dropbox Upload Error: {e}")
            return None

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

if __name__ == "__main__":
    db = DropboxStorage()
    # db.upload_file("lab05.pdf")
    # db.delete_file("id:KbksDpmCpUAAAAAAAAAABw")
