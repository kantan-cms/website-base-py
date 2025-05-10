#!/bin/bash

# Kantan CMS Build Script (Python Version)
# This script automates the process of fetching data from Kantan CMS,
# converting it to the appropriate format, and deploying the site.
# This version uses the Python implementations of the scripts.

echo "====================================================="
echo "🚀 Starting Kantan CMS build process (Python version)"
echo "====================================================="

# Step 1: Fetch data from Kantan CMS API
echo "📥 Step 1/4: Fetching data from Kantan CMS..."
python ./scripts/get_from_cms_runner.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to fetch data from CMS"
    exit 1
fi
echo "✅ Data fetching completed successfully"
echo

# Step 2: Convert JSON data to markdown files
echo "🔄 Step 2/4: Converting content to markdown..."
python ./scripts/run_convert_runner.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to convert content"
    exit 1
fi
echo "✅ Content conversion completed successfully"
echo

# Step 3: Build the site with Bun
echo "🏗️ Step 3/4: Building the site with Bun..."
bun run build
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to build the site"
    exit 1
fi
echo "✅ Site build completed successfully"
echo

# Step 4: Create ZIP archive and deploy to hosting
echo "📤 Step 4/4: Packaging and deploying site..."
python ./scripts/zip_and_export_runner.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to package and deploy site"
    exit 1
fi
echo "✅ Deployment completed successfully"
echo

echo "====================================================="
echo "✨ Build process completed successfully!"
echo "====================================================="
