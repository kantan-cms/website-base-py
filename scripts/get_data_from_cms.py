"""
Script to fetch data from Kantan CMS API
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, cast

import requests
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv(dotenv_path=".env.local")

# Debug environment variables
print("Environment variables:")
print("PROJECT_ID:", os.environ.get("PROJECT_ID"))
print("CMS_API_KEY:", "(set)" if os.environ.get("CMS_API_KEY") else "(not set)")
print("KANTAN_REQUIRED_COLLECTIONS:", os.environ.get("KANTAN_REQUIRED_COLLECTIONS"))
print("KANTAN_STORAGE_PATH:", os.environ.get("KANTAN_STORAGE_PATH"))


# Configuration
class KantanConfig(TypedDict):
    project_id: str
    api_key: str
    base_url: str
    required_collections: List[str]
    storage_path: str


config: KantanConfig = {
    "project_id": os.environ.get("PROJECT_ID", ""),
    "api_key": os.environ.get("CMS_API_KEY", ""),
    "base_url": f"{os.environ.get('CMS_BASE_URL')}/v1/api",
    "required_collections": os.environ.get("KANTAN_REQUIRED_COLLECTIONS", "").split(",")
    if os.environ.get("KANTAN_REQUIRED_COLLECTIONS")
    else [],
    "storage_path": os.environ.get("KANTAN_STORAGE_PATH", "./tmp/"),
}


# Interfaces for API responses
class Collection(TypedDict):
    id: str
    name: str
    description: Optional[str]
    type: str
    order: Optional[int]
    created_at: str
    updated_at: str


class CollectionsResponse(TypedDict):
    collections: List[Collection]


class CollectionCountResponse(TypedDict):
    count: int


class Record(TypedDict, total=False):
    id: str
    # Additional fields can be any type


class RecordsResponse(TypedDict):
    records: List[Record]


class RecordCountResponse(TypedDict):
    count: int


class ApiValidationResponse(TypedDict):
    status: int


# Create a session with authentication headers
session = requests.Session()
session.headers.update(
    {
        "X-Project-Id": config["project_id"],
        "X-API-Key": config["api_key"],
        "Content-Type": "application/json",
    }
)


def validate_api_key() -> bool:
    """
    Validates the API key and project ID
    """
    try:
        print("Validating API credentials...")

        # Check if credentials are provided
        if not config["project_id"]:
            print("❌ Project ID is missing.")
            return False

        if not config["api_key"]:
            print("❌ API Key is missing.")
            return False

        print(f"Project ID: {config['project_id']}")
        api_key = config["api_key"]
        masked_key = f"{api_key[:4]}{'*' * max(0, len(api_key) - 4)}"
        print(f"API Key: {masked_key}")
        print(f"API Base URL: {config['base_url']}")

        response = session.get(f"{config['base_url']}/api_key/validate")
        response.raise_for_status()
        data = response.json()
        print("API Response:", data)
        return data["status"] == 200
    except requests.RequestException as error:
        print("API key validation failed:")
        if error.response is not None:
            print(f"Status: {error.response.status_code}")
            print(f"Message: {error}")
            print(f"Response data: {error.response.text}")
        else:
            print(f"Error: {error}")
        return False


def count_collections() -> int:
    """
    Counts the total number of collections
    """
    try:
        response = session.get(f"{config['base_url']}/collections_count/")
        response.raise_for_status()
        data = response.json()
        return data["count"]
    except requests.RequestException as error:
        print("Error counting collections:", error)
        return 0


def get_collections() -> List[Collection]:
    """
    Retrieves all collections with pagination
    """
    try:
        count = count_collections()
        page_size = 100
        pages = (count + page_size - 1) // page_size  # Ceiling division

        all_collections: List[Collection] = []

        for page in range(1, pages + 1):
            response = session.get(
                f"{config['base_url']}/collections/?page_size={page_size}&page_num={page}"
            )
            response.raise_for_status()
            data = response.json()

            all_collections.extend(data["collections"])

        # Filter collections if required
        if config["required_collections"]:
            return [
                collection
                for collection in all_collections
                if collection["name"] in config["required_collections"]
            ]

        return all_collections
    except requests.RequestException as error:
        print("Error retrieving collections:", error)
        return []


def count_records(collection_id: str) -> int:
    """
    Counts the total number of records in a collection
    """
    try:
        response = session.get(
            f"{config['base_url']}/collections/{collection_id}/records_count/"
        )
        response.raise_for_status()
        data = response.json()
        return data["count"]
    except requests.RequestException as error:
        print(f"Error counting records for collection {collection_id}:", error)
        return 0


def get_records(collection: Collection) -> List[Record]:
    """
    Retrieves all records from a collection with pagination
    """
    try:
        count = count_records(collection["id"])
        page_size = 100
        pages = (count + page_size - 1) // page_size  # Ceiling division

        all_records: List[Record] = []

        for page in range(1, pages + 1):
            response = session.get(
                f"{config['base_url']}/collections/{collection['id']}/records/?page_size={page_size}&page_num={page}"
            )
            response.raise_for_status()
            data = response.json()

            all_records.extend(data["records"])

        # Save records to file
        save_records_to_file(collection, all_records)

        return all_records
    except requests.RequestException as error:
        print(f"Error retrieving records for collection {collection['id']}:", error)
        return []


def save_records_to_file(collection: Collection, records: List[Record]) -> None:
    """
    Saves records to a JSON file
    """
    try:
        # Ensure directory exists
        storage_path = Path(config["storage_path"])
        storage_path.mkdir(parents=True, exist_ok=True)

        # Write to file
        file_path = storage_path / f"{collection['name']}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

        print(f"✓ Saved {len(records)} records for collection \"{collection['name']}\"")
    except Exception as error:
        print(f"Error saving records for collection {collection['name']}:", error)


def fetch_all_data() -> None:
    """
    Main function to fetch all data
    """
    print("Starting Kantan CMS data fetch...")

    # Validate API key
    is_valid = validate_api_key()

    if not is_valid:
        print("❌ API validation failed. Check your projectId and apiKey.")
        return

    print("✓ API credentials validated")

    # Get collections
    collections = get_collections()

    if not collections:
        print("❌ No collections found or matching requirements.")
        return

    print(f"✓ Found {len(collections)} collections")

    # Process each collection
    for collection in collections:
        print(f"Processing collection: {collection['name']} ({collection['id']})")
        records = get_records(collection)
        print(
            f"✓ Processed {len(records)} records for collection \"{collection['name']}\""
        )

    print("✓ All data fetched successfully")


if __name__ == "__main__":
    try:
        fetch_all_data()
    except Exception as error:
        print("Error in main execution:", error)
        exit(1)
