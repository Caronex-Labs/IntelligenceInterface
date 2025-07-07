"""
Configuration models for the FastAPI SQLModel generator.

This module provides all the configuration models used for code generation,
including entities, domains, use cases, services, and validation schemas.
"""

from .config_models import (
    # Base enums and types
    FieldType,
    RelationshipType,
    HTTPMethod,
    DependencyScope,
    
    # Field and entity configurations
    FieldConfig,
    RelationshipConfig,
    EntityConfig,
    EndpointConfig,
    
    # Domain configurations
    DomainConfig,
    Configuration,
    
    # Advanced entity domain configurations
    MixinConfig,
    DomainRelationshipConfig,
    SQLModelConfig,
    EntityDomainConfig,
    
    # Use case configurations
    DependencyConfig,
    DependencyInjectionConfig,
    UseCaseMethodConfig,
    ServiceCompositionConfig,
    ErrorHandlingConfig,
    UseCaseConfig,
    
    # Service configurations
    ServiceMethodConfig,
    ServiceConfig,
)

from .internal_models import (
    # Internal data models
    TemplateContext,
    GenerationResult,
    LayerInfo,
    SchemaInfo,
    ValidationContext,
)

__all__ = [
    # Base enums and types
    "FieldType",
    "RelationshipType", 
    "HTTPMethod",
    "DependencyScope",
    
    # Field and entity configurations
    "FieldConfig",
    "RelationshipConfig",
    "EntityConfig",
    "EndpointConfig",
    
    # Domain configurations
    "DomainConfig",
    "Configuration",
    
    # Advanced entity domain configurations
    "MixinConfig",
    "DomainRelationshipConfig",
    "SQLModelConfig",
    "EntityDomainConfig",
    
    # Use case configurations
    "DependencyConfig",
    "DependencyInjectionConfig",
    "UseCaseMethodConfig",
    "ServiceCompositionConfig",
    "ErrorHandlingConfig",
    "UseCaseConfig",
    
    # Service configurations
    "ServiceMethodConfig",
    "ServiceConfig",
    
    # Internal data models
    "TemplateContext",
    "GenerationResult",
    "LayerInfo",
    "SchemaInfo",
    "ValidationContext",
]
