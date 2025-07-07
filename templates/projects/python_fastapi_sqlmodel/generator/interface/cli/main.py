"""
Main CLI interface for FastAPI SQLModel generator.

Provides command-line interface for:
- Project initialization
- Core layer generation
- Repository generation
- Use case generation
- Service generation
- Full project generation from comprehensive config
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from ...utils.logging_utils import configure_logging, get_logger
from ...types.models import (
    EntityDomainConfig,
    UseCaseConfig,
    ServiceConfig,
    Configuration
)
from ...utils.schema import (
    get_all_schemas,
    get_schema_by_name,
    format_schema_for_cli,
    get_usage_examples,
    get_sample_configs
)

logger = get_logger(__name__)


class GeneratorCLI:
    """Main CLI interface for the FastAPI SQLModel generator."""

    def __init__(self):
        """Initialize the CLI interface."""
        self.logger = get_logger(__name__)

    def setup_logging(self, verbose: bool = False) -> None:
        """
        Setup logging configuration.
        
        Args:
            verbose: Enable verbose logging output
        """
        level = logging.DEBUG if verbose else logging.INFO
        configure_logging(level=level, json_format=False)

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create command-line argument parser with subcommands.
        
        Returns:
            Configured argument parser
        """
        parser = argparse.ArgumentParser(
            description='FastAPI SQLModel Generator',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Initialize a new project (relative path)
  fastapi-sqlmodel-gen init --name "My API" --output ./my-api
  
  # Initialize a new project (absolute path)  
  fastapi-sqlmodel-gen init --name "My API" --output /home/user/projects/my-api
  
  # Generate core layer (relative path)
  fastapi-sqlmodel-gen gen-core --config domain.yaml --output ./app
  
  # Generate repository layer (parent directory)
  fastapi-sqlmodel-gen gen-repository --config domain.yaml --output ../src/app
  
  # Generate use case layer (absolute path)
  fastapi-sqlmodel-gen gen-usecase --config usecase.yaml --output /project/src/app
  
  # Generate service
  fastapi-sqlmodel-gen gen-service --config service.yaml --output ./app
  
  # Generate all layers from comprehensive config
  fastapi-sqlmodel-gen gen-all --config project.yaml --output ./app

Note: All --output parameters accept both absolute paths (/absolute/path) and 
      relative paths (./relative/path, ../parent/dir). Relative paths are 
      resolved from the current working directory.
            """
        )
        
        # Add global arguments
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        # Create subparsers
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add subcommands
        self._add_init_command(subparsers)
        self._add_gen_core_command(subparsers)
        self._add_gen_repository_command(subparsers)
        self._add_gen_usecase_command(subparsers)
        self._add_gen_service_command(subparsers)
        self._add_gen_all_command(subparsers)
        self._add_add_domain_command(subparsers)
        self._add_validate_command(subparsers)
        self._add_usage_command(subparsers)
        self._add_schema_command(subparsers)
        self._add_workflow_command(subparsers)
        
        return parser

    def _add_init_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add init subcommand to parser."""
        init_parser = subparsers.add_parser(
            'init',
            help='Initialize a new FastAPI SQLModel project',
            description='Create complete project structure with all necessary files'
        )
        init_parser.add_argument(
            '--name', '-n',
            type=str,
            required=True,
            help='Name of the project to create'
        )
        init_parser.add_argument(
            '--output', '-o',
            type=Path,
            default=Path.cwd(),
            help='Output directory for project. Accepts absolute paths (/absolute/path) or relative paths (./relative/path, ../parent/dir). Default: current directory'
        )
        init_parser.add_argument(
            '--auth',
            type=str,
            choices=['none', 'email_password'],
            default='none',
            help='Authentication type (default: none)'
        )
        init_parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing output directory before initialization'
        )

    def _add_gen_core_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add gen-core subcommand to parser."""
        core_parser = subparsers.add_parser(
            'gen-core',
            help='Generate core layer (entities, exceptions)',
            description='Generate core entities and exceptions from configuration'
        )
        core_parser.add_argument(
            '--config', '-c',
            type=Path,
            required=True,
            help='Configuration file (YAML/JSON)'
        )
        core_parser.add_argument(
            '--output', '-o',
            type=Path,
            default=Path.cwd(),
            help='Output directory. Accepts absolute paths (/absolute/path) or relative paths (./relative/path, ../parent/dir). Default: current directory'
        )
        core_parser.add_argument(
            '--show-schema',
            action='store_true',
            help='Display expected configuration schema before generation'
        )

    def _add_gen_repository_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add gen-repository subcommand to parser."""
        repo_parser = subparsers.add_parser(
            'gen-repository',
            help='Generate repository layer (protocols, implementations)',
            description='Generate repository interfaces and implementations from configuration'
        )
        repo_parser.add_argument(
            '--config', '-c',
            type=Path,
            required=True,
            help='Configuration file (YAML/JSON)'
        )
        repo_parser.add_argument(
            '--output', '-o',
            type=Path,
            default=Path.cwd(),
            help='Output directory. Accepts absolute paths (/absolute/path) or relative paths (./relative/path, ../parent/dir). Default: current directory'
        )
        repo_parser.add_argument(
            '--show-schema',
            action='store_true',
            help='Display expected configuration schema before generation'
        )

    def _add_gen_usecase_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add gen-usecase subcommand to parser."""
        usecase_parser = subparsers.add_parser(
            'gen-usecase',
            help='Generate use case layer (business logic orchestration)',
            description='Generate use case implementations and schemas from configuration'
        )
        usecase_parser.add_argument(
            '--config', '-c',
            type=Path,
            required=True,
            help='Configuration file (YAML/JSON)'
        )
        usecase_parser.add_argument(
            '--output', '-o',
            type=Path,
            default=Path.cwd(),
            help='Output directory. Accepts absolute paths (/absolute/path) or relative paths (./relative/path, ../parent/dir). Default: current directory'
        )
        usecase_parser.add_argument(
            '--show-schema',
            action='store_true',
            help='Display expected configuration schema before generation'
        )

    def _add_gen_service_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add gen-service subcommand to parser."""
        service_parser = subparsers.add_parser(
            'gen-service',
            help='Generate domain-agnostic service',
            description='Generate service protocols and implementations from configuration'
        )
        service_parser.add_argument(
            '--config', '-c',
            type=Path,
            required=True,
            help='Configuration file (YAML/JSON)'
        )
        service_parser.add_argument(
            '--output', '-o',
            type=Path,
            default=Path.cwd(),
            help='Output directory. Accepts absolute paths (/absolute/path) or relative paths (./relative/path, ../parent/dir). Default: current directory'
        )
        service_parser.add_argument(
            '--show-schema',
            action='store_true',
            help='Display expected configuration schema before generation'
        )

    def _add_gen_all_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add gen-all subcommand to parser."""
        all_parser = subparsers.add_parser(
            'gen-all',
            help='Generate all layers from comprehensive configuration',
            description='Generate complete domain with all layers from a single configuration file'
        )
        all_parser.add_argument(
            '--config', '-c',
            type=Path,
            required=True,
            help='Comprehensive configuration file (YAML/JSON)'
        )
        all_parser.add_argument(
            '--output', '-o',
            type=Path,
            default=Path.cwd(),
            help='Output directory. Accepts absolute paths (/absolute/path) or relative paths (./relative/path, ../parent/dir). Default: current directory'
        )
        all_parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing output before generation'
        )

    def _add_usage_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add usage subcommand to parser."""
        usage_parser = subparsers.add_parser(
            'usage',
            help='Show comprehensive usage instructions and examples',
            description='Display detailed usage instructions with examples for all commands'
        )
        usage_parser.add_argument(
            '--command', '-c',
            type=str,
            dest='usage_command',
            choices=['init', 'gen-core', 'gen-repository', 'gen-usecase', 'gen-service', 'gen-all'],
            help='Show usage for specific command (default: all commands)'
        )

    def _add_schema_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add schema subcommand to parser."""
        schema_parser = subparsers.add_parser(
            'schema',
            help='Display configuration schemas',
            description='Show expected configuration schemas for different config types'
        )
        schema_parser.add_argument(
            '--type', '-t',
            type=str,
            choices=['entity-domain', 'usecase', 'service', 'configuration', 'all'],
            default='all',
            help='Configuration type to show schema for (default: all)'
        )
        schema_parser.add_argument(
            '--format', '-f',
            type=str,
            choices=['yaml', 'json'],
            default='yaml',
            help='Output format (default: yaml)'
        )
        schema_parser.add_argument(
            '--sample',
            action='store_true',
            help='Show sample configuration instead of schema'
        )

    def _add_add_domain_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add add-domain subcommand to parser."""
        add_domain_parser = subparsers.add_parser(
            'add-domain',
            help='Add a new domain to the project',
            description='Create blank domain directories and configs for user configuration'
        )
        add_domain_parser.add_argument(
            '--name', '-n',
            type=str,
            required=True,
            help='Name of the domain to create'
        )
        add_domain_parser.add_argument(
            '--layers', '-l',
            type=str,
            default='core,interface',
            help='Comma-separated list of layers (default: core,interface)'
        )
        add_domain_parser.add_argument(
            '--output', '-o',
            type=Path,
            default=Path.cwd(),
            help='Output directory. Accepts absolute paths (/absolute/path) or relative paths (./relative/path, ../parent/dir). Default: current directory'
        )

    def _add_validate_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add validate subcommand to parser."""
        validate_parser = subparsers.add_parser(
            'validate',
            help='Validate domain configuration',
            description='Validate configuration files for correctness'
        )
        validate_parser.add_argument(
            '--config', '-c',
            type=Path,
            required=True,
            help='Configuration file to validate'
        )
        validate_parser.add_argument(
            '--domain', '-d',
            type=str,
            help='Domain name (optional)'
        )

    def _add_workflow_command(self, subparsers: argparse._SubParsersAction) -> None:
        """Add workflow subcommand to parser."""
        workflow_parser = subparsers.add_parser(
            'workflow',
            help='Display complete 6-step workflow guide',
            description='Show comprehensive 6-step workflow guide for FastAPI SQLModel project generation'
        )

    def init(self, name: str, output: Path, auth: str = 'none', clean: bool = False) -> int:
        """
        Initialize a new FastAPI SQLModel project.
        
        Args:
            name: Project name
            output: Output directory
            auth: Authentication type
            clean: Clean existing directory
            
        Returns:
            Exit code (0 for success)
        """
        self.logger.debug("Starting init command", extra={
            "command": "init",
            "project_name": name,
            "output_directory": str(output),
            "auth_type": auth,
            "clean": clean
        })
        
        with self.logger.timed_operation("project_initialization", extra={"project_name": name}):
            self.logger.info("Initializing project", extra={
                "command": "init",
                "project_name": name,
                "output_directory": str(output),
                "auth_type": auth,
                "clean": clean
            })
            
            try:
                from ...core.initialize import ProjectInitializer
                initializer = ProjectInitializer(str(output), clean)
                initializer.initialize(auth == 'email_password')
            except Exception as e:
                self.logger.error(f"Project initialization failed: {e}")
                return 1
            
        self.logger.info("Project initialization completed", extra={
            "command": "init",
            "project_name": name,
            "operation": "complete"
        })
        return 0

    def gen_core(self, config: Path, output: Path) -> int:
        """
        Generate core layer from configuration.
        
        Args:
            config: Configuration file path
            output: Output directory
            
        Returns:
            Exit code (0 for success)
        """
        self.logger.debug("Starting gen-core command", extra={
            "command": "gen-core",
            "config_file": str(config),
            "output_directory": str(output)
        })
        
        with self.logger.timed_operation("core_generation", extra={"config_file": str(config)}):
            self.logger.info("Generating core layer", extra={
                "command": "gen-core",
                "config_file": str(config),
                "output_directory": str(output),
                "layer": "core"
            })
            
            try:
                from ...core.layers import LayerGenerator
                layer_generator = LayerGenerator(str(output))
                success = layer_generator.generate_core_layer(str(config))
                if not success:
                    self.logger.error("Core layer generation failed")
                    return 1
            except Exception as e:
                self.logger.error(f"Core layer generation failed: {e}")
                return 1
            
        self.logger.info("Core layer generation completed", extra={
            "command": "gen-core",
            "layer": "core",
            "operation": "complete"
        })
        return 0

    def gen_repository(self, config: Path, output: Path) -> int:
        """
        Generate repository layer from configuration.
        
        Args:
            config: Configuration file path
            output: Output directory
            
        Returns:
            Exit code (0 for success)
        """
        self.logger.debug("Starting gen-repository command", extra={
            "command": "gen-repository",
            "config_file": str(config),
            "output_directory": str(output)
        })
        
        with self.logger.timed_operation("repository_generation", extra={"config_file": str(config)}):
            self.logger.info("Generating repository layer", extra={
                "command": "gen-repository",
                "config_file": str(config),
                "output_directory": str(output),
                "layer": "repository"
            })
            
            try:
                from ...core.layers import LayerGenerator
                layer_generator = LayerGenerator(str(output))
                success = layer_generator.generate_repository_layer(str(config))
                if not success:
                    self.logger.error("Repository layer generation failed")
                    return 1
            except Exception as e:
                self.logger.error(f"Repository layer generation failed: {e}")
                return 1
            
        self.logger.info("Repository layer generation completed", extra={
            "command": "gen-repository",
            "layer": "repository",
            "operation": "complete"
        })
        return 0

    def gen_usecase(self, config: Path, output: Path) -> int:
        """
        Generate use case layer from configuration.
        
        Args:
            config: Configuration file path
            output: Output directory
            
        Returns:
            Exit code (0 for success)
        """
        self.logger.debug("Starting gen-usecase command", extra={
            "command": "gen-usecase",
            "config_file": str(config),
            "output_directory": str(output)
        })
        
        with self.logger.timed_operation("usecase_generation", extra={"config_file": str(config)}):
            self.logger.info("Generating use case layer", extra={
                "command": "gen-usecase",
                "config_file": str(config),
                "output_directory": str(output),
                "layer": "usecase"
            })
            
            try:
                from ...core.layers import LayerGenerator
                layer_generator = LayerGenerator(str(output))
                success = layer_generator.generate_usecase_layer(str(config))
                if not success:
                    self.logger.error("Use case layer generation failed")
                    return 1
            except Exception as e:
                self.logger.error(f"Use case layer generation failed: {e}")
                return 1
            
        self.logger.info("Use case layer generation completed", extra={
            "command": "gen-usecase",
            "layer": "usecase",
            "operation": "complete"
        })
        return 0

    def gen_service(self, config: Path, output: Path) -> int:
        """
        Generate service from configuration.
        
        Args:
            config: Configuration file path
            output: Output directory
            
        Returns:
            Exit code (0 for success)
        """
        self.logger.debug("Starting gen-service command", extra={
            "command": "gen-service",
            "config_file": str(config),
            "output_directory": str(output)
        })
        
        with self.logger.timed_operation("service_generation", extra={"config_file": str(config)}):
            self.logger.info("Generating service", extra={
                "command": "gen-service",
                "config_file": str(config),
                "output_directory": str(output),
                "layer": "service"
            })
            
            try:
                from ...core.layers import LayerGenerator
                layer_generator = LayerGenerator(str(output))
                success = layer_generator.generate_service_layer(str(config))
                if not success:
                    self.logger.error("Service layer generation failed")
                    return 1
            except Exception as e:
                self.logger.error(f"Service layer generation failed: {e}")
                return 1
            
        self.logger.info("Service generation completed", extra={
            "command": "gen-service",
            "layer": "service",
            "operation": "complete"
        })
        return 0

    def gen_all(self, config: Path, output: Path, clean: bool = False) -> int:
        """
        Generate all layers from comprehensive configuration.
        
        Args:
            config: Configuration file path
            output: Output directory
            clean: Clean existing output
            
        Returns:
            Exit code (0 for success)
        """
        self.logger.debug("Starting gen-all command", extra={
            "command": "gen-all",
            "config_file": str(config),
            "output_directory": str(output),
            "clean": clean
        })
        
        with self.logger.timed_operation("comprehensive_generation", extra={"config_file": str(config)}):
            self.logger.info("Generating all layers", extra={
                "command": "gen-all",
                "config_file": str(config),
                "output_directory": str(output),
                "clean": clean,
                "layers": "all"
            })
            
            try:
                from ...core.domain import DomainManager
                domain_manager = DomainManager(str(output))
                success = domain_manager.generate_all_layers(str(config), clean)
                if not success:
                    self.logger.error("Comprehensive generation failed")
                    return 1
            except Exception as e:
                self.logger.error(f"Comprehensive generation failed: {e}")
                return 1
            
        self.logger.info("All layers generation completed", extra={
            "command": "gen-all",
            "layers": "all",
            "operation": "complete"
        })
        return 0

    def add_domain(self, name: str, layers: str, output: Path) -> int:
        """
        Add a new domain to the project.
        
        Args:
            name: Domain name
            layers: Comma-separated list of layers
            output: Output directory
            
        Returns:
            Exit code (0 for success)
        """
        layer_list = [layer.strip() for layer in layers.split(',')]
        
        self.logger.debug("Starting add-domain command", extra={
            "command": "add-domain",
            "domain_name": name,
            "layers": layer_list,
            "output_directory": str(output)
        })
        
        with self.logger.timed_operation("domain_addition", extra={"domain_name": name}):
            self.logger.info("Adding domain", extra={
                "command": "add-domain",
                "domain_name": name,
                "layers": layer_list,
                "output_directory": str(output)
            })
            
            try:
                from ...core.domain import DomainManager
                domain_manager = DomainManager(str(output))
                success = domain_manager.add_domain(name, layer_list)
                if not success:
                    self.logger.error("Domain addition failed")
                    return 1
            except Exception as e:
                self.logger.error(f"Domain addition failed: {e}")
                return 1
            
        self.logger.info("Domain addition completed", extra={
            "command": "add-domain",
            "domain_name": name,
            "operation": "complete"
        })
        return 0

    def validate(self, config: Path, domain: Optional[str] = None) -> int:
        """
        Validate domain configuration.
        
        Args:
            config: Configuration file path
            domain: Domain name (optional)
            
        Returns:
            Exit code (0 for success)
        """
        self.logger.debug("Starting validate command", extra={
            "command": "validate",
            "config_file": str(config),
            "domain": domain
        })
        
        with self.logger.timed_operation("configuration_validation", extra={"config_file": str(config)}):
            self.logger.info("Validating configuration", extra={
                "command": "validate",
                "config_file": str(config),
                "domain": domain
            })
            
            try:
                from ...core.validator import ProjectValidator
                validator = ProjectValidator(".")  # Use current directory as base
                
                if domain:
                    # Validate specific domain
                    result = validator.validate_domain(domain)
                else:
                    # Validate configuration file
                    result = validator.validate_config(str(config))
                
                if not result.is_valid:
                    self.logger.error("Validation failed")
                    for error in result.errors:
                        print(f"ERROR: {error}")
                    for warning in result.warnings:
                        print(f"WARNING: {warning}")
                    return 1
                else:
                    print("Validation successful")
                    for warning in result.warnings:
                        print(f"WARNING: {warning}")
                        
            except Exception as e:
                self.logger.error(f"Validation failed: {e}")
                return 1
            
        self.logger.info("Configuration validation completed", extra={
            "command": "validate",
            "config_file": str(config),
            "operation": "complete"
        })
        return 0

    def show_usage(self, command: Optional[str] = None) -> int:
        """
        Display usage instructions and examples.
        
        Args:
            command: Specific command to show usage for (None for all)
            
        Returns:
            Exit code (0 for success)
        """
        try:
            from ...core.schema import SchemaProvider
            schema_provider = SchemaProvider(".")
            
            result = schema_provider.get_usage(command=command, interface_type="cli")
            
            if not result.get("success", True):
                print(f"Error: {result.get('error', 'Usage retrieval failed')}")
                return 1
            
            if command:
                # Show usage for specific command
                usage_data = result
                print(f"\n=== {command.upper()} COMMAND USAGE ===")
                print(f"\nDescription: {usage_data['description']}")
                print(f"\nExamples:")
                print(usage_data['cli_example'])
                if usage_data['config_schema'] != 'No configuration file required - uses command arguments':
                    print(f"\nRequired Configuration Schema: {usage_data['config_schema']}")
                    print(f"Use 'fastapi-sqlmodel-gen schema --type {usage_data['config_schema']}' to see the schema")
            else:
                # Show usage for all commands
                print("\n=== FASTAPI SQLMODEL GENERATOR USAGE ===")
                print("\nAvailable Commands:")
                
                commands = result.get("commands", {})
                for cmd_name, cmd_data in commands.items():
                    print(f"\n{cmd_name}:")
                    print(f"  {cmd_data['description']}")
                    print(f"  Example: {cmd_data['cli_example']}")
            
            print(f"\nFor detailed schemas: fastapi-sqlmodel-gen schema --help")
            print(f"For command-specific usage: fastapi-sqlmodel-gen usage --command <command>")
            return 0
            
        except Exception as e:
            self.logger.error(f"Usage display failed: {e}")
            return 1

    def show_schema(self, schema_type: str = 'all', format_type: str = 'yaml', 
                   show_sample: bool = False) -> int:
        """
        Display configuration schemas.
        
        Args:
            schema_type: Type of schema to display
            format_type: Output format (yaml/json)
            show_sample: Show sample config instead of schema
            
        Returns:
            Exit code (0 for success)
        """
        try:
            from ...core.schema import SchemaProvider
            schema_provider = SchemaProvider(".")
            
            result = schema_provider.get_schema(
                schema_type=schema_type,
                output_format=format_type,
                show_sample=show_sample,
                interface_type="cli"
            )
            
            if not result.get("success", True):
                print(f"Error: {result.get('error', 'Schema retrieval failed')}")
                return 1
            
            if show_sample:
                if schema_type == 'all':
                    print("\n=== SAMPLE CONFIGURATIONS ===")
                    for name, sample in result.get("samples", {}).items():
                        print(f"\n--- {name.upper().replace('_', ' ')} ---")
                        print(sample)
                else:
                    print(f"\n=== {schema_type.upper()} SAMPLE CONFIGURATION ===")
                    print(result.get("sample", ""))
            else:
                if schema_type == 'all':
                    print("\n=== CONFIGURATION SCHEMAS ===")
                    for name, schema in result.get("schemas", {}).items():
                        print(f"\n--- {name.upper().replace('_', ' ')} SCHEMA ---")
                        print(schema)
                else:
                    print(f"\n=== {schema_type.upper()} SCHEMA ===")
                    print(result.get("schema", ""))
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Schema display failed: {e}")
            return 1

    def show_workflow(self) -> int:
        """
        Display complete 6-step workflow guide.
        
        Returns:
            Exit code (0 for success)
        """
        try:
            from ...core.schema import SchemaProvider
            schema_provider = SchemaProvider(".")
            
            result = schema_provider.get_workflow_guide(interface_type="cli")
            
            if not result.get("success", True):
                print(f"Error: {result.get('error', 'Workflow guide retrieval failed')}")
                return 1
            
            # Display the workflow guide
            print(f"\n{result['workflow_title']}")
            print("=" * len(result['workflow_title']))
            print(f"\n{result['description']}")
            
            print("\n🔄 STEP-BY-STEP WORKFLOW:")
            for step in result['steps']:
                print(f"\n📍 STEP {step['step']}: {step['title']}")
                print(f"   📝 {step['description']}")
                print(f"   🔧 Command: {step['cli_command']}")
                print(f"   ✅ Expected: {step['expected_output']}")
                print(f"   ➡️  Next: {step['next_step']}")
            
            # Display additional info
            additional_info = result.get('additional_info', {})
            
            if additional_info.get('best_practices'):
                print("\n💡 BEST PRACTICES:")
                for practice in additional_info['best_practices']:
                    print(f"   • {practice}")
            
            if additional_info.get('troubleshooting'):
                print("\n🔧 TROUBLESHOOTING:")
                for tip in additional_info['troubleshooting']:
                    print(f"   • {tip}")
            
            if additional_info.get('available_commands'):
                print("\n📋 AVAILABLE COMMANDS:")
                for command in additional_info['available_commands']:
                    print(f"   • {command}")
            
            print(f"\n💻 For detailed help: fastapi-sqlmodel-gen --help")
            print(f"📖 For command-specific help: fastapi-sqlmodel-gen <command> --help")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Workflow guide display failed: {e}")
            return 1

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with given arguments.
        
        Args:
            args: Command line arguments (defaults to sys.argv)
            
        Returns:
            Exit code
        """
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        self.setup_logging(parsed_args.verbose if hasattr(parsed_args, 'verbose') else False)
        
        # Log CLI execution start
        self.logger.debug("CLI execution started", extra={
            "command": getattr(parsed_args, 'command', None),
            "verbose": getattr(parsed_args, 'verbose', False),
            "args": str(parsed_args)
        })
        
        try:
            # Handle commands
            if parsed_args.command == 'init':
                return self.init(
                    name=parsed_args.name,
                    output=parsed_args.output,
                    auth=parsed_args.auth,
                    clean=parsed_args.clean
                )
            elif parsed_args.command == 'gen-core':
                # Show schema if requested
                if getattr(parsed_args, 'show_schema', False):
                    print("\n=== ENTITY DOMAIN CONFIG SCHEMA ===")
                    domain_schema = get_schema_by_name('entity_domain')
                    if domain_schema:
                        print(format_schema_for_cli(domain_schema))
                    print("=" * 40)
                
                return self.gen_core(
                    config=parsed_args.config,
                    output=parsed_args.output
                )
            elif parsed_args.command == 'gen-repository':
                # Show schema if requested
                if getattr(parsed_args, 'show_schema', False):
                    print("\n=== ENTITY DOMAIN CONFIG SCHEMA ===")
                    domain_schema = get_schema_by_name('entity_domain')
                    if domain_schema:
                        print(format_schema_for_cli(domain_schema))
                    print("=" * 40)
                
                return self.gen_repository(
                    config=parsed_args.config,
                    output=parsed_args.output
                )
            elif parsed_args.command == 'gen-usecase':
                # Show schema if requested
                if getattr(parsed_args, 'show_schema', False):
                    print("\n=== USECASE CONFIG SCHEMA ===")
                    usecase_schema = get_schema_by_name('usecase')
                    if usecase_schema:
                        print(format_schema_for_cli(usecase_schema))
                    print("=" * 40)
                
                return self.gen_usecase(
                    config=parsed_args.config,
                    output=parsed_args.output
                )
            elif parsed_args.command == 'gen-service':
                # Show schema if requested
                if getattr(parsed_args, 'show_schema', False):
                    print("\n=== SERVICE CONFIG SCHEMA ===")
                    service_schema = get_schema_by_name('service')
                    if service_schema:
                        print(format_schema_for_cli(service_schema))
                    print("=" * 40)
                
                return self.gen_service(
                    config=parsed_args.config,
                    output=parsed_args.output
                )
            elif parsed_args.command == 'gen-all':
                return self.gen_all(
                    config=parsed_args.config,
                    output=parsed_args.output,
                    clean=parsed_args.clean
                )
            elif parsed_args.command == 'add-domain':
                return self.add_domain(
                    name=parsed_args.name,
                    layers=parsed_args.layers,
                    output=parsed_args.output
                )
            elif parsed_args.command == 'validate':
                return self.validate(
                    config=parsed_args.config,
                    domain=getattr(parsed_args, 'domain', None)
                )
            elif parsed_args.command == 'usage':
                return self.show_usage(getattr(parsed_args, 'usage_command', None))
            elif parsed_args.command == 'schema':
                return self.show_schema(
                    schema_type=parsed_args.type,
                    format_type=parsed_args.format,
                    show_sample=parsed_args.sample
                )
            elif parsed_args.command == 'workflow':
                return self.show_workflow()
            else:
                self.logger.warning("No command provided", extra={"operation": "cli_help"})
                parser.print_help()
                return 1
                
        except Exception as e:
            self.logger.error("CLI execution failed", exc_info=True, extra={
                "command": getattr(parsed_args, 'command', None),
                "error_type": type(e).__name__,
                "operation": "cli_execution"
            })
            return 1
        finally:
            self.logger.debug("CLI execution completed", extra={
                "command": getattr(parsed_args, 'command', None),
                "operation": "cli_complete"
            })


def main():
    """Main entry point for CLI."""
    cli = GeneratorCLI()
    sys.exit(cli.run())
