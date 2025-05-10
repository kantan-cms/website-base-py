#!/usr/bin/env python3
"""
Kantan CMS ZIP and Export Runner
This script creates a ZIP archive of static output and uploads it to Kantan CMS
It uses the zip_and_export.py Python file to perform the operations
"""
import sys

print("Starting ZIP creation and upload process...")

# Run the export script
try:
    print("Creating ZIP archive of static output...")
    from scripts.zip_and_export import deploy_to_kantan

    # Check if --preview flag is provided
    is_preview = "--preview" in sys.argv

    # Run the deployment function
    deploy_to_kantan(is_preview)

    print("✅ ZIP creation and upload process completed successfully.")
except Exception as e:
    print(f"❌ Error occurred during ZIP creation or upload: {e}")
    sys.exit(1)
