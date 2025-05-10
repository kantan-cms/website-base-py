"""
Script to zip and export static output to Kantan CMS
"""
import os
import sys
import zipfile
from pathlib import Path
from typing import Dict, Literal, TypedDict, Union

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env.local")


# Configuration
class KantanConfig(TypedDict):
    project_id: str
    api_key: str
    base_url: str
    static_output_dir: str
    zip_filename: str


config: KantanConfig = {
    "project_id": os.environ.get("PROJECT_ID", ""),
    "api_key": os.environ.get("CMS_API_KEY", ""),
    "base_url": os.environ.get("CMS_BASE_URL", ""),
    "static_output_dir": os.environ.get("STATIC_OUTPUT_DIR", "./out"),
    "zip_filename": os.environ.get("ZIP_FILENAME", "site-export.zip"),
}


# API response types
class PresignedZipUrl(TypedDict):
    url: str


class PresignedZipResponse(TypedDict):
    presigned_zip: PresignedZipUrl


class HostingStatus(TypedDict):
    status: Literal[
        "host_error",
        "preview_error",
        "host_complete",
        "preview_complete",
        "waiting",
        "running",
    ]
    status_message: str


class UpdateHostingStatusReq(TypedDict):
    hosting: HostingStatus


# Create a session with authentication headers
session = requests.Session()
session.headers.update(
    {
        "X-Project-Id": config["project_id"],
        "X-API-Key": config["api_key"],
        "Content-Type": "application/json",
    }
)


def create_zip_archive(output_path: str, source_dir: str) -> str:
    """
    Creates a ZIP archive of the static output directory
    """
    print(f"Creating ZIP archive of {source_dir}...")

    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory {source_dir} does not exist")

    # Create the ZIP file
    with zipfile.ZipFile(
        output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zipf:
        source_path = Path(source_dir)

        # Walk through the directory and add all files
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate the relative path for the archive
                rel_path = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, rel_path)

    # Get the size of the created ZIP file
    zip_size = os.path.getsize(output_path)
    print(f"✓ Archive created: {output_path} ({zip_size} bytes)")

    return output_path


def get_presigned_url() -> str:
    """
    Requests a presigned URL for uploading the ZIP archive
    """
    try:
        response = session.post(
            f"{config['base_url']}/v1/api/hosting/build/upload_presigned_url/"
        )
        response.raise_for_status()
        data = response.json()
        return data["presigned_zip"]["url"]
    except requests.RequestException as error:
        print("Error getting presigned URL:", error)
        raise Exception("Failed to get presigned URL for upload")


def upload_zip_to_presigned_url(zip_path: str, presigned_url: str) -> bool:
    """
    Uploads the ZIP archive to the presigned URL
    """
    try:
        with open(zip_path, "rb") as file:
            file_size = os.path.getsize(zip_path)

            response = requests.put(
                presigned_url,
                data=file,
                headers={
                    "Content-Type": "application/zip",
                    "Content-Length": str(file_size),
                },
            )

            response.raise_for_status()
            return response.status_code == 200
    except requests.RequestException as error:
        print("Error uploading ZIP file:", error)
        raise Exception("Failed to upload ZIP file")


def update_hosting_status(
    status: Literal["host_complete", "preview_complete"], message: str
) -> bool:
    """
    Updates the hosting status after upload
    """
    try:
        request_body: UpdateHostingStatusReq = {
            "hosting": {"status": status, "status_message": message}
        }

        response = session.post(
            f"{config['base_url']}/v1/api/hosting/status/", json=request_body
        )
        response.raise_for_status()
        return response.status_code == 200
    except requests.RequestException as error:
        print("Error updating hosting status:", error)
        raise Exception("Failed to update hosting status")


def deploy_to_kantan(is_preview: bool = False) -> None:
    """
    Main deployment function
    """
    try:
        print("Starting deployment to Kantan CMS...")

        # 1. Create ZIP archive of the static output
        zip_path = os.path.abspath(config["zip_filename"])
        create_zip_archive(zip_path, config["static_output_dir"])

        # 2. Get presigned URL for upload
        print("Requesting presigned upload URL...")
        presigned_url = get_presigned_url()
        print("✓ Received presigned URL")
        print("presignedUrl", presigned_url)

        # 3. Upload the ZIP file
        print("Uploading ZIP archive...")
        upload_success = upload_zip_to_presigned_url(zip_path, presigned_url)
        print("uploadSuccess", upload_success)
        print("✓ Upload completed successfully")

        # 4. Update the hosting status
        status_type = "preview_complete" if is_preview else "host_complete"
        status_message = (
            "Preview deployment complete"
            if is_preview
            else "Production deployment complete"
        )

        print(f"Updating hosting status to {status_type}...")
        status_update_success = update_hosting_status(status_type, status_message)
        print("✓ Status updated successfully")

        # 5. Clean up the ZIP file
        os.remove(zip_path)
        print("✓ Cleaned up temporary ZIP file")

        print("✓ Deployment to Kantan CMS completed successfully")
        print(
            f"{'Preview' if is_preview else 'Production'} site will be available shortly"
        )
    except Exception as error:
        print("Deployment failed:", error)
        sys.exit(1)


if __name__ == "__main__":
    # Parse command line arguments
    is_preview = "--preview" in sys.argv

    try:
        deploy_to_kantan(is_preview)
    except Exception as error:
        print("Unhandled error during deployment:", error)
        sys.exit(1)
