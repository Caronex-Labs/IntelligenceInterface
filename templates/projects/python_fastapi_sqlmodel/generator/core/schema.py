"""
Schema Provider for FastAPI SQLModel Generator.

Handles schema retrieval, usage examples, and output formatting
for both CLI and MCP interfaces.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Type
import json

from pydantic import BaseModel

from ..utils.type_aliases import PathLike
from ..types.models.internal_models import SchemaInfo
from ..utils.logging_utils import get_logger
from ..utils.schema import (
    get_all_schemas,
    get_schema_by_name,
    format_schema_for_cli,
    format_schema_for_mcp,
    get_usage_examples,
    get_sample_configs
)

logger = get_logger(__name__)


class SchemaProvider:
    """
    Core schema provider class.
    
    Provides configuration schemas, usage examples, and formatting
    for both CLI and MCP interfaces.
    """

    AVAILABLE_SCHEMAS = ["entity-domain", "usecase", "service", "configuration"]
    OUTPUT_FORMATS = ["yaml", "json"]

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize schema provider.
        
        Args:
            target_dir: Target project directory
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        self.logger.debug("SchemaProvider initialized", extra={
            "target_dir": str(self.target_dir),
            "available_schemas": self.AVAILABLE_SCHEMAS,
            "operation": "init"
        })

    def get_schema(self, schema_type: str = "all", output_format: str = "yaml", 
                   show_sample: bool = False, interface_type: str = "cli") -> SchemaInfo:
        """
        Get configuration schema(s).
        
        Args:
            schema_type: Type of schema ("entity-domain", "usecase", "service", "configuration", "all")
            output_format: Output format ("yaml", "json")
            show_sample: Return sample configuration instead of schema
            interface_type: Interface type ("cli", "mcp") for formatting
            
        Returns:
            SchemaInfo object with schema information
        """
        self.logger.debug("Getting schema", extra={
            "schema_type": schema_type,
            "output_format": output_format,
            "show_sample": show_sample,
            "interface_type": interface_type,
            "operation": "get_schema"
        })
        
        try:
            with self.logger.timed_operation("schema_retrieval", extra={"schema_type": schema_type}):
                if show_sample:
                    result = self._get_sample_configs(schema_type, output_format, interface_type)
                else:
                    result = self._get_schemas(schema_type, output_format, interface_type)
            
            self.logger.info("Schema retrieved successfully", extra={
                "schema_type": schema_type,
                "output_format": output_format,
                "show_sample": show_sample,
                "interface_type": interface_type,
                "operation": "get_schema",
                "phase": "complete"
            })
            
            return result
            
        except Exception as e:
            self.logger.error("Schema retrieval failed", exc_info=True, extra={
                "schema_type": schema_type,
                "output_format": output_format,
                "operation": "get_schema",
                "phase": "failed"
            })
            return SchemaInfo(
                name=schema_type,
                schema={"error": str(e)},
                format=output_format,
                description=f"Error retrieving schema for {schema_type}",
                metadata={
                    "success": False,
                    "error": str(e),
                    "schema_type": schema_type,
                    "output_format": output_format
                }
            )

    def get_usage(self, command: Optional[str] = None, interface_type: str = "cli") -> SchemaInfo:
        """
        Get usage examples and instructions.
        
        Args:
            command: Specific command to show usage for (None for all)
            interface_type: Interface type ("cli", "mcp") for formatting
            
        Returns:
            SchemaInfo object with usage information
        """
        self.logger.debug("Getting usage information", extra={
            "command": command,
            "interface_type": interface_type,
            "operation": "get_usage"
        })
        
        try:
            with self.logger.timed_operation("usage_retrieval", extra={"command": command}):
                usage_examples = get_usage_examples()
                
                if command:
                    # Get usage for specific command
                    cmd_key = command.replace('-', '_')
                    if cmd_key in usage_examples:
                        result = self._format_single_usage(usage_examples[cmd_key], command, interface_type)
                    else:
                        result = SchemaInfo(
                            name=f"usage_{command}",
                            schema={"error": f"Unknown command: {command}"},
                            format="text",
                            description=f"Usage information for command: {command}",
                            metadata={
                                "success": False,
                                "error": f"Unknown command: {command}",
                                "available_commands": list(usage_examples.keys())
                            }
                        )
                else:
                    # Get usage for all commands
                    result = self._format_all_usage(usage_examples, interface_type)
            
            self.logger.info("Usage information retrieved successfully", extra={
                "command": command,
                "interface_type": interface_type,
                "operation": "get_usage",
                "phase": "complete"
            })
            
            return result
            
        except Exception as e:
            self.logger.error("Usage retrieval failed", exc_info=True, extra={
                "command": command,
                "interface_type": interface_type,
                "operation": "get_usage",
                "phase": "failed"
            })
            return SchemaInfo(
                name=f"usage_{command or 'all'}",
                schema={"error": str(e)},
                format="text",
                description="Usage information retrieval failed",
                metadata={
                    "success": False,
                    "error": str(e),
                    "command": command,
                    "interface_type": interface_type
                }
            )

    def list_available_schemas(self) -> List[str]:
        """
        Get list of available schema types.
        
        Returns:
            List of available schema types
        """
        return self.AVAILABLE_SCHEMAS.copy()

    def list_available_formats(self) -> List[str]:
        """
        Get list of available output formats.
        
        Returns:
            List of available output formats
        """
        return self.OUTPUT_FORMATS.copy()

    def validate_schema_type(self, schema_type: str) -> bool:
        """
        Validate if schema type is available.
        
        Args:
            schema_type: Schema type to validate
            
        Returns:
            True if schema type is valid
        """
        return schema_type in self.AVAILABLE_SCHEMAS or schema_type == "all"

    def validate_output_format(self, output_format: str) -> bool:
        """
        Validate if output format is supported.
        
        Args:
            output_format: Output format to validate
            
        Returns:
            True if output format is valid
        """
        return output_format in self.OUTPUT_FORMATS

    def _get_schemas(self, schema_type: str, output_format: str, interface_type: str) -> SchemaInfo:
        """Get configuration schemas."""
        if schema_type == "all":
            schemas = get_all_schemas()
            formatted_schemas = {}
            
            for name, schema in schemas.items():
                if interface_type == "mcp":
                    formatted_schemas[name] = self._format_for_mcp(schema, output_format)
                else:
                    formatted_schemas[name] = self._format_for_cli(schema, output_format)
            
            return SchemaInfo(
                name="all_schemas",
                schema=formatted_schemas,
                format=output_format,
                description="All available configuration schemas",
                metadata={
                    "success": True,
                    "schema_type": "all",
                    "output_format": output_format,
                    "interface_type": interface_type,
                    "schema_count": len(formatted_schemas)
                }
            )
        else:
            schema_name = schema_type.replace('-', '_')
            schema = get_schema_by_name(schema_name)
            
            if schema:
                if interface_type == "mcp":
                    formatted_schema = self._format_for_mcp(schema, output_format)
                else:
                    formatted_schema = self._format_for_cli(schema, output_format)
                
                return SchemaInfo(
                    name=schema_type,
                    schema=formatted_schema if isinstance(formatted_schema, dict) else {"content": formatted_schema},
                    format=output_format,
                    description=f"Configuration schema for {schema_type}",
                    metadata={
                        "success": True,
                        "schema_type": schema_type,
                        "output_format": output_format,
                        "interface_type": interface_type
                    }
                )
            else:
                return SchemaInfo(
                    name=schema_type,
                    schema={"error": f"Unknown schema type: {schema_type}"},
                    format=output_format,
                    description=f"Schema not found for {schema_type}",
                    metadata={
                        "success": False,
                        "error": f"Unknown schema type: {schema_type}",
                        "available_schemas": self.AVAILABLE_SCHEMAS
                    }
                )

    def _get_sample_configs(self, schema_type: str, output_format: str, interface_type: str) -> SchemaInfo:
        """Get sample configurations."""
        samples = get_sample_configs()
        
        if schema_type == "all":
            formatted_samples = {}
            
            for name, sample in samples.items():
                if interface_type == "mcp":
                    formatted_samples[name] = self._format_for_mcp(sample, output_format)
                else:
                    formatted_samples[name] = self._format_for_cli(sample, output_format)
            
            return SchemaInfo(
                name="all_samples",
                schema=formatted_samples,
                format=output_format,
                description="Sample configurations for all schema types",
                examples=[formatted_samples],
                metadata={
                    "success": True,
                    "schema_type": "all",
                    "output_format": output_format,
                    "interface_type": interface_type,
                    "sample_count": len(formatted_samples)
                }
            )
        else:
            schema_name = schema_type.replace('-', '_')
            
            if schema_name in samples:
                sample = samples[schema_name]
                
                if interface_type == "mcp":
                    formatted_sample = self._format_for_mcp(sample, output_format)
                else:
                    formatted_sample = self._format_for_cli(sample, output_format)
                
                return SchemaInfo(
                    name=f"{schema_type}_sample",
                    schema=formatted_sample if isinstance(formatted_sample, dict) else {"content": formatted_sample},
                    format=output_format,
                    description=f"Sample configuration for {schema_type}",
                    examples=[formatted_sample] if isinstance(formatted_sample, dict) else [],
                    metadata={
                        "success": True,
                        "schema_type": schema_type,
                        "output_format": output_format,
                        "interface_type": interface_type
                    }
                )
            else:
                return SchemaInfo(
                    name=f"{schema_type}_sample",
                    schema={"error": f"No sample available for schema type: {schema_type}"},
                    format=output_format,
                    description=f"Sample configuration not found for {schema_type}",
                    metadata={
                        "success": False,
                        "error": f"No sample available for schema type: {schema_type}",
                        "available_schemas": list(samples.keys())
                    }
                )

    def _format_single_usage(self, usage_data: Dict[str, Any], command: str, interface_type: str) -> SchemaInfo:
        """Format usage information for a single command."""
        if interface_type == "mcp":
            schema_content = {
                "command": command,
                "description": usage_data.get("description", ""),
                "examples": {
                    "cli": usage_data.get("cli", ""),
                    "mcp": usage_data.get("mcp", "")
                },
                "config_schema": usage_data.get("config_schema", "")
            }
        else:
            # CLI format
            schema_content = {
                "command": command,
                "description": usage_data.get("description", ""),
                "cli_example": usage_data.get("cli", ""),
                "config_schema": usage_data.get("config_schema", "")
            }
        
        return SchemaInfo(
            name=f"usage_{command}",
            schema=schema_content,
            format="text",
            description=f"Usage information for {command} command",
            usage_notes=[usage_data.get("description", "")],
            metadata={
                "success": True,
                "command": command,
                "interface_type": interface_type
            }
        )

    def _format_all_usage(self, usage_examples: Dict[str, Any], interface_type: str) -> SchemaInfo:
        """Format usage information for all commands."""
        commands = {}
        usage_notes = []
        
        for cmd_key, usage_data in usage_examples.items():
            cmd_name = cmd_key.replace('_', '-')
            
            if interface_type == "mcp":
                commands[cmd_name] = {
                    "description": usage_data.get("description", ""),
                    "examples": {
                        "cli": usage_data.get("cli", ""),
                        "mcp": usage_data.get("mcp", "")
                    },
                    "config_schema": usage_data.get("config_schema", "")
                }
            else:
                commands[cmd_name] = {
                    "description": usage_data.get("description", ""),
                    "cli_example": usage_data.get("cli", "").split('\n')[0] if usage_data.get("cli") else "",
                    "config_schema": usage_data.get("config_schema", "")
                }
            
            # Collect usage notes
            if usage_data.get("description"):
                usage_notes.append(f"{cmd_name}: {usage_data.get('description')}")
        
        return SchemaInfo(
            name="usage_all_commands",
            schema={"commands": commands},
            format="text",
            description="Usage information for all available commands",
            usage_notes=usage_notes,
            metadata={
                "success": True,
                "interface_type": interface_type,
                "command_count": len(commands)
            }
        )

    def _format_for_cli(self, data: Any, output_format: str) -> str:
        """Format data for CLI output."""
        if output_format == "json":
            return json.dumps(data, indent=2)
        else:
            return format_schema_for_cli(data)

    def _format_for_mcp(self, data: Any, output_format: str) -> Any:
        """Format data for MCP output."""
        if output_format == "json":
            return data  # MCP expects structured data
        else:
            return format_schema_for_mcp(data)

    def get_workflow_guide(self, interface_type: str = "cli") -> Dict[str, Any]:
        """
        Get complete 6-step workflow guide for project generation.
        
        Args:
            interface_type: Type of interface ("cli" or "mcp")
            
        Returns:
            Dictionary with complete workflow guidance
        """
        operation_context = {
            "operation": "get_workflow_guide",
            "interface_type": interface_type
        }
        
        self.logger.debug("Retrieving workflow guide", extra=operation_context)
        
        # Define the complete 6-step workflow
        workflow_steps = [
            {
                "step": 1,
                "title": "Initialize Project",
                "description": "Create a new FastAPI SQLModel project with basic structure",
                "cli_command": "fastapi-sqlmodel-gen init --name \"MyApp\" --output ./myapp",
                "mcp_tool": "initialize_project",
                "mcp_params": {
                    "project_name": "MyApp",
                    "output_dir": "./myapp"
                },
                "expected_output": "Project directory created with basic FastAPI structure",
                "next_step": "Add domains to define your business entities"
            },
            {
                "step": 2,
                "title": "Add Domain",
                "description": "Add a business domain with entities (e.g., User, Product, Order)",
                "cli_command": "fastapi-sqlmodel-gen add-domain --name \"User\" --layers core,interface",
                "mcp_tool": "add_domain_to_project",
                "mcp_params": {
                    "name": "User",
                    "output_dir": "./myapp",
                    "layers": "core,interface"
                },
                "expected_output": "Domain directory created with YAML configuration templates",
                "next_step": "Edit the generated YAML configuration files"
            },
            {
                "step": 3,
                "title": "Edit Configurations",
                "description": "Customize the generated YAML configuration files to define your entities, fields, and relationships",
                "cli_command": "# Edit files manually:\n# ./myapp/app/core/User/domain.yaml\n# ./myapp/app/core/User/entities.yaml",
                "mcp_tool": "# Manual step - no MCP tool needed",
                "mcp_params": {},
                "expected_output": "Configured entities with proper fields, types, and relationships",
                "next_step": "Validate your configuration before generating code"
            },
            {
                "step": 4,
                "title": "Validate Configuration",
                "description": "Ensure your domain configuration is valid before code generation",
                "cli_command": "fastapi-sqlmodel-gen validate --domain User",
                "mcp_tool": "validate_configuration",
                "mcp_params": {
                    "config": "# JSON string of your domain configuration"
                },
                "expected_output": "Validation results showing any errors or warnings",
                "next_step": "Generate code for individual layers or all at once"
            },
            {
                "step": 5,
                "title": "Generate Individual Layers",
                "description": "Generate specific layers of your application (core, interface, repository, usecase)",
                "cli_command": "fastapi-sqlmodel-gen gen-core --config ./myapp/app/core/User/domain.yaml --output ./myapp\nfastapi-sqlmodel-gen gen-interface --config ./myapp/app/interface/User/interface.yaml --output ./myapp\nfastapi-sqlmodel-gen gen-repository --config ./myapp/app/repository/User/repository.yaml --output ./myapp",
                "mcp_tool": "generate_domain_from_config / generate_service_from_config",
                "mcp_params": {
                    "domain_config": "# JSON string of domain configuration",
                    "output_dir": "./myapp"
                },
                "expected_output": "Generated Python files for entities, repositories, services, and API endpoints",
                "next_step": "Or use gen-all for comprehensive generation"
            },
            {
                "step": 6,
                "title": "Generate All Layers",
                "description": "Generate complete application with all layers in one command",
                "cli_command": "fastapi-sqlmodel-gen gen-all --config comprehensive_config.yaml --output ./myapp",
                "mcp_tool": "generate_all_layers",
                "mcp_params": {
                    "config": "# JSON string of comprehensive configuration",
                    "output_dir": "./myapp",
                    "clean_existing": False
                },
                "expected_output": "Complete FastAPI application with all layers generated",
                "next_step": "Run and test your generated application"
            }
        ]
        
        # Additional guidance
        additional_info = {
            "best_practices": [
                "Always validate your configuration before generating code",
                "Start with simple entities and add complexity gradually",
                "Use descriptive names for entities and fields",
                "Test each step before moving to the next",
                "Keep backup of your configuration files"
            ],
            "troubleshooting": [
                "If validation fails, check your YAML syntax and field types",
                "Ensure all required fields are defined",
                "Check that relationship references exist",
                "Use get_configuration_schema for valid field types"
            ],
            "available_commands": [
                "init - Initialize new project",
                "add-domain - Add business domain",
                "validate - Validate configuration",
                "gen-core - Generate domain entities",
                "gen-interface - Generate API interfaces",
                "gen-repository - Generate data repositories",
                "gen-usecase - Generate business use cases",
                "gen-service - Generate services",
                "gen-all - Generate complete application",
                "schema - Get configuration schemas",
                "usage - Get command usage examples"
            ]
        }
        
        # Format response based on interface type
        if interface_type == "mcp":
            result = {
                "success": True,
                "workflow_title": "FastAPI SQLModel Generator - Complete 6-Step Workflow",
                "description": "End-to-end guide for generating a complete FastAPI SQLModel application",
                "steps": workflow_steps,
                "additional_info": additional_info,
                "interface_type": interface_type
            }
        else:
            # CLI format with more readable structure
            result = {
                "success": True,
                "workflow_title": "FastAPI SQLModel Generator - Complete 6-Step Workflow",
                "description": "End-to-end guide for generating a complete FastAPI SQLModel application",
                "steps": workflow_steps,
                "additional_info": additional_info,
                "interface_type": interface_type
            }
        
        self.logger.info("Workflow guide retrieved successfully", extra={
            **operation_context,
            "step_count": len(workflow_steps),
            "result": "success"
        })
        
        return result
