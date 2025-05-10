"""
Types for the content conversion system
"""
from typing import Any, Callable, Dict, List, Optional, Protocol, TypedDict


# Base content item type
class ContentItem(TypedDict, total=False):
    id: str
    # Additional fields can be any type
    # Python's TypedDict doesn't support index signatures directly like TypeScript's [key: string]: unknown
    # But total=False allows for optional fields


# Exported item type
class ExportedItem(TypedDict, total=False):
    # Can have any fields of any type
    pass


# Type for formatter functions
class FormatterProtocol(Protocol):
    def __call__(self, value: Any) -> str:
        ...


# Type for extractor functions
class ExtractorProtocol(Protocol):
    def __call__(self, item: ContentItem) -> str:
        ...


# Type for condition functions
class ConditionProtocol(Protocol):
    def __call__(self, item: ContentItem) -> bool:
        ...


# Frontmatter field configuration
class FrontmatterFieldConfig(TypedDict, total=False):
    sourceField: str
    targetField: str
    formatter: Optional[FormatterProtocol]
    required: Optional[bool]


# Extractor configuration
class ExtractorConfig(TypedDict):
    field: str
    extractor: ExtractorProtocol
    condition: ConditionProtocol


# Content converter configuration
class ContentConverterConfig(TypedDict):
    # Collection information
    collectionName: str  # Name of the collection (e.g., 'Blog', 'Project')

    # File paths
    sourceFile: str  # Path to the source JSON file
    targetDir: str  # Directory where converted files will be stored

    # Content mapping
    slugField: str  # Field to use for generating the slug
    contentField: str  # Field containing the main content

    # Output configuration
    outputFormat: str  # 'markdown' or 'json'

    # Field mappings and transformations
    frontmatterFields: List[FrontmatterFieldConfig]
    extractors: List[ExtractorConfig]


# Latest items exporter configuration
class LatestItemsExporterConfig(TypedDict):
    # Source and target
    sourceFile: str
    targetFile: str

    # Selection and sorting
    itemCount: int
    sortField: str
    sortDirection: str  # 'asc' or 'desc'

    # Formatting and defaults
    formatters: Dict[str, Callable[[ContentItem], Any]]
    defaultValues: Dict[str, Any]

    # Output TypeScript configuration
    interfaceName: str
    exportName: str
