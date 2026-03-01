import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
import mimetypes
from pathlib import Path

envpath = Path('.') / '.env'
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

        self.FILEPATH_NAME = os.getenv("FILENAME")

    def upload_file(self, file_name):
        try:
            mime_type, _ = mimetypes.guess_type(self.FILEPATH_NAME)
            
            file_metadata = {'name': os.path.basename(file_name)}
            media = MediaFileUpload(self.FILEPATH_NAME, mimetype=mime_type)

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


if __name__ == "__main__":
    gd = GoogleDriveStorage()
    gd.upload_file("C:\\Users\\steve\\Downloads\\Unibase\\test_files\\lab05.pdf")
    # gd.delete_file("12EsdFFzeqvJSrrxtUtYu3NAlBVv4-k4R")