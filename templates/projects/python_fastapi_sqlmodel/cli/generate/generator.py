"""
Main domain generator with enhanced output directory management.

This module provides the core domain generation functionality with proper
output directory handling, validation, and error management.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from .config.loader import ConfigurationLoader
from .config.breakdown import ConfigBreakdownEngine
from ..helpers.generation_helpers import DomainGeneratorHelper, GenerationResult

logger = logging.getLogger(__name__)


class DomainGenerator:
    """Production domain generator with enhanced output management."""
    
    def __init__(self, output_dir: Optional[Path] = None, clean_existing: bool = False, 
                 create_structure: bool = True, validate_config: bool = True,
                 validate_syntax: bool = False, validate_imports: bool = False,
                 fail_on_validation_error: bool = False):
        """
        Initialize domain generator.
        
        Args:
            output_dir: Target output directory. Defaults to './generated'.
            clean_existing: Remove existing output directory before generation.
            create_structure: Create parent directories if they don't exist.
            validate_config: Perform strict configuration validation.
            validate_syntax: Enable AST syntax validation of generated Python files.
            validate_imports: Enable import resolution validation of generated Python files.
            fail_on_validation_error: Exit with error if validation finds critical errors.
        """
        self.validate_config = validate_config
        self.validate_syntax = validate_syntax
        self.validate_imports = validate_imports
        self.fail_on_validation_error = fail_on_validation_error
        self.loader = ConfigurationLoader()
        self.breakdown_engine = ConfigBreakdownEngine()
        
        # Set default output directory
        if output_dir is None:
            output_dir = Path.cwd() / "generated"
        
        self.output_dir = output_dir
        self.clean_existing = clean_existing
        self.create_structure = create_structure
        
        # Initialize helper
        self.generator_helper = DomainGeneratorHelper()
        
        # Prepare output directory
        if create_structure:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if clean_existing and self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DomainGenerator initialized with output: {self.output_dir}")
    
    def generate_from_config_file(self, config_file: Path) -> GenerationResult:
        """
        Generate domain from configuration file.
        
        Handles both external configs (one-time use) and co-located configs.
        External configs are automatically broken down into co-located structure.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            GenerationResult with success status and generated files
        """
        logger.info(f"Generating domain from config file: {config_file}")
        
        try:
            # Check if this is an external config that needs breakdown
            if self.breakdown_engine.is_external_config(config_file):
                logger.info("🔄 External config detected, breaking down into co-located structure...")
                
                # Break down external config into co-located structure
                domain_config_path, entities_config_path, breakdown_info = (
                    self.breakdown_engine.breakdown_external_config(config_file, self.output_dir)
                )
                
                logger.info("✅ Breakdown complete:")
                logger.info(f"   📄 Domain config: {domain_config_path}")
                logger.info(f"   📄 Entities config: {entities_config_path}")
                
                # Use the co-located domain directory for generation
                domain_dir = domain_config_path.parent
                domain_name = breakdown_info['domain_name']
                
                # Generate from co-located configs
                return self.generate_domain(domain_name, domain_dir)
                
            else:
                # This is already a co-located config or single config file
                logger.info("📁 Co-located or single config detected")
                
                # Check if this is a co-located domain config (domain.yaml in domain directory)
                if config_file.name == 'domain.yaml' and len(config_file.parts) >= 2:
                    # This is a co-located domain config, use the breakdown engine to load it
                    domain_dir = config_file.parent
                    domain_name = domain_dir.name
                    logger.info(f"📁 Loading co-located domain config from: {domain_dir}")
                    
                    # Generate from co-located directory
                    return self.generate_domain(domain_name, domain_dir)
                    
                else:
                    # This is a traditional single config file
                    logger.info("📄 Loading traditional config file")
                    config = self.loader.load_from_file(config_file)
                    domain_name = config.domain.name if config.domain else 'unknown'
                    
                    # Use the config file's directory
                    return self.generate_domain(domain_name, config_file.parent)
            
        except Exception as e:
            logger.error(f"Failed to generate from config file {config_file}: {e}")
            return GenerationResult(
                domain_name="unknown",
                output_dir=self.output_dir,
                success=False,
                errors=[f"Configuration loading failed: {str(e)}"]
            )
    
    def generate_domain(self, domain_name: str, config_dir: Path, layers: Optional[list] = None) -> GenerationResult:
        """
        Generate complete domain from configuration directory.
        
        Args:
            domain_name: Name of the domain to generate
            config_dir: Directory containing configuration files
            layers: List of layers to generate (default: all)
            
        Returns:
            GenerationResult with success status and generated files
        """
        logger.info(f"Generating domain: {domain_name}")
        
        try:
            # Generate using helper
            result = self.generator_helper.generate_complete_domain(
                domain_name=domain_name,
                config_dir=config_dir,
                output_dir=self.output_dir,
                layers=layers
            )
            
            if result.success:
                logger.info(f"Successfully generated {result.total_files_generated} files to {result.output_dir}")
                for file_result in result.generated_files:
                    if file_result.success:
                        rel_path = file_result.file_path.relative_to(result.output_dir)
                        logger.debug(f"Generated: {rel_path}")
                
                # Perform validation if requested
                if self.validate_syntax or self.validate_imports:
                    self._perform_post_generation_validation(result)
            else:
                logger.error(f"Generation failed with {result.total_errors} errors")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate domain {domain_name}: {e}")
            return GenerationResult(
                domain_name=domain_name,
                output_dir=self.output_dir,
                success=False,
                errors=[f"Generation failed: {str(e)}"]
            )
    
    def generate_complete_application(
        self,
        app_name: str,
        domains: List[str],
        config_dir: Path,
        output_dir: Path,
        app_config: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        Generate complete FastAPI application with all domains and layers.
        
        Args:
            app_name: Name of the application
            domains: List of domain names to include
            config_dir: Directory containing domain configurations
            output_dir: Output directory for generated application
            app_config: Additional application configuration
            
        Returns:
            Complete application generation result
        """
        logger.info(f"Generating complete application: {app_name}")
        
        try:
            # Use helper for complete application generation
            result = self.generator_helper.generate_complete_application(
                app_name=app_name,
                domains=domains,
                config_dir=config_dir,
                output_dir=output_dir,
                app_config=app_config
            )
            
            if result.success:
                logger.info(f"Successfully generated complete application '{app_name}' with {len(result.generated_files)} files")
            else:
                logger.error(f"Application generation failed with {len(result.errors)} errors")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate complete application {app_name}: {e}")
            return GenerationResult(
                domain_name=f"complete_app_{app_name}",
                output_dir=output_dir,
                success=False,
                errors=[f"Application generation failed: {str(e)}"]
            )
    
    def generate_entity_layer(self, domain_name: str, config_dir: Path) -> GenerationResult:
        """
        Generate only the entity layer for a domain.
        
        Args:
            domain_name: Name of the domain to generate
            config_dir: Directory containing configuration files
            
        Returns:
            GenerationResult with success status and generated files
        """
        return self.generate_domain(domain_name, config_dir, layers=['domain'])
    
    def cleanup_domain(self, domain_name: str):
        """Clean up generated files for a specific domain."""
        try:
            self.generator_helper.cleanup_output_directory(self.output_dir, domain_name)
            logger.info(f"Cleaned up domain: {domain_name}")
        except Exception as e:
            logger.error(f"Failed to cleanup domain {domain_name}: {e}")
    
    def generate_from_yaml_string(self, yaml_content: str, domain_name: str = "test") -> GenerationResult:
        """
        Generate domain from YAML string (for testing).
        
        Args:
            yaml_content: YAML configuration as string
            domain_name: Domain name for generation
            
        Returns:
            GenerationResult with success status and generated files
        """
        import tempfile
        import yaml
        
        logger.info(f"Generating domain '{domain_name}' from YAML string")
        
        try:
            # Parse YAML content
            config_dict = yaml.safe_load(yaml_content)
            
            # Create temporary directory for configuration files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Write domain.yaml - handle both old and new format
                domain_config = {}
                if 'domain' in config_dict:
                    domain_config = config_dict['domain']
                else:
                    # If no domain key, assume the whole thing is domain config
                    domain_config = {k: v for k, v in config_dict.items() if k != 'entities'}
                
                domain_config_path = temp_path / f"{domain_name}_domain.yaml" 
                with open(domain_config_path, 'w') as f:
                    yaml.dump(domain_config, f)
                
                # Write entities.yaml - convert to list format expected by EntityDomainLoader
                entities_config = config_dict.get('entities', [])
                
                # EntityDomainLoader expects entities as a list, not a dictionary
                if isinstance(entities_config, list):
                    # Already in correct list format
                    entities_list = entities_config
                elif isinstance(entities_config, dict):
                    # Convert dictionary format to list format
                    entities_list = list(entities_config.values())
                else:
                    # Fallback for other formats
                    entities_list = []
                
                # Wrap in the structure expected by EntityDomainLoader
                entities_final = {'entities': entities_list}
                
                entities_config_path = temp_path / f"{domain_name}_entities.yaml"
                with open(entities_config_path, 'w') as f:
                    yaml.dump(entities_final, f)
                
                # Generate domain
                return self.generate_domain(domain_name, temp_path)
        
        except Exception as e:
            logger.error(f"Failed to generate from YAML string: {e}")
            return GenerationResult(
                domain_name=domain_name,
                output_dir=self.output_dir,
                success=False,
                errors=[f"YAML generation failed: {str(e)}"]
            )
    
    def discover_domains_from_structure(self, project_dir: Path) -> List[str]:
        """
        Auto-discover domains from project structure.
        
        Scans app/domain/ directory for existing domain directories and returns
        list of discovered domain names for CLI integration.
        
        Args:
            project_dir: Root directory of the project
            
        Returns:
            List of discovered domain names
        """
        discovered_domains = []
        
        # Check app/domain directory
        domain_dir = project_dir / 'app' / 'domain'
        
        if not domain_dir.exists():
            logger.info(f"Domain directory not found: {domain_dir}")
            return discovered_domains
        
        logger.info(f"Scanning for domains in: {domain_dir}")
        
        # Look for subdirectories that could be domains
        for item in domain_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                # Skip template directories
                if item.name == '{{domain}}':
                    continue
                    
                # Check if it looks like a domain directory
                if self._is_valid_domain_directory(item):
                    discovered_domains.append(item.name)
                    logger.debug(f"Discovered domain: {item.name}")
        
        logger.info(f"Discovered {len(discovered_domains)} domains: {discovered_domains}")
        return sorted(discovered_domains)
    
    def generate_with_co_location_support(self, domain_name: str, project_dir: Path) -> GenerationResult:
        """
        Generate domain using co-location architecture support.
        
        Args:
            domain_name: Name of the domain to generate
            project_dir: Root directory of the project
            
        Returns:
            GenerationResult with co-location metadata
        """
        logger.info(f"Generating domain '{domain_name}' with co-location support")
        
        try:
            # Use helper's co-location generation method
            from ..helpers.generation_helpers import generate_with_co_location
            
            result = generate_with_co_location(domain_name, project_dir)
            
            # Perform validation if requested
            if self.validate_syntax or self.validate_imports:
                self._perform_post_generation_validation(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate domain with co-location support: {e}")
            return GenerationResult(
                domain_name=domain_name,
                output_dir=project_dir,
                success=False,
                errors=[f"Co-location generation failed: {str(e)}"]
            )
    
    def ensure_templates_co_located(self, domain_name: str, output_dir: Path) -> List[str]:
        """
        Ensure templates are co-located for a domain.
        
        Args:
            domain_name: Name of the domain
            output_dir: Target directory for co-located templates
            
        Returns:
            List of template files that were copied
        """
        logger.info(f"Ensuring templates are co-located for domain: {domain_name}")
        
        try:
            from ..helpers.generation_helpers import ensure_templates_co_located
            
            copied_templates = ensure_templates_co_located(domain_name, output_dir)
            
            logger.info(f"Successfully ensured {len(copied_templates)} templates are co-located")
            return copied_templates
            
        except Exception as e:
            logger.error(f"Failed to ensure templates co-located: {e}")
            return []
    
    def _is_valid_domain_directory(self, domain_path: Path) -> bool:
        """
        Check if a directory looks like a valid domain directory.
        
        Args:
            domain_path: Path to potential domain directory
            
        Returns:
            True if it appears to be a valid domain directory
        """
        # Check for common domain files
        domain_files = [
            'entities.py',
            'exceptions.py',
            '__init__.py'
        ]
        
        # Check for co-located templates
        template_files = [
            'entities.py.j2',
            'exceptions.py.j2',
            'domain.yaml',
            'entities.yaml'
        ]
        
        # At least one domain file should exist
        has_domain_files = any((domain_path / file).exists() for file in domain_files)
        
        # Or co-located templates
        has_templates = any((domain_path / file).exists() for file in template_files)
        
        return has_domain_files or has_templates

    def get_output_info(self) -> Dict[str, Any]:
        """Get detailed information about the output directory."""
        return {
            'output_dir': str(self.output_dir),
            'exists': self.output_dir.exists(),
            'is_directory': self.output_dir.is_dir() if self.output_dir.exists() else False,
            'clean_existing': self.clean_existing,
            'create_structure': self.create_structure
        }


    def _perform_post_generation_validation(self, result: GenerationResult):
        """
        Perform validation on generated files.
        
        Args:
            result: Generation result containing generated files
        """
        try:
            # Get list of generated Python files
            output_files = [f.file_path for f in result.generated_files if f.success]
            
            # Determine validation scope
            validate_syntax = self.validate_syntax
            validate_imports = self.validate_imports
            
            # If both flags are set to False but validate is True, do comprehensive validation
            if not validate_syntax and not validate_imports:
                validate_syntax = True
                validate_imports = True
            
            # Perform validation
            if validate_syntax or validate_imports:
                logger.info("🔍 Validating generated code...")
                
                validation_report = self.generator_helper.validate_generated_files(
                    output_files, self.output_dir
                )
                
                # Display validation results
                formatted_report = self.generator_helper.format_validation_report(validation_report)
                logger.info(f"\n{formatted_report}")
                
                # Handle validation failures
                if not validation_report['success'] and self.fail_on_validation_error:
                    logger.error("❌ Validation failed with critical errors")
                    result.success = False
                    result.errors.append("Code validation failed with critical errors")
                elif validation_report['warnings'] > 0:
                    logger.warning(f"⚠️ Validation completed with {validation_report['warnings']} warnings")
                
        except Exception as e:
            logger.warning(f"⚠️ Validation error: {e}")
            if self.fail_on_validation_error:
                result.success = False
                result.errors.append(f"Validation failed: {e}")


def create_generator(output_dir: Optional[str] = None, clean: bool = False, 
                    validate: bool = True, validate_syntax: bool = False,
                    validate_imports: bool = False, fail_on_validation_error: bool = False) -> DomainGenerator:
    """
    Convenience function to create a DomainGenerator instance.
    
    Args:
        output_dir: Output directory path as string
        clean: Clean existing directory before generation
        validate: Perform strict configuration validation
        validate_syntax: Enable AST syntax validation of generated Python files
        validate_imports: Enable import resolution validation of generated Python files  
        fail_on_validation_error: Exit with error if validation finds critical errors
        
    Returns:
        Configured DomainGenerator instance
    """
    output_path = Path(output_dir) if output_dir else None
    
    return DomainGenerator(
        output_dir=output_path,
        clean_existing=clean,
        validate_config=validate,
        validate_syntax=validate_syntax,
        validate_imports=validate_imports,
        fail_on_validation_error=fail_on_validation_error
    )