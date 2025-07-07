"""
Core classes for FastAPI SQLModel Generator.

This package contains the core classes that orchestrate the generation process:
- ProjectInitializer: Initialize new projects
- DomainManager: Manage domain creation and configuration
- LayerGenerator: Generate individual layers
- ProjectValidator: Validate configurations and domains
- SchemaProvider: Provide schemas and usage information
"""

from .initialize import ProjectInitializer
from .domain import DomainManager
from .layers import LayerGenerator
from .validator import ProjectValidator, ValidationResult
from .schema import SchemaProvider

__all__ = [
    "ProjectInitializer",
    "DomainManager", 
    "LayerGenerator",
    "ProjectValidator",
    "ValidationResult",
    "SchemaProvider"
]