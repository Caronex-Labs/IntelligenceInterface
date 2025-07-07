"""Type aliases for primitive types and file system interactions.

This module defines minimal type aliases for cases where Pydantic models
are not appropriate, focusing on primitive types and file system operations.
"""

from pathlib import Path
from typing import Any

# File system types
PathLike = str | Path

# Raw data types (before Pydantic validation)
JSONValue = str | int | float | bool | None | dict[str, Any] | list[Any]
YAMLContent = dict[str, Any]