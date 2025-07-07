"""Health Repository Implementation - Co-location Architecture

This module provides the SQLModel-based repository implementation for Health data access.
The implementation follows hexagonal architecture principles with async/await patterns
for PostgreSQL database operations.

Generated from: app/repository/Health/repository.py.j2
Configuration: app/repository/Health/repository.yaml
"""

import logging
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime

# SQLModel and SQLAlchemy imports
from sqlmodel import SQLModel, Session, select, and_, or_, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text

# @pyhex:begin:custom_repository_imports
# Add custom repository imports here - preserved during regeneration
# @pyhex:end:custom_repository_imports

# Domain imports
from app.core.Health.entities import Health
from .protocols import HealthCheckRepositoryProtocol, HealthCheckQueryBuilderProtocol
# Repository exceptions
class HealthCheckRepositoryError(Exception):
    """Base exception for HealthCheck repository operations."""
    pass


class HealthCheckNotFoundError(HealthCheckRepositoryError):
    """Raised when HealthCheck entity is not found."""
    pass


class HealthCheckDuplicateError(HealthCheckRepositoryError):
    """Raised when HealthCheck entity violates unique constraints."""
    pass


class HealthCheckValidationError(HealthCheckRepositoryError):
    """Raised when HealthCheck entity validation fails."""
    pass


class SQLModelHealthCheckRepository(HealthCheckRepositoryProtocol):
    """
    SQLModel-based repository implementation for Health entities.
    
    This repository provides async database operations with PostgreSQL using SQLModel.
    It implements the HealthRepositoryProtocol interface ensuring consistent
    data access patterns across the application.
    
    Features:
    - Async/await database operations
    - Connection pooling and session management  
    - Transaction support with rollback handling
    - Business validation and error handling
    - Soft delete operations
    - Custom query methods for complex data access
- Query logging and performance monitoring    
    Database Configuration:
    - Provider: postgresql
    - Dialect: asyncpg
    - Connection Pool: 5-20 connections
    - Session Management: dependency_injection
    """

    def __init__(
        self, 
        session: AsyncSession    ):
        """
        Initialize Health repository with async database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # @pyhex:begin:custom_repository_init
        # Add custom repository initialization here - preserved during regeneration
        # @pyhex:end:custom_repository_init

    # CRUD Operations Implementation

async def create(
        self,
        entity: Health,
        *,
        validate: bool = True,
        return_created: bool = True
    ) -> Health:
        """
        Create a new Health entity in the database.
        
        This method handles entity creation with business validation,
        duplicate detection, and proper error handling.
        """
        try:
            self.logger.info(f"Creating new Health entity")
            
            # Business validation
            if validate:
                await self._validate_entity_creation(entity)
            
            # @pyhex:begin:custom_create_logic
            # Add custom creation logic here - preserved during regeneration
            # @pyhex:end:custom_create_logic
            
            # Add entity to session
            self.session.add(entity)
            
            # Flush to get generated ID but don't commit yet
            await self.session.flush()
            
# Refresh to get all generated fields
            await self.session.refresh(entity)
            
            # Commit transaction
            await self.session.commit()
            
            
            self.logger.info(f"Successfully created Health with ID: {entity.id}")
            
            return entity
            
        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower():
                raise HealthDuplicateError(f"Health already exists: {e}")
            raise HealthRepositoryError(f"Database integrity error: {e}")
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Database error creating Health: {e}")
            raise HealthRepositoryError(f"Failed to create Health: {e}")
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Unexpected error creating Health: {e}")
            raise HealthRepositoryError(f"Unexpected error: {e}")

async def get_by_id(
        self,
        entity_id: UUID,
        *,
        include_deleted: bool = False,
        eager_load: Optional[List[str]] = None
    ) -> Optional[Health]:
        """
        Retrieve Health entity by unique identifier.
        
        This method supports eager loading of relationships and
        optional inclusion of soft-deleted entities.
        """
        try:
self.logger.debug(f"Fetching Health with ID: {entity_id}")
            
            
            # Build query
            statement = select(Health).where(Health.id == entity_id)
            
# Handle soft delete filtering
            if not include_deleted:
statement = statement.where(Health.is_deleted == False)
            
            # Add eager loading if specified
            if eager_load:
                for relationship in eager_load:
                    if hasattr(Health, relationship):
                        statement = statement.options(selectinload(getattr(Health, relationship)))
            
            # @pyhex:begin:custom_get_by_id_logic
            # Add custom get_by_id logic here - preserved during regeneration
            # @pyhex:end:custom_get_by_id_logic
            
            # Execute query
            result = await self.session.exec(statement)
            entity = result.first()
            
            
if entity:
                self.logger.debug(f"Found Health with ID: {entity_id}")
            else:
                self.logger.debug(f"Health not found with ID: {entity_id}")
            
            return entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error fetching Health {entity_id}: {e}")
            raise HealthRepositoryError(f"Failed to fetch Health: {e}")

    async def update(
        self,
        entity_id: UUID,
        updates: Dict[str, Any],
        *,
        partial: bool = True,
        validate: bool = True
    ) -> Optional[Health]:
        """
        Update existing Health entity with new data.
        
        This method supports partial updates and business validation
        with proper transaction handling.
        """
        try:
self.logger.info(f"Updating Health {entity_id} with {len(updates)} changes")
            
            # Get existing entity
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None
            
            # Validate updates
            if validate:
                await self._validate_entity_update(entity, updates)
            
            # @pyhex:begin:custom_update_logic
            # Add custom update logic here - preserved during regeneration
            # @pyhex:end:custom_update_logic
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
                elif not partial:
                    raise HealthValidationError(f"Field '{field}' does not exist on Health")
            
            # Update timestamp
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.utcnow()
            
            # Flush changes
            await self.session.flush()
            
            
            # Commit transaction
            await self.session.commit()
            
            
self.logger.info(f"Successfully updated Health {entity_id}")
            
            return entity
            
        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower():
                raise HealthDuplicateError(f"Update violates unique constraint: {e}")
            raise HealthRepositoryError(f"Database integrity error: {e}")
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Database error updating Health {entity_id}: {e}")
            raise HealthRepositoryError(f"Failed to update Health: {e}")

async def delete(
        self,
        entity_id: UUID,
        *,
        soft_delete: bool = True,
        cascade: bool = True
    ) -> bool:
        """
        Delete Health entity from the database.
        
        This method supports both soft and hard delete operations
        with cascade handling for related entities.
        """
        try:
self.logger.info(f"Deleting Health {entity_id} (soft={soft_delete})")
            
            # Get existing entity
            entity = await self.get_by_id(entity_id)
            if not entity:
                return False
            
            # Business validation for deletion
if True:  # Business validation enabled
                await self._validate_entity_deletion(entity)
            
            # @pyhex:begin:custom_delete_logic
            # Add custom deletion logic here - preserved during regeneration
            # @pyhex:end:custom_delete_logic
            
            if soft_delete and hasattr(entity, 'is_deleted'):
                # Soft delete: mark as deleted
                entity.is_deleted = True
                if hasattr(entity, 'deleted_at'):
                    entity.deleted_at = datetime.utcnow()
                
                # Handle cascade soft delete
                if cascade:
                    await self._cascade_soft_delete(entity)
                    
            else:
                # Hard delete: remove from database
                if cascade:
                    await self._cascade_hard_delete(entity)
                
                await self.session.delete(entity)
            
            # Commit transaction
            await self.session.commit()
            
            
self.logger.info(f"Successfully deleted Health {entity_id}")
            
            return True
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Database error deleting Health {entity_id}: {e}")
            raise HealthRepositoryError(f"Failed to delete Health: {e}")

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
        
        This method provides comprehensive querying capabilities with
        performance optimization and proper error handling.
        """
        try:
self.logger.debug(f"Listing Health entities: offset={offset}, limit={limit}")
            
            # Validate pagination parameters
            if limit > 100:
                limit = 100
            
            # Build base query
            statement = select(Health)
            
# Handle soft delete filtering
            if not include_deleted:
statement = statement.where(Health.is_deleted == False)
            
            # Apply filters
            if filters:
                statement = self._apply_filters(statement, filters)
            
            # Apply sorting
            if sort_by and hasattr(Health, sort_by):
                sort_column = getattr(Health, sort_by)
                if sort_order.lower() == "desc":
                    statement = statement.order_by(desc(sort_column))
                else:
                    statement = statement.order_by(asc(sort_column))
            else:
                # Default sorting by created_at
                if hasattr(Health, 'created_at'):
                    statement = statement.order_by(desc(Health.created_at))
            
            # Apply pagination
            statement = statement.offset(offset).limit(limit)
            
            # @pyhex:begin:custom_list_logic
            # Add custom listing logic here - preserved during regeneration
            # @pyhex:end:custom_list_logic
            
            # Execute query
            result = await self.session.exec(statement)
            entities = result.all()
            
self.logger.debug(f"Found {len(entities)} Health entities")
            
            return list(entities)
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error listing Health entities: {e}")
            raise HealthRepositoryError(f"Failed to list Health entities: {e}")

    async def count(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> int:
        """Count Health entities matching criteria."""
        try:
            # Build count query
            statement = select(func.count(Health.id))
            
# Handle soft delete filtering
            if not include_deleted:
statement = statement.where(Health.is_deleted == False)
            
            # Apply filters
            if filters:
                statement = self._apply_filters(statement, filters)
            
            # Execute count query
            result = await self.session.exec(statement)
            count = result.one()
            
            return count
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error counting Health entities: {e}")
            raise HealthRepositoryError(f"Failed to count Health entities: {e}")

    # Custom Query Methods
async def find_by_id(
        self,
entity_id: UUID    ) -> Optional[Health]:
        """
        Find Health by unique identifier
        
        """
        try:
self.logger.debug(f"Executing find_by_id query")
            
            
            # Build query based on method configuration
statement = select(Health)
            
            
# Apply parameter-based filters
            
            
            
            
# Execute single result query
            result = await self.session.exec(statement)
            entity = result.first()
            
            # @pyhex:begin:custom_find_by_id_logic
            # Add custom find_by_id logic here - preserved during regeneration
            # @pyhex:end:custom_find_by_id_logic
            
            
return entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in find_by_id: {e}")
            raise HealthRepositoryError(f"Failed to execute find_by_id: {e}")

async def find_by_email(
        self,
email: str    ) -> Optional[Health]:
        """
        Find Health by email address
        
This method uses caching with TTL of 300 seconds.
        """
        try:
self.logger.debug(f"Executing find_by_email query")
            
# Check cache first
            if self.cache_manager:
                cache_key = f"Health_find_by_email_{hash(email)}"
                cached_result = await self.cache_manager.get_cached(cache_key)
                if cached_result:
                    return cached_result
            
            # Build query based on method configuration
statement = select(Health)
            
            
# Apply parameter-based filters
if email:
                statement = statement.where(Health.email == email)
            
            
            
            
# Execute single result query
            result = await self.session.exec(statement)
            entity = result.first()
            
            # @pyhex:begin:custom_find_by_email_logic
            # Add custom find_by_email logic here - preserved during regeneration
            # @pyhex:end:custom_find_by_email_logic
            
# Cache the result
            if self.cache_manager and entity:
                cache_key = f"Health_find_by_email_{hash(email)}"
                await self.cache_manager.set_cached(cache_key, entity, 300)
            
return entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in find_by_email: {e}")
            raise HealthRepositoryError(f"Failed to execute find_by_email: {e}")

async def find_active_entities(
        self,
    ) -> List[Health]:
        """
        Find all active Health entities
        
        """
        try:
self.logger.debug(f"Executing find_active_entities query")
            
            
            # Build query based on method configuration
statement = select(Health)
            
# Apply predefined filters
statement = statement.where(Health.status == active)
            
            
            
            
            
# Execute list query
            result = await self.session.exec(statement)
            entity = result.all()
            
            # @pyhex:begin:custom_find_active_entities_logic
            # Add custom find_active_entities logic here - preserved during regeneration
            # @pyhex:end:custom_find_active_entities_logic
            
            
return list(entity)
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in find_active_entities: {e}")
            raise HealthRepositoryError(f"Failed to execute find_active_entities: {e}")

async def find_by_status(
        self,
status: str    ) -> List[Health]:
        """
        Find Health entities by status
        
        """
        try:
self.logger.debug(f"Executing find_by_status query")
            
            
            # Build query based on method configuration
statement = select(Health)
            
            
# Apply parameter-based filters
if status:
                statement = statement.where(Health.status == status)
            
            
            
            
# Execute list query
            result = await self.session.exec(statement)
            entity = result.all()
            
            # @pyhex:begin:custom_find_by_status_logic
            # Add custom find_by_status logic here - preserved during regeneration
            # @pyhex:end:custom_find_by_status_logic
            
            
return list(entity)
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in find_by_status: {e}")
            raise HealthRepositoryError(f"Failed to execute find_by_status: {e}")

async def count_by_status(
        self,
status: str    ) -> int:
        """
        Count Health entities by status
        
        """
        try:
self.logger.debug(f"Executing count_by_status query")
            
            
            # Build query based on method configuration
statement = select(func.count(Health.id))
            
            
# Apply parameter-based filters
if status:
                statement = statement.where(Health.status == status)
            
            
            
            
# Execute aggregate query
            result = await self.session.exec(statement)
            entity = result.one()
            
            # @pyhex:begin:custom_count_by_status_logic
            # Add custom count_by_status logic here - preserved during regeneration
            # @pyhex:end:custom_count_by_status_logic
            
            
return entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in count_by_status: {e}")
            raise HealthRepositoryError(f"Failed to execute count_by_status: {e}")

async def search_by_name(
        self,
search_term: str    ) -> List[Health]:
        """
        Search Health entities by name using full-text search
        
        """
        try:
self.logger.debug(f"Executing search_by_name query")
            
            
            # Build query based on method configuration
statement = select(Health)
            
            
# Apply parameter-based filters
if search_term:
                statement = statement.where(Health.name.ilike(f"%{" + "search_term" + "}%"))
            
            
            
            
            
            # @pyhex:begin:custom_search_by_name_logic
            # Add custom search_by_name logic here - preserved during regeneration
            # @pyhex:end:custom_search_by_name_logic
            
            
return entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in search_by_name: {e}")
            raise HealthRepositoryError(f"Failed to execute search_by_name: {e}")


    # Transaction Management
async def begin_transaction(self) -> None:
        """Begin a new database transaction."""
        # AsyncSession automatically handles transactions
        pass

    async def commit_transaction(self) -> None:
        """Commit the current database transaction."""
        await self.session.commit()

    async def rollback_transaction(self) -> None:
        """Rollback the current database transaction."""
        await self.session.rollback()

    # Helper Methods
    def _apply_filters(self, statement, filters: Dict[str, Any]):
        """Apply filters to query statement."""
        for field, value in filters.items():
            if hasattr(Health, field):
                column = getattr(Health, field)
                if isinstance(value, dict):
                    # Handle complex filter operations
                    for op, val in value.items():
                        if op == "eq":
                            statement = statement.where(column == val)
                        elif op == "ne":
                            statement = statement.where(column != val)
                        elif op == "gt":
                            statement = statement.where(column > val)
                        elif op == "gte":
                            statement = statement.where(column >= val)
                        elif op == "lt":
                            statement = statement.where(column < val)
                        elif op == "lte":
                            statement = statement.where(column <= val)
                        elif op == "in":
                            statement = statement.where(column.in_(val))
                        elif op == "like":
                            statement = statement.where(column.like(f"%{val}%"))
                        elif op == "ilike":
                            statement = statement.where(column.ilike(f"%{val}%"))
                else:
                    # Simple equality filter
                    statement = statement.where(column == value)
        return statement

    async def _validate_entity_creation(self, entity: Health) -> None:
        """Validate entity before creation."""
        # @pyhex:begin:custom_create_validation
        # Add custom creation validation here - preserved during regeneration
        # @pyhex:end:custom_create_validation
        pass

    async def _validate_entity_update(self, entity: Health, updates: Dict[str, Any]) -> None:
        """Validate entity before update."""
        # @pyhex:begin:custom_update_validation
        # Add custom update validation here - preserved during regeneration
        # @pyhex:end:custom_update_validation
        pass

    async def _validate_entity_deletion(self, entity: Health) -> None:
        """Validate entity before deletion."""
        # @pyhex:begin:custom_delete_validation
        # Add custom deletion validation here - preserved during regeneration
        # @pyhex:end:custom_delete_validation
        pass

async def _cascade_soft_delete(self, entity: Health) -> None:
        """Handle cascade soft delete for related entities."""
        # @pyhex:begin:custom_cascade_soft_delete
        # Add custom cascade soft delete logic here - preserved during regeneration
        # @pyhex:end:custom_cascade_soft_delete
        pass

    async def _cascade_hard_delete(self, entity: Health) -> None:
        """Handle cascade hard delete for related entities."""
        # @pyhex:begin:custom_cascade_hard_delete
        # Add custom cascade hard delete logic here - preserved during regeneration
        # @pyhex:end:custom_cascade_hard_delete
        pass

    # @pyhex:begin:custom_repository_methods
    # Add custom repository methods here - preserved during regeneration
    # @pyhex:end:custom_repository_methods


class HealthQueryBuilder(HealthQueryBuilderProtocol):
    """Query builder for complex Health queries."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.statement = select(Health)
        
    def filter_by(self, **kwargs) -> "HealthQueryBuilder":
        """Add filter conditions to the query."""
        for field, value in kwargs.items():
            if hasattr(Health, field):
                column = getattr(Health, field)
                self.statement = self.statement.where(column == value)
        return self
        
    def order_by(self, field: str, direction: str = "asc") -> "HealthQueryBuilder":
        """Add ordering to the query."""
        if hasattr(Health, field):
            column = getattr(Health, field)
            if direction.lower() == "desc":
                self.statement = self.statement.order_by(desc(column))
            else:
                self.statement = self.statement.order_by(asc(column))
        return self
        
    def join(self, relationship: str, join_type: str = "inner") -> "HealthQueryBuilder":
        """Add join to the query."""
        # Join implementation depends on specific relationships
        return self
        
    def limit(self, count: int) -> "HealthQueryBuilder":
        """Limit query results."""
        self.statement = self.statement.limit(count)
        return self
        
    def offset(self, count: int) -> "HealthQueryBuilder":
        """Skip query results."""
        self.statement = self.statement.offset(count)
        return self
        
    async def execute(self) -> List[Health]:
        """Execute the built query and return results."""
        result = await self.session.exec(self.statement)
        return list(result.all())
        
    async def first(self) -> Optional[Health]:
        """Execute query and return first result."""
        result = await self.session.exec(self.statement)
        return result.first()
        
    async def count(self) -> int:
        """Execute query and return count of results."""
        count_statement = select(func.count()).select_from(self.statement.subquery())
        result = await self.session.exec(count_statement)
        return result.one()

# @pyhex:begin:custom_repository_classes
# Add custom repository classes here - preserved during regeneration
# @pyhex:end:custom_repository_classes