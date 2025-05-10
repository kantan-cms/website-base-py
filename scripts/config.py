"""
Configuration for the content conversion system
"""
import os
import pathlib
from datetime import datetime
from typing import List

from dotenv import load_dotenv

from scripts.types import ContentConverterConfig, LatestItemsExporterConfig

# Load environment variables from .env.local file
load_dotenv(dotenv_path=".env.local")

# Get environment variables with defaults
STORAGE_PATH = os.environ.get("KANTAN_STORAGE_PATH", str(pathlib.Path("..") / "tmp"))
REQUIRED_COLLECTIONS = (
    os.environ.get("KANTAN_REQUIRED_COLLECTIONS", "Blog").split(",")
    if os.environ.get("KANTAN_REQUIRED_COLLECTIONS")
    else ["Blog"]
)


def format_date_to_iso(date_string: str) -> str:
    """
    Formats a date string to YYYY-MM-DD format
    """
    date_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    return date_obj.date().isoformat()  # YYYY-MM-DD format


# Configuration Objects
# Array of content converter configurations for different content types
converter_configs: List[ContentConverterConfig] = [
    # Blog converter configuration
    {
        "collectionName": REQUIRED_COLLECTIONS[0],
        "sourceFile": str(
            pathlib.Path(STORAGE_PATH) / f"{REQUIRED_COLLECTIONS[0]}.json"
        ),
        "targetDir": str(pathlib.Path("docs") / "docs"),
        "slugField": "fname",
        "contentField": "content",
        "outputFormat": "markdown",
        "frontmatterFields": [
            {"sourceField": "name", "targetField": "title", "required": True},
            {
                "sourceField": "date",
                "targetField": "date",
                "formatter": format_date_to_iso,
                "required": True,
            },
            {"sourceField": "order", "targetField": "order"},
        ],
        "extractors": [],
    },
]

# Array of latest items exporter configurations
exporter_configs: List[LatestItemsExporterConfig] = []


def create_slug(text: str) -> str:
    """
    Creates a URL-friendly slug from a string
    """
    # Convert to lowercase
    slug = text.lower()
    # Remove special characters
    slug = "".join(c for c in slug if c.isalnum() or c.isspace() or c == "-")
    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")
    # Replace multiple hyphens with single hyphen
    while "--" in slug:
        slug = slug.replace("--", "-")
    # Trim leading/trailing hyphens
    return slug.strip("-")
