#!/usr/bin/env python3
"""
Command-line interface for FastAPI SQLModel project and domain generation.

Provides a user-friendly CLI for:
1. Initializing complete FastAPI projects
2. Generating domains from configuration files
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from .generator import DomainGenerator, create_generator
from .project_initializer import ProjectInitializer


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description='FastAPI SQLModel Project Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize a new project
  fastapi-sqlmodel-generator init --project-name "My API" --output ./my-api
  
  # Generate from external config (auto-breakdown to co-located)
  fastapi-sqlmodel-generator generate --config external_domain.yaml --output ./app
  
  # Generate from co-located config (auto-detected)
  fastapi-sqlmodel-generator generate --config app/domain/HealthStatus/domain.yaml --output ./app
  
  # Clean existing directory before generation
  fastapi-sqlmodel-generator generate --config domain.yaml --output ./app --clean
  
  # Generate with comprehensive validation
  fastapi-sqlmodel-generator generate --config domain.yaml --validate
  
  # Show complete usage documentation
  fastapi-sqlmodel-generator docs
        """
    )
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init subcommand
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize a new FastAPI SQLModel project',
        description='Create complete project structure with all necessary files'
    )
    init_parser.add_argument(
        '--project-name', '-n',
        type=str,
        required=True,
        help='Name of the project to create'
    )
    init_parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path.cwd(),
        help='Output directory for project (default: current directory)'
    )
    init_parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean existing output directory before initialization'
    )
    init_parser.add_argument(
        '--description', '-d',
        type=str,
        help='Project description'
    )
    init_parser.add_argument(
        '--author', '-a',
        type=str,
        help='Project author'
    )
    
    # Generate subcommand  
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate domain from configuration file',
        description='Generate domain code from YAML configuration with co-location auto-detection'
    )
    
    # Docs subcommand
    docs_parser = subparsers.add_parser(
        'docs',
        help='Show documentation and usage guide',
        description='Display the complete LLM usage guide as text'
    )
    generate_parser.add_argument(
        '--config', '-c',
        type=Path,
        required=True,
        help='Path to YAML configuration file'
    )
    generate_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output directory (default: ./generated)'
    )
    generate_parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean existing output directory before generation'
    )
    generate_parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip strict configuration validation (for testing)'
    )
    generate_parser.add_argument(
        '--validate',
        action='store_true',
        help='Enable comprehensive validation of generated code (syntax and imports)'
    )
    generate_parser.add_argument(
        '--validate-syntax-only',
        action='store_true',
        help='Enable only AST syntax validation of generated Python files'
    )
    generate_parser.add_argument(
        '--validate-imports-only',
        action='store_true',
        help='Enable only import resolution validation of generated Python files'
    )
    generate_parser.add_argument(
        '--fail-on-validation-error',
        action='store_true',
        help='Exit with error code if validation finds critical errors'
    )
    generate_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate configuration and show what would be generated'
    )
    
    # Global options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show tool information and exit'
    )
    
    return parser


def validate_init_args(args) -> tuple[bool, Optional[str]]:
    """Validate init command arguments."""
    # Check project name
    if not args.project_name or not args.project_name.strip():
        return False, "Project name cannot be empty"
    
    # Check output directory validity
    try:
        args.output.resolve()
    except Exception as e:
        return False, f"Invalid output directory path: {e}"
    
    return True, None


def validate_generate_args(args) -> tuple[bool, Optional[str]]:
    """Validate generate command arguments."""
    # Check config file exists
    if not args.config.exists():
        return False, f"Configuration file not found: {args.config}"
    
    if not args.config.is_file():
        return False, f"Configuration path is not a file: {args.config}"
    
    # Check output directory validity
    if args.output:
        try:
            args.output.resolve()
        except Exception as e:
            return False, f"Invalid output directory path: {e}"
    
    return True, None


def handle_init_command(args):
    """Handle project initialization command."""
    print(f"🚀 Initializing FastAPI SQLModel project: {args.project_name}")
    print("=" * 60)
    
    # Validate arguments
    is_valid, error_msg = validate_init_args(args)
    if not is_valid:
        print(f"❌ Error: {error_msg}", file=sys.stderr)
        return False
    
    try:
        # Create project initializer
        initializer = ProjectInitializer()
        
        # Prepare project configuration
        project_config = {}
        if args.description:
            project_config['description'] = args.description
        if args.author:
            project_config['author'] = args.author
        
        # Initialize project
        results = initializer.initialize_project(
            project_name=args.project_name,
            target_dir=args.output,
            project_config=project_config,
            clean_existing=args.clean
        )
        
        # Show results
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        if success_count == total_count:
            print("✅ Project initialization successful!")
            print(f"📁 Project created in: {args.output.absolute()}")
            print(f"📄 Generated {success_count} files")
            
            # Show generated files
            for result in results[:10]:  # Show first 10 files
                status = "✅" if result.success else "❌"
                rel_path = result.file_path.relative_to(args.output) if result.file_path.is_relative_to(args.output) else result.file_path
                print(f"   {status} {rel_path}")
            
            if total_count > 10:
                print(f"   ... and {total_count - 10} more files")
            
            print("\n🎯 Next steps:")
            print(f"   1. cd {args.output}")
            print("   2. uv sync  # Install dependencies and create uv.lock")
            print("   3. just dev  # Start development server")
            print("   4. Visit http://localhost:8000/docs")
            print("\n📖 To add domains:")
            print("   fastapi-sqlmodel-generator generate --config domain.yaml --output ./app")
            
        else:
            print("⚠️ Project initialization completed with issues")
            print(f"📄 Generated {success_count}/{total_count} files successfully")
            
            # Show errors
            for result in results:
                if not result.success:
                    print(f"   ❌ {result.file_path}: {'; '.join(result.errors)}")
        
        # Validate initialization
        validation = initializer.validate_initialization(args.output)
        if not validation['success']:
            print("\n⚠️ Validation warnings:")
            for error in validation['errors']:
                print(f"   - {error}")
        
        return success_count == total_count
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def handle_generate_command(args):
    """Handle domain generation command with co-location auto-detection."""
    
    print(f"🚀 Generating domain from: {args.config}")
    
    # Validate arguments
    is_valid, error_msg = validate_generate_args(args)
    if not is_valid:
        print(f"❌ Error: {error_msg}", file=sys.stderr)
        return False
    
    try:
        # Auto-detect configuration type and workflow
        config_type, domain_name = auto_detect_config_type(args.config)
        print(f"📋 Detected config type: {config_type}")
        
        if config_type == "co_located":
            return handle_co_located_generation(args, domain_name)
        elif config_type == "external":
            return handle_external_config_breakdown(args)
        else:
            return handle_traditional_generation(args)
            
    except Exception as e:
        print(f"❌ Generation failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def auto_detect_config_type(config_path):
    """Auto-detect if config is external, co-located, or traditional."""
    config_path = Path(config_path)
    
    # Check if config is in co-located structure (app/domain/DomainName/)
    if len(config_path.parts) >= 3 and config_path.parts[-3:-1] == ('app', 'domain'):
        domain_name = config_path.parts[-2]
        return "co_located", domain_name
    
    # Check if config contains multiple entities (external config)
    try:
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # If config has multiple entities, it's external
        if isinstance(config_data, dict) and 'entities' in config_data:
            entities = config_data['entities']
            if isinstance(entities, list) and len(entities) > 1:
                return "external", None
    except Exception:
        pass
    
    return "traditional", None


def handle_co_located_generation(args, domain_name):
    """Handle co-location architecture generation for detected domain."""
    print(f"🏗️ Co-location Architecture Generation for domain: {domain_name}")
    print("=" * 60)
    
    try:
        from .config.loader import CoLocationConfigLoader
        from .generator import create_generator
        from ..helpers.generation_helpers import copy_templates_to_domain
        
        # Determine project directory
        project_dir = Path.cwd()
        if args.output:
            project_dir = args.output.parent if args.output.name == 'app' else args.output
        
        # Check for domain directory
        domain_dir = project_dir / 'app' / 'domain' / domain_name
        
        if not domain_dir.exists():
            print(f"❌ Domain directory not found: {domain_dir}")
            print("💡 Creating domain directory structure")
            domain_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Using domain directory: {domain_dir}")
        
        # Load co-located configuration
        co_loader = CoLocationConfigLoader()
        
        try:
            config = co_loader.load_co_located_configs(domain_dir)
            print(f"✅ Loaded co-located configuration for domain: {domain_name}")
        except Exception as e:
            print(f"⚠️ Failed to load co-located config: {e}")
            print("💡 Using minimal configuration")
            config = co_loader._create_minimal_configuration(domain_name)
        
        # Determine validation settings
        validate_config = not args.no_validate
        validate_syntax = args.validate or args.validate_syntax_only
        validate_imports = args.validate or args.validate_imports_only
        fail_on_validation_error = args.fail_on_validation_error
        
        # Create generator for co-located output
        output_dir = project_dir / 'app' if args.output is None else args.output
        generator = create_generator(
            output_dir=str(output_dir),
            clean=args.clean,
            validate=validate_config,
            validate_syntax=validate_syntax,
            validate_imports=validate_imports,
            fail_on_validation_error=fail_on_validation_error
        )
        
        # Generate domain
        result = generator.generate_domain(domain_name, domain_dir)
        
        # Copy templates to domain directory for customization
        if result.success:
            copy_result = copy_templates_to_domain(domain_name, domain_dir)
            print(f"📋 Copied templates to domain directory: {copy_result}")
        
        # Show results
        if result.success:
            print("✅ Co-location generation successful!")
            print(f"📁 Domain: {domain_name}")
            print(f"📄 Generated {result.total_files_generated} files")
            print(f"🎯 Templates and configs available in: {domain_dir}")
        else:
            print("❌ Co-location generation failed")
            for error in result.errors:
                print(f"   - {error}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Co-location generation failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def handle_external_config_breakdown(args):
    """Handle external config breakdown into co-located structure."""
    print("📦 External Config → Co-located Breakdown")
    print("=" * 50)
    
    try:
        import yaml
        
        # Load external configuration
        with open(args.config, 'r') as f:
            external_config = yaml.safe_load(f)
        
        if 'entities' not in external_config or not isinstance(external_config['entities'], list):
            print("❌ External config must contain 'entities' list")
            return False
        
        # Break down into domains based on entities
        for entity in external_config['entities']:
            domain_name = entity.get('name', 'UnknownDomain')
            print(f"🔄 Processing domain: {domain_name}")
            
            # Create domain-specific config structure
            domain_config = {
                'name': domain_name,
                'description': f"{domain_name} domain configuration",
                'package': domain_name.lower()
            }
            
            entities_config = {
                'entities': [entity],
                'endpoints': external_config.get('endpoints', [])
            }
            
            # Determine project directory and create co-located structure
            project_dir = Path.cwd()
            if args.output:
                project_dir = args.output.parent if args.output.name == 'app' else args.output
            
            domain_dir = project_dir / 'app' / 'domain' / domain_name
            domain_dir.mkdir(parents=True, exist_ok=True)
            
            # Write co-located configs
            domain_config_file = domain_dir / 'domain.yaml'
            entities_config_file = domain_dir / 'entities.yaml'
            
            with open(domain_config_file, 'w') as f:
                yaml.dump(domain_config, f, default_flow_style=False)
            
            with open(entities_config_file, 'w') as f:
                yaml.dump(entities_config, f, default_flow_style=False)
            
            print(f"✅ Created co-located config for {domain_name} in {domain_dir}")
            
            # Now generate using co-located approach
            class CoLocatedArgs:
                def __init__(self, original_args, config_path):
                    for attr in dir(original_args):
                        if not attr.startswith('_'):
                            setattr(self, attr, getattr(original_args, attr))
                    self.config = config_path
            
            co_located_args = CoLocatedArgs(args, domain_config_file)
            result = handle_co_located_generation(co_located_args, domain_name)
            
            if not result:
                print(f"❌ Failed to generate domain: {domain_name}")
                return False
        
        print("✅ External config breakdown and generation completed!")
        print("💡 Future changes should be made in co-located config files")
        return True
        
    except Exception as e:
        print(f"❌ External config breakdown failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def handle_traditional_generation(args):
    """Handle traditional generation workflow (fallback)."""
    print("🔧 Traditional Generation Workflow")
    
    # Determine validation settings
    validate_config = not args.no_validate
    validate_syntax = args.validate or args.validate_syntax_only
    validate_imports = args.validate or args.validate_imports_only
    fail_on_validation_error = args.fail_on_validation_error
    
    # Create generator
    generator = create_generator(
        output_dir=str(args.output) if args.output else None,
        clean=args.clean,
        validate=validate_config,
        validate_syntax=validate_syntax,
        validate_imports=validate_imports,
        fail_on_validation_error=fail_on_validation_error
    )
    
    # Perform dry run if requested
    if args.dry_run:
        return dry_run(generator, args.config)
    
    # Generate domain
    result = generator.generate_from_config_file(args.config)
    
    # Show results
    show_generation_result(result, args.config)
    
    return result.success




def show_generation_result(result, config_file: Path):
    """Show the results of generation."""
    if result.success:
        files = [f.file_path for f in result.generated_files if f.success]
        print(f"✅ Successfully generated domain from {config_file}")
        print(f"📁 Output: {result.output_dir}")
        print(f"📄 Generated {len(files)} files:")
        
        for file_path in sorted(files):
            rel_path = file_path.relative_to(result.output_dir)
            size = file_path.stat().st_size if file_path.exists() else 0
            print(f"   - {rel_path} ({size} bytes)")
        
        print("\n🎯 Domain integration:")
        print("   1. Import domain routes in app/main.py")
        print("   2. Run tests: uv run just test")
        print("   3. Start server: uv run just dev")
        
    else:
        print(f"❌ Generation failed for {config_file}")
        print("🔥 Errors:")
        for error in result.errors:
            print(f"   - {error}")


def dry_run(generator: DomainGenerator, config_file: Path):
    """Perform a dry run - validate config and show what would be generated."""
    print(f"🧪 Dry run for: {config_file}")
    print("=" * 40)
    
    try:
        # Try to load the configuration
        from cli.generate.config.loader import ConfigurationLoader
        loader = ConfigurationLoader()
        config = loader.load_from_file(config_file)
        
        print("✅ Configuration valid")
        print(f"📋 Domain: {config.domain.name}")
        print(f"📋 Description: {config.domain.description or 'No description'}")
        print(f"📋 Entities: {len(config.entities)}")
        
        for entity in config.entities:
            print(f"   - {entity.name} ({len(entity.fields)} fields)")
        
        print(f"📋 Endpoints: {len(config.endpoints)}")
        
        info = generator.get_output_info()
        print(f"\n📁 Would generate to: {info['absolute_path']}")
        
        # Estimate what would be generated
        domain_name = config.domain.name.lower()
        expected_files = [
            f"domain/{domain_name}/entities.py",
            f"domain/{domain_name}/exceptions.py",
            f"repository/{domain_name}/repository.py",
            f"repository/{domain_name}/protocols.py",
            f"usecase/{domain_name}/usecase.py",
            f"usecase/{domain_name}/schemas.py",
            f"usecase/{domain_name}/protocols.py",
            f"interface/{domain_name}/router.py",
            f"interface/{domain_name}/dependencies.py",
            f"interface/{domain_name}/protocols.py"
        ]
        
        print("📄 Expected files:")
        for file_path in expected_files:
            print(f"   - {file_path}")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
    
    return True


def handle_docs_command(args):
    """Handle docs command - show LLM usage guide."""
    try:
        # Import the embedded documentation
        from .docs import get_documentation
        
        # Display the documentation content
        content = get_documentation()
        print(content)
        return True
        
    except Exception as e:
        print(f"❌ Error loading documentation: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def show_info():
    """Show tool information."""
    print("🔍 FastAPI SQLModel Project Generator")
    print("=" * 40)
    print("Version: 1.0.0")
    print("Description: Generate FastAPI projects and domains from YAML configurations")
    print("")
    print("Available commands:")
    print("  init     - Initialize a new FastAPI SQLModel project")
    print("  generate - Generate domain from configuration file")
    print("  docs     - Show complete LLM usage guide")
    print("")
    print("Features:")
    print("  ✅ Complete project scaffolding")
    print("  ✅ Clean Architecture (Domain/Repository/UseCase/Interface)")
    print("  ✅ Co-location architecture with auto-detection")
    print("  ✅ SQLModel integration")
    print("  ✅ FastAPI with async/await")
    print("  ✅ Comprehensive test generation")
    print("  ✅ Docker and CI/CD setup")
    print("  ✅ Project commands with Justfile")


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Show info and exit if requested
    if args.info:
        show_info()
        return
    
    # Check if command was provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Handle commands
        if args.command == 'init':
            success = handle_init_command(args)
        elif args.command == 'generate':
            success = handle_generate_command(args)
        elif args.command == 'docs':
            success = handle_docs_command(args)
        else:
            print(f"❌ Unknown command: {args.command}", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()