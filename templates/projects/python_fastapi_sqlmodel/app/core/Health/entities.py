"""Health domain entities - Generated from Co-located Template.

This module contains SQLModel entities for the Health domain following
hexagonal architecture principles with co-location pattern implementation.

Generated from:
- domain.yaml: Base entity configuration and mixins
- entities.yaml: Entity-specific field definitions and relationships
- entities.py.j2: This Jinja2 template

Co-location Architecture:
- Templates, configurations, and generated files in same directory
- Hierarchical configuration merging for complete context
- @pyhex preservation markers for custom business logic
"""

# Standard library imports
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
# Third-party imports
from sqlmodel import SQLModel, Field

# @pyhex:begin:custom_imports
# Add custom imports here - preserved during regeneration
# @pyhex:end:custom_imports


# @pyhex:begin:custom_mixins
# Add custom mixin classes here - preserved during regeneration
# @pyhex:end:custom_mixins

# Health check entity for monitoring system status
class HealthCheckBase(SQLModel):
    """Base model for HealthCheck with shared fields and validation.
    
    This base class contains common fields and validation logic that will be
    inherited by both the table model and API schemas.
    
    Attributes:
        id: UUID primary key
        service_name: Name of the service being checked
        status: Current health status (healthy, unhealthy, unknown)
        last_check_time: Timestamp of last health check
        response_time_ms: Response time in milliseconds
        error_message: Error message if unhealthy
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    # Business fields from entities.yaml configuration
    id: Optional[UUID] = Field(
        default=None,
        primary_key=True,
        description="UUID primary key"    )
    service_name: str = Field(
        default=None,
        description="Name of the service being checked"    )
    status: str = Field(
        default="healthy",
        description="Current health status (healthy, unhealthy, unknown)"    )
    last_check_time: Optional[datetime] = Field(
        default=datetime.utcnow,
        description="Timestamp of last health check"    )
    response_time_ms: Optional[int] = Field(
        default=None,
        description="Response time in milliseconds"    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if unhealthy"    )
    created_at: Optional[datetime] = Field(
        default=datetime.utcnow,
        description="Creation timestamp"    )
    updated_at: Optional[datetime] = Field(
        default=datetime.utcnow,
        description="Last update timestamp"    )

    # @pyhex:begin:custom_fields_healthcheck
    # Add custom fields for HealthCheck here - preserved during regeneration
    # @pyhex:end:custom_fields_healthcheck

    class Config:
        """Pydantic configuration for HealthCheck."""
        validate_assignment = True
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        
        # @pyhex:begin:custom_config_healthcheck
        # Add custom Pydantic configuration here - preserved during regeneration
        # @pyhex:end:custom_config_healthcheck




    # @pyhex:begin:custom_methods_healthcheck
    # Add custom methods for HealthCheck here - preserved during regeneration
    # @pyhex:end:custom_methods_healthcheck


class HealthCheck(HealthCheckBase, table=True):
    """SQLModel table definition for HealthCheck.
    
    This class represents the database table for HealthCheck entities.
    It inherits all fields and validation from HealthCheckBase and adds
    table-specific configuration and relationships.
    """
    
    __tablename__ = "health_checks"
    

    # Relationships from entities.yaml configuration

    # @pyhex:begin:custom_relationships_healthcheck
    # Add custom relationships for HealthCheck here - preserved during regeneration
    # @pyhex:end:custom_relationships_healthcheck

    def __repr__(self) -> str:
        """String representation of HealthCheck."""
        return f"HealthCheck(id={self.id}, id={self.id})"

    # @pyhex:begin:custom_table_methods_healthcheck
    # Add custom table-specific methods here - preserved during regeneration
    # @pyhex:end:custom_table_methods_healthcheck


# API Schema Models for FastAPI integration
class HealthCheckCreate(HealthCheckBase):
    """Request schema for creating HealthCheck.
    
    Excludes auto-generated fields like id, timestamps.
    Used for POST requests in FastAPI endpoints.
    """
    pass


class HealthCheckUpdate(SQLModel):
    """Request schema for updating HealthCheck.
    
    All fields are optional to support partial updates.
    Used for PUT/PATCH requests in FastAPI endpoints.
    """
    service_name: Optional[str] = Field(
        default=None,
        description="Name of the service being checked"
    )
    status: Optional[str] = Field(
        default=None,
        description="Current health status (healthy, unhealthy, unknown)"
    )
    last_check_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last health check"
    )
    response_time_ms: Optional[int] = Field(
        default=None,
        description="Response time in milliseconds"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if unhealthy"
    )

    # @pyhex:begin:custom_update_fields_healthcheck
    # Add custom update fields here - preserved during regeneration
    # @pyhex:end:custom_update_fields_healthcheck


class HealthCheckResponse(HealthCheckBase):
    """Response schema for HealthCheck.
    
    Includes all fields including auto-generated ones.
    Used for API responses in FastAPI endpoints.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config(HealthCheckBase.Config):
        """Response model configuration."""

    # @pyhex:begin:custom_response_methods_healthcheck
    # Add custom response methods here - preserved during regeneration
    # @pyhex:end:custom_response_methods_healthcheck



# @pyhex:begin:custom_entities
# Add custom entity classes here - preserved during regeneration
# @pyhex:end:custom_entities


# Domain service functions
def create_healthcheck_from_dict(data: Dict[str, Any]) -> HealthCheck:
    """Create HealthCheck instance from dictionary.
    
    Args:
        data: Dictionary containing HealthCheck field values
        
    Returns:
        New HealthCheck instance
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # @pyhex:begin:custom_creation_logic_healthcheck
    # Add custom creation logic here - preserved during regeneration
    # @pyhex:end:custom_creation_logic_healthcheck
    
    return HealthCheck(**data)


def validate_healthcheck_business_rules(entity: HealthCheck) -> List[str]:
    """Validate business rules for HealthCheck.
    
    Args:
        entity: HealthCheck instance to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    
    # @pyhex:begin:custom_business_validation_healthcheck
    # Add custom business rule validation here - preserved during regeneration
    # @pyhex:end:custom_business_validation_healthcheck
    
    return errors



# @pyhex:begin:custom_domain_functions
# Add custom domain service functions here - preserved during regeneration
# @pyhex:end:custom_domain_functions


# Export all entity classes for easy importing
__all__ = [
    "HealthCheck",
    "HealthCheckBase", 
    "HealthCheckCreate",
    "HealthCheckUpdate",
    "HealthCheckResponse",
    # Custom exports
    # @pyhex:begin:custom_exports
    # Add custom exports here - preserved during regeneration
    # @pyhex:end:custom_exports
]