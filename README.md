# Kantan CMS Python Scripts

This directory contains Python versions of the TypeScript scripts used for interacting with Kantan CMS.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have a `.env.local` file in the project root with the necessary environment variables:

```
PROJECT_ID=your_project_id
CMS_API_KEY=your_api_key
CMS_BASE_URL=https://api-dev.kantan-cms.com
KANTAN_REQUIRED_COLLECTIONS=Blog
KANTAN_STORAGE_PATH=./tmp
STATIC_OUTPUT_DIR=./out
ZIP_FILENAME=site-export.zip
```

## Build
To build the project, run the following command:

```bash
bash build.sh
```

## Available Scripts

### 1. Fetch Data from CMS

Fetches data from the Kantan CMS API and saves it to JSON files.

```bash
./scripts/get_from_cms_runner.py
```

### 2. Convert Content

Converts JSON data from the CMS into markdown files.

```bash
./scripts/run_convert_runner.py
```

### 3. Zip and Export

Creates a ZIP archive of static output and uploads it to Kantan CMS.

```bash
./scripts/zip_and_export_runner.py
```

To deploy to preview instead of production:

```bash
./scripts/zip_and_export_runner.py --preview
```

## Module Structure

- `types.py` - Type definitions
- `config.py` - Configuration settings and utility functions
- `convert_content.py` - Content conversion functionality
- `get_data_from_cms.py` - API client for fetching data from Kantan CMS
- `zip_and_export.py` - Functionality for zipping and exporting static output
- Runner scripts (`*_runner.py`) - Command-line interfaces for the modules
