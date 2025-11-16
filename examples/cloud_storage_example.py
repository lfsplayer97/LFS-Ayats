"""
Example: Using Cloud Storage Integration for Backups

This example demonstrates how to use the cloud storage integrations
to backup telemetry data to Google Drive or Dropbox.
"""

from src.integrations import GoogleDriveIntegration, DropboxIntegration


def google_drive_example():
    """
    Example of using Google Drive integration.

    Setup Instructions:
    1. Go to Google Cloud Console (console.cloud.google.com)
    2. Create a new project or select existing one
    3. Enable Google Drive API
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download credentials JSON file
    6. Run OAuth flow to get authorized user credentials
    7. Save to credentials.json in project root
    """
    try:
        print("Google Drive Integration Example")
        print("=" * 60)

        # Initialize Google Drive integration
        gdrive = GoogleDriveIntegration("./credentials.json")

        # Example 1: Upload a single session file
        print("\n1. Uploading single session file...")
        file_id = gdrive.upload_session(
            "./data/telemetry_session.json",
            folder_id=None,  # Optional: specify folder ID
        )
        if file_id:
            print(f"   ✓ Uploaded successfully! File ID: {file_id}")

        # Example 2: Auto-backup all files in data directory
        print("\n2. Auto-backup all session files...")
        count = gdrive.auto_backup(
            "./data/",
            folder_id=None,  # Optional: specify folder ID
            file_extensions=[".json", ".csv"],
        )
        print(f"   ✓ Backed up {count} files to Google Drive")

    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo use Google Drive integration, install:")
        print(
            "  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have credentials.json file set up.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def dropbox_example():
    """
    Example of using Dropbox integration.

    Setup Instructions:
    1. Go to Dropbox App Console (dropbox.com/developers/apps)
    2. Create a new app
    3. Generate an access token
    4. Use the access token in the integration
    """
    try:
        print("\n\nDropbox Integration Example")
        print("=" * 60)

        # Initialize Dropbox integration
        # Replace with your actual Dropbox access token
        dropbox = DropboxIntegration(access_token="YOUR_DROPBOX_ACCESS_TOKEN_HERE")

        # Example 1: Upload a single file
        print("\n1. Uploading single file...")
        success = dropbox.upload_file(
            "./data/telemetry_session.json", "/LFS-Ayats/telemetry_session.json"
        )
        if success:
            print("   ✓ Uploaded successfully!")

        # Example 2: Auto-backup all files
        print("\n2. Auto-backup all session files...")
        count = dropbox.auto_backup(
            "./data/", dropbox_folder="/LFS-Ayats", file_extensions=[".json", ".csv"]
        )
        print(f"   ✓ Backed up {count} files to Dropbox")

    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo use Dropbox integration, install:")
        print("  pip install dropbox")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def schedule_backup_example():
    """
    Example of scheduling automatic backups.

    This would typically run as a background task or cron job.
    """
    import time
    from datetime import datetime

    print("\n\nScheduled Backup Example")
    print("=" * 60)
    print("This would run as a background service...")
    print("(Press Ctrl+C to stop the simulation)\n")

    try:
        # Initialize your preferred cloud storage
        # gdrive = GoogleDriveIntegration('./credentials.json')

        backup_interval = 3600  # 1 hour in seconds

        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Running backup...")

            # Perform backup
            # count = gdrive.auto_backup('./data/')
            # print(f"[{current_time}] Backed up {count} files")

            print(f"[{current_time}] Next backup in {backup_interval} seconds\n")
            time.sleep(backup_interval)

    except KeyboardInterrupt:
        print("\nBackup service stopped.")


if __name__ == "__main__":
    # Run Google Drive example
    google_drive_example()

    # Run Dropbox example
    dropbox_example()

    # Uncomment to test scheduled backups
    # schedule_backup_example()
