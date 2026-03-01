from box_sdk_gen import BoxClient, AccessToken, BoxOAuth, OAuthConfig
import os
from dotenv import load_dotenv
from pathlib import Path

envpath = Path('.') / '.env'
load_dotenv(dotenv_path=envpath, override=True)


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip().strip("'").strip('"')


def _cloud_name(file_name: str) -> str:
    return file_name.replace("\\", "__")


class BoxStorage:
    def __init__(self):
        CLIENT_ID = _env("BOX_CLIENT_ID")
        CLIENT_SECRET = _env("BOX_CLIENT_SECRET")
        ACCESS_TOKEN = _env("BOX_ACCESS_TOKEN")
        REFRESH_TOKEN = _env("BOX_REFRESH_TOKEN")
        self.last_error = ""

        auth = BoxOAuth(
            OAuthConfig(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        )
        access_token = AccessToken(access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
        auth.token_storage.store(access_token)
        self.client = BoxClient(auth=auth)
    
    def upload_file(self, input_file: Path, file_name: str):
        """
        input_file: local path to chunk file
        file_name: expects a string object, that may be a path or a file basename
        """
        try:
            file_basename = _cloud_name(file_name)

            with open(input_file, "rb") as f:
                msg = self.client.uploads.upload_file(
                    attributes={
                        "name": file_basename,
                        "parent": {"id": "0"}
                    },
                    file=f
                )
            print(f"Successfully uploaded {file_basename} at file ID: {msg.entries[0].id}") # TODO: what if msg.entries more than 1 item?
            return str(msg.entries[0].id)

        except Exception as e:
            self.last_error = str(e)
            print(f"Box: Encountered error {e}")
            return None
        
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
