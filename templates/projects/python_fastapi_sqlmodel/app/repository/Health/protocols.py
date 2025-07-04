"""Health Repository Protocols - Co-location Architecture

This module defines the repository interfaces and protocols for Health data access operations.
These protocols ensure clean separation between business logic and data persistence,
supporting dependency injection, testing, and multiple implementation strategies.

Generated from: app/repository/Health/protocols.py.j2
Configuration: app/repository/Health/repository.yaml
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime

# @pyhex:begin:custom_protocol_imports
# Add custom protocol imports here - preserved during regeneration
# @pyhex:end:custom_protocol_imports

from app.domain.Health.entities import HealthCheck


class HealthCheckRepositoryProtocol(ABC):
    """
    Protocol for HealthCheck repository data access operations.
    
    This protocol defines the interface for all HealthCheck data operations,
    ensuring consistent implementation across different repository implementations.
    
    Repository Features:
    - Async database operations with PostgreSQL
    - Full CRUD operations with business validation
    - Custom query methods for complex data access
    - Transaction management and error handling
    - Connection pooling and session management
    
    CRUD Operations:
    - create: Create new Health with validation
    - get_by_id: Retrieve Health by unique identifier
    - update: Update existing Health with partial support
    - delete: Soft delete Health
    - list: Paginated listing with filtering and sorting
    
    Query Methods:
- find_by_id: Find Health by unique identifier
- find_by_email: Find Health by email address
- find_active_entities: Find all active Health entities
- find_by_status: Find Health entities by status
- count_by_status: Count Health entities by status
- search_by_name: Search Health entities by name using full-text search
    """

    # @pyhex:begin:custom_protocol_attributes
    # Add custom protocol attributes here - preserved during regeneration
    # @pyhex:end:custom_protocol_attributes

    # CRUD Operations
@abstractmethod
    async def create(
        self,
        entity: Health,
        *,
        validate: bool = True,
        return_created: bool = True
    ) -> Health:
        """
        Create a new Health entity in the database.
        
        Args:
            entity: Health entity to create
            validate: Whether to run business validation
            return_created: Whether to return the created entity with generated fields
            
        Returns:
            Health: Created entity with generated ID and timestamps
            
        Raises:
            HealthValidationError: When entity validation fails
            HealthDuplicateError: When entity violates unique constraints
            DatabaseError: When database operation fails
        """
        ...

@abstractmethod
    async def get_by_id(
        self,
        entity_id: UUID,
        *,
        include_deleted: bool = False,
        eager_load: Optional[List[str]] = None
    ) -> Optional[Health]:
        """
        Retrieve Health entity by unique identifier.
        
        Args:
            entity_id: Unique identifier of the Health
            include_deleted: Whether to include soft-deleted entities
            eager_load: List of relationships to eager load
            
        Returns:
            Optional[Health]: Found entity or None if not found
            
        Raises:
            DatabaseError: When database operation fails
        """
        ...


@abstractmethod
    async def delete(
        self,
        entity_id: UUID,
        *,
        soft_delete: bool = True,
        cascade: bool = True
    ) -> bool:
        """
        Delete Health entity from the database.
        
        Args:
            entity_id: Unique identifier of the Health
            soft_delete: Whether to perform soft delete (mark as deleted)
            cascade: Whether to cascade delete to related entities
            
        Returns:
            bool: True if entity was deleted, False if not found
            
        Raises:
            HealthNotFoundError: When entity doesn't exist
            DatabaseError: When database operation fails
        """
        ...

@abstractmethod
    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        include_deleted: bool = False
    ) -> List[Health]:
        """
        List Health entities with pagination, filtering, and sorting.
        
        Args:
            offset: Number of entities to skip
            limit: Maximum number of entities to return
            filters: Dictionary of filters to apply
            sort_by: Field name to sort by
            sort_order: Sort order ("asc" or "desc")
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            List[Health]: List of entities matching criteria
            
        Raises:
            ValidationError: When filter parameters are invalid
            DatabaseError: When database operation fails
        """
        ...

    @abstractmethod
    async def count(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> int:
        """
        Count Health entities matching criteria.
        
        Args:
            filters: Dictionary of filters to apply
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            int: Number of entities matching criteria
            
        Raises:
            ValidationError: When filter parameters are invalid
            DatabaseError: When database operation fails
        """
        ...

    # Custom Query Methods
@abstractmethod
    async def find_by_id(
        self,
entity_id: UUID    ) -> Optional[Health]:
        """
        Find Health by unique identifier
        
Args:
entity_id: UUID - Entity Id        
        Returns:
            Optional[Health]: Single entity or None if not found            
        
        Raises:
ValidationError: When parameters are invalid
            DatabaseError: When database operation fails
        """
        ...

@abstractmethod
    async def find_by_email(
        self,
email: str    ) -> Optional[Health]:
        """
        Find Health by email address
        
Args:
email: str - Email        
        Returns:
            Optional[Health]: Single entity or None if not found            
Note:
            This method uses caching with TTL of 300 seconds
        
        Raises:
HealthDuplicateError: When unique constraint is violated
ValidationError: When parameters are invalid
            DatabaseError: When database operation fails
        """
        ...

@abstractmethod
    async def find_active_entities(
        self,
    ) -> List[Health]:
        """
        Find all active Health entities
        
        
        Returns:
            List[Health]: List of entities matching criteria            
        
        Raises:
ValidationError: When parameters are invalid
            DatabaseError: When database operation fails
        """
        ...

@abstractmethod
    async def find_by_status(
        self,
status: str    ) -> List[Health]:
        """
        Find Health entities by status
        
Args:
status: str - Status        
        Returns:
            List[Health]: List of entities matching criteria            
        
        Raises:
ValidationError: When parameters are invalid
            DatabaseError: When database operation fails
        """
        ...

@abstractmethod
    async def count_by_status(
        self,
status: str    ) -> int:
        """
        Count Health entities by status
        
Args:
status: str - Status        
        Returns:
            int: Count result            
        
        Raises:
ValidationError: When parameters are invalid
            DatabaseError: When database operation fails
        """
        ...

@abstractmethod
    async def search_by_name(
        self,
search_term: str    ) -> List[Health]:
        """
        Search Health entities by name using full-text search
        
Args:
search_term: str - Search Term        
        Returns:
            List[Health]: Query result            
        
        Raises:
ValidationError: When parameters are invalid
            DatabaseError: When database operation fails
        """
        ...


    # Transaction Management
@abstractmethod
    async def begin_transaction(self) -> None:
        """Begin a new database transaction."""
        ...

    @abstractmethod
    async def commit_transaction(self) -> None:
        """Commit the current database transaction."""
        ...

    @abstractmethod  
    async def rollback_transaction(self) -> None:
        """Rollback the current database transaction."""
        ...

    # @pyhex:begin:custom_protocol_methods
    # Add custom protocol method signatures here - preserved during regeneration
    # @pyhex:end:custom_protocol_methods


class HealthQueryBuilderProtocol(ABC):
    """
    Protocol for Health query building operations.
    
    This protocol defines advanced query building capabilities for complex
    database operations that go beyond basic CRUD.
    """

    @abstractmethod
    def filter_by(self, **kwargs) -> "HealthQueryBuilderProtocol":
        """Add filter conditions to the query."""
        ...

    @abstractmethod
    def order_by(self, field: str, direction: str = "asc") -> "HealthQueryBuilderProtocol":
        """Add ordering to the query."""
        ...

    @abstractmethod
    def join(self, relationship: str, join_type: str = "inner") -> "HealthQueryBuilderProtocol":
        """Add join to the query."""
        ...

    @abstractmethod
    def limit(self, count: int) -> "HealthQueryBuilderProtocol":
        """Limit query results."""
        ...

    @abstractmethod
    def offset(self, count: int) -> "HealthQueryBuilderProtocol":
        """Skip query results."""
        ...

    @abstractmethod
    async def execute(self) -> List[Health]:
        """Execute the built query and return results."""
        ...

    @abstractmethod
    async def first(self) -> Optional[Health]:
        """Execute query and return first result."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Execute query and return count of results."""
        ...

    # @pyhex:begin:custom_query_builder_methods
    # Add custom query builder method signatures here - preserved during regeneration
    # @pyhex:end:custom_query_builder_methods



# @pyhex:begin:custom_protocols
# Add custom protocol definitions here - preserved during regeneration
# @pyhex:end:custom_protocols