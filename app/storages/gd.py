import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv
import mimetypes
from pathlib import Path

envpath = Path('.') / '.env'
load_dotenv(dotenv_path=envpath, override=True)


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip().strip("'").strip('"')


def _cloud_name(file_name: str) -> str:
    return file_name.replace("\\", "__")


class GoogleDriveStorage:
    def __init__(self):
        CLIENT_ID = _env("GD_CLIENT_ID")
        CLIENT_SECRET = _env("GD_CLIENT_SECRET")
        REFRESH_TOKEN = _env("GD_REFRESH_TOKEN")
        TOKEN_URI = "https://oauth2.googleapis.com/token"
        self.last_error = ""

        creds = Credentials(
            token=None,
            refresh_token=REFRESH_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri=TOKEN_URI
        )

        self.drive_service = build('drive', 'v3', credentials=creds)
    
    def upload_file(self, input_file: Path, file_name: str):
        try:
            mime_type, _ = mimetypes.guess_type(file_name)
            mime_type = mime_type or "application/octet-stream"
            
            file_metadata = {'name': _cloud_name(file_name)}
            with open(input_file, "rb") as f:
                media = MediaIoBaseUpload(f, mime_type, resumable=False)

                response = self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            print(f"File Uploaded successfully. File {file_name} uploaded at File ID: {response.get('id')}")
            return str(response.get('id'))

        except Exception as e:
            self.last_error = str(e)
            print(f"An error occured: {e}")
            return None

    def delete_file(self, file_id):
        try:
            response = self.drive_service.files().delete(
                fileId=file_id
            ).execute()
            
            print(f"File {file_id} deleted successfully (Status 204).")
            return response
            
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    gd = GoogleDriveStorage()
    gd.upload_file(Path("C:\\Users\\steve\\Downloads\\Unibase\\test_files\\lab05.pdf"), "lab05.pdf")
    # gd.delete_file("12EsdFFzeqvJSrrxtUtYu3NAlBVv4-k4R")
