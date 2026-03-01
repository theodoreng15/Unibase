import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv
import mimetypes
from pathlib import Path
import io

envpath = Path('../..') / '.env'
load_dotenv(dotenv_path=envpath)

class GoogleDriveStorage():
    def __init__(self):
        CLIENT_ID = os.getenv("GD_CLIENT_ID")
        CLIENT_SECRET = os.getenv("GD_CLIENT_SECRET")
        REFRESH_TOKEN = os.getenv("GD_REFRESH_TOKEN")
        TOKEN_URI = "https://oauth2.googleapis.com/token"

        creds = Credentials(
            token=None,
            refresh_token=REFRESH_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri=TOKEN_URI
        )

        self.drive_service = build('drive', 'v3', credentials=creds)

    def upload_file(self, input_file, file_name):
        try:
            filename_base = os.path.basename(file_name)
            mime_type, _ = mimetypes.guess_type(filename_base)
            
            file_metadata = {'name': filename_base}
            media = MediaIoBaseUpload(input_file, mime_type)

            response = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            print(f"File Uploaded successfully. File {file_name} uploaded at File ID: {response.get('id')}")
            return str(response.get('id'))

        except Exception as e:
            print(f"An error occured: {e}")

    def delete_file(self, file_id):
        try:
            response = self.drive_service.files().delete(
                fileId=file_id
            ).execute()
            
            print(f"File {file_id} deleted successfully (Status 204).")
            return response
            
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def get_file(self, file_id: str) -> bytes:
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            
            file_stream = io.BytesIO()
            
            downloader = MediaIoBaseDownload(file_stream, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_stream.seek(0)
            return file_stream.read()
            
        except Exception as e:
            print(f"Google Drive Download Error: {e}")
            return None


if __name__ == "__main__":
    gd = GoogleDriveStorage()
