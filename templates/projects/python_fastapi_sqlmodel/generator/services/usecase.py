"""
Ultra-Simple UseCase Layer Generator.

Convention-based usecase generation with validated configs using ConfigProcessor.
"""

from pathlib import Path
import logging

from ..utils import TemplateCodeGenerator, ConfigProcessor, ConfigProcessingError
from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import GenerationResult, TemplateContext
from ..types.models.config_models import UseCaseDomainConfig

logger = get_logger(__name__)


class UseCaseLayerGenerator:
    """Ultra-simple usecase generator using conventions and validated configs."""

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize usecase generator.
        
        Args:
            target_dir: Root of target project
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        # Template source is always at fixed location relative to this file
        template_base = Path(__file__).parent.parent.parent
        self.template_generator = TemplateCodeGenerator(template_base)
        self.config_processor = ConfigProcessor(template_base)
        
        self.logger.debug("UseCase layer generator initialized", extra={
            "target_dir": str(self.target_dir),
            "template_base": str(template_base),
            "operation": "init"
        })

    def generate_usecase(self, domain_name: str) -> GenerationResult:
        """
        Generate usecase using validated configs and templates.
        
        Args:
            domain_name: Domain name (e.g., "Health")
            
        Returns:
            GenerationResult with detailed information about the operation
        """
        result = GenerationResult(
            success=True,
            operation_type="generate_usecase",
            metadata={"domain": domain_name}
        )
        
        with self.logger.timed_operation("generate_usecase", {"domain": domain_name}):
            try:
                self.logger.debug("Starting usecase generation", extra={
                    "domain": domain_name,
                    "operation": "generate_usecase",
                    "phase": "start"
                })
                
                # Load and validate usecase configuration
                usecase_dir = self.target_dir / "app" / "usecase" / domain_name
                
                if not usecase_dir.exists():
                    error_msg = f"UseCase directory not found: {usecase_dir}"
                    self.logger.error("UseCase directory not found", extra={
                        "domain": domain_name,
                        "path": str(usecase_dir),
                        "operation": "generate_usecase"
                    })
                    result.add_error(error_msg)
                    return result
                
                # Load usecase config using ConfigProcessor for validation
                try:
                    self.logger.debug("Loading usecase configuration", extra={
                        "domain": domain_name,
                        "config_dir": str(usecase_dir),
                        "operation": "load_config"
                    })
                    usecase_config = self.config_processor.load_usecase_config(usecase_dir)
                    
                    self.logger.debug("UseCase config loaded successfully", extra={
                        "domain": domain_name,
                        "usecase_name": usecase_config.name,
                        "method_count": len(usecase_config.methods),
                        "has_business_rules": bool(usecase_config.business_rules),
                        "has_orchestration": bool(usecase_config.orchestration),
                        "operation": "config_validation"
                    })
                except ConfigProcessingError as e:
                    error_msg = f"UseCase config validation failed: {str(e)}"
                    self.logger.error("UseCase config validation failed", exc_info=True, extra={
                        "domain": domain_name,
                        "config_dir": str(usecase_dir),
                        "operation": "validate_config"
                    })
                    result.add_error(error_msg)
                    return result
            
                # Create template context from validated config
                context = TemplateContext(
                    domain=domain_name,
                    package_name=usecase_config.package,
                    plural_name=f"{domain_name}s",
                    description=usecase_config.description,
                    metadata={
                        'usecase': usecase_config.name,
                        'usecase_description': usecase_config.description,
                        'usecase_package': usecase_config.package,
                        'methods': [method.model_dump() for method in usecase_config.methods],
                        'dependencies': usecase_config.dependencies.model_dump() if hasattr(usecase_config.dependencies, 'model_dump') else usecase_config.dependencies,
                        'error_handling': usecase_config.error_handling.model_dump() if hasattr(usecase_config.error_handling, 'model_dump') else usecase_config.error_handling,
                        'business_rules': usecase_config.business_rules,
                        'orchestration': usecase_config.orchestration,
                        'integration': usecase_config.integration
                    }
                )
                
                self.logger.debug("Template context created", extra={
                    "domain": domain_name,
                    "usecase_name": usecase_config.name,
                    "method_count": len(usecase_config.methods),
                    "dependency_count": len(usecase_config.dependencies.model_dump() if hasattr(usecase_config.dependencies, 'model_dump') else usecase_config.dependencies),
                    "has_error_handling": bool(usecase_config.error_handling),
                    "business_rules_count": len(usecase_config.business_rules) if usecase_config.business_rules else 0,
                    "has_orchestration": bool(usecase_config.orchestration),
                    "has_integration": bool(usecase_config.integration),
                    "operation": "create_context"
                })
            
                # Process all .j2 templates in the target directory
                templates_found = list(usecase_dir.glob("*.j2"))
                self.logger.debug("Processing usecase templates", extra={
                    "domain": domain_name,
                    "template_count": len(templates_found),
                    "templates": [t.name for t in templates_found],
                    "operation": "process_templates"
                })
                
                for template in templates_found:
                    self.logger.debug("Processing template", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "operation": "process_template"
                    })
                    
                    code = self.template_generator.generate_from_template(template, context)
                    output_file = usecase_dir / template.name[:-3]  # Remove .j2
                    output_file.write_text(code)
                    result.add_generated_file(str(output_file))
                    
                    self.logger.info("UseCase file generated", extra={
                        "file": str(output_file),
                        "domain": domain_name,
                        "template": template.name,
                        "operation": "generate_file"
                    })
                
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "usecase"
                self.config_processor.update_domain_status("usecase", layer_path, domain_name, "generated")
                
                self.logger.info("UseCase generation completed successfully", extra={
                    "domain": domain_name,
                    "files_generated": len(templates_found),
                    "operation": "generate_usecase"
                })
                
                result.metadata.update({
                    "templates_processed": len(templates_found),
                    "usecase_name": usecase_config.name
                })
                
                return result
            
            except Exception as e:
                error_msg = f"UseCase generation failed: {str(e)}"
                self.logger.error("UseCase generation failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "generate_usecase"
                })
                result.add_error(error_msg)
                return result
    
    def get_from_config(self, config: UseCaseDomainConfig, domain_name: str) -> GenerationResult:
        """
        Generate usecase from validated UseCaseDomainConfig object.
        
        Args:
            config: Validated UseCaseDomainConfig object
            domain_name: Domain name for the usecase
            
        Returns:
            GenerationResult with detailed information about the operation
        """
        result = GenerationResult(
            success=True,
            operation_type="get_from_config",
            metadata={"domain": domain_name, "usecase_name": config.name}
        )
        
        with self.logger.timed_operation("get_from_config", {"domain": domain_name}):
            try:
                self.logger.debug("Starting usecase generation from config", extra={
                    "domain": domain_name,
                    "usecase_name": config.name,
                    "method_count": len(config.methods),
                    "operation": "get_from_config"
                })
                
                usecase_dir = self.target_dir / "app" / "usecase" / domain_name
                usecase_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.debug("UseCase directory prepared", extra={
                    "domain": domain_name,
                    "directory": str(usecase_dir),
                    "operation": "prepare_directory"
                })
            
                # Create template context from config object
                context = TemplateContext(
                    domain=domain_name,
                    package_name=config.package,
                    plural_name=f"{domain_name}s",
                    description=config.description,
                    metadata={
                        'usecase': config.name,
                        'usecase_description': config.description,
                        'usecase_package': config.package,
                        'methods': [method.model_dump() for method in config.methods],
                        'dependencies': config.dependencies.model_dump() if hasattr(config.dependencies, 'model_dump') else config.dependencies,
                        'error_handling': config.error_handling.model_dump() if hasattr(config.error_handling, 'model_dump') else config.error_handling,
                        'business_rules': config.business_rules,
                        'orchestration': config.orchestration,
                        'integration': config.integration
                    }
                )
                
                self.logger.debug("Template context created from config", extra={
                    "domain": domain_name,
                    "usecase_name": config.name,
                    "usecase_description": config.description[:100] if config.description else None,
                    "method_count": len(config.methods),
                    "dependency_count": len(config.dependencies.model_dump() if hasattr(config.dependencies, 'model_dump') else config.dependencies),
                    "has_error_handling": bool(config.error_handling),
                    "business_rules_count": len(config.business_rules) if config.business_rules else 0,
                    "has_orchestration": bool(config.orchestration),
                    "has_integration": bool(config.integration),
                    "operation": "create_context"
                })
            
                # Find and process templates from template source
                template_source = Path(__file__).parent.parent.parent / "app" / "usecase" / "{{domain}}"
                
                self.logger.debug("Processing templates from source", extra={
                    "domain": domain_name,
                    "template_source": str(template_source),
                    "operation": "find_templates"
                })
                
                # Process all .j2 templates
                templates_found = list(template_source.glob("*.j2"))
                self.logger.debug("Templates discovered", extra={
                    "domain": domain_name,
                    "template_count": len(templates_found),
                    "templates": [t.name for t in templates_found],
                    "operation": "discover_templates"
                })
                
                for template in templates_found:
                    self.logger.debug("Processing template from source", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "template_path": str(template),
                        "operation": "process_template"
                    })
                    
                    code = self.template_generator.generate_from_template(template, context)
                    output_file = usecase_dir / template.name[:-3]  # Remove .j2
                    output_file.write_text(code)
                    result.add_generated_file(str(output_file))
                    
                    self.logger.info("UseCase file generated", extra={
                        "file": str(output_file),
                        "domain": domain_name,
                        "template": template.name,
                        "operation": "generate_file"
                    })
                
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "usecase"
                self.config_processor.update_domain_status("usecase", layer_path, domain_name, "generated")
                
                self.logger.info("UseCase generation from config completed successfully", extra={
                    "domain": domain_name,
                    "files_generated": len(templates_found),
                    "operation": "get_from_config"
                })
                
                result.metadata.update({
                    "templates_processed": len(templates_found),
                    "method_count": len(config.methods)
                })
                
                return result
            
            except Exception as e:
                error_msg = f"UseCase generation from config failed: {str(e)}"
                self.logger.error("UseCase generation from config failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "get_from_config"
                })
                result.add_error(error_msg)
                return result

    def regenerate_all_usecases(self) -> GenerationResult:
        """Regenerate all existing usecases in target project."""
        result = GenerationResult(
            success=True,
            operation_type="regenerate_all_usecases"
        )
        
        with self.logger.timed_operation("regenerate_all_usecases"):
            usecase_dir = self.target_dir / "app" / "usecase"
            
            if not usecase_dir.exists():
                error_msg = f"No app/usecase directory found: {usecase_dir}"
                self.logger.error("No app/usecase directory found", extra={
                    "path": str(usecase_dir),
                    "operation": "regenerate_all_usecases"
                })
                result.add_error(error_msg)
                return result
            
            self.logger.debug("Starting regeneration of all usecases", extra={
                "usecase_dir": str(usecase_dir),
                "operation": "regenerate_all_usecases"
            })
            
            # Sync domain registry first
            self.config_processor.sync_domain_registry("usecase", usecase_dir)
            
            # Get all domains from layer config
            domains = self.config_processor.get_all_domains("usecase", usecase_dir)
            
            self.logger.info("Found domains for regeneration", extra={
                "domain_count": len(domains),
                "domains": [d.name for d in domains],
                "operation": "discover_domains"
            })
            
            generated_count = 0
            skipped_count = 0
            
            for domain in domains:
                if domain.status in ["configured", "generated"]:
                    self.logger.debug("Regenerating domain", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "operation": "regenerate_domain"
                    })
                    
                    domain_result = self.generate_usecase(domain.name)
                    if not domain_result.success:
                        result.success = False
                        result.errors.extend(domain_result.errors)
                        self.logger.warning("Domain regeneration failed", extra={
                            "domain": domain.name,
                            "operation": "regenerate_domain"
                        })
                    else:
                        generated_count += 1
                        result.files_generated.extend(domain_result.files_generated)
                        result.files_modified.extend(domain_result.files_modified)
                else:
                    skipped_count += 1
                    result.add_skipped_file(f"Domain {domain.name} (status: {domain.status})")
                    self.logger.debug("Skipping domain with status", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "operation": "skip_domain"
                    })
            
            result.metadata.update({
                "total_domains": len(domains),
                "generated_count": generated_count,
                "skipped_count": skipped_count
            })
            
            self.logger.info("UseCase regeneration completed", extra={
                "total_domains": len(domains),
                "generated_count": generated_count,
                "skipped_count": skipped_count,
                "success": result.success,
                "operation": "regenerate_all_usecases"
            })
            
            return result
    
    def create_blank_usecase(self, domain_name: str) -> GenerationResult:
        """
        Create a blank usecase with config files processed from templates.
        
        Args:
            domain_name: Name of domain to create usecase for
            
        Returns:
            GenerationResult with detailed information about the operation
        """
        result = GenerationResult(
            success=True,
            operation_type="create_blank_usecase",
            metadata={"domain": domain_name}
        )
        
        with self.logger.timed_operation("create_blank_usecase", {"domain": domain_name}):
            try:
                self.logger.debug("Creating blank usecase", extra={
                    "domain": domain_name,
                    "operation": "create_blank_usecase"
                })
                
                # Create usecase directory
                usecase_dir = self.target_dir / "app" / "usecase" / domain_name
                usecase_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.debug("UseCase directory created", extra={
                    "domain": domain_name,
                    "directory": str(usecase_dir),
                    "operation": "create_directory"
                })
                
                # Use the template file that was already copied during initialization
                template_config_path = usecase_dir / "usecase.yaml"
                
                # Create template context
                context = TemplateContext(
                    domain=domain_name,
                    plural_name=f"{domain_name}s",
                    metadata={
                        'domain_name': domain_name,
                        'domain_name_plural': f"{domain_name}s",
                        'entity_name': domain_name.title()
                    }
                )
                
                self.logger.debug("Template context created for blank usecase", extra={
                    "domain": domain_name,
                    "entity_name": domain_name.title(),
                    "operation": "create_context"
                })
            
                if template_config_path.exists():
                    # Template file already exists from initialization - process it
                    self.logger.debug("Processing existing template config", extra={
                        "domain": domain_name,
                        "config_path": str(template_config_path),
                        "operation": "process_existing_template"
                    })
                    
                    config_content = self.template_generator.generate_from_template(template_config_path, context)
                    template_config_path.write_text(config_content)
                    result.add_generated_file(str(template_config_path))
                else:
                    # Fallback: copy from template source and process
                    template_source = Path(__file__).parent.parent.parent / "app" / "usecase" / "{{domain}}" / "usecase.yaml"
                    
                    self.logger.debug("Using fallback template source", extra={
                        "domain": domain_name,
                        "template_source": str(template_source),
                        "operation": "fallback_template"
                    })
                    
                    if template_source.exists():
                        config_content = self.template_generator.generate_from_template(template_source, context)
                        template_config_path.write_text(config_content)
                        result.add_generated_file(str(template_config_path))
                    else:
                        error_msg = f"Template source not found: {template_source}"
                        self.logger.error("Template source not found", extra={
                            "domain": domain_name,
                            "template_source": str(template_source),
                            "operation": "template_not_found"
                        })
                        result.add_error(error_msg)
                        return result
                
                # Add to layer config as blank domain
                layer_path = self.target_dir / "app" / "usecase"
                self.config_processor.create_blank_domain("usecase", layer_path, domain_name)
                
                self.logger.info("Blank usecase created successfully", extra={
                    "domain": domain_name,
                    "config_path": str(template_config_path),
                    "usecase_dir": str(usecase_dir),
                    "operation": "create_blank_usecase"
                })
                
                result.metadata.update({
                    "config_path": str(template_config_path),
                    "usecase_dir": str(usecase_dir)
                })
                
                return result
            
            except Exception as e:
                error_msg = f"Failed to create blank usecase: {str(e)}"
                self.logger.error("Failed to create blank usecase", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "create_blank_usecase"
                })
                result.add_error(error_msg)
                return result
