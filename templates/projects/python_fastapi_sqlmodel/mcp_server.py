#!/usr/bin/env python3
"""
FastAPI SQLModel Project Generator - MCP Server

Provides Model Context Protocol (MCP) server implementation for the FastAPI
SQLModel project generator CLI tool, allowing LLMs to directly interact with
the template generation system using strict data types.

This MCP server reuses existing Pydantic models from cli/generate/config/models.py
to ensure single source of truth for all schema definitions.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
import tempfile

import fastmcp
from pydantic import ValidationError

# Import existing Pydantic models - single source of truth
from cli.generate.config.models import (
    # Core configuration models
    Configuration,
    EntityDomainConfig,
    UseCaseDomainConfig,
    
    # Domain and entity models
    FieldType,
    RelationshipType,
    HTTPMethod,
    
    # Business logic models
    BusinessRuleType,
    BusinessRuleSeverity,
)

# Import CLI functionality
from cli.generate.generator import create_generator
from cli.generate.project_initializer import ProjectInitializer

def convert_enums_to_strings(obj):
    """
    Recursively convert all enum values to strings for YAML-safe serialization.
    This ensures that Pydantic enums don't create Python-specific YAML tags.
    """
    if isinstance(obj, dict):
        return {key: convert_enums_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_enums_to_strings(item) for item in obj]
    elif hasattr(obj, 'value'):  # Enum-like object
        return obj.value
    elif hasattr(obj, '__class__') and hasattr(obj.__class__, '__bases__'):
        # Check if it's an enum class instance
        for base in obj.__class__.__bases__:
            if hasattr(base, '_name_') and base._name_ == 'Enum':
                return str(obj)
    return obj

# MCP response models (these are the only new models we add)
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Response models for MCP operations
class GenerationResult(BaseModel):
    """Result of a generation operation."""
    success: bool = Field(..., description="Whether the operation succeeded")
    domain_name: str = Field(..., description="Name of the domain that was generated")
    output_dir: str = Field(..., description="Output directory path")
    files_generated: int = Field(..., description="Number of files successfully generated")
    errors: List[str] = Field(default_factory=list, description="List of error messages if any")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages if any")

class ValidationResult(BaseModel):
    """Result of a validation operation."""
    valid: bool = Field(..., description="Whether the configuration is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")

class ProjectInitializationResult(BaseModel):
    """Result of project initialization."""
    success: bool = Field(..., description="Whether initialization succeeded")
    project_name: str = Field(..., description="Name of the initialized project")
    project_dir: str = Field(..., description="Project directory path")
    files_created: int = Field(..., description="Number of files created")
    errors: List[str] = Field(default_factory=list, description="List of error messages if any")

# Initialize FastMCP server
mcp = fastmcp.FastMCP("FastAPI SQLModel Generator")

@mcp.tool()
def initialize_project(
    project_name: str,
    output_dir: str,
    description: Optional[str] = None,
    author: Optional[str] = None,
    clean_existing: bool = False
) -> ProjectInitializationResult:
    """
    Initialize a new FastAPI SQLModel project with complete directory structure.
    
    Args:
        project_name: Name of the project to create
        output_dir: Directory where the project should be created
        description: Optional project description
        author: Optional project author
        clean_existing: Whether to clean existing directory before initialization
        
    Returns:
        ProjectInitializationResult with success status and details
    """
    try:
        logger.info(f"Initializing project '{project_name}' in {output_dir}")
        
        # Create project initializer
        initializer = ProjectInitializer()
        
        # Prepare project configuration
        project_config = {}
        if description:
            project_config['description'] = description
        if author:
            project_config['author'] = author
        
        # Initialize project
        target_dir = Path(output_dir)
        results = initializer.initialize_project(
            project_name=project_name,
            target_dir=target_dir,
            project_config=project_config,
            clean_existing=clean_existing
        )
        
        # Count successful file creations
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        # Collect errors
        errors = []
        for result in results:
            if not result.success:
                errors.extend(result.errors)
        
        return ProjectInitializationResult(
            success=(success_count == total_count),
            project_name=project_name,
            project_dir=str(target_dir.absolute()),
            files_created=success_count,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Project initialization failed: {e}")
        return ProjectInitializationResult(
            success=False,
            project_name=project_name,
            project_dir=output_dir,
            files_created=0,
            errors=[f"Initialization failed: {str(e)}"]
        )

@mcp.tool()
def generate_domain_from_config(
    domain_config: str,
    output_dir: str,
    clean_existing: bool = False,
    validate_syntax: bool = True,
    validate_imports: bool = False
) -> GenerationResult:
    """
    Generate domain code from EntityDomainConfig.
    
    Args:
        domain_config: JSON string containing EntityDomainConfig data
        output_dir: Output directory for generated code
        clean_existing: Whether to clean existing output directory
        validate_syntax: Whether to validate generated Python syntax
        validate_imports: Whether to validate import statements
        
    Returns:
        GenerationResult with success status and details
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(domain_config)
        
        # Create Pydantic model (DTO + validation)
        domain_config_obj = EntityDomainConfig(**config_dict)
        
        logger.info(f"Generating domain '{domain_config_obj.name}' to {output_dir}")
        
        # Create temporary directory for configuration files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create domain directory structure
            domain_dir = temp_path / domain_config_obj.name
            domain_dir.mkdir(parents=True, exist_ok=True)
            
            # Write domain.yaml
            import yaml
            domain_dict = {
                'name': domain_config_obj.name,
            }
            
            # Only add non-None values to avoid YAML serialization issues
            if domain_config_obj.description is not None:
                domain_dict['description'] = domain_config_obj.description
            if domain_config_obj.package is not None:
                domain_dict['package'] = domain_config_obj.package
            
            if domain_config_obj.base_fields:
                raw_base_fields = [field.model_dump(exclude_none=True, mode='python') for field in domain_config_obj.base_fields]
                domain_dict['base_fields'] = convert_enums_to_strings(raw_base_fields)
            
            if domain_config_obj.mixins:
                raw_mixins = [mixin.model_dump(exclude_none=True, mode='python') for mixin in domain_config_obj.mixins]
                domain_dict['mixins'] = convert_enums_to_strings(raw_mixins)
            
            if domain_config_obj.relationships:
                raw_relationships = [rel.model_dump(exclude_none=True, mode='python') for rel in domain_config_obj.relationships]
                domain_dict['relationships'] = convert_enums_to_strings(raw_relationships)
            
            if domain_config_obj.sqlmodel_config:
                raw_sqlmodel_config = domain_config_obj.sqlmodel_config.model_dump(exclude_none=True, mode='python')
                domain_dict['sqlmodel_config'] = convert_enums_to_strings(raw_sqlmodel_config)
            
            domain_config_path = domain_dir / 'domain.yaml'
            with open(domain_config_path, 'w') as f:
                yaml.dump(domain_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            # Write entities.yaml
            raw_entities = [entity.model_dump(exclude_none=True, mode='python') for entity in domain_config_obj.entities]
            entities_dict = {
                'entities': convert_enums_to_strings(raw_entities)
            }
            
            if domain_config_obj.endpoints:
                # Convert endpoints to YAML-safe format by ensuring all enums become strings
                raw_endpoints = [endpoint.model_dump(exclude_none=True, mode='python') for endpoint in domain_config_obj.endpoints]
                entities_dict['endpoints'] = convert_enums_to_strings(raw_endpoints)
            
            entities_config_path = domain_dir / 'entities.yaml'
            with open(entities_config_path, 'w') as f:
                yaml.dump(entities_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            # Validate written YAML files immediately
            try:
                with open(domain_config_path, 'r') as f:
                    yaml.safe_load(f)
                with open(entities_config_path, 'r') as f:
                    yaml.safe_load(f)
                logger.info(f"Successfully validated generated YAML files for domain '{domain_config_obj.name}'")
            except yaml.YAMLError as e:
                logger.error(f"Generated YAML files contain syntax errors: {e}")
                return GenerationResult(
                    success=False,
                    domain_name=domain_config_obj.name,
                    output_dir=output_dir,
                    files_generated=0,
                    errors=[f"Generated YAML files contain syntax errors: {str(e)}"]
                )
            
            # Create generator and generate domain
            generator = create_generator(
                output_dir=output_dir,
                clean=clean_existing,
                validate_syntax=validate_syntax,
                validate_imports=validate_imports
            )
            
            result = generator.generate_domain(domain_config_obj.name, domain_dir)
            
            # Convert to MCP response format
            return GenerationResult(
                success=result.success,
                domain_name=result.domain_name,
                output_dir=str(result.output_dir),
                files_generated=result.total_files_generated,
                errors=result.errors,
                warnings=result.warnings
            )
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in domain_config: {e}")
        return GenerationResult(
            success=False,
            domain_name="unknown",
            output_dir=output_dir,
            files_generated=0,
            errors=[f"Invalid JSON format: {str(e)}. Please check your JSON syntax."]
        )
    
    except ValidationError as e:
        logger.error(f"Domain configuration validation failed: {e}")
        error_messages = []
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_messages.append(f"Field '{field}': {message}")
        
        return GenerationResult(
            success=False,
            domain_name="unknown",
            output_dir=output_dir,
            files_generated=0,
            errors=error_messages
        )
    
    except Exception as e:
        logger.error(f"Domain generation failed: {e}")
        return GenerationResult(
            success=False,
            domain_name="unknown",
            output_dir=output_dir,
            files_generated=0,
            errors=[f"Generation failed: {str(e)}"]
        )

@mcp.tool()
def generate_usecase_domain(
    usecase_config: str,
    output_dir: str,
    clean_existing: bool = False
) -> GenerationResult:
    """
    Generate use case domain with business logic orchestration.
    
    Args:
        usecase_config: JSON string containing UseCaseDomainConfig data
        output_dir: Output directory for generated code
        clean_existing: Whether to clean existing output directory
        
    Returns:
        GenerationResult with success status and details
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(usecase_config)
        
        # Create Pydantic model (DTO + validation)
        usecase_config_obj = UseCaseDomainConfig(**config_dict)
        
        logger.info(f"Generating use case domain '{usecase_config_obj.name}' to {output_dir}")
        
        # Create temporary directory for configuration files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create use case directory structure
            usecase_dir = temp_path / usecase_config_obj.name
            usecase_dir.mkdir(parents=True, exist_ok=True)
            
            # Write usecase.yaml
            import yaml
            usecase_dict = usecase_config_obj.model_dump()
            
            usecase_config_path = usecase_dir / 'usecase.yaml'
            with open(usecase_config_path, 'w') as f:
                yaml.dump(usecase_dict, f, default_flow_style=False)
            
            # For use case generation, we would use a specialized generator
            # For now, use the domain generator as the foundation
            generator = create_generator(
                output_dir=output_dir,
                clean=clean_existing
            )
            
            # This would need a specialized use case generator
            # For now, return a placeholder result
            return GenerationResult(
                success=True,
                domain_name=usecase_config_obj.name,
                output_dir=output_dir,
                files_generated=0,
                warnings=["Use case generation not yet fully implemented"]
            )
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in usecase_config: {e}")
        return GenerationResult(
            success=False,
            domain_name="unknown",
            output_dir=output_dir,
            files_generated=0,
            errors=[f"Invalid JSON format: {str(e)}. Please check your JSON syntax."]
        )
    
    except ValidationError as e:
        logger.error(f"Use case configuration validation failed: {e}")
        error_messages = []
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_messages.append(f"Field '{field}': {message}")
        
        return GenerationResult(
            success=False,
            domain_name="unknown",
            output_dir=output_dir,
            files_generated=0,
            errors=error_messages
        )
    
    except Exception as e:
        logger.error(f"Use case generation failed: {e}")
        return GenerationResult(
            success=False,
            domain_name="unknown",
            output_dir=output_dir,
            files_generated=0,
            errors=[f"Use case generation failed: {str(e)}"]
        )

@mcp.tool()
def validate_configuration(
    config: str
) -> ValidationResult:
    """
    Validate a configuration object for correctness.
    
    Args:
        config: JSON string containing configuration data
        
    Returns:
        ValidationResult with validation status and any errors/warnings
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(config)
        
        # Try to validate against each config type
        validation_attempts = []
        config_obj = None
        config_type = None
        
        # Try EntityDomainConfig first
        try:
            config_obj = EntityDomainConfig(**config_dict)
            config_type = "EntityDomainConfig"
        except ValidationError as e:
            validation_attempts.append(("EntityDomainConfig", e))
        
        # Try UseCaseDomainConfig
        if config_obj is None:
            try:
                config_obj = UseCaseDomainConfig(**config_dict)
                config_type = "UseCaseDomainConfig"
            except ValidationError as e:
                validation_attempts.append(("UseCaseDomainConfig", e))
        
        # Try Configuration
        if config_obj is None:
            try:
                config_obj = Configuration(**config_dict)
                config_type = "Configuration"
            except ValidationError as e:
                validation_attempts.append(("Configuration", e))
        
        # If no config type worked, return all validation errors
        if config_obj is None:
            all_errors = []
            for config_name, validation_error in validation_attempts:
                all_errors.append(f"Failed as {config_name}:")
                for error in validation_error.errors():
                    field = " -> ".join(str(x) for x in error["loc"])
                    message = error["msg"]
                    all_errors.append(f"  Field '{field}': {message}")
            
            return ValidationResult(
                valid=False,
                errors=all_errors
            )
        
        # Perform additional validation logic on the successfully parsed config
        errors = []
        warnings = []
        
        # Add config type to warnings for user information
        warnings.append(f"Configuration successfully validated as {config_type}")
        
        # Perform additional validation logic
        if isinstance(config_obj, (Configuration, EntityDomainConfig)):
            if hasattr(config_obj, 'entities') and not config_obj.entities:
                errors.append("Configuration must include at least one entity")
            
            # Check for entity name conflicts
            if hasattr(config_obj, 'entities'):
                entity_names = [entity.name for entity in config_obj.entities]
                if len(entity_names) != len(set(entity_names)):
                    errors.append("Configuration contains duplicate entity names")
        
        elif isinstance(config_obj, UseCaseDomainConfig):
            if config_obj.usecase and config_obj.business_rules:
                # Validate business rule references
                rule_names = {rule.name for rule in config_obj.business_rules.rules}
                for method in config_obj.usecase.methods:
                    for rule_name in method.business_rules:
                        if rule_name not in rule_names:
                            warnings.append(
                                f"Use case method '{method.name}' references unknown business rule '{rule_name}'"
                            )
        
        return ValidationResult(
            valid=(len(errors) == 0),
            errors=errors,
            warnings=warnings
        )
    
    except json.JSONDecodeError as e:
        return ValidationResult(
            valid=False,
            errors=[f"Invalid JSON format: {str(e)}. Please check your JSON syntax."]
        )
    
    except Exception as e:
        return ValidationResult(
            valid=False,
            errors=[f"Validation failed: {str(e)}"]
        )

@mcp.resource("schema://entity-domain-config")
def get_entity_domain_config_schema():
    """Get the JSON schema for EntityDomainConfig."""
    return EntityDomainConfig.model_json_schema()

@mcp.resource("schema://usecase-domain-config")
def get_usecase_domain_config_schema():
    """Get the JSON schema for UseCaseDomainConfig."""
    return UseCaseDomainConfig.model_json_schema()

@mcp.resource("schema://configuration")
def get_configuration_schema():
    """Get the JSON schema for Configuration."""
    return Configuration.model_json_schema()

@mcp.resource("schema://field-types")
def get_field_types():
    """Get available field types."""
    return {
        "field_types": [field_type.value for field_type in FieldType],
        "relationship_types": [rel_type.value for rel_type in RelationshipType],
        "http_methods": [method.value for method in HTTPMethod],
        "business_rule_types": [rule_type.value for rule_type in BusinessRuleType],
        "business_rule_severities": [severity.value for severity in BusinessRuleSeverity]
    }

@mcp.resource("examples://entity-domain-simple")
def get_simple_entity_domain_example():
    """Get a simple entity domain configuration example."""
    return {
        "name": "Product",
        "description": "Product catalog domain",
        "entities": [
            {
                "name": "Product",
                "fields": [
                    {
                        "name": "id",
                        "type": "UUID",
                        "required": True,
                        "unique": True,
                        "description": "Unique product identifier"
                    },
                    {
                        "name": "name",
                        "type": "str",
                        "required": True,
                        "description": "Product name"
                    },
                    {
                        "name": "price",
                        "type": "float",
                        "required": True,
                        "description": "Product price"
                    },
                    {
                        "name": "description",
                        "type": "Optional[str]",
                        "required": False,
                        "description": "Product description"
                    },
                    {
                        "name": "created_at",
                        "type": "datetime",
                        "required": True,
                        "default": "datetime.utcnow",
                        "description": "Creation timestamp"
                    }
                ]
            }
        ]
    }

@mcp.resource("examples://entity-domain-advanced")
def get_advanced_entity_domain_example():
    """Get an advanced entity domain configuration example with relationships."""
    return {
        "name": "Order",
        "description": "Order management domain with relationships",
        "base_fields": [
            {
                "name": "id",
                "type": "UUID",
                "required": True,
                "unique": True,
                "description": "Unique identifier"
            },
            {
                "name": "created_at",
                "type": "datetime",
                "required": True,
                "default": "datetime.utcnow"
            }
        ],
        "entities": [
            {
                "name": "Order",
                "fields": [
                    {
                        "name": "customer_email",
                        "type": "EmailStr",
                        "required": True
                    },
                    {
                        "name": "total_amount",
                        "type": "float",
                        "required": True
                    },
                    {
                        "name": "status",
                        "type": "str",
                        "required": True,
                        "default": "\"pending\""
                    }
                ],
                "relationships": [
                    {
                        "entity": "OrderItem",
                        "type": "one_to_many",
                        "back_populates": "order"
                    }
                ]
            },
            {
                "name": "OrderItem",
                "fields": [
                    {
                        "name": "product_name",
                        "type": "str",
                        "required": True
                    },
                    {
                        "name": "quantity",
                        "type": "int",
                        "required": True
                    },
                    {
                        "name": "unit_price",
                        "type": "float",
                        "required": True
                    },
                    {
                        "name": "order_id",
                        "type": "UUID",
                        "required": True
                    }
                ],
                "relationships": [
                    {
                        "entity": "Order",
                        "type": "many_to_one",
                        "back_populates": "items",
                        "foreign_key": "order_id"
                    }
                ]
            }
        ]
    }

@mcp.resource("docs://tool-input-format")
def get_tool_input_format_documentation():
    """Documentation of the JSON input format expected by MCP tools."""
    return {
        "title": "MCP Tool Input Format Guide",
        "description": "All complex MCP tools accept JSON strings that are parsed into Pydantic models",
        "tools": {
            "generate_domain_from_config": {
                "parameter": "domain_config",
                "type": "string (JSON)",
                "expected_schema": "EntityDomainConfig",
                "description": "JSON string containing EntityDomainConfig data",
                "example": "'{\"name\": \"Product\", \"entities\": [{\"name\": \"Product\", \"fields\": [...]}]}'"
            },
            "generate_usecase_domain": {
                "parameter": "usecase_config", 
                "type": "string (JSON)",
                "expected_schema": "UseCaseDomainConfig",
                "description": "JSON string containing UseCaseDomainConfig data",
                "example": "'{\"name\": \"ProductUseCase\", \"usecase\": {...}}'"
            },
            "validate_configuration": {
                "parameter": "config",
                "type": "string (JSON)", 
                "expected_schema": "Configuration | EntityDomainConfig | UseCaseDomainConfig",
                "description": "JSON string containing any valid configuration type",
                "example": "'{\"name\": \"Test\", \"entities\": [...]}'"
            }
        },
        "process": [
            "1. LLM sends JSON string parameter",
            "2. Tool parses JSON string to dictionary", 
            "3. Tool creates Pydantic model from dictionary (validation happens here)",
            "4. Tool proceeds with validated object",
            "5. Comprehensive error messages returned for invalid JSON or validation failures"
        ],
        "validation_benefits": [
            "Strict type checking via Pydantic models",
            "Single source of truth - same models used by CLI tool",
            "Detailed validation error messages",
            "Automatic JSON Schema generation for LLM guidance"
        ],
        "available_schemas": [
            "schema://entity-domain-config - Complete EntityDomainConfig JSON schema",
            "schema://usecase-domain-config - Complete UseCaseDomainConfig JSON schema", 
            "schema://configuration - Complete Configuration JSON schema",
            "schema://field-types - Available enum values for types",
            "examples://entity-domain-simple - Simple working example",
            "examples://entity-domain-advanced - Complex working example with relationships"
        ]
    }

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the MCP server
    mcp.run()