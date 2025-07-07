"""{{domain|title}} Repository Module - Co-location Architecture

This module provides complete repository layer implementation for {{domain|title}} domain
with async database operations, CRUD functionality, and custom query methods.

Repository Components:
- SQLModel{{domain|title}}Repository: Main repository implementation
- {{domain|title}}RepositoryProtocol: Repository interface protocol
- {{domain|title}}QueryBuilder: Advanced query building utilities
- Repository exceptions and error handling

Generated from repository templates with co-location pattern.
"""

# @pyhex:begin:custom_repository_module_imports
# Add custom repository module imports here - preserved during regeneration
# @pyhex:end:custom_repository_module_imports

from .protocols import (
    {{domain|title}}RepositoryProtocol,
    {{domain|title}}QueryBuilderProtocol,
    {% if repository.caching.enabled %}{{domain|title}}CacheProtocol,{% endif %}
)

from .repository import (
    SQLModel{{domain|title}}Repository,
    {{domain|title}}QueryBuilder,
    {{domain|title}}RepositoryError,
    {{domain|title}}NotFoundError,
    {{domain|title}}DuplicateError,
    {{domain|title}}ValidationError,
)

# @pyhex:begin:custom_repository_module_exports
# Add custom repository module exports here - preserved during regeneration
# @pyhex:end:custom_repository_module_exports

__all__ = [
    # Repository protocols
    "{{domain|title}}RepositoryProtocol",
    "{{domain|title}}QueryBuilderProtocol",
    {% if repository.caching.enabled %}"{{domain|title}}CacheProtocol",{% endif %}
    
    # Repository implementations
    "SQLModel{{domain|title}}Repository",
    "{{domain|title}}QueryBuilder",
    
    # Repository exceptions
    "{{domain|title}}RepositoryError",
    "{{domain|title}}NotFoundError", 
    "{{domain|title}}DuplicateError",
    "{{domain|title}}ValidationError",
    
    # @pyhex:begin:custom_repository_module_all
    # Add custom repository module exports here - preserved during regeneration
    # @pyhex:end:custom_repository_module_all
]