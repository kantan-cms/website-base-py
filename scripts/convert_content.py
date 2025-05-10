"""
Content conversion script for Kantan CMS
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, TypeVar, cast

from scripts.config import converter_configs, exporter_configs, create_slug
from scripts.types import (
    ContentConverterConfig,
    ContentItem,
    ExportedItem,
    LatestItemsExporterConfig,
)

T = TypeVar("T")


def ensure_directory_exists(dir_path: str) -> None:
    """
    Ensures that the specified directory exists, creating it if necessary
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def read_json_file(file_path: str) -> List[Any]:
    """
    Reads and parses a JSON file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_frontmatter(item: ContentItem, config: List[Dict[str, Any]]) -> str:
    """
    Generates frontmatter for a markdown file based on configuration
    """
    frontmatter_lines = ["---"]

    for field in config:
        source_field = field["sourceField"]
        target_field = field["targetField"]
        formatter = field.get("formatter")
        required = field.get("required", False)

        if (
            source_field in item
            and item[source_field] is not None
            and item[source_field] != ""
        ):
            value = item[source_field]
            formatted_value = formatter(value) if formatter else value

            # Add quotes for string values
            if isinstance(formatted_value, str):
                formatted_value = f'"{formatted_value}"'

            frontmatter_lines.append(f"{target_field}: {formatted_value}")
        elif required:
            frontmatter_lines.append(f'{target_field}: ""')

    frontmatter_lines.append("---")
    frontmatter_lines.append("")
    return "\n".join(frontmatter_lines)


def process_content_item(
    item: ContentItem,
    target_dir: str,
    config: ContentConverterConfig,
    processed_slugs: Set[str],
) -> None:
    """
    Processes a single content item and converts it to the target format
    """
    # Create a slug from the specified field
    slug_field = config["slugField"]
    slug = create_slug(str(item.get(slug_field, "")))

    # Handle duplicate slugs by adding a unique identifier
    if slug in processed_slugs:
        # Add a short part of the ID to make it unique
        unique_id = item["id"][:8]
        slug = f"{slug}-{unique_id}"

    processed_slugs.add(slug)

    # Apply extractors to enrich the item with additional data
    for extractor_config in config["extractors"]:
        condition = extractor_config["condition"]
        if condition(item):
            field = extractor_config["field"]
            extractor = extractor_config["extractor"]
            item[field] = extractor(item)

    content_field = config["contentField"]
    output_format = config["outputFormat"]

    if output_format == "markdown":
        # Generate frontmatter
        frontmatter = generate_frontmatter(item, config["frontmatterFields"])

        # Combine frontmatter and content
        file_content = f"{frontmatter}\n{item.get(content_field, '')}"
        file_extension = "md"
    else:
        # For JSON output, create a JSON representation
        output_object: Dict[str, Any] = {}

        for field in config["frontmatterFields"]:
            source_field = field["sourceField"]
            target_field = field["targetField"]
            formatter = field.get("formatter")

            if source_field in item:
                value = item[source_field]
                output_object[target_field] = formatter(value) if formatter else value

        # Add the content field
        output_object["content"] = item.get(content_field, "")

        file_content = json.dumps(output_object, indent=2)
        file_extension = "json"

    target_path = os.path.join(target_dir, f"{slug}.{file_extension}")

    # Write to the target file
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    print(f"Converted: {target_path}")


async def convert_content(config: ContentConverterConfig) -> None:
    """
    Converts content items from JSON to the target format based on configuration
    """
    try:
        # Create target directory if it doesn't exist
        ensure_directory_exists(config["targetDir"])

        # Read the source JSON file
        source_path = os.path.abspath(config["sourceFile"])
        items = read_json_file(source_path)

        print(f"Found {len(items)} items to convert for {config['collectionName']}")

        # Keep track of processed slugs to handle duplicates
        processed_slugs: Set[str] = set()

        # Process each item
        for item in items:
            process_content_item(
                cast(ContentItem, item), config["targetDir"], config, processed_slugs
            )

        print(
            f"Content conversion completed successfully for {config['collectionName']}"
        )
    except Exception as error:
        print(f"Error converting content for {config['collectionName']}:", error)


async def export_latest_items(config: LatestItemsExporterConfig) -> None:
    """
    Exports the latest items to a Python file based on configuration
    """
    try:
        # Create directory for the target file if it doesn't exist
        target_dir = os.path.dirname(config["targetFile"])
        ensure_directory_exists(target_dir)

        # Read the source JSON file
        source_path = os.path.join(os.getcwd(), config["sourceFile"])
        items = read_json_file(source_path)

        print(f"Found {len(items)} items to extract latest from")

        # Sort items based on configuration
        sort_field = config["sortField"]
        sort_direction = config["sortDirection"]

        def sort_key(item: Dict[str, Any]) -> str:
            return str(item.get(sort_field, ""))

        sorted_items = sorted(items, key=sort_key, reverse=(sort_direction == "desc"))

        # Take the latest N items
        latest_items = sorted_items[: config["itemCount"]]

        # Format the items based on configuration
        formatted_items: List[ExportedItem] = []

        for item in latest_items:
            formatted_item = dict(config["defaultValues"])

            # Apply formatters to each field
            for field, formatter in config["formatters"].items():
                formatted_item[field] = formatter(cast(ContentItem, item))

            formatted_items.append(cast(ExportedItem, formatted_item))

        # Create the Python file content
        py_content = f"""# Auto-generated from {config['sourceFile']}
# Last updated: {datetime.now().isoformat()}

from typing import List, TypedDict

class {config['interfaceName']}(TypedDict):
"""

        # Add type hints for each field
        if formatted_items:
            first_item = formatted_items[0]
            for key, value in first_item.items():
                type_name = type(value).__name__
                if type_name == "str":
                    type_hint = "str"
                elif type_name == "int":
                    type_hint = "int"
                elif type_name == "float":
                    type_hint = "float"
                elif type_name == "bool":
                    type_hint = "bool"
                elif type_name == "list":
                    type_hint = "list"
                elif type_name == "dict":
                    type_hint = "dict"
                else:
                    type_hint = "Any"

                py_content += f"    {key}: {type_hint}\n"

        py_content += f"\n\n{config['exportName']}: List[{config['interfaceName']}] = {json.dumps(formatted_items, indent=2)}\n"

        # Write to the target file
        with open(config["targetFile"], "w", encoding="utf-8") as f:
            f.write(py_content)

        print(f"Exported latest items to: {config['targetFile']}")

    except Exception as error:
        print("Error exporting latest items:", error)


async def main() -> None:
    """
    Execute the conversion and extraction
    """
    try:
        # Process all converter configurations
        for config in converter_configs:
            await convert_content(config)

        # Process all exporter configurations
        for config in exporter_configs:
            await export_latest_items(config)

        print("All conversions completed successfully")
    except Exception as error:
        print("Error during content conversion:", error)


if __name__ == "__main__":
    import asyncio
    from datetime import datetime

    asyncio.run(main())
