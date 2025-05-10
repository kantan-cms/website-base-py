#!/usr/bin/env python3
"""
Kantan CMS Data Fetcher
This script fetches data from the Kantan CMS API and saves it to JSON files
It uses the get_data_from_cms.py Python file to perform the API calls
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv(dotenv_path=".env.local")

# Set default values if environment variables are not set
STORAGE_PATH = os.environ.get("KANTAN_STORAGE_PATH", "./tmp/")

# Remove trailing slash if present
STORAGE_PATH = STORAGE_PATH.rstrip("/")

print("=====================================================")
print("📥 Starting Kantan CMS data fetching process")
print("=====================================================")
print(f"Using storage path: {STORAGE_PATH}")

# Check if the storage directory exists, create it if not
storage_dir = Path(STORAGE_PATH)
if not storage_dir.exists():
    print(f"Creating {STORAGE_PATH} directory for storing fetched data...")
    storage_dir.mkdir(parents=True, exist_ok=True)

print("Fetching data from Kantan CMS API...")
print("This may take a moment depending on the amount of data...")

# Run the data fetching script
try:
    # Import and run the data fetching module
    from scripts.get_data_from_cms import fetch_all_data

    fetch_all_data()

    print("✅ Data fetching completed successfully")
    print(f"Data has been saved to the {STORAGE_PATH} directory")
except Exception as e:
    print(f"❌ Error occurred during data fetching: {e}")
    sys.exit(1)

print("=====================================================")
