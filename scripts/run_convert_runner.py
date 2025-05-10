#!/usr/bin/env python3
"""
Kantan CMS Content Converter
This script converts JSON data from the CMS into markdown files
It uses the convert_content.py Python file to perform the conversion
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv(dotenv_path=".env.local")

# Set default values if environment variables are not set
STORAGE_PATH = os.environ.get("KANTAN_STORAGE_PATH", "./tmp/")
REQUIRED_COLLECTIONS = os.environ.get("KANTAN_REQUIRED_COLLECTIONS", "")

# Remove trailing slash if present
STORAGE_PATH = STORAGE_PATH.rstrip("/")

# Get the first collection from the list (usually Blog)
FIRST_COLLECTION = REQUIRED_COLLECTIONS.split(",")[0] if REQUIRED_COLLECTIONS else ""

print("=====================================================")
print("🔄 Starting content conversion process")
print("=====================================================")
print(f"Using storage path: {STORAGE_PATH}")
print(f"Required collections: {REQUIRED_COLLECTIONS}")

# Check if the storage directory exists and contains the required data
storage_dir = Path(STORAGE_PATH)
if not storage_dir.exists():
    print(f"❌ Error: {STORAGE_PATH} directory not found")
    print("Please run get_from_cms_runner.py first to fetch data from the CMS")
    sys.exit(1)

first_collection_file = storage_dir / f"{FIRST_COLLECTION}.json"
if FIRST_COLLECTION and not first_collection_file.exists():
    print(f"❌ Error: {FIRST_COLLECTION}.json not found in {STORAGE_PATH} directory")
    print("Please run get_from_cms_runner.py first to fetch data from the CMS")
    sys.exit(1)

print("Converting JSON data to markdown files...")
print("This will create/update files in the content/blog directory...")

# Run the conversion script
try:
    # Import and run the conversion module
    import asyncio
    from scripts.convert_content import main

    asyncio.run(main())

    # Count the number of markdown files created
    blog_dir = Path("./content/blog")
    if blog_dir.exists():
        file_count = len(list(blog_dir.glob("*.md")))
        print("✅ Content conversion completed successfully")
        print(f"Created/updated {file_count} markdown files in content/blog directory")
    else:
        print("✅ Content conversion completed successfully")
        print("No markdown files were created in content/blog directory")
except Exception as e:
    print(f"❌ Error occurred during content conversion: {e}")
    sys.exit(1)

print("=====================================================")
