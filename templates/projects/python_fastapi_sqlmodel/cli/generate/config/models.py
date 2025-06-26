"""
Pydantic models for type-safe configuration validation.

This module defines the core configuration models used throughout the template generation system.
All configuration is loaded and validated through these models to ensure type safety and
proper structure before template processing begins.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
import logging

logger = logging.getLogger(__name__)


class FieldType(str, Enum):
    """Supported field types for entity configurations."""
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DATETIME = "datetime"
    EMAIL = "EmailStr"
    OPTIONAL_STR = "Optional[str]"
    OPTIONAL_INT = "Optional[int]"
    OPTIONAL_FLOAT = "Optional[float]"
    OPTIONAL_BOOL = "Optional[bool]"
    OPTIONAL_DATETIME = "Optional[datetime]"
    LIST_STR = "List[str]"
    LIST_INT = "List[int]"


class RelationshipType(str, Enum):
    """Supported relationship types between entities."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class HTTPMethod(str, Enum):
    """Supported HTTP methods for API endpoints."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class FieldConfig(BaseModel):
    """Configuration for an entity field."""
    
    name: str = Field(..., description="Field name")
    type: FieldType = Field(..., description="Field type")
    required: bool = Field(default=True, description="Whether field is required")
    index: bool = Field(default=False, description="Whether field should be indexed")
    unique: bool = Field(default=False, description="Whether field should be unique")
    default: Optional[str] = Field(default=None, description="Default value expression")
    description: Optional[str] = Field(default=None, description="Field description")
    
    @field_validator('name')
    def validate_field_name(cls, v):
        """Validate field name follows Python naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Field name '{v}' is not a valid Python identifier")
        if v.startswith('_'):
            raise ValueError(f"Field name '{v}' should not start with underscore")
        return v
    
    @field_validator('default')
    def validate_default_expression(cls, v, info):
        """Validate default value expressions."""
        if v is None:
            return v
        
        # Common default expressions that are allowed
        allowed_defaults = [
            'datetime.utcnow',
            'datetime.now',
            'uuid.uuid4',
            'str(uuid.uuid4())',
        ]
        
        # Allow simple literals
        if v in ['true', 'false', 'null'] or v.isdigit() or v.startswith('"'):
            return v
            
        if v not in allowed_defaults:
            logger.warning(f"Default expression '{v}' may not be supported")
            
        return v


class RelationshipConfig(BaseModel):
    """Configuration for entity relationships."""
    
    entity: str = Field(..., description="Related entity name")
    type: RelationshipType = Field(..., description="Relationship type")
    back_populates: Optional[str] = Field(default=None, description="Back-reference field name")
    foreign_key: Optional[str] = Field(default=None, description="Foreign key field reference")
    
    @field_validator('entity')
    def validate_entity_name(cls, v):
        """Validate related entity name."""
        if not v.isidentifier():
            raise ValueError(f"Entity name '{v}' is not a valid Python identifier")
        return v


class EntityConfig(BaseModel):
    """Configuration for a domain entity."""
    
    name: str = Field(..., description="Entity name")
    fields: List[FieldConfig] = Field(..., description="Entity fields")
    relationships: List[RelationshipConfig] = Field(default_factory=list, description="Entity relationships")
    table_name: Optional[str] = Field(default=None, description="Custom table name")
    description: Optional[str] = Field(default=None, description="Entity description")
    
    @field_validator('name')
    def validate_entity_name(cls, v):
        """Validate entity name follows Python class naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Entity name '{v}' is not a valid Python identifier")
        if not v[0].isupper():
            raise ValueError(f"Entity name '{v}' should start with uppercase letter")
        return v
    
    @field_validator('fields')
    def validate_required_fields(cls, v):
        """Ensure entities have at least basic required fields."""
        if not v:
            raise ValueError("Entity must have at least one field")
        
        field_names = [field.name for field in v]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Entity cannot have duplicate field names")
            
        return v
    
    @model_validator(mode='after')
    def validate_table_name(self):
        """Generate table name if not provided."""
        if self.table_name is None:
            entity_name = self.name
            # Convert PascalCase to snake_case
            table_name = ''
            for i, char in enumerate(entity_name):
                if char.isupper() and i > 0:
                    table_name += '_'
                table_name += char.lower()
            self.table_name = table_name
        return self


class EndpointConfig(BaseModel):
    """Configuration for API endpoints."""
    
    method: HTTPMethod = Field(..., description="HTTP method")
    path: str = Field(..., description="Endpoint path")
    operation: str = Field(..., description="Operation identifier")
    description: Optional[str] = Field(default=None, description="Endpoint description")
    
    @field_validator('path')
    def validate_path(cls, v):
        """Validate endpoint path format."""
        if not v.startswith('/'):
            v = '/' + v
        return v


class DomainConfig(BaseModel):
    """Configuration for a domain/module."""
    
    name: str = Field(..., description="Domain name")
    plural: Optional[str] = Field(default=None, description="Plural form of domain name")
    description: Optional[str] = Field(default=None, description="Domain description")
    package: Optional[str] = Field(default=None, description="Python package name")
    
    @field_validator('name')
    def validate_domain_name(cls, v):
        """Validate domain name follows Python naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Domain name '{v}' is not a valid Python identifier")
        if not v[0].isupper():
            raise ValueError(f"Domain name '{v}' should start with uppercase letter")
        return v
    
    @model_validator(mode='after')
    def generate_defaults(self):
        """Generate default values for optional fields."""
        name = self.name
        
        # Generate plural form if not provided
        if self.plural is None:
            if name.endswith('y'):
                plural = name[:-1] + 'ies'
            elif name.endswith(('s', 'sh', 'ch', 'x', 'z')):
                plural = name + 'es'
            else:
                plural = name + 's'
            self.plural = plural
        
        # Generate package name if not provided
        if self.package is None:
            # Convert PascalCase to snake_case
            package = ''
            for i, char in enumerate(name):
                if char.isupper() and i > 0:
                    package += '_'
                package += char.lower()
            self.package = package
            
        return self


class Configuration(BaseModel):
    """Root configuration model for template generation."""
    
    domain: DomainConfig = Field(..., description="Domain configuration")
    entities: List[EntityConfig] = Field(..., description="Entity configurations")
    endpoints: List[EndpointConfig] = Field(default_factory=list, description="API endpoint configurations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('entities')
    def validate_entities(cls, v):
        """Validate entity configurations."""
        if not v:
            raise ValueError("Configuration must include at least one entity")
        
        entity_names = [entity.name for entity in v]
        if len(entity_names) != len(set(entity_names)):
            raise ValueError("Configuration cannot have duplicate entity names")
        
        return v
    
    @model_validator(mode='after')
    def generate_default_endpoints(self):
        """Generate default CRUD endpoints if none provided."""
        if not self.endpoints and self.entities:
            default_endpoints = [
                EndpointConfig(method=HTTPMethod.POST, path="/", operation="create"),
                EndpointConfig(method=HTTPMethod.GET, path="/{id}", operation="get_by_id"), 
                EndpointConfig(method=HTTPMethod.GET, path="/", operation="list"),
                EndpointConfig(method=HTTPMethod.PUT, path="/{id}", operation="update"),
                EndpointConfig(method=HTTPMethod.DELETE, path="/{id}", operation="delete"),
            ]
            self.endpoints = default_endpoints
            logger.info("Generated default CRUD endpoints")
        
        # Validate that domain name matches at least one entity
        entity_names = [entity.name for entity in self.entities]
        if self.domain.name not in entity_names:
            logger.warning(f"Domain name '{self.domain.name}' does not match any entity name")
        
        return self
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True,
        "extra": "forbid",  # Reject unknown fields
    }