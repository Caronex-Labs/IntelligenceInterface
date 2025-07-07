
"""
Ultra-Simple Core Layer Generator.

Convention-based core layer generation with validated configs using ConfigProcessor.
"""

from pathlib import Path

from ..utils import TemplateCodeGenerator, ConfigProcessor, ConfigProcessingError
from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import GenerationResult, TemplateContext
from ..types.models.config_models import EntityDomainConfig

logger = get_logger(__name__)


class CoreLayerGenerator:
    """Ultra-simple core layer generator using conventions and validated configs."""

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize domain generator.
        
        Args:
            target_dir: Root of target project
        """
        self.target_dir = Path(target_dir)
        
        # Template source is always at fixed location relative to this file
        template_base = Path(__file__).parent.parent.parent
        self.template_generator = TemplateCodeGenerator(template_base)
        self.config_processor = ConfigProcessor(template_base)
        
        logger.debug("CoreLayerGenerator initialized", extra={
            "target_dir": str(self.target_dir),
            "template_base": str(template_base),
            "operation": "init"
        })

    def generate_domain(self, domain_name: str) -> GenerationResult:
        """
        Generate domain using validated configs and templates.
        
        Args:
            domain_name: Domain name (e.g., "Health")
            
        Returns:
            GenerationResult with detailed information about what was generated
        """
        result = GenerationResult(
            success=True,
            operation_type="generate_domain"
        )
        
        logger.debug("Starting domain generation", extra={
            "domain": domain_name,
            "operation": "generate_domain",
            "phase": "start"
        })
        
        with logger.timed_operation("generate_domain", {"domain": domain_name}):
            try:
                # Load and validate domain configuration
                domain_dir = self.target_dir / "app" / "core" / domain_name
                
                logger.debug("Checking domain directory", extra={
                    "domain": domain_name,
                    "path": str(domain_dir),
                    "exists": domain_dir.exists(),
                    "operation": "check_directory"
                })
                
                if not domain_dir.exists():
                    error_msg = f"Domain directory not found: {domain_dir}"
                    logger.error("Domain directory not found", extra={
                        "domain": domain_name,
                        "path": str(domain_dir),
                        "operation": "generate_domain"
                    })
                    result.add_error(error_msg)
                    return result
                
                # Load domain config using ConfigProcessor for validation
                try:
                    logger.debug("Loading domain configuration", extra={
                        "domain": domain_name,
                        "config_dir": str(domain_dir),
                        "operation": "load_config"
                    })
                    domain_config = self.config_processor.load_domain_config(domain_dir)
                    
                    logger.debug("Domain configuration loaded successfully", extra={
                        "domain": domain_name,
                        "config_name": domain_config.name,
                        "entity_count": len(domain_config.entities) if domain_config.entities else 0,
                        "operation": "load_config"
                    })
                    
                except ConfigProcessingError as e:
                    error_msg = f"Domain config validation failed: {str(e)}"
                    logger.error("Domain config validation failed", exc_info=True, extra={
                        "domain": domain_name,
                        "operation": "validate_config"
                    })
                    result.add_error(error_msg)
                    return result
                
                # Create template context from validated config using TemplateContext model
                context = TemplateContext(
                    domain=domain_name,
                    entities=domain_config.entities or [],
                    package_name=domain_config.package,
                    plural_name=domain_config.plural,
                    description=domain_config.description or f"{domain_name} domain",
                    metadata={
                        'domain_name': domain_config.name,
                        'config_loaded_from': str(domain_dir)
                    }
                )
                
                logger.debug("Template context created", extra={
                    "domain": domain_name,
                    "entity_count": len(context.entities),
                    "package_name": context.package_name,
                    "plural_name": context.plural_name,
                    "operation": "create_context"
                })
                
                # Process all .j2 templates in the target directory
                templates = list(domain_dir.glob("*.j2"))
                logger.debug("Found templates for processing", extra={
                    "domain": domain_name,
                    "template_count": len(templates),
                    "templates": [t.name for t in templates],
                    "operation": "find_templates"
                })
                
                for template in templates:
                    logger.debug("Processing template", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "template_path": str(template),
                        "operation": "process_template"
                    })
                    
                    try:
                        code = self.template_generator.generate_from_template(template, context)
                        output_file = domain_dir / template.name[:-3]  # Remove .j2
                        output_file.write_text(code)
                        
                        result.add_generated_file(str(output_file))
                        
                        logger.info("Domain file generated", extra={
                            "file": str(output_file),
                            "domain": domain_name,
                            "template": template.name,
                            "operation": "generate_file"
                        })
                    except Exception as template_error:
                        error_msg = f"Failed to process template {template.name}: {str(template_error)}"
                        result.add_error(error_msg)
                        logger.error("Template processing failed", exc_info=True, extra={
                            "domain": domain_name,
                            "template": template.name,
                            "operation": "process_template"
                        })
                
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "core"
                logger.debug("Updating domain status", extra={
                    "domain": domain_name,
                    "layer": "core",
                    "status": "generated",
                    "layer_path": str(layer_path),
                    "operation": "update_status"
                })
                
                try:
                    self.config_processor.update_domain_status("core", layer_path, domain_name, "generated")
                except Exception as status_error:
                    warning_msg = f"Failed to update domain status: {str(status_error)}"
                    result.add_warning(warning_msg)
                    logger.warning("Domain status update failed", exc_info=True, extra={
                        "domain": domain_name,
                        "operation": "update_status"
                    })
                
                result.metadata.update({
                    "domain": domain_name,
                    "template_count": len(templates),
                    "entity_count": len(context.entities)
                })
                
                logger.info("Domain generation completed successfully", extra={
                    "domain": domain_name,
                    "template_count": len(templates),
                    "files_generated": len(result.files_generated),
                    "operation": "generate_domain"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Domain generation failed: {str(e)}"
                result.add_error(error_msg)
                logger.error("Domain generation failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "generate_domain"
                })
                return result
    
    def get_from_config(self, config: EntityDomainConfig) -> GenerationResult:
        """
        Generate domain from validated EntityDomainConfig object.
        
        Args:
            config: Validated EntityDomainConfig object
            
        Returns:
            GenerationResult with detailed information about what was generated
        """
        domain_name = config.name
        result = GenerationResult(
            success=True,
            operation_type="get_from_config"
        )
        
        logger.debug("Starting domain generation from config", extra={
            "domain": domain_name,
            "config_type": type(config).__name__,
            "operation": "get_from_config",
            "phase": "start"
        })
        
        with logger.timed_operation("get_from_config", {"domain": domain_name}):
            try:
                domain_dir = self.target_dir / "app" / "core" / domain_name
                
                logger.debug("Creating domain directory", extra={
                    "domain": domain_name,
                    "path": str(domain_dir),
                    "operation": "create_directory"
                })
                
                domain_dir.mkdir(parents=True, exist_ok=True)
                
                # Create template context from config object using TemplateContext model
                context = TemplateContext(
                    domain=domain_name,
                    entities=config.entities or [],
                    package_name=config.package,
                    plural_name=config.plural,
                    description=config.description or f"{domain_name} domain",
                    metadata={
                        'domain_name': config.name,
                        'config_source': 'direct_config_object'
                    }
                )
                
                logger.debug("Template context created from config", extra={
                    "domain": domain_name,
                    "entity_count": len(context.entities),
                    "plural": context.plural_name,
                    "package": context.package_name,
                    "operation": "create_context"
                })
                
                # Find and process templates from template source
                template_source = Path(__file__).parent.parent.parent / "app" / "core" / "{{domain}}"
                
                logger.debug("Looking for templates in source", extra={
                    "domain": domain_name,
                    "template_source": str(template_source),
                    "source_exists": template_source.exists(),
                    "operation": "find_template_source"
                })
                
                if not template_source.exists():
                    error_msg = f"Template source directory not found: {template_source}"
                    result.add_error(error_msg)
                    logger.error("Template source not found", extra={
                        "domain": domain_name,
                        "template_source": str(template_source),
                        "operation": "find_template_source"
                    })
                    return result
                
                # Process all .j2 templates
                templates = list(template_source.glob("*.j2"))
                logger.debug("Found templates in source", extra={
                    "domain": domain_name,
                    "template_count": len(templates),
                    "templates": [t.name for t in templates],
                    "operation": "find_templates"
                })
                
                for template in templates:
                    logger.debug("Processing template from source", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "template_path": str(template),
                        "operation": "process_template"
                    })
                    
                    try:
                        code = self.template_generator.generate_from_template(template, context)
                        output_file = domain_dir / template.name[:-3]  # Remove .j2
                        output_file.write_text(code)
                        
                        result.add_generated_file(str(output_file))
                        
                        logger.info("Domain file generated", extra={
                            "file": str(output_file),
                            "domain": domain_name,
                            "template": template.name,
                            "operation": "generate_file"
                        })
                    except Exception as template_error:
                        error_msg = f"Failed to process template {template.name}: {str(template_error)}"
                        result.add_error(error_msg)
                        logger.error("Template processing failed", exc_info=True, extra={
                            "domain": domain_name,
                            "template": template.name,
                            "operation": "process_template"
                        })
                
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "core"
                logger.debug("Updating domain status", extra={
                    "domain": domain_name,
                    "layer": "core",
                    "status": "generated",
                    "layer_path": str(layer_path),
                    "operation": "update_status"
                })
                
                try:
                    self.config_processor.update_domain_status("core", layer_path, domain_name, "generated")
                except Exception as status_error:
                    warning_msg = f"Failed to update domain status: {str(status_error)}"
                    result.add_warning(warning_msg)
                    logger.warning("Domain status update failed", exc_info=True, extra={
                        "domain": domain_name,
                        "operation": "update_status"
                    })
                
                result.metadata.update({
                    "domain": domain_name,
                    "template_count": len(templates),
                    "entity_count": len(context.entities),
                    "config_source": "direct_config_object"
                })
                
                logger.info("Domain generation from config completed successfully", extra={
                    "domain": domain_name,
                    "template_count": len(templates),
                    "files_generated": len(result.files_generated),
                    "operation": "get_from_config"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Domain generation from config failed: {str(e)}"
                result.add_error(error_msg)
                logger.error("Domain generation from config failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "get_from_config"
                })
                return result

    def regenerate_all_domains(self) -> GenerationResult:
        """Regenerate all existing domains in target project."""
        result = GenerationResult(
            success=True,
            operation_type="regenerate_all_domains"
        )
        
        logger.debug("Starting regeneration of all domains", extra={
            "operation": "regenerate_all_domains",
            "phase": "start"
        })
        
        with logger.timed_operation("regenerate_all_domains"):
            domain_dir = self.target_dir / "app" / "core"
            
            logger.debug("Checking core directory", extra={
                "path": str(domain_dir),
                "exists": domain_dir.exists(),
                "operation": "check_core_directory"
            })
            
            if not domain_dir.exists():
                error_msg = f"Core directory not found: {domain_dir}"
                result.add_error(error_msg)
                logger.error("Core directory not found", extra={
                    "path": str(domain_dir),
                    "operation": "regenerate_all_domains"
                })
                return result
            
            # Sync domain registry first
            logger.debug("Syncing domain registry", extra={
                "layer": "core",
                "path": str(domain_dir),
                "operation": "sync_registry"
            })
            
            try:
                self.config_processor.sync_domain_registry("core", domain_dir)
            except Exception as sync_error:
                warning_msg = f"Failed to sync domain registry: {str(sync_error)}"
                result.add_warning(warning_msg)
                logger.warning("Domain registry sync failed", exc_info=True, extra={
                    "operation": "sync_registry"
                })
            
            # Get all domains from layer config
            try:
                domains = self.config_processor.get_all_domains("core", domain_dir)
            except Exception as get_domains_error:
                error_msg = f"Failed to get domains from layer config: {str(get_domains_error)}"
                result.add_error(error_msg)
                logger.error("Failed to get domains", exc_info=True, extra={
                    "operation": "get_domains"
                })
                return result
            
            logger.info("Found domains for regeneration", extra={
                "domain_count": len(domains),
                "domains": [d.name for d in domains],
                "operation": "get_domains"
            })
            
            regenerated_count = 0
            skipped_count = 0
            
            for domain in domains:
                if domain.status in ["configured", "generated"]:
                    logger.debug("Regenerating domain", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "operation": "regenerate_domain"
                    })
                    
                    domain_result = self.generate_domain(domain.name)
                    if not domain_result.success:
                        result.errors.extend(domain_result.errors)
                        result.warnings.extend(domain_result.warnings)
                        logger.warning("Domain regeneration failed", extra={
                            "domain": domain.name,
                            "errors": len(domain_result.errors),
                            "operation": "regenerate_domain"
                        })
                    else:
                        regenerated_count += 1
                        result.files_generated.extend(domain_result.files_generated)
                        result.files_modified.extend(domain_result.files_modified)
                else:
                    logger.debug("Skipping domain regeneration", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "reason": "status_not_eligible",
                        "operation": "skip_domain"
                    })
                    result.add_skipped_file(f"Domain {domain.name} (status: {domain.status})")
                    skipped_count += 1
            
            # Set overall success based on whether we had any errors
            if result.errors:
                result.success = False
            
            result.metadata.update({
                "total_domains": len(domains),
                "regenerated": regenerated_count,
                "skipped": skipped_count,
                "domain_names": [d.name for d in domains]
            })
            
            logger.info("Domain regeneration completed", extra={
                "total_domains": len(domains),
                "regenerated": regenerated_count,
                "skipped": skipped_count,
                "success": result.success,
                "files_generated": len(result.files_generated),
                "operation": "regenerate_all_domains"
            })
            
            return result
    
    def create_blank_domain(self, domain_name: str) -> GenerationResult:
        """
        Create a blank domain with config files processed from templates.
        
        Args:
            domain_name: Name of domain to create
            
        Returns:
            GenerationResult with detailed information about what was created
        """
        result = GenerationResult(
            success=True,
            operation_type="create_blank_domain"
        )
        
        logger.debug("Starting blank domain creation", extra={
            "domain": domain_name,
            "operation": "create_blank_domain",
            "phase": "start"
        })
        
        with logger.timed_operation("create_blank_domain", {"domain": domain_name}):
            try:
                # Create domain directory
                domain_dir = self.target_dir / "app" / "core" / domain_name
                
                logger.debug("Creating domain directory", extra={
                    "domain": domain_name,
                    "path": str(domain_dir),
                    "operation": "create_directory"
                })
                
                domain_dir.mkdir(parents=True, exist_ok=True)
                
                # Create template context using TemplateContext model
                context = TemplateContext(
                    domain=domain_name,
                    entities=[],  # Blank domain starts with no entities
                    package_name=domain_name.lower(),
                    plural_name=f"{domain_name}s",
                    description=f"Blank {domain_name} domain",
                    metadata={
                        'domain_name': domain_name,
                        'entity_name': domain_name.title(),
                        'creation_type': 'blank_domain'
                    }
                )
                
                logger.debug("Template context created for blank domain", extra={
                    "domain": domain_name,
                    "entity_name": context.metadata.get('entity_name'),
                    "plural": context.plural_name,
                    "package": context.package_name,
                    "operation": "create_context"
                })
                
                # Process domain.yaml template
                domain_yaml = domain_dir / "domain.yaml"
                logger.debug("Processing domain.yaml template", extra={
                    "domain": domain_name,
                    "file_path": str(domain_yaml),
                    "exists": domain_yaml.exists(),
                    "operation": "process_domain_yaml"
                })
                
                try:
                    if domain_yaml.exists():
                        # Template file already exists from initialization - process it
                        logger.debug("Using existing domain.yaml template", extra={
                            "domain": domain_name,
                            "template_path": str(domain_yaml),
                            "operation": "use_existing_template"
                        })
                        config_content = self.template_generator.generate_from_template(domain_yaml, context)
                        domain_yaml.write_text(config_content)
                        result.add_generated_file(str(domain_yaml))
                    else:
                        # Fallback: copy from template source and process
                        template_source = Path(__file__).parent.parent.parent / "app" / "core" / "{{domain}}" / "domain.yaml"
                        logger.debug("Using fallback domain.yaml template", extra={
                            "domain": domain_name,
                            "template_source": str(template_source),
                            "source_exists": template_source.exists(),
                            "operation": "use_fallback_template"
                        })
                        
                        if template_source.exists():
                            config_content = self.template_generator.generate_from_template(template_source, context)
                            domain_yaml.write_text(config_content)
                            result.add_generated_file(str(domain_yaml))
                        else:
                            error_msg = f"Domain template source not found: {template_source}"
                            result.add_error(error_msg)
                            logger.error("Domain template source not found", extra={
                                "domain": domain_name,
                                "template_source": str(template_source),
                                "operation": "find_template_source"
                            })
                            return result
                except Exception as domain_yaml_error:
                    error_msg = f"Failed to process domain.yaml template: {str(domain_yaml_error)}"
                    result.add_error(error_msg)
                    logger.error("Domain.yaml processing failed", exc_info=True, extra={
                        "domain": domain_name,
                        "operation": "process_domain_yaml"
                    })
                
                # Process entities.yaml template
                entities_yaml = domain_dir / "entities.yaml"
                logger.debug("Processing entities.yaml template", extra={
                    "domain": domain_name,
                    "file_path": str(entities_yaml),
                    "exists": entities_yaml.exists(),
                    "operation": "process_entities_yaml"
                })
                
                try:
                    if entities_yaml.exists():
                        # Template file already exists from initialization - process it
                        logger.debug("Using existing entities.yaml template", extra={
                            "domain": domain_name,
                            "template_path": str(entities_yaml),
                            "operation": "use_existing_template"
                        })
                        config_content = self.template_generator.generate_from_template(entities_yaml, context)
                        entities_yaml.write_text(config_content)
                        result.add_generated_file(str(entities_yaml))
                    else:
                        # Fallback: copy from template source and process
                        template_source = Path(__file__).parent.parent.parent / "app" / "core" / "{{domain}}" / "entities.yaml"
                        logger.debug("Using fallback entities.yaml template", extra={
                            "domain": domain_name,
                            "template_source": str(template_source),
                            "source_exists": template_source.exists(),
                            "operation": "use_fallback_template"
                        })
                        
                        if template_source.exists():
                            config_content = self.template_generator.generate_from_template(template_source, context)
                            entities_yaml.write_text(config_content)
                            result.add_generated_file(str(entities_yaml))
                        else:
                            error_msg = f"Entities template source not found: {template_source}"
                            result.add_error(error_msg)
                            logger.error("Entities template source not found", extra={
                                "domain": domain_name,
                                "template_source": str(template_source),
                                "operation": "find_template_source"
                            })
                            return result
                except Exception as entities_yaml_error:
                    error_msg = f"Failed to process entities.yaml template: {str(entities_yaml_error)}"
                    result.add_error(error_msg)
                    logger.error("Entities.yaml processing failed", exc_info=True, extra={
                        "domain": domain_name,
                        "operation": "process_entities_yaml"
                    })
                
                # Add to layer config as blank domain
                layer_path = self.target_dir / "app" / "core"
                logger.debug("Adding blank domain to layer config", extra={
                    "domain": domain_name,
                    "layer": "core",
                    "layer_path": str(layer_path),
                    "operation": "add_to_config"
                })
                
                try:
                    self.config_processor.create_blank_domain("core", layer_path, domain_name)
                except Exception as config_error:
                    warning_msg = f"Failed to add domain to layer config: {str(config_error)}"
                    result.add_warning(warning_msg)
                    logger.warning("Layer config update failed", exc_info=True, extra={
                        "domain": domain_name,
                        "operation": "add_to_config"
                    })
                
                result.metadata.update({
                    "domain": domain_name,
                    "domain_dir": str(domain_dir),
                    "config_files": ["domain.yaml", "entities.yaml"],
                    "creation_type": "blank_domain"
                })
                
                logger.info("Blank domain created successfully", extra={
                    "domain": domain_name,
                    "domain_dir": str(domain_dir),
                    "files_generated": len(result.files_generated),
                    "config_files": ["domain.yaml", "entities.yaml"],
                    "operation": "create_blank_domain"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Blank domain creation failed: {str(e)}"
                result.add_error(error_msg)
                logger.error("Blank domain creation failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "create_blank_domain"
                })
                return result
