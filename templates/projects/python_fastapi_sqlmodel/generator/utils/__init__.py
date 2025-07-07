"""
Utility functions for the FastAPI SQLModel generator.

This module provides utilities for schema handling, formatting, template processing,
configuration processing, and common operations used across the generator.
"""

from .schema import (
    get_model_schema,
    format_schema_for_cli,
    format_schema_for_mcp,
    get_usage_examples,
    get_all_schemas,
    get_schema_by_name,
    get_sample_configs,
    SchemaFormatter
)

from .template_code_generator import (
    TemplateCodeGenerator
)

from .config_processor import (
    ConfigProcessor,
    ConfigProcessingError
)

from .type_aliases import (
    PathLike,
    JSONValue,
    YAMLContent
)

__all__ = [
    "get_model_schema",
    "format_schema_for_cli", 
    "format_schema_for_mcp",
    "get_usage_examples",
    "get_all_schemas",
    "get_schema_by_name", 
    "get_sample_configs",
    "SchemaFormatter",
    "TemplateCodeGenerator",
    "ConfigProcessor",
    "ConfigProcessingError",
    "PathLike",
    "JSONValue",
    "YAMLContent"
]
