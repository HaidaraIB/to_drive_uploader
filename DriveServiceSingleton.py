import os
import json
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from Config import Config

log = logging.getLogger(__name__)


class DriveServiceSingleton:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._drive_service = self.__get_drive_service()
            self._initialized = True

    @property
    def service(self):
        """Returns the authenticated Drive service instance"""
        return self._drive_service

    @classmethod
    def __get_drive_service(cls):
        """Private method to create and authenticate Drive service"""
        try:
            with open(Config.CREDENTIALS_FILE) as f:
                client_config = json.load(f)

            with open(Config.REFRESH_TOKEN_FILE) as f:
                refresh_token = f.read().strip()

            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_config["installed"]["client_id"],
                client_secret=client_config["installed"]["client_secret"],
                scopes=Config.SCOPES,
            )

            # Refresh the token
            creds.refresh(Request())

            return build(
                "drive",
                "v3",
                credentials=creds,
                static_discovery=False,  # Crucial for new versions
                cache_discovery=False,  # Disables the problematic cache
                always_use_jwt_access=True,  # New auth mechanism
            )
        except Exception as e:
            log.error(f"Failed to initialize Drive service: {str(e)}")
            raise

    def upload_file(self, file_path, folder_id):
        """
        Uploads a file to the specified folder

        Args:
            file_path (str): Path to the file to upload
            folder_id (str): ID of the folder to upload to

        Returns:
            dict: The uploaded file metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
            googleapiclient.errors.HttpError: If the API request fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        file_metadata = {"name": file_name, "parents": [folder_id]}

        media = MediaFileUpload(file_path)

        try:
            file = (
                self.service.files()
                .create(
                    body=file_metadata, media_body=media, fields="id,name,webViewLink"
                )
                .execute()
            )

            log.info(f"✅ File uploaded successfully!")
            log.info(f"📄 Name: {file.get('name')}")
            log.info(f"🆔 ID: {file.get('id')}")
            log.info(f"🔗 View at: {file.get('webViewLink')}")

            return file
        except Exception as e:
            log.error(f"Failed to upload file {file_name}: {str(e)}")
            raise
