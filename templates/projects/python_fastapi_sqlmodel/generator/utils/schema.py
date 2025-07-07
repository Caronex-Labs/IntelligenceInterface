"""
Schema utilities for the FastAPI SQLModel generator.

This module provides utilities for extracting and formatting Pydantic model schemas,
ensuring a single source of truth for configuration schemas across CLI and MCP interfaces.
"""

import json
import yaml
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel

from ..types.models import (
    EntityDomainConfig,
    UseCaseConfig,
    ServiceConfig,
    Configuration,
    FieldConfig,
    EntityConfig,
    EndpointConfig,
    DomainConfig
)
from ..types.models.internal_models import SchemaInfo


class SchemaFormatter:
    """Handles schema extraction and formatting for different interfaces."""

    @staticmethod
    def get_model_schema(model_class: Type[BaseModel]) -> dict[str, Any]:
        """
        Extract JSON schema from a Pydantic model.
        
        Args:
            model_class: Pydantic model class
            
        Returns:
            JSON schema dictionary
        """
        return model_class.model_json_schema()

    @staticmethod
    def format_schema_for_cli(schema: dict[str, Any], indent: int = 2) -> str:
        """
        Format schema for CLI display in YAML-like format.
        
        Args:
            schema: JSON schema dictionary
            indent: Indentation spaces
            
        Returns:
            Formatted schema string for CLI
        """
        try:
            # Convert to YAML for better CLI readability
            return yaml.dump(schema, default_flow_style=False, indent=indent, sort_keys=False)
        except Exception:
            # Fallback to JSON if YAML fails
            return json.dumps(schema, indent=indent)

    @staticmethod 
    def format_schema_for_mcp(schema: dict[str, Any]) -> dict[str, Any]:
        """
        Format schema for MCP interface (returns as-is since MCP uses JSON).
        
        Args:
            schema: JSON schema dictionary
            
        Returns:
            Schema dictionary for MCP
        """
        return schema

    @staticmethod
    def get_simplified_schema(model_class: Type[BaseModel]) -> dict[str, Any]:
        """
        Get a simplified schema showing only required fields and types.
        
        Args:
            model_class: Pydantic model class
            
        Returns:
            Simplified schema dictionary
        """
        full_schema = model_class.model_json_schema()
        properties = full_schema.get('properties', {})
        required = full_schema.get('required', [])
        
        simplified = {}
        for field_name, field_info in properties.items():
            field_type = field_info.get('type', 'unknown')
            field_desc = field_info.get('description', '')
            is_required = field_name in required
            
            simplified[field_name] = {
                'type': field_type,
                'required': is_required,
                'description': field_desc
            }
            
            # Add enum values if present
            if 'enum' in field_info:
                simplified[field_name]['enum'] = field_info['enum']
                
            # Add default if present
            if 'default' in field_info:
                simplified[field_name]['default'] = field_info['default']
        
        return simplified


def get_model_schema(model_class: Type[BaseModel]) -> dict[str, Any]:
    """
    Get JSON schema for a Pydantic model.
    
    Args:
        model_class: Pydantic model class
        
    Returns:
        JSON schema dictionary
    """
    return SchemaFormatter.get_model_schema(model_class)


def format_schema_for_cli(schema: dict[str, Any]) -> str:
    """
    Format schema for CLI display.
    
    Args:
        schema: JSON schema dictionary
        
    Returns:
        YAML-formatted schema string
    """
    return SchemaFormatter.format_schema_for_cli(schema)


def format_schema_for_mcp(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Format schema for MCP interface.
    
    Args:
        schema: JSON schema dictionary
        
    Returns:
        Schema dictionary for MCP
    """
    return SchemaFormatter.format_schema_for_mcp(schema)


def get_all_schemas() -> dict[str, dict[str, Any]]:
    """
    Get schemas for all main configuration models.
    
    Returns:
        Dictionary mapping model names to their schemas
    """
    return {
        'entity_domain': get_model_schema(EntityDomainConfig),
        'usecase': get_model_schema(UseCaseConfig),
        'service': get_model_schema(ServiceConfig),
        'configuration': get_model_schema(Configuration),
        'field': get_model_schema(FieldConfig),
        'entity': get_model_schema(EntityConfig),
        'endpoint': get_model_schema(EndpointConfig),
        'domain': get_model_schema(DomainConfig)
    }


def get_schema_by_name(schema_name: str) -> dict[str, Any] | None:
    """
    Get schema by name.
    
    Args:
        schema_name: Name of the schema to retrieve
        
    Returns:
        Schema dictionary or None if not found
    """
    schemas = get_all_schemas()
    return schemas.get(schema_name.lower())


def get_usage_examples() -> dict[str, dict[str, str]]:
    """
    Get usage examples for each command with sample configurations.
    
    Returns:
        Dictionary with command examples
    """
    return {
        'init': {
            'cli': '''# Initialize a new FastAPI project
fastapi-sqlmodel-gen init --name "My API" --output ./my-api

# Initialize with email/password authentication
fastapi-sqlmodel-gen init --name "My API" --auth email_password --output ./my-api --clean''',
            'description': 'Initialize a new FastAPI SQLModel project with complete structure',
            'config_schema': 'No configuration file required - uses command arguments'
        },
        
        'gen_domain': {
            'cli': '''# Generate domain layer from configuration
fastapi-sqlmodel-gen gen-domain --config domain.yaml --output ./app

# Show schema before generating
fastapi-sqlmodel-gen gen-domain --config domain.yaml --output ./app --show-schema''',
            'description': 'Generate domain entities and exceptions from EntityDomainConfig',
            'config_schema': 'entity_domain'
        },
        
        'gen_repository': {
            'cli': '''# Generate repository layer
fastapi-sqlmodel-gen gen-repository --config domain.yaml --output ./app''',
            'description': 'Generate repository protocols and implementations from EntityDomainConfig',
            'config_schema': 'entity_domain'
        },
        
        'gen_usecase': {
            'cli': '''# Generate use case layer
fastapi-sqlmodel-gen gen-usecase --config usecase.yaml --output ./app''',
            'description': 'Generate use case orchestration and schemas from UseCaseConfig',
            'config_schema': 'usecase'
        },
        
        'gen_service': {
            'cli': '''# Generate domain-agnostic service
fastapi-sqlmodel-gen gen-service --config service.yaml --output ./app''',
            'description': 'Generate service protocols and implementations from ServiceConfig',
            'config_schema': 'service'
        },
        
        'gen_all': {
            'cli': '''# Generate all layers from comprehensive config
fastapi-sqlmodel-gen gen-all --config project.yaml --output ./app

# Clean existing and regenerate all
fastapi-sqlmodel-gen gen-all --config project.yaml --output ./app --clean''',
            'description': 'Generate complete project with all layers from comprehensive configuration',
            'config_schema': 'configuration'
        }
    }


def get_sample_configs() -> dict[str, BaseModel]:
    """
    Get sample configuration examples for each config type.
    
    Returns:
        Dictionary with actual Pydantic model instances
    """
    # Create actual Pydantic model instances instead of dictionaries
    sample_field_configs = [
        FieldConfig(
            name='email',
            type='EmailStr',
            required=True,
            unique=True,
            description='User email address'
        ),
        FieldConfig(
            name='first_name',
            type='str',
            required=True,
            description='User first name'
        ),
        FieldConfig(
            name='is_active',
            type='bool',
            required=True,
            default='true',
            description='Whether user is active'
        )
    ]
    
    sample_entity = EntityConfig(
        name='User',
        fields=sample_field_configs,
        relationships=[]
    )
    
    sample_endpoints = [
        EndpointConfig(
            method='POST',
            path='/',
            operation='create',
            description='Create a new user'
        ),
        EndpointConfig(
            method='GET',
            path='/{id}',
            operation='get_by_id',
            description='Get user by ID'
        )
    ]
    
    entity_domain_sample = EntityDomainConfig(
        name='User',
        description='User management domain',
        entities=[sample_entity],
        endpoints=sample_endpoints
    )
    
    usecase_sample = UseCaseConfig(
        name='UserUseCase',
        description='User management use case orchestration',
        methods=[
            {
                'name': 'create_user',
                'description': 'Create a new user account',
                'dependencies': ['UserRepository'],
                'orchestration_steps': [
                    'validate_user_data',
                    'check_email_uniqueness',
                    'create_user_entity',
                    'save_to_repository'
                ]
            }
        ]
    )
    
    service_sample = ServiceConfig(
        name='EmailService',
        description='Email sending service',
        methods=[
            {
                'name': 'send_email',
                'parameters': [
                    FieldConfig(
                        name='to_email',
                        type='EmailStr',
                        required=True,
                        description='Recipient email address'
                    ),
                    FieldConfig(
                        name='subject',
                        type='str',
                        required=True,
                        description='Email subject'
                    ),
                    FieldConfig(
                        name='body',
                        type='str',
                        required=True,
                        description='Email body content'
                    )
                ],
                'return_type': 'bool',
                'description': 'Send an email and return success status'
            }
        ],
        dependencies=[]
    )
    
    return {
        'entity_domain': entity_domain_sample,
        'usecase': usecase_sample,
        'service': service_sample
    }
