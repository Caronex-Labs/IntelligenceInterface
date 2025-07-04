"""
Pydantic models for type-safe configuration validation.

This module defines the core configuration models used throughout the template generation system.
All configuration is loaded and validated through these models to ensure type safety and
proper structure before template processing begins.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
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
    UUID = "UUID"
    OPTIONAL_STR = "Optional[str]"
    OPTIONAL_INT = "Optional[int]"
    OPTIONAL_FLOAT = "Optional[float]"
    OPTIONAL_BOOL = "Optional[bool]"
    OPTIONAL_DATETIME = "Optional[datetime]"
    OPTIONAL_UUID = "Optional[UUID]"
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


class BusinessRuleType(str, Enum):
    """Supported business rule types."""
    VALIDATION = "validation"
    CONSTRAINT = "constraint"
    BUSINESS_LOGIC = "business_logic"
    SECURITY = "security"


class BusinessRuleSeverity(str, Enum):
    """Supported business rule severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class DependencyScope(str, Enum):
    """Supported dependency injection scopes."""
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"


class FieldConfig(BaseModel):
    """Configuration for an entity field."""
    
    name: str = Field(..., description="Field name")
    type: FieldType = Field(..., description="Field type")
    required: bool = Field(default=True, description="Whether field is required")
    index: bool = Field(default=False, description="Whether field should be indexed")
    unique: bool = Field(default=False, description="Whether field should be unique")
    default: Optional[str] = Field(default=None, description="Default value expression")
    description: Optional[str] = Field(default=None, description="Field description")
    sqlmodel_field: Optional[str] = Field(default=None, description="SQLModel Field() expression")
    
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
    mixins: List[str] = Field(default_factory=list, description="Mixin names to apply to this entity")
    
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


class CoLocationConfig(BaseModel):
    """Configuration for co-location metadata and tracking."""
    
    template_source: str = Field(..., description="Source of templates (global, co_located, custom)")
    config_source: str = Field(..., description="Source of configuration (global, co_located, merged)")
    generation_mode: str = Field(default="standard", description="Generation mode (standard, co_located, hybrid)")
    co_located_directory: Optional[str] = Field(default=None, description="Path to co-located directory")
    template_version: Optional[str] = Field(default=None, description="Version of templates used")
    last_updated: Optional[datetime] = Field(default=None, description="Last update timestamp")
    custom_templates: List[str] = Field(default_factory=list, description="List of custom template files")
    override_count: int = Field(default=0, description="Number of configuration overrides applied")
    
    @field_validator('template_source')
    def validate_template_source(cls, v):
        """Validate template source type."""
        allowed_sources = ['global', 'co_located', 'custom', 'hybrid']
        if v not in allowed_sources:
            raise ValueError(f"Template source '{v}' must be one of {allowed_sources}")
        return v
    
    @field_validator('config_source')
    def validate_config_source(cls, v):
        """Validate configuration source type."""
        allowed_sources = ['global', 'co_located', 'merged', 'custom']
        if v not in allowed_sources:
            raise ValueError(f"Config source '{v}' must be one of {allowed_sources}")
        return v
    
    @field_validator('generation_mode')
    def validate_generation_mode(cls, v):
        """Validate generation mode."""
        allowed_modes = ['standard', 'co_located', 'hybrid', 'custom']
        if v not in allowed_modes:
            raise ValueError(f"Generation mode '{v}' must be one of {allowed_modes}")
        return v


class Configuration(BaseModel):
    """Root configuration model for template generation."""
    
    domain: DomainConfig = Field(..., description="Domain configuration")
    entities: List[EntityConfig] = Field(..., description="Entity configurations")
    endpoints: List[EndpointConfig] = Field(default_factory=list, description="API endpoint configurations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    co_location: Optional[CoLocationConfig] = Field(default=None, description="Co-location metadata")
    
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


class MixinConfig(BaseModel):
    """Configuration for reusable field mixins."""
    
    name: str = Field(..., description="Mixin name")
    fields: List[FieldConfig] = Field(..., description="Fields provided by this mixin")
    description: Optional[str] = Field(default=None, description="Mixin description")
    
    @field_validator('name')
    def validate_mixin_name(cls, v):
        """Validate mixin name follows Python naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Mixin name '{v}' is not a valid Python identifier")
        if not v[0].isupper():
            raise ValueError(f"Mixin name '{v}' should start with uppercase letter")
        return v


class DomainRelationshipConfig(BaseModel):
    """Configuration for domain-level relationship definitions."""
    
    name: str = Field(..., description="Relationship name")
    from_entity: str = Field(..., description="Source entity name")
    to_entity: str = Field(..., description="Target entity name")
    type: RelationshipType = Field(..., description="Relationship type")
    back_populates: Optional[str] = Field(default=None, description="Back-reference field name")
    foreign_key: Optional[str] = Field(default=None, description="Foreign key reference")
    
    @field_validator('from_entity', 'to_entity')
    def validate_entity_names(cls, v):
        """Validate entity names in relationships."""
        if not v.isidentifier():
            raise ValueError(f"Entity name '{v}' is not a valid Python identifier")
        return v


class SQLModelConfig(BaseModel):
    """Configuration for SQLModel-specific settings."""
    
    table_naming: str = Field(default="snake_case", description="Table naming convention")
    field_naming: str = Field(default="snake_case", description="Field naming convention")
    generate_id_fields: bool = Field(default=True, description="Auto-generate ID fields")
    timestamp_fields: List[str] = Field(default_factory=list, description="Auto-generated timestamp fields")
    
    @field_validator('table_naming', 'field_naming')
    def validate_naming_convention(cls, v):
        """Validate naming conventions."""
        allowed_conventions = ["snake_case", "camelCase", "PascalCase"]
        if v not in allowed_conventions:
            raise ValueError(f"Naming convention '{v}' must be one of {allowed_conventions}")
        return v


class EntityDomainConfig(BaseModel):
    """Configuration for entity domain with separate domain and entity files."""
    
    # Domain configuration
    name: str = Field(..., description="Domain name")
    plural: Optional[str] = Field(default=None, description="Plural form of domain name")
    description: Optional[str] = Field(default=None, description="Domain description")
    package: Optional[str] = Field(default=None, description="Python package name")
    
    # Domain-level configurations
    base_fields: List[FieldConfig] = Field(default_factory=list, description="Base fields for all entities")
    mixins: List[MixinConfig] = Field(default_factory=list, description="Reusable field mixins")
    relationships: List[DomainRelationshipConfig] = Field(default_factory=list, description="Domain relationships")
    sqlmodel_config: Optional[SQLModelConfig] = Field(default=None, description="SQLModel-specific configuration")
    
    # Entity configurations (loaded from entities.yaml)
    entities: List[EntityConfig] = Field(default_factory=list, description="Entity configurations")
    endpoints: List[EndpointConfig] = Field(default_factory=list, description="API endpoint configurations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Breakdown metadata (optional, added when config comes from external breakdown)
    breakdown_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Config breakdown tracking metadata")
    
    @field_validator('name')
    def validate_domain_name(cls, v):
        """Validate domain name follows Python naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Domain name '{v}' is not a valid Python identifier")
        if not v[0].isupper():
            raise ValueError(f"Domain name '{v}' should start with uppercase letter")
        return v
    
    @model_validator(mode='after')
    def generate_defaults_and_validate(self):
        """Generate default values and validate entity domain configuration."""
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
        
        # Apply base fields to all entities if configured
        if self.base_fields:
            for entity in self.entities:
                # Add base fields that don't already exist
                existing_field_names = {field.name for field in entity.fields}
                for base_field in self.base_fields:
                    if base_field.name not in existing_field_names:
                        entity.fields.insert(0, base_field)
        
        # Apply mixins to entities
        for entity in self.entities:
            if hasattr(entity, 'mixins') and getattr(entity, 'mixins'):
                # Find requested mixins and apply their fields
                for mixin_name in entity.mixins:
                    mixin = next((m for m in self.mixins if m.name == mixin_name), None)
                    if mixin:
                        # Add mixin fields that don't already exist
                        existing_field_names = {field.name for field in entity.fields}
                        for mixin_field in mixin.fields:
                            if mixin_field.name not in existing_field_names:
                                entity.fields.append(mixin_field)
                    else:
                        logger.warning(f"Mixin '{mixin_name}' not found for entity '{entity.name}'")
        
        # Apply domain relationships to entities
        for domain_rel in self.relationships:
            # Find the source entity and add relationship if not already present
            source_entity = next((e for e in self.entities if e.name == domain_rel.from_entity), None)
            if source_entity:
                # Check if relationship already exists
                existing_rel = next(
                    (rel for rel in source_entity.relationships 
                     if rel.entity == domain_rel.to_entity and rel.type == domain_rel.type),
                    None
                )
                
                if not existing_rel:
                    entity_rel = RelationshipConfig(
                        entity=domain_rel.to_entity,
                        type=domain_rel.type,
                        back_populates=domain_rel.back_populates,
                        foreign_key=domain_rel.foreign_key
                    )
                    source_entity.relationships.append(entity_rel)
        
        # Generate default endpoints if none provided
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
        
        return self
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True,
        "extra": "forbid",  # Reject unknown fields
    }


class BusinessRuleConfig(BaseModel):
    """Configuration for business rules and validation constraints."""
    
    name: str = Field(..., description="Business rule name")
    type: BusinessRuleType = Field(..., description="Rule type")
    condition: str = Field(..., description="Rule condition expression")
    error_message: Optional[str] = Field(default=None, description="Error message when rule fails")
    severity: BusinessRuleSeverity = Field(default=BusinessRuleSeverity.ERROR, description="Rule severity level")
    context: Optional[str] = Field(default=None, description="Context where rule applies")
    custom_exception: Optional[str] = Field(default=None, description="Custom exception class name")
    
    @field_validator('name')
    def validate_rule_name(cls, v):
        """Validate business rule name."""
        if not v.strip():
            raise ValueError("Business rule name cannot be empty")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Business rule name '{v}' should contain only alphanumeric characters, underscores, and hyphens")
        return v
    
    @field_validator('condition')
    def validate_condition(cls, v):
        """Validate rule condition."""
        if not v.strip():
            raise ValueError("Business rule condition cannot be empty")
        return v


class ValidationGroupConfig(BaseModel):
    """Configuration for validation group with execution order."""
    
    name: str = Field(..., description="Validation group name")
    rules: List[str] = Field(..., description="Business rule names in this group")
    execution_order: Optional[List[str]] = Field(default=None, description="Explicit rule execution order")
    description: Optional[str] = Field(default=None, description="Group description")
    
    @field_validator('name')
    def validate_group_name(cls, v):
        """Validate validation group name."""
        if not v.strip():
            raise ValueError("Validation group name cannot be empty")
        return v
    
    @field_validator('rules')
    def validate_rules_list(cls, v):
        """Validate rules list."""
        if not v:
            raise ValueError("Validation group must contain at least one rule")
        return v
    
    @model_validator(mode='after')
    def validate_execution_order(self):
        """Validate execution order contains only rules from the group."""
        if self.execution_order:
            rule_set = set(self.rules)
            for rule in self.execution_order:
                if rule not in rule_set:
                    raise ValueError(f"Execution order contains rule '{rule}' not in group rules")
        return self


class DependencyConfig(BaseModel):
    """Configuration for service dependencies."""
    
    repositories: List[str] = Field(default_factory=list, description="Repository dependencies")
    services: List[str] = Field(default_factory=list, description="Service dependencies")
    external_apis: List[str] = Field(default_factory=list, description="External API dependencies")
    event_handlers: List[str] = Field(default_factory=list, description="Event handler dependencies")
    
    @field_validator('repositories', 'services', 'external_apis', 'event_handlers')
    def validate_dependency_names(cls, v):
        """Validate dependency names."""
        for dep in v:
            if not dep.strip():
                raise ValueError("Dependency name cannot be empty")
        return v


class DependencyInjectionConfig(BaseModel):
    """Configuration for dependency injection patterns."""
    
    interface_mappings: Dict[str, str] = Field(default_factory=dict, description="Interface to implementation mappings")
    scoped_dependencies: List[str] = Field(default_factory=list, description="Scoped lifetime dependencies")
    singleton_dependencies: List[str] = Field(default_factory=list, description="Singleton lifetime dependencies")
    transient_dependencies: List[str] = Field(default_factory=list, description="Transient lifetime dependencies")
    
    @field_validator('interface_mappings')
    def validate_interface_mappings(cls, v):
        """Validate interface mappings."""
        for interface, implementation in v.items():
            if not interface.strip() or not implementation.strip():
                raise ValueError("Interface and implementation names cannot be empty")
        return v


class UseCaseMethodConfig(BaseModel):
    """Configuration for a use case method."""
    
    name: str = Field(..., description="Method name")
    input_schema: Optional[str] = Field(default=None, description="Input schema class name")
    output_schema: Optional[str] = Field(default=None, description="Output schema class name")
    transaction_boundary: bool = Field(default=False, description="Whether method requires transaction boundary")
    dependencies: Union[List[str], DependencyConfig] = Field(default_factory=list, description="Method dependencies")
    business_rules: List[str] = Field(default_factory=list, description="Business rules for this method")
    orchestration_steps: List[str] = Field(default_factory=list, description="Ordered orchestration steps")
    description: Optional[str] = Field(default=None, description="Method description")
    
    @field_validator('name')
    def validate_method_name(cls, v):
        """Validate method name follows Python naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Method name '{v}' is not a valid Python identifier")
        if v.startswith('_'):
            raise ValueError(f"Method name '{v}' should not start with underscore")
        return v
    
    @model_validator(mode='after')
    def validate_schemas(self):
        """Validate schema names."""
        if self.input_schema and not self.input_schema.isidentifier():
            raise ValueError(f"Input schema '{self.input_schema}' is not a valid Python identifier")
        if self.output_schema and not self.output_schema.isidentifier():
            raise ValueError(f"Output schema '{self.output_schema}' is not a valid Python identifier")
        return self


class ServiceCompositionConfig(BaseModel):
    """Configuration for service composition patterns."""
    
    transaction_manager: Optional[str] = Field(default=None, description="Transaction manager service")
    event_publisher: Optional[str] = Field(default=None, description="Event publisher service")
    cache_manager: Optional[str] = Field(default=None, description="Cache manager service")
    logger: Optional[str] = Field(default=None, description="Logger service")
    metrics_collector: Optional[str] = Field(default=None, description="Metrics collector service")


class ErrorHandlingConfig(BaseModel):
    """Configuration for error handling patterns."""
    
    aggregation_strategy: str = Field(default="fail_fast", description="Error aggregation strategy")
    early_termination: bool = Field(default=True, description="Whether to terminate on first error")
    custom_exceptions: List[Dict[str, str]] = Field(default_factory=list, description="Custom exception mappings")
    default_error_response: Optional[str] = Field(default=None, description="Default error response format")
    
    @field_validator('aggregation_strategy')
    def validate_aggregation_strategy(cls, v):
        """Validate aggregation strategy."""
        allowed_strategies = ["fail_fast", "collect_all_errors", "collect_first_error_per_type"]
        if v not in allowed_strategies:
            raise ValueError(f"Aggregation strategy '{v}' must be one of {allowed_strategies}")
        return v


class UseCaseConfig(BaseModel):
    """Configuration for use case business logic orchestration."""
    
    name: str = Field(..., description="Use case name")
    description: Optional[str] = Field(default=None, description="Use case description")
    methods: List[UseCaseMethodConfig] = Field(default_factory=list, description="Use case methods")
    dependencies: Union[List[str], DependencyConfig] = Field(default_factory=list, description="Use case dependencies")
    error_handling: Union[Dict[str, str], ErrorHandlingConfig] = Field(default_factory=dict, description="Error handling configuration")
    service_composition: Optional[ServiceCompositionConfig] = Field(default=None, description="Service composition configuration")
    dependency_injection: Optional[DependencyInjectionConfig] = Field(default=None, description="Dependency injection configuration")
    
    @field_validator('name')
    def validate_use_case_name(cls, v):
        """Validate use case name follows Python naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Use case name '{v}' is not a valid Python identifier")
        if not v[0].isupper():
            raise ValueError(f"Use case name '{v}' should start with uppercase letter")
        return v
    
    @field_validator('methods')
    def validate_methods_unique(cls, v):
        """Validate method names are unique."""
        method_names = [method.name for method in v]
        if len(method_names) != len(set(method_names)):
            raise ValueError("Use case cannot have duplicate method names")
        return v
    
    @model_validator(mode='after')
    def validate_dependencies(self):
        """Validate dependency references."""
        if isinstance(self.dependencies, list):
            # Convert list to DependencyConfig for consistency
            self.dependencies = DependencyConfig(services=self.dependencies)
        
        if isinstance(self.error_handling, dict):
            # Convert dict to ErrorHandlingConfig for consistency
            self.error_handling = ErrorHandlingConfig(**self.error_handling)
        
        return self


class BusinessRulesConfig(BaseModel):
    """Configuration for business rules and validation."""
    
    rules: List[BusinessRuleConfig] = Field(..., description="Business rules")
    validation_groups: List[ValidationGroupConfig] = Field(default_factory=list, description="Validation groups")
    error_handling: Optional[ErrorHandlingConfig] = Field(default=None, description="Error handling configuration")
    
    @field_validator('rules')
    def validate_rules_unique(cls, v):
        """Validate rule names are unique."""
        rule_names = [rule.name for rule in v]
        if len(rule_names) != len(set(rule_names)):
            raise ValueError("Business rules cannot have duplicate names")
        return v
    
    @model_validator(mode='after')
    def validate_group_rule_references(self):
        """Validate validation groups reference existing rules."""
        rule_names = {rule.name for rule in self.rules}
        
        for group in self.validation_groups:
            for rule_name in group.rules:
                if rule_name not in rule_names:
                    raise ValueError(f"Validation group '{group.name}' references unknown rule '{rule_name}'")
        
        return self


class UseCaseDomainConfig(BaseModel):
    """Configuration for use case domain with business logic orchestration."""
    
    # Use case configuration
    name: str = Field(..., description="Use case domain name")
    description: Optional[str] = Field(default=None, description="Use case domain description")
    package: Optional[str] = Field(default=None, description="Python package name")
    
    # Use case specific configurations
    usecase: Optional[UseCaseConfig] = Field(default=None, description="Use case configuration")
    business_rules: Optional[BusinessRulesConfig] = Field(default=None, description="Business rules configuration")
    
    # Integration with other layers
    entity_dependencies: List[str] = Field(default_factory=list, description="Entity dependencies")
    repository_dependencies: List[str] = Field(default_factory=list, description="Repository dependencies")
    external_dependencies: List[str] = Field(default_factory=list, description="External service dependencies")
    
    @field_validator('name')
    def validate_use_case_domain_name(cls, v):
        """Validate use case domain name."""
        if not v.isidentifier():
            raise ValueError(f"Use case domain name '{v}' is not a valid Python identifier")
        if not v[0].isupper():
            raise ValueError(f"Use case domain name '{v}' should start with uppercase letter")
        return v
    
    @model_validator(mode='after')
    def generate_defaults_and_validate(self):
        """Generate default values and validate use case domain configuration."""
        name = self.name
        
        # Generate package name if not provided
        if self.package is None:
            # Convert PascalCase to snake_case
            package = ''
            for i, char in enumerate(name):
                if char.isupper() and i > 0:
                    package += '_'
                package += char.lower()
            self.package = package
        
        # Validate business rule references in use case methods
        if self.usecase and self.business_rules:
            rule_names = {rule.name for rule in self.business_rules.rules}
            
            for method in self.usecase.methods:
                for rule_name in method.business_rules:
                    if rule_name not in rule_names:
                        logger.warning(
                            f"Use case method '{method.name}' references unknown business rule '{rule_name}'"
                        )
        
        return self
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True,
        "extra": "forbid",  # Reject unknown fields
    }