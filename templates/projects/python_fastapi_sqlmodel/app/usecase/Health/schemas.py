"""
Health Use Case Schemas - Co-location Architecture

This module defines use case-level validation and data transfer objects for Health operations.
These schemas provide input validation, output formatting, and data transformation
between the API layer and business logic layer.

Generated from: app/usecase/Health/schemas.py.j2
Configuration: app/usecase/Health/usecase.yaml
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator

# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports

from app.core.Health.entities import Health


# Base Schemas for Common Patterns
class BaseRequest(BaseModel):
    """Base class for all use case request schemas."""
    
    request_id: Optional[str] = Field(default=None, description="Optional request tracking ID")
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "use_enum_values": True,
    }


class BaseResponse(BaseModel):
    """Base class for all use case response schemas."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    @classmethod
    def from_entity(cls, entity: Health) -> "HealthResponse":
        """Create response from domain entity."""
        return cls(
            # @pyhex:begin:custom:entity_to_response_mapping
            # Map entity fields to response fields
            **entity.model_dump()
            # @pyhex:end:custom:entity_to_response_mapping
        )
    
    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
    }


# Request Schemas
class CreateHealthRequest(BaseRequest):
    """
    Request schema for creating a new Health.
    
    This schema validates input data for Health creation,
    ensuring all required fields are present and properly formatted.
    """
    
    # @pyhex:begin:custom:create_request_fields
    # Add Health creation fields here
    name: str = Field(..., min_length=1, max_length=255, description="Health name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Health description")
    # @pyhex:end:custom:create_request_fields
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate Health name."""
        if not v or v.isspace():
            raise ValueError("Health name cannot be empty or whitespace only")
        return v.strip()
    
    @model_validator(mode='after')
    def validate_create_request(self):
        """Validate the complete create request."""
        # @pyhex:begin:custom:create_request_validation
        # Add custom creation validation logic here
        # @pyhex:end:custom:create_request_validation
        return self


class UpdateHealthRequest(BaseRequest):
    """
    Request schema for updating an existing Health.
    
    This schema validates update data for Health modifications,
    supporting partial updates with field-level validation.
    """
    
    id: UUID = Field(..., description="Health ID to update")
    
    # @pyhex:begin:custom:update_request_fields
    # Add Health update fields here (all optional)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Updated Health name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Updated Health description")
    # @pyhex:end:custom:update_request_fields
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate Health name if provided."""
        if v is not None:
            if not v or v.isspace():
                raise ValueError("Health name cannot be empty or whitespace only")
            return v.strip()
        return v
    
    @model_validator(mode='after')
    def validate_update_request(self):
        """Validate the complete update request."""
        # Check that at least one field is being updated
        update_fields = {k: v for k, v in self.model_dump().items() 
                        if k not in {'id', 'request_id'} and v is not None}
        
        if not update_fields:
            raise ValueError("At least one field must be provided for update")
        
        # @pyhex:begin:custom:update_request_validation
        # Add custom update validation logic here
        # @pyhex:end:custom:update_request_validation
        return self


class DeleteHealthRequest(BaseRequest):
    """
    Request schema for deleting a Health.
    
    This schema validates deletion requests and supports
    soft delete options and cascading delete preferences.
    """
    
    id: UUID = Field(..., description="Health ID to delete")
    force: bool = Field(default=False, description="Force delete even if dependencies exist")
    soft_delete: bool = Field(default=True, description="Perform soft delete (mark as deleted)")
    
    # @pyhex:begin:custom:delete_request_fields
    # Add custom deletion fields here
    # @pyhex:end:custom:delete_request_fields


class GetHealthRequest(BaseRequest):
    """
    Request schema for retrieving a Health by ID.
    
    This schema validates Health retrieval requests
    and supports optional related data inclusion.
    """
    
    id: UUID = Field(..., description="Health ID to retrieve")
    include_related: bool = Field(default=False, description="Include related entities in response")
    
    # @pyhex:begin:custom:get_request_fields
    # Add custom retrieval fields here
    # @pyhex:end:custom:get_request_fields


class ListHealthchecksRequest(BaseRequest):
    """
    Request schema for listing HealthChecks with filtering and pagination.
    
    This schema supports advanced filtering, sorting, and pagination
    for Health list operations.
    """
    
    # Pagination
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")
    
    # Filtering
    name_filter: Optional[str] = Field(default=None, description="Filter by Health name (partial match)")
    created_after: Optional[datetime] = Field(default=None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(default=None, description="Filter by creation date (before)")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort order")
    
    # Include options
    include_related: bool = Field(default=False, description="Include related entities in response")
    include_deleted: bool = Field(default=False, description="Include soft-deleted records")
    
    # @pyhex:begin:custom:list_request_fields
    # Add custom filtering and sorting fields here
    # @pyhex:end:custom:list_request_fields
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate date range filters."""
        if (self.created_after and self.created_before and 
            self.created_after >= self.created_before):
            raise ValueError("created_after must be before created_before")
        return self
    
    def to_filters(self) -> Dict[str, Any]:
        """Convert request to repository filter format."""
        filters = {}
        
        if self.name_filter:
            filters['name__icontains'] = self.name_filter
        
        if self.created_after:
            filters['created_at__gte'] = self.created_after
            
        if self.created_before:
            filters['created_at__lte'] = self.created_before
        
        if not self.include_deleted:
            filters['deleted_at__isnull'] = True
        
        # @pyhex:begin:custom:filter_conversion
        # Add custom filter conversion logic here
        # @pyhex:end:custom:filter_conversion
        
        return filters


# Response Schemas
class HealthResponse(BaseResponse):
    """
    Response schema for Health data.
    
    This schema formats Health data for API responses,
    including all relevant fields and computed properties.
    """
    
    id: UUID = Field(..., description="Health unique identifier")
    
    # @pyhex:begin:custom:response_fields
    # Add Health response fields here
    name: str = Field(..., description="Health name")
    description: Optional[str] = Field(default=None, description="Health description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    # @pyhex:end:custom:response_fields
    
    # Computed properties
    @property
    def display_name(self) -> str:
        """Get display name for Health."""
        return self.name
    
    # @pyhex:begin:custom:response_properties
    # Add custom computed properties here
    # @pyhex:end:custom:response_properties


class ListHealthchecksResponse(BaseResponse):
    """
    Response schema for Health list operations.
    
    This schema provides paginated Health results
    with metadata for pagination and filtering.
    """
    
    items: List[HealthResponse] = Field(..., description="List of HealthChecks")
    total_count: int = Field(..., description="Total number of HealthChecks matching filters")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records requested")
    has_more: bool = Field(..., description="Whether more records are available")
    
    @model_validator(mode='after')
    def compute_has_more(self):
        """Compute has_more field based on pagination."""
        self.has_more = (self.skip + len(self.items)) < self.total_count
        return self


class DeleteResponse(BaseResponse):
    """
    Response schema for delete operations.
    
    This schema provides confirmation and details
    about successful deletion operations.
    """
    
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion result message")
    deleted_id: Optional[UUID] = Field(default=None, description="ID of deleted Health")
    
    # @pyhex:begin:custom:delete_response_fields
    # Add custom deletion response fields here
    # @pyhex:end:custom:delete_response_fields


# Error Response Schemas
class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""
    
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    invalid_value: Optional[Any] = Field(default=None, description="The invalid value")


class UseCaseErrorResponse(BaseResponse):
    """
    Error response schema for use case operations.
    
    This schema provides structured error information
    for failed use case operations.
    """
    
    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ValidationErrorDetail]] = Field(default=None, description="Detailed error information")
    request_id: Optional[str] = Field(default=None, description="Request ID for error tracking")
    
    # @pyhex:begin:custom:error_response_fields
    # Add custom error response fields here
    # @pyhex:end:custom:error_response_fields


# Business Rule Validation Schemas
class BusinessRuleViolation(BaseModel):
    """Schema for business rule validation violations."""
    
    rule_name: str = Field(..., description="Name of violated business rule")
    rule_type: str = Field(..., description="Type of business rule")
    error_message: str = Field(..., description="Business rule violation message")
    severity: str = Field(..., description="Violation severity level")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class BusinessRuleValidationResponse(BaseResponse):
    """Response schema for business rule validation results."""
    
    is_valid: bool = Field(..., description="Whether all business rules passed")
    violations: List[BusinessRuleViolation] = Field(default_factory=list, description="List of rule violations")
    validation_group: Optional[str] = Field(default=None, description="Validation group that was executed")


# @pyhex:begin:custom:schemas
# Add custom schema definitions here
# @pyhex:end:custom:schemas


# Schema Collections for Easy Import
REQUEST_SCHEMAS = {
    "create": CreateHealthRequest,
    "update": UpdateHealthRequest,
    "delete": DeleteHealthRequest,
    "get": GetHealthRequest,
    "list": ListHealthchecksRequest,
}

RESPONSE_SCHEMAS = {
    "Health": HealthResponse,
    "list": ListHealthchecksResponse,
    "delete": DeleteResponse,
    "error": UseCaseErrorResponse,
    "validation": BusinessRuleValidationResponse,
}

__all__ = [
    # Request schemas
    "CreateHealthRequest",
    "UpdateHealthRequest", 
    "DeleteHealthRequest",
    "GetHealthRequest",
    "ListHealthchecksRequest",
    
    # Response schemas
    "HealthResponse",
    "ListHealthchecksResponse",
    "DeleteResponse",
    "UseCaseErrorResponse",
    "BusinessRuleValidationResponse",
    
    # Collections
    "REQUEST_SCHEMAS",
    "RESPONSE_SCHEMAS",
]