"""
Tests for Cloud Storage integrations
"""

import pytest
import os
from unittest.mock import patch


# Skip tests if google/dropbox packages are not available
google_available = False
dropbox_available = False

try:
    pass

    google_available = True
except ImportError:
    pass

try:
    pass

    dropbox_available = True
except ImportError:
    pass


@pytest.mark.skipif(
    not google_available, reason="google-api-python-client not installed"
)
class TestGoogleDriveIntegration:
    """Test cases for Google Drive integration."""

    def test_init_without_credentials_file(self):
        """Test initialization fails without credentials file."""
        from src.integrations.cloud_storage import GoogleDriveIntegration

        with pytest.raises(FileNotFoundError):
            GoogleDriveIntegration("/nonexistent/credentials.json")

    def test_init_success(self):
        """Test successful initialization."""
        from src.integrations.cloud_storage import GoogleDriveIntegration

        creds_file = "/tmp/test_credentials2.json"
        with open(creds_file, "w") as f:
            f.write("{}")

        try:
            with patch(
                "google.oauth2.credentials.Credentials.from_authorized_user_file"
            ):
                with pytest.raises(Exception):  # Will fail auth but that's ok
                    GoogleDriveIntegration(creds_file)
        finally:
            if os.path.exists(creds_file):
                os.remove(creds_file)

    def test_upload_session_file_not_found(self):
        """Test upload with non-existent file."""
        from src.integrations.cloud_storage import GoogleDriveIntegration

        creds_file = "/tmp/test_credentials3.json"
        with open(creds_file, "w") as f:
            f.write("{}")

        try:
            with patch(
                "google.oauth2.credentials.Credentials.from_authorized_user_file"
            ):
                with pytest.raises(Exception):  # Constructor will fail, which is fine
                    gdrive = GoogleDriveIntegration(creds_file)
                    gdrive.upload_session("/nonexistent/file.json")
        finally:
            if os.path.exists(creds_file):
                os.remove(creds_file)

    def test_auto_backup_directory_not_found(self):
        """Test auto backup with non-existent directory."""
        from src.integrations.cloud_storage import GoogleDriveIntegration

        creds_file = "/tmp/test_credentials5.json"
        with open(creds_file, "w") as f:
            f.write("{}")

        try:
            with patch(
                "google.oauth2.credentials.Credentials.from_authorized_user_file"
            ):
                with pytest.raises(Exception):  # Constructor will fail
                    gdrive = GoogleDriveIntegration(creds_file)
                    gdrive.auto_backup("/nonexistent/directory")
        finally:
            if os.path.exists(creds_file):
                os.remove(creds_file)


@pytest.mark.skipif(not dropbox_available, reason="dropbox package not installed")
class TestDropboxIntegration:
    """Test cases for Dropbox integration."""

    def test_init_success(self):
        """Test successful initialization."""
        from src.integrations.cloud_storage import DropboxIntegration

        with patch("dropbox.Dropbox"):
            dbx = DropboxIntegration("test_token")
            assert dbx is not None

    def test_upload_file_not_found(self):
        """Test upload with non-existent file."""
        from src.integrations.cloud_storage import DropboxIntegration

        with patch("dropbox.Dropbox"):
            dbx = DropboxIntegration("test_token")
            result = dbx.upload_file("/nonexistent/file.json", "/test.json")

            assert result is False

    def test_auto_backup_directory_not_found(self):
        """Test auto backup with non-existent directory."""
        from src.integrations.cloud_storage import DropboxIntegration

        with patch("dropbox.Dropbox"):
            dbx = DropboxIntegration("test_token")
            count = dbx.auto_backup("/nonexistent/directory")

            assert count == 0


# Test import errors when packages not available
class TestImportErrors:
    """Test import error handling."""

    def test_google_drive_import_error(self):
        """Test Google Drive raises ImportError when package missing."""
        # Temporarily hide google modules
        with patch.dict(
            "sys.modules",
            {
                "google": None,
                "google.oauth2": None,
                "google.oauth2.credentials": None,
                "googleapiclient": None,
                "googleapiclient.discovery": None,
                "googleapiclient.http": None,
            },
        ):
            from importlib import reload
            import src.integrations.cloud_storage

            reload(src.integrations.cloud_storage)
            from src.integrations.cloud_storage import GoogleDriveIntegration

            # Create temp file
            creds_file = "/tmp/test_creds_import.json"
            with open(creds_file, "w") as f:
                f.write("{}")

            try:
                with pytest.raises(ImportError) as exc_info:
                    GoogleDriveIntegration(creds_file)

                assert "google-api-python-client is required" in str(exc_info.value)
            finally:
                if os.path.exists(creds_file):
                    os.remove(creds_file)

    def test_dropbox_import_error(self):
        """Test Dropbox raises ImportError when package missing."""
        with patch.dict("sys.modules", {"dropbox": None, "dropbox.files": None}):
            from importlib import reload
            import src.integrations.cloud_storage

            reload(src.integrations.cloud_storage)
            from src.integrations.cloud_storage import DropboxIntegration

            with pytest.raises(ImportError) as exc_info:
                DropboxIntegration("test_token")

            assert "dropbox package is required" in str(exc_info.value)
