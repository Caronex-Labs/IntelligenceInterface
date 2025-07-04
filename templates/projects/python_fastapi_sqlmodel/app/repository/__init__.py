"""Repository Layer - Async Database Access with SQLModel

This module provides the repository layer for the hexagonal architecture,
implementing async database operations with PostgreSQL and SQLModel.

Repository Pattern Implementation:
- Async/await database operations
- CRUD operations for all entities
- Custom query methods with business logic
- Transaction management and error handling
- Connection pooling and session management

Architecture:
- Repository protocols define interfaces
- SQLModel implementations provide concrete repositories
- Dependency injection for use case integration
- @pyhex markers for custom query extensions
"""

# @pyhex:begin:custom_repository_imports
# Add custom repository imports here - preserved during regeneration
# @pyhex:end:custom_repository_imports

__version__ = "1.0.0"
__all__ = [
    # Repository base classes and utilities will be exported here
    # Individual domain repositories will be added during generation
    
    # @pyhex:begin:custom_repository_exports
    # Add custom repository exports here - preserved during regeneration
    # @pyhex:end:custom_repository_exports
]