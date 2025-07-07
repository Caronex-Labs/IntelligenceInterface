#!/usr/bin/env python3
"""
FastAPI SQLModel Project Generator - MCP Server

Provides Model Context Protocol (MCP) server implementation for the FastAPI
SQLModel project generator, allowing AI assistants to directly interact with
the template generation system.
"""

import json
import logging
import sys
import os
from typing import Dict, Any
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import fastmcp
from pydantic import ValidationError

# Now import from the project
from generator.interface.mcp.server import create_mcp_server
from generator.types.models import (
    EntityDomainConfig,
    UseCaseConfig,
    ServiceConfig,
    Configuration
)
from generator.utils.logging_utils import configure_logging, get_logger

# Configure logging
configure_logging(level=logging.INFO, json_format=False)
logger = get_logger(__name__)

# Initialize FastMCP server
mcp = fastmcp.FastMCP("FastAPI SQLModel Generator")

# Create our internal server instance for business logic
_internal_server = create_mcp_server()

@mcp.tool()
def initialize_project(
    project_name: str,
    output_dir: str,
    description: str = None,
    author: str = None,
    auth_type: str = "none",
    clean_existing: bool = False
) -> Dict[str, Any]:
    """
    Initialize a new FastAPI SQLModel project with complete directory structure.
    
    Args:
        project_name: Name of the project to create
        output_dir: Directory where the project should be created
        description: Optional project description
        author: Optional project author
        auth_type: Authentication type (none, email_password)
        clean_existing: Whether to clean existing directory before initialization
        
    Returns:
        Dictionary with success status and details
    """
    return _internal_server.init(
        project_name=project_name,
        output_dir=output_dir,
        auth_type=auth_type,
        clean_existing=clean_existing
    )

@mcp.tool()
def generate_domain_from_config(
    domain_config: str,
    output_dir: str,
    clean_existing: bool = False,
    validate_syntax: bool = True,
    validate_imports: bool = False
) -> Dict[str, Any]:
    """
    Generate domain code from EntityDomainConfig.
    
    Args:
        domain_config: JSON string containing EntityDomainConfig data
        output_dir: Output directory for generated code
        clean_existing: Whether to clean existing output directory
        validate_syntax: Whether to validate generated Python syntax
        validate_imports: Whether to validate import statements
        
    Returns:
        Dictionary with success status and details
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(domain_config)
        return _internal_server.gen_domain(config_dict, output_dir)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}"
        }

@mcp.tool()
def generate_usecase_domain(
    usecase_config: str,
    output_dir: str,
    clean_existing: bool = False
) -> Dict[str, Any]:
    """
    Generate use case domain with business logic orchestration.
    
    Args:
        usecase_config: JSON string containing UseCaseConfig data
        output_dir: Output directory for generated code
        clean_existing: Whether to clean existing output directory
        
    Returns:
        Dictionary with success status and details
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(usecase_config)
        return _internal_server.gen_usecase(config_dict, output_dir)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}"
        }

@mcp.tool()
def generate_service_from_config(
    service_config: str,
    output_dir: str,
    clean_existing: bool = False
) -> Dict[str, Any]:
    """
    Generate domain-agnostic service from ServiceDomainConfig.
    
    Args:
        service_config: JSON string containing ServiceDomainConfig data
        output_dir: Output directory for generated code
        clean_existing: Whether to clean existing output directory
        
    Returns:
        Dictionary with success status and details
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(service_config)
        return _internal_server.gen_service(config_dict, output_dir)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}"
        }

@mcp.tool()
def generate_all_layers(
    config: str,
    output_dir: str,
    clean_existing: bool = False
) -> Dict[str, Any]:
    """
    Generate all layers from comprehensive configuration.
    
    Args:
        config: JSON string containing comprehensive configuration
        output_dir: Output directory for generated code
        clean_existing: Whether to clean existing output
        
    Returns:
        Dictionary with success status and details
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(config)
        return _internal_server.gen_all(config_dict, output_dir, clean_existing)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}"
        }

@mcp.tool()
def validate_configuration(
    config: str
) -> Dict[str, Any]:
    """
    Validate a configuration object for correctness.
    
    Args:
        config: JSON string containing configuration data
        
    Returns:
        Dictionary with validation status and any errors/warnings
    """
    try:
        # Parse JSON string to dictionary
        config_dict = json.loads(config)
        return _internal_server.validate_config(config_dict)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "valid": False,
            "error": f"Invalid JSON format: {str(e)}"
        }

@mcp.tool()
def get_usage_examples(
    command: str = None
) -> Dict[str, Any]:
    """
    Get usage instructions and examples for commands.
    
    Args:
        command: Specific command to get usage for (optional)
        
    Returns:
        Dictionary with usage information
    """
    return _internal_server.get_usage(command)

@mcp.tool()
def get_configuration_schema(
    schema_type: str = "all",
    show_sample: bool = False
) -> Dict[str, Any]:
    """
    Get configuration schemas for different config types.
    
    Args:
        schema_type: Type of schema to retrieve (entity-domain, usecase, service, configuration, all)
        show_sample: Show sample config instead of schema
        
    Returns:
        Dictionary with schema information
    """
    return _internal_server.get_schema(schema_type, show_sample)

@mcp.tool()
def add_domain_to_project(
    name: str,
    output_dir: str,
    layers: str = "core,interface"
) -> Dict[str, Any]:
    """
    Add a new domain to the project.
    
    Args:
        name: Name of the domain to create
        output_dir: Output directory
        layers: Comma-separated list of layers
        
    Returns:
        Dictionary with success status and details
    """
    return _internal_server.add_domain(name, layers, output_dir)

@mcp.tool()
def get_workflow_guide() -> Dict[str, Any]:
    """
    Get complete 6-step workflow guide for project generation.
    
    Returns:
        Dictionary with complete workflow guidance including:
        - Step-by-step instructions
        - CLI and MCP command examples
        - Best practices and troubleshooting
    """
    from generator.core.schema import SchemaProvider
    
    # Create schema provider for workflow guide
    schema_provider = SchemaProvider(".")
    return schema_provider.get_workflow_guide(interface_type="mcp")

@mcp.resource("schema://entity-domain-config")
def get_entity_domain_config_schema():
    """Get the JSON schema for EntityDomainConfig."""
    return EntityDomainConfig.model_json_schema()

@mcp.resource("schema://usecase-config")
def get_usecase_config_schema():
    """Get the JSON schema for UseCaseConfig."""
    return UseCaseConfig.model_json_schema()

@mcp.resource("schema://service-config")
def get_service_config_schema():
    """Get the JSON schema for ServiceConfig."""
    return ServiceConfig.model_json_schema()

@mcp.resource("schema://configuration")
def get_configuration_schema():
    """Get the JSON schema for Configuration."""
    return Configuration.model_json_schema()

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

if __name__ == "__main__":
    logger.info("Starting FastAPI SQLModel Generator MCP Server")
    mcp.run()