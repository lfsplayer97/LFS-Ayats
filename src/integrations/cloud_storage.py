"""
Cloud Storage Integration
Upload and backup telemetry data to cloud storage services
"""

import os
from typing import Optional, List
from datetime import datetime


class GoogleDriveIntegration:
    """
    Google Drive integration for backing up telemetry data.

    This class provides methods to upload files to Google Drive
    and manage automatic backups of telemetry sessions.

    Args:
        credentials_path: Path to Google OAuth2 credentials JSON file

    Example:
        >>> gdrive = GoogleDriveIntegration('./credentials.json')
        >>> file_id = gdrive.upload_session('session_data.json', folder_id='...')
        >>> print(f"Uploaded: {file_id}")

    Reference:
        https://developers.google.com/drive/api/guides/about-sdk

    Note:
        Requires google-api-python-client package to be installed.
        This is a minimal implementation that requires the package
        to be installed separately to avoid adding it as a core dependency.
    """

    def __init__(self, credentials_path: str):
        """
        Initialize Google Drive integration.

        Args:
            credentials_path: Path to credentials JSON file

        Raises:
            ImportError: If google-api-python-client is not installed
            FileNotFoundError: If credentials file doesn't exist
        """
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload

            self._Credentials = Credentials
            self._build = build
            self._MediaFileUpload = MediaFileUpload
        except ImportError as e:
            raise ImportError(
                "google-api-python-client is required for Google Drive integration. "
                "Install it with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            ) from e

        self.credentials_path = credentials_path
        self._service = None

    def _get_service(self):
        """Get or create Google Drive service."""
        if self._service is None:
            creds = self._Credentials.from_authorized_user_file(self.credentials_path)
            self._service = self._build("drive", "v3", credentials=creds)
        return self._service

    def upload_session(
        self, session_file: str, folder_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload session file to Google Drive.

        Args:
            session_file: Path to session file to upload
            folder_id: Optional Google Drive folder ID to upload to

        Returns:
            File ID of uploaded file, or None if failed

        Example:
            >>> file_id = gdrive.upload_session('session.json', folder_id='abc123')
        """
        if not os.path.exists(session_file):
            print(f"Session file not found: {session_file}")
            return None

        try:
            service = self._get_service()

            file_metadata = {"name": os.path.basename(session_file)}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = self._MediaFileUpload(session_file, resumable=True)
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            file_id = file.get("id")
            print(f"Uploaded {session_file} to Google Drive: {file_id}")
            return file_id

        except Exception as e:
            print(f"Failed to upload to Google Drive: {e}")
            return None

    def auto_backup(
        self,
        data_dir: str,
        folder_id: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
    ) -> int:
        """
        Automatically backup all session files in a directory.

        Args:
            data_dir: Directory containing session files
            folder_id: Optional Google Drive folder ID
            file_extensions: List of file extensions to backup (default: ['.json', '.csv'])

        Returns:
            Number of files successfully uploaded

        Example:
            >>> count = gdrive.auto_backup('./data/', folder_id='abc123')
            >>> print(f"Backed up {count} files")
        """
        if not os.path.exists(data_dir):
            print(f"Data directory not found: {data_dir}")
            return 0

        if file_extensions is None:
            file_extensions = [".json", ".csv"]

        uploaded_count = 0

        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)

            # Check if file has valid extension
            if any(filename.endswith(ext) for ext in file_extensions):
                if os.path.isfile(file_path):
                    file_id = self.upload_session(file_path, folder_id)
                    if file_id:
                        uploaded_count += 1

        return uploaded_count


class DropboxIntegration:
    """
    Dropbox integration for backing up telemetry data.

    This class provides methods to upload files to Dropbox
    and manage automatic backups of telemetry sessions.

    Args:
        access_token: Dropbox access token

    Example:
        >>> dropbox = DropboxIntegration(access_token='...')
        >>> dropbox.upload_file('session.json', '/telemetry/session.json')

    Reference:
        https://www.dropbox.com/developers/documentation/python

    Note:
        Requires dropbox package to be installed.
        This is a minimal implementation that requires the package
        to be installed separately to avoid adding it as a core dependency.
    """

    def __init__(self, access_token: str):
        """
        Initialize Dropbox integration.

        Args:
            access_token: Dropbox access token

        Raises:
            ImportError: If dropbox package is not installed
        """
        try:
            import dropbox
            from dropbox.files import WriteMode

            self._dropbox = dropbox
            self._WriteMode = WriteMode
        except ImportError as e:
            raise ImportError(
                "dropbox package is required for Dropbox integration. "
                "Install it with: pip install dropbox"
            ) from e

        self.dbx = self._dropbox.Dropbox(access_token)

    def upload_file(
        self, local_path: str, dropbox_path: str, overwrite: bool = True
    ) -> bool:
        """
        Upload file to Dropbox.

        Args:
            local_path: Path to local file
            dropbox_path: Destination path in Dropbox (must start with '/')
            overwrite: Whether to overwrite existing files

        Returns:
            True if upload successful, False otherwise

        Example:
            >>> success = dropbox.upload_file(
            ...     'session.json',
            ...     '/telemetry/session.json'
            ... )
        """
        if not os.path.exists(local_path):
            print(f"Local file not found: {local_path}")
            return False

        try:
            with open(local_path, "rb") as f:
                mode = self._WriteMode.overwrite if overwrite else self._WriteMode.add
                self.dbx.files_upload(f.read(), dropbox_path, mode=mode)

            print(f"Uploaded {local_path} to Dropbox: {dropbox_path}")
            return True

        except Exception as e:
            print(f"Failed to upload to Dropbox: {e}")
            return False

    def auto_backup(
        self,
        data_dir: str,
        dropbox_folder: str = "/telemetry",
        file_extensions: Optional[List[str]] = None,
    ) -> int:
        """
        Automatically backup all session files to Dropbox.

        Args:
            data_dir: Directory containing session files
            dropbox_folder: Destination folder in Dropbox
            file_extensions: List of file extensions to backup (default: ['.json', '.csv'])

        Returns:
            Number of files successfully uploaded

        Example:
            >>> count = dropbox.auto_backup('./data/', '/telemetry')
            >>> print(f"Backed up {count} files")
        """
        if not os.path.exists(data_dir):
            print(f"Data directory not found: {data_dir}")
            return 0

        if file_extensions is None:
            file_extensions = [".json", ".csv"]

        uploaded_count = 0

        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)

            # Check if file has valid extension
            if any(filename.endswith(ext) for ext in file_extensions):
                if os.path.isfile(file_path):
                    dropbox_path = f"{dropbox_folder}/{filename}"
                    if self.upload_file(file_path, dropbox_path):
                        uploaded_count += 1

        return uploaded_count
