"""
MCP server interface for FastAPI SQLModel generator.

Provides MCP (Model Context Protocol) interface for:
- Project initialization
- Domain generation
- Repository generation  
- Use case generation
- Service generation
- Full project generation from comprehensive config
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from ...types.models import (
    EntityDomainConfig,
    UseCaseConfig,
    ServiceConfig,
    Configuration
)
from ...utils.schema import (
    get_all_schemas,
    get_schema_by_name,
    format_schema_for_mcp,
    get_usage_examples,
    get_sample_configs
)
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)


class GeneratorMCPServer:
    """MCP server interface for the FastAPI SQLModel generator."""

    def __init__(self):
        """Initialize the MCP server interface."""
        self.logger = get_logger(__name__)
        self.tools = self._register_tools()
        
        # Log server initialization
        self.logger.info("MCP server initialized", extra={
            "operation": "server_init",
            "tool_count": len(self.tools),
            "available_tools": list(self.tools.keys())
        })

    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Register all available MCP tools.
        
        Returns:
            Dictionary of tool definitions
        """
        self.logger.debug("Registering MCP tools", extra={"operation": "register_tools"})
        
        tools = {
            "initialize_project": {
                "description": "Initialize a new FastAPI SQLModel project with complete directory structure",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project to create"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for the project"
                        },
                        "auth_type": {
                            "type": "string",
                            "enum": ["none", "email_password"],
                            "default": "none",
                            "description": "Authentication type to include"
                        },
                        "clean_existing": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to clean existing directory before initialization"
                        }
                    },
                    "required": ["project_name", "output_dir"]
                }
            },
            "generate_domain": {
                "description": "Generate domain layer (entities, exceptions) from configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "EntityDomainConfig as JSON object"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for generated code"
                        }
                    },
                    "required": ["config", "output_dir"]
                }
            },
            "generate_repository": {
                "description": "Generate repository layer (protocols, implementations) from configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "EntityDomainConfig as JSON object"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for generated code"
                        }
                    },
                    "required": ["config", "output_dir"]
                }
            },
            "generate_usecase": {
                "description": "Generate use case layer (business logic orchestration) from configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "UseCaseConfig as JSON object"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for generated code"
                        }
                    },
                    "required": ["config", "output_dir"]
                }
            },
            "generate_service": {
                "description": "Generate domain-agnostic service from configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "ServiceConfig as JSON object"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for generated code"
                        }
                    },
                    "required": ["config", "output_dir"]
                }
            },
            "generate_all": {
                "description": "Generate all layers from comprehensive configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "Comprehensive configuration as JSON object"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for generated code"
                        },
                        "clean_existing": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to clean existing output before generation"
                        }
                    },
                    "required": ["config", "output_dir"]
                }
            },
            "get_usage": {
                "description": "Get usage instructions and examples for commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "enum": ["init", "gen-domain", "gen-repository", "gen-usecase", "gen-service", "gen-all"],
                            "description": "Specific command to get usage for (optional, defaults to all commands)"
                        }
                    },
                    "required": []
                }
            },
            "get_schema": {
                "description": "Get configuration schemas for different config types",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "schema_type": {
                            "type": "string",
                            "enum": ["entity-domain", "usecase", "service", "configuration", "all"],
                            "default": "all",
                            "description": "Configuration type to get schema for"
                        },
                        "show_sample": {
                            "type": "boolean",
                            "default": False,
                            "description": "Show sample configuration instead of schema"
                        }
                    },
                    "required": []
                }
            },
            "add_domain": {
                "description": "Add a new domain to the project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the domain to create"
                        },
                        "layers": {
                            "type": "string",
                            "default": "core,interface",
                            "description": "Comma-separated list of layers"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory"
                        }
                    },
                    "required": ["name", "output_dir"]
                }
            },
            "validate_configuration": {
                "description": "Validate domain configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "Configuration to validate"
                        },
                        "domain": {
                            "type": "string",
                            "description": "Domain name (optional)"
                        }
                    },
                    "required": ["config"]
                }
            },
            "get_workflow_guide": {
                "description": "Get complete 6-step workflow guide for project generation",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        self.logger.debug("MCP tools registered successfully", extra={
            "operation": "register_tools",
            "tool_count": len(tools),
            "tools": list(tools.keys())
        })
        
        return tools

    def get_tool_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools for MCP.
        
        Returns:
            List of tool definitions
        """
        self.logger.debug("Retrieving tool list", extra={
            "operation": "get_tool_list",
            "tool_count": len(self.tools)
        })
        
        tool_list = [
            {
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["parameters"]
            }
            for name, tool in self.tools.items()
        ]
        
        self.logger.info("Tool list retrieved successfully", extra={
            "operation": "get_tool_list",
            "tool_count": len(tool_list)
        })
        
        return tool_list

    async def init(self, project_name: str, output_dir: str, 
                   auth_type: str = 'none', clean_existing: bool = False) -> Dict[str, Any]:
        """
        Initialize a new FastAPI SQLModel project.
        
        Args:
            project_name: Name of the project
            output_dir: Output directory path
            auth_type: Authentication type
            clean_existing: Clean existing directory
            
        Returns:
            Result dictionary with success status and details
        """
        operation_context = {
            "operation": "init_project",
            "project_name": project_name,
            "output_dir": output_dir,
            "auth_type": auth_type,
            "clean_existing": clean_existing
        }
        
        self.logger.debug("Starting project initialization", extra=operation_context)
        
        with self.logger.timed_operation("project_initialization", operation_context):
            try:
                self.logger.info("Initializing project", extra=operation_context)
                
                from ...core.initialize import ProjectInitializer
                initializer = ProjectInitializer(output_dir, clean_existing)
                initializer.initialize(auth_type == 'email_password')
                
                result = {
                    "success": True,
                    "message": f"Project '{project_name}' initialized successfully",
                    "output_dir": output_dir
                }
                
                self.logger.info("Project initialization completed successfully", extra={
                    **operation_context,
                    "result": "success"
                })
                
                return result
                
            except Exception as e:
                error_context = {
                    **operation_context,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                self.logger.error("Project initialization failed", 
                                exc_info=True, extra=error_context)
                
                return {
                    "success": False,
                    "error": str(e)
                }

    async def gen_domain(self, config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Generate domain layer from configuration.
        
        Args:
            config: EntityDomainConfig as dictionary
            output_dir: Output directory path
            
        Returns:
            Result dictionary with success status and details
        """
        operation_context = {
            "operation": "generate_domain",
            "output_dir": output_dir,
            "domain_name": config.get("name", "unknown"),
            "entity_count": len(config.get("entities", []))
        }
        
        self.logger.debug("Starting domain generation", extra=operation_context)
        
        with self.logger.timed_operation("domain_generation", operation_context):
            try:
                self.logger.info("Generating domain layer", extra=operation_context)
                
                # Save config to temporary file and use LayerGenerator
                import tempfile
                import yaml
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    temp_config_path = f.name
                
                try:
                    from ...core.layers import LayerGenerator
                    layer_generator = LayerGenerator(output_dir)
                    success = layer_generator.generate_core_layer(temp_config_path)
                    
                    if not success:
                        raise RuntimeError("Domain layer generation failed")
                    
                    result = {
                        "success": True,
                        "message": "Domain layer generated successfully",
                        "files_generated": []  # TODO: Layer generator could return file list
                    }
                finally:
                    os.unlink(temp_config_path)
                
                self.logger.info("Domain generation completed successfully", extra={
                    **operation_context,
                    "files_count": len(result["files_generated"]),
                    "result": "success"
                })
                
                return result
                
            except Exception as e:
                error_context = {
                    **operation_context,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                self.logger.error("Domain generation failed", 
                                exc_info=True, extra=error_context)
                
                return {
                    "success": False,
                    "error": str(e)
                }

    async def gen_repository(self, config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Generate repository layer from configuration.
        
        Args:
            config: EntityDomainConfig as dictionary
            output_dir: Output directory path
            
        Returns:
            Result dictionary with success status and details
        """
        operation_context = {
            "operation": "generate_repository",
            "output_dir": output_dir,
            "domain_name": config.get("name", "unknown"),
            "entity_count": len(config.get("entities", [])),
            "database_config": config.get("database", {}).get("type", "unknown")
        }
        
        self.logger.debug("Starting repository generation", extra=operation_context)
        
        with self.logger.timed_operation("repository_generation", operation_context):
            try:
                self.logger.info("Generating repository layer", extra=operation_context)
                
                # Save config to temporary file and use LayerGenerator
                import tempfile
                import yaml
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    temp_config_path = f.name
                
                try:
                    from ...core.layers import LayerGenerator
                    layer_generator = LayerGenerator(output_dir)
                    success = layer_generator.generate_repository_layer(temp_config_path)
                    
                    if not success:
                        raise RuntimeError("Repository layer generation failed")
                    
                    result = {
                        "success": True,
                        "message": "Repository layer generated successfully",
                        "files_generated": []  # TODO: Layer generator could return file list
                    }
                finally:
                    os.unlink(temp_config_path)
                
                self.logger.info("Repository generation completed successfully", extra={
                    **operation_context,
                    "files_count": len(result["files_generated"]),
                    "result": "success"
                })
                
                return result
                
            except Exception as e:
                error_context = {
                    **operation_context,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                self.logger.error("Repository generation failed", 
                                exc_info=True, extra=error_context)
                
                return {
                    "success": False,
                    "error": str(e)
                }

    async def gen_usecase(self, config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Generate use case layer from configuration.
        
        Args:
            config: UseCaseConfig as dictionary
            output_dir: Output directory path
            
        Returns:
            Result dictionary with success status and details
        """
        operation_context = {
            "operation": "generate_usecase",
            "output_dir": output_dir,
            "domain_name": config.get("domain_name", "unknown"),
            "method_count": len(config.get("methods", [])),
            "business_rules_count": len(config.get("business_rules", []))
        }
        
        self.logger.debug("Starting use case generation", extra=operation_context)
        
        with self.logger.timed_operation("usecase_generation", operation_context):
            try:
                self.logger.info("Generating use case layer", extra=operation_context)
                
                # Save config to temporary file and use LayerGenerator
                import tempfile
                import yaml
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    temp_config_path = f.name
                
                try:
                    from ...core.layers import LayerGenerator
                    layer_generator = LayerGenerator(output_dir)
                    success = layer_generator.generate_usecase_layer(temp_config_path)
                    
                    if not success:
                        raise RuntimeError("Use case layer generation failed")
                    
                    result = {
                        "success": True,
                        "message": "Use case layer generated successfully",
                        "files_generated": []  # TODO: Layer generator could return file list
                    }
                finally:
                    os.unlink(temp_config_path)
                
                self.logger.info("Use case generation completed successfully", extra={
                    **operation_context,
                    "files_count": len(result["files_generated"]),
                    "result": "success"
                })
                
                return result
                
            except Exception as e:
                error_context = {
                    **operation_context,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                self.logger.error("Use case generation failed", 
                                exc_info=True, extra=error_context)
                
                return {
                    "success": False,
                    "error": str(e)
                }

    async def gen_service(self, config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Generate service from configuration.
        
        Args:
            config: ServiceConfig as dictionary
            output_dir: Output directory path
            
        Returns:
            Result dictionary with success status and details
        """
        operation_context = {
            "operation": "generate_service",
            "output_dir": output_dir,
            "service_name": config.get("name", "unknown"),
            "method_count": len(config.get("methods", [])),
            "dependency_count": len(config.get("dependencies", []))
        }
        
        self.logger.debug("Starting service generation", extra=operation_context)
        
        with self.logger.timed_operation("service_generation", operation_context):
            try:
                self.logger.info("Generating service", extra=operation_context)
                
                # Save config to temporary file and use LayerGenerator
                import tempfile
                import yaml
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    temp_config_path = f.name
                
                try:
                    from ...core.layers import LayerGenerator
                    layer_generator = LayerGenerator(output_dir)
                    success = layer_generator.generate_service_layer(temp_config_path)
                    
                    if not success:
                        raise RuntimeError("Service generation failed")
                    
                    result = {
                        "success": True,
                        "message": "Service generated successfully",
                        "files_generated": []  # TODO: Layer generator could return file list
                    }
                finally:
                    os.unlink(temp_config_path)
                
                self.logger.info("Service generation completed successfully", extra={
                    **operation_context,
                    "files_count": len(result["files_generated"]),
                    "result": "success"
                })
                
                return result
                
            except Exception as e:
                error_context = {
                    **operation_context,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                self.logger.error("Service generation failed", 
                                exc_info=True, extra=error_context)
                
                return {
                    "success": False,
                    "error": str(e)
                }

    async def gen_all(self, config: Dict[str, Any], output_dir: str, 
                      clean_existing: bool = False) -> Dict[str, Any]:
        """
        Generate all layers from comprehensive configuration.
        
        Args:
            config: Comprehensive configuration as dictionary
            output_dir: Output directory path
            clean_existing: Clean existing output
            
        Returns:
            Result dictionary with success status and details
        """
        operation_context = {
            "operation": "generate_all",
            "output_dir": output_dir,
            "clean_existing": clean_existing,
            "domain_count": len(config.get("domains", [])),
            "service_count": len(config.get("services", []))
        }
        
        self.logger.debug("Starting comprehensive generation", extra=operation_context)
        
        with self.logger.timed_operation("comprehensive_generation", operation_context):
            try:
                self.logger.info("Generating all layers", extra=operation_context)
                
                # Save config to temporary file and use DomainManager
                import tempfile
                import yaml
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    temp_config_path = f.name
                
                try:
                    from ...core.domain import DomainManager
                    domain_manager = DomainManager(output_dir)
                    success = domain_manager.generate_all_layers(temp_config_path, clean_existing)
                    
                    if not success:
                        raise RuntimeError("Comprehensive generation failed")
                    
                    result = {
                        "success": True,
                        "message": "All layers generated successfully",
                        "layers_generated": ["domain", "repository", "usecase", "interface", "service"],
                        "files_generated": []  # TODO: Domain manager could return file list
                    }
                finally:
                    os.unlink(temp_config_path)
                
                self.logger.info("Comprehensive generation completed successfully", extra={
                    **operation_context,
                    "layers_count": len(result["layers_generated"]),
                    "files_count": len(result["files_generated"]),
                    "result": "success"
                })
                
                return result
                
            except Exception as e:
                error_context = {
                    **operation_context,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                self.logger.error("Comprehensive generation failed", 
                                exc_info=True, extra=error_context)
                
                return {
                    "success": False,
                    "error": str(e)
                }

    async def get_usage(self, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage instructions and examples for commands.
        
        Args:
            command: Specific command to get usage for (None for all)
            
        Returns:
            Usage information dictionary
        """
        operation_context = {
            "operation": "get_usage",
            "command": command or "all"
        }
        
        self.logger.debug("Retrieving usage information", extra=operation_context)
        
        try:
            usage_examples = get_usage_examples()
            
            if command:
                # Return usage for specific command
                cmd_key = command.replace('-', '_')
                if cmd_key in usage_examples:
                    example = usage_examples[cmd_key]
                    result = {
                        "success": True,
                        "command": command,
                        "description": example['description'],
                        "examples": example['cli'],
                        "config_schema": example['config_schema']
                    }
                    
                    self.logger.info("Usage information retrieved for specific command", extra={
                        **operation_context,
                        "result": "success"
                    })
                    
                    return result
                else:
                    self.logger.warning("Unknown command requested", extra={
                        **operation_context,
                        "available_commands": list(usage_examples.keys())
                    })
                    
                    return {
                        "success": False,
                        "error": f"Unknown command: {command}"
                    }
            else:
                # Return usage for all commands
                formatted_usage = {}
                for cmd_key, example in usage_examples.items():
                    cmd_name = cmd_key.replace('_', '-')
                    formatted_usage[cmd_name] = {
                        "description": example['description'],
                        "example": example['cli'].split('\n')[0],  # First line of examples
                        "config_schema": example['config_schema']
                    }
                
                result = {
                    "success": True,
                    "all_commands": formatted_usage
                }
                
                self.logger.info("Usage information retrieved for all commands", extra={
                    **operation_context,
                    "command_count": len(formatted_usage),
                    "result": "success"
                })
                
                return result
                
        except Exception as e:
            error_context = {
                **operation_context,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            
            self.logger.error("Failed to retrieve usage information", 
                            exc_info=True, extra=error_context)
            
            return {
                "success": False,
                "error": str(e)
            }

    async def get_schema(self, schema_type: str = 'all', show_sample: bool = False) -> Dict[str, Any]:
        """
        Get configuration schemas for different config types.
        
        Args:
            schema_type: Type of schema to retrieve
            show_sample: Show sample config instead of schema
            
        Returns:
            Schema information dictionary
        """
        operation_context = {
            "operation": "get_schema",
            "schema_type": schema_type,
            "show_sample": show_sample
        }
        
        self.logger.debug("Retrieving schema information", extra=operation_context)
        
        try:
            if show_sample:
                samples = get_sample_configs()
                
                if schema_type == 'all':
                    result = {
                        "success": True,
                        "type": "samples",
                        "schemas": samples
                    }
                    
                    self.logger.info("Sample configurations retrieved for all types", extra={
                        **operation_context,
                        "sample_count": len(samples),
                        "result": "success"
                    })
                    
                    return result
                else:
                    schema_name = schema_type.replace('-', '_')
                    if schema_name in samples:
                        result = {
                            "success": True,
                            "type": "sample",
                            "schema_type": schema_type,
                            "schema": samples[schema_name]
                        }
                        
                        self.logger.info("Sample configuration retrieved for specific type", extra={
                            **operation_context,
                            "result": "success"
                        })
                        
                        return result
                    else:
                        self.logger.warning("Unknown schema type requested for sample", extra={
                            **operation_context,
                            "available_types": list(samples.keys())
                        })
                        
                        return {
                            "success": False,
                            "error": f"Unknown schema type: {schema_type}"
                        }
            else:
                # Return actual schemas
                if schema_type == 'all':
                    schemas = get_all_schemas()
                    formatted_schemas = {}
                    for name, schema in schemas.items():
                        formatted_schemas[name] = format_schema_for_mcp(schema)
                    
                    result = {
                        "success": True,
                        "type": "schemas",
                        "schemas": formatted_schemas
                    }
                    
                    self.logger.info("Schemas retrieved for all types", extra={
                        **operation_context,
                        "schema_count": len(formatted_schemas),
                        "result": "success"
                    })
                    
                    return result
                else:
                    schema_name = schema_type.replace('-', '_')
                    schema = get_schema_by_name(schema_name)
                    if schema:
                        result = {
                            "success": True,
                            "type": "schema",
                            "schema_type": schema_type,
                            "schema": format_schema_for_mcp(schema)
                        }
                        
                        self.logger.info("Schema retrieved for specific type", extra={
                            **operation_context,
                            "result": "success"
                        })
                        
                        return result
                    else:
                        available_schemas = get_all_schemas()
                        self.logger.warning("Unknown schema type requested", extra={
                            **operation_context,
                            "available_types": list(available_schemas.keys())
                        })
                        
                        return {
                            "success": False,
                            "error": f"Unknown schema type: {schema_type}"
                        }
                        
        except Exception as e:
            error_context = {
                **operation_context,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            
            self.logger.error("Failed to retrieve schema information", 
                            exc_info=True, extra=error_context)
            
            return {
                "success": False,
                "error": str(e)
            }

    async def add_domain(self, name: str, layers: str, output_dir: str) -> Dict[str, Any]:
        """
        Add a new domain to the project.
        
        Args:
            name: Domain name
            layers: Comma-separated list of layers
            output_dir: Output directory path
            
        Returns:
            Result dictionary with success status and details
        """
        layer_list = [layer.strip() for layer in layers.split(',')]
        operation_context = {
            "operation": "add_domain",
            "domain_name": name,
            "layers": layer_list,
            "output_dir": output_dir,
            "layer_count": len(layer_list)
        }
        
        self.logger.debug("Starting domain addition", extra=operation_context)
        
        with self.logger.timed_operation("domain_addition", operation_context):
            try:
                self.logger.info("Adding domain to project", extra=operation_context)
                
                from ...core.domain import DomainManager
                domain_manager = DomainManager(output_dir)
                success = domain_manager.add_domain(name, layer_list)
                
                if not success:
                    raise RuntimeError("Domain addition failed")
                
                result = {
                    "success": True,
                    "message": f"Domain '{name}' added successfully",
                    "output_dir": output_dir,
                    "layers": layer_list
                }
                
                self.logger.info("Domain addition completed successfully", extra={
                    **operation_context,
                    "result": "success"
                })
                
                return result
                
            except Exception as e:
                error_context = {
                    **operation_context,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                self.logger.error("Domain addition failed", 
                                exc_info=True, extra=error_context)
                
                return {
                    "success": False,
                    "error": str(e)
                }

    async def validate_config(self, config: Dict[str, Any], domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate domain configuration.
        
        Args:
            config: Configuration dictionary to validate
            domain: Domain name (optional)
            
        Returns:
            Result dictionary with validation status and details
        """
        operation_context = {
            "operation": "validate_config",
            "domain": domain,
            "config_keys": list(config.keys()) if config else [],
            "config_size": len(config) if config else 0
        }
        
        self.logger.debug("Starting configuration validation", extra=operation_context)
        
        try:
            self.logger.info("Validating configuration", extra=operation_context)
            
            from ...core.validator import ProjectValidator
            
            # Save config to temporary file for validation
            import tempfile
            import yaml
            import os
            
            if domain:
                # Validate specific domain
                validator = ProjectValidator(".")
                validation_result = validator.validate_domain(domain)
            else:
                # Validate configuration data
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    temp_config_path = f.name
                
                try:
                    validator = ProjectValidator(".")
                    validation_result = validator.validate_config(temp_config_path)
                finally:
                    os.unlink(temp_config_path)
            
            result = {
                "success": True,
                "valid": validation_result.is_valid,
                "message": "Configuration is valid" if validation_result.is_valid else "Configuration has errors",
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            }
            
            self.logger.info("Configuration validation completed successfully", extra={
                **operation_context,
                "validation_result": "valid",
                "error_count": len(result["errors"]),
                "warning_count": len(result["warnings"])
            })
            
            return result
            
        except Exception as e:
            error_context = {
                **operation_context,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            
            self.logger.error("Configuration validation failed", 
                            exc_info=True, extra=error_context)
            
            return {
                "success": False,
                "valid": False,
                "error": str(e)
            }

    async def get_workflow_guide(self) -> Dict[str, Any]:
        """
        Get complete 6-step workflow guide for project generation.
        
        Returns:
            Result dictionary with complete workflow guidance
        """
        operation_context = {
            "operation": "get_workflow_guide"
        }
        
        self.logger.debug("Retrieving workflow guide", extra=operation_context)
        
        try:
            self.logger.info("Getting workflow guide", extra=operation_context)
            
            from ...core.schema import SchemaProvider
            
            # Create schema provider for workflow guide
            schema_provider = SchemaProvider(".")
            result = schema_provider.get_workflow_guide(interface_type="mcp")
            
            self.logger.info("Workflow guide retrieved successfully", extra={
                **operation_context,
                "step_count": len(result.get("steps", [])),
                "result": "success"
            })
            
            return result
            
        except Exception as e:
            error_context = {
                **operation_context,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            
            self.logger.error("Failed to retrieve workflow guide", 
                            exc_info=True, extra=error_context)
            
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP tool calls.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        operation_context = {
            "operation": "handle_tool_call",
            "tool_name": tool_name,
            "argument_keys": list(arguments.keys()) if arguments else []
        }
        
        self.logger.debug("Handling MCP tool call", extra=operation_context)
        
        with self.logger.timed_operation(f"tool_call_{tool_name}", operation_context):
            if tool_name == "initialize_project":
                return await self.init(
                    project_name=arguments["project_name"],
                    output_dir=arguments["output_dir"],
                    auth_type=arguments.get("auth_type", "none"),
                    clean_existing=arguments.get("clean_existing", False)
                )
            elif tool_name == "generate_domain":
                return await self.gen_domain(
                    config=arguments["config"],
                    output_dir=arguments["output_dir"]
                )
            elif tool_name == "generate_repository":
                return await self.gen_repository(
                    config=arguments["config"],
                    output_dir=arguments["output_dir"]
                )
            elif tool_name == "generate_usecase":
                return await self.gen_usecase(
                    config=arguments["config"],
                    output_dir=arguments["output_dir"]
                )
            elif tool_name == "generate_service":
                return await self.gen_service(
                    config=arguments["config"],
                    output_dir=arguments["output_dir"]
                )
            elif tool_name == "generate_all":
                return await self.gen_all(
                    config=arguments["config"],
                    output_dir=arguments["output_dir"],
                    clean_existing=arguments.get("clean_existing", False)
                )
            elif tool_name == "add_domain":
                return await self.add_domain(
                    name=arguments["name"],
                    layers=arguments.get("layers", "core,interface"),
                    output_dir=arguments["output_dir"]
                )
            elif tool_name == "validate_configuration":
                return await self.validate_config(
                    config=arguments["config"],
                    domain=arguments.get("domain")
                )
            elif tool_name == "get_usage":
                return await self.get_usage(
                    command=arguments.get("command")
                )
            elif tool_name == "get_schema":
                return await self.get_schema(
                    schema_type=arguments.get("schema_type", "all"),
                    show_sample=arguments.get("show_sample", False)
                )
            elif tool_name == "get_workflow_guide":
                return await self.get_workflow_guide()
            else:
                self.logger.warning("Unknown tool requested", extra={
                    **operation_context,
                    "available_tools": list(self.tools.keys())
                })
                
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }


def create_mcp_server() -> GeneratorMCPServer:
    """
    Create and return an MCP server instance.
    
    Returns:
        Configured MCP server
    """
    logger.info("Creating MCP server instance", extra={
        "operation": "create_server"
    })
    
    server = GeneratorMCPServer()
    
    logger.info("MCP server instance created successfully", extra={
        "operation": "create_server",
        "tool_count": len(server.tools),
        "result": "success"
    })
    
    return server
