"""
Ultra-Simple Repository Layer Generator.

Convention-based repository generation with validated configs using ConfigProcessor.
"""

from pathlib import Path

from ..utils import TemplateCodeGenerator, ConfigProcessor, ConfigProcessingError
from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import GenerationResult, TemplateContext
from ..types.models.config_models import RepositoryLayerConfig

logger = get_logger(__name__)


class RepositoryLayerGenerator:
    """Ultra-simple repository generator using conventions and validated configs."""

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize repository generator.
        
        Args:
            target_dir: Root of target project
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        # Template source is always at fixed location relative to this file
        template_base = Path(__file__).parent.parent.parent
        self.template_generator = TemplateCodeGenerator(template_base)
        self.config_processor = ConfigProcessor(template_base)
        
        self.logger.debug("Repository generator initialized", extra={
            "target_dir": str(self.target_dir),
            "template_base": str(template_base),
            "operation": "init"
        })

    def generate_repository(self, domain_name: str) -> GenerationResult:
        """
        Generate repository using validated configs and templates.
        
        Args:
            domain_name: Domain name (e.g., "Health")
            
        Returns:
            GenerationResult with operation details
        """
        result = GenerationResult(
            success=True,
            operation_type="generate_repository",
            metadata={"domain": domain_name}
        )
        
        with self.logger.timed_operation("generate_repository", {"domain": domain_name}):
            try:
                self.logger.debug("Starting repository generation", extra={
                    "domain": domain_name,
                    "operation": "generate_repository",
                    "phase": "start"
                })
                
                # Load and validate repository configuration
                repository_dir = self.target_dir / "app" / "repository" / domain_name
                
                if not repository_dir.exists():
                    error_msg = f"Repository directory not found: {repository_dir}"
                    self.logger.error("Repository directory not found", extra={
                        "domain": domain_name,
                        "path": str(repository_dir),
                        "operation": "generate_repository"
                    })
                    result.add_error(error_msg)
                    return result
                
                self.logger.debug("Repository directory found", extra={
                    "domain": domain_name,
                    "path": str(repository_dir),
                    "operation": "validate_directory"
                })
                
                # Load repository config using ConfigProcessor for validation
                try:
                    repository_config = self.config_processor.load_repository_config(repository_dir)
                    self.logger.debug("Repository config loaded successfully", extra={
                        "domain": domain_name,
                        "config_path": str(repository_dir / "repository.yaml"),
                        "operation": "load_config"
                    })
                except ConfigProcessingError as e:
                    error_msg = f"Repository config validation failed: {str(e)}"
                    self.logger.error("Repository config validation failed", exc_info=True, extra={
                        "domain": domain_name,
                        "config_path": str(repository_dir / "repository.yaml"),
                        "operation": "validate_config"
                    })
                    result.add_error(error_msg)
                    return result
            
                # Create template context from validated config
                context = TemplateContext(
                    domain=domain_name,
                    package_name=f"{domain_name.lower()}_repository",
                    plural_name=f"{domain_name}s",
                    description=f"Repository layer for {domain_name} domain",
                    metadata={
                        'domain_name': domain_name,
                        'entity_name': domain_name.title(),
                        'domain_name_plural': f"{domain_name}s",
                        'repository': repository_config.repository,
                        'database': repository_config.database,
                        'patterns': repository_config.patterns,
                        'caching': repository_config.caching,
                        'transactions': repository_config.transactions,
                        'connection': repository_config.connection
                    }
                )
                
                self.logger.debug("Template context created", extra={
                    "domain": domain_name,
                    "entity_name": domain_name.title(),
                    "repository_type": repository_config.repository.type if repository_config.repository else "default",
                    "database_type": repository_config.database.type if repository_config.database else "default",
                    "patterns_enabled": len(repository_config.patterns.enabled) if repository_config.patterns else 0,
                    "caching_enabled": repository_config.caching.enabled if repository_config.caching else False,
                    "transactions_enabled": repository_config.transactions.enabled if repository_config.transactions else False,
                    "operation": "create_context"
                })
                
                # Process all .j2 templates in the target directory
                templates = list(repository_dir.glob("*.j2"))
                self.logger.debug("Found templates for processing", extra={
                    "domain": domain_name,
                    "template_count": len(templates),
                    "templates": [t.name for t in templates],
                    "operation": "discover_templates"
                })
                
                for template in templates:
                    self.logger.debug("Processing template", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "template_path": str(template),
                        "operation": "process_template"
                    })
                    
                    try:
                        code = self.template_generator.generate_from_template(template, context)
                        output_file = repository_dir / template.name[:-3]  # Remove .j2
                        output_file.write_text(code)
                        
                        result.add_generated_file(str(output_file))
                        
                        self.logger.info("Repository file generated", extra={
                            "file": str(output_file),
                            "domain": domain_name,
                            "template": template.name,
                            "file_size": len(code),
                            "operation": "generate_file"
                        })
                    except Exception as template_error:
                        error_msg = f"Failed to process template {template.name}: {str(template_error)}"
                        result.add_error(error_msg)
                        self.logger.error("Template processing failed", exc_info=True, extra={
                            "domain": domain_name,
                            "template": template.name,
                            "operation": "process_template"
                        })
                
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "repository"
                self.config_processor.update_domain_status("repository", layer_path, domain_name, "generated")
                
                self.logger.info("Repository generation completed successfully", extra={
                    "domain": domain_name,
                    "files_generated": len(result.files_generated),
                    "operation": "generate_repository"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Repository generation failed: {str(e)}"
                result.add_error(error_msg)
                self.logger.error("Repository generation failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "generate_repository"
                })
                return result
    
    def get_from_config(self, config: RepositoryLayerConfig, domain_name: str) -> GenerationResult:
        """
        Generate repository from validated RepositoryLayerConfig object.
        
        Args:
            config: Validated RepositoryLayerConfig object
            domain_name: Domain name for the repository
            
        Returns:
            GenerationResult with operation details
        """
        result = GenerationResult(
            success=True,
            operation_type="get_from_config",
            metadata={"domain": domain_name, "config_type": type(config).__name__}
        )
        
        with self.logger.timed_operation("get_from_config", {"domain": domain_name}):
            try:
                self.logger.debug("Starting repository generation from config", extra={
                    "domain": domain_name,
                    "config_type": type(config).__name__,
                    "operation": "get_from_config",
                    "phase": "start"
                })
                
                repository_dir = self.target_dir / "app" / "repository" / domain_name
                repository_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.debug("Repository directory created", extra={
                    "domain": domain_name,
                    "path": str(repository_dir),
                    "operation": "create_directory"
                })
                
                # Create template context from config object
                context = TemplateContext(
                    domain=domain_name,
                    package_name=f"{domain_name.lower()}_repository",
                    plural_name=f"{domain_name}s",
                    description=f"Repository layer for {domain_name} domain",
                    metadata={
                        'domain_name': domain_name,
                        'entity_name': domain_name.title(),
                        'domain_name_plural': f"{domain_name}s",
                        'repository': config.repository,
                        'database': config.database,
                        'patterns': config.patterns,
                        'caching': config.caching,
                        'transactions': config.transactions,
                        'connection': config.connection
                    }
                )
                
                self.logger.debug("Template context created from config", extra={
                    "domain": domain_name,
                    "entity_name": domain_name.title(),
                    "repository_type": config.repository.type if config.repository else "default",
                    "database_type": config.database.type if config.database else "default",
                    "patterns_enabled": len(config.patterns.enabled) if config.patterns else 0,
                    "caching_enabled": config.caching.enabled if config.caching else False,
                    "transactions_enabled": config.transactions.enabled if config.transactions else False,
                    "operation": "create_context"
                })
                
                # Find and process templates from template source
                template_source = Path(__file__).parent.parent.parent / "app" / "repository" / "{{domain}}"
                
                self.logger.debug("Template source located", extra={
                    "domain": domain_name,
                    "template_source": str(template_source),
                    "operation": "locate_template_source"
                })
                
                # Process all .j2 templates
                templates = list(template_source.glob("*.j2"))
                self.logger.debug("Found templates in source", extra={
                    "domain": domain_name,
                    "template_count": len(templates),
                    "templates": [t.name for t in templates],
                    "operation": "discover_source_templates"
                })
                
                for template in templates:
                    self.logger.debug("Processing template from source", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "template_path": str(template),
                        "operation": "process_source_template"
                    })
                    
                    try:
                        code = self.template_generator.generate_from_template(template, context)
                        output_file = repository_dir / template.name[:-3]  # Remove .j2
                        output_file.write_text(code)
                        
                        result.add_generated_file(str(output_file))
                        
                        self.logger.info("Repository file generated", extra={
                            "file": str(output_file),
                            "domain": domain_name,
                            "template": template.name,
                            "file_size": len(code),
                            "operation": "generate_file"
                        })
                    except Exception as template_error:
                        error_msg = f"Failed to process template {template.name}: {str(template_error)}"
                        result.add_error(error_msg)
                        self.logger.error("Template processing failed", exc_info=True, extra={
                            "domain": domain_name,
                            "template": template.name,
                            "operation": "process_source_template"
                        })
                
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "repository"
                self.config_processor.update_domain_status("repository", layer_path, domain_name, "generated")
                
                self.logger.info("Repository generation from config completed successfully", extra={
                    "domain": domain_name,
                    "files_generated": len(result.files_generated),
                    "operation": "get_from_config"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Repository generation from config failed: {str(e)}"
                result.add_error(error_msg)
                self.logger.error("Repository generation from config failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "get_from_config"
                })
                return result

    def regenerate_all_repositories(self) -> GenerationResult:
        """Regenerate all existing repositories in target project."""
        result = GenerationResult(
            success=True,
            operation_type="regenerate_all_repositories"
        )
        
        with self.logger.timed_operation("regenerate_all_repositories"):
            repository_dir = self.target_dir / "app" / "repository"
            
            self.logger.debug("Starting repository regeneration", extra={
                "repository_dir": str(repository_dir),
                "operation": "regenerate_all_repositories",
                "phase": "start"
            })
            
            if not repository_dir.exists():
                error_msg = f"Repository directory not found: {repository_dir}"
                self.logger.error("Repository directory not found", extra={
                    "path": str(repository_dir),
                    "operation": "regenerate_all_repositories"
                })
                result.add_error(error_msg)
                return result
            
            # Sync domain registry first
            self.logger.debug("Syncing domain registry", extra={
                "layer": "repository",
                "path": str(repository_dir),
                "operation": "sync_domain_registry"
            })
            self.config_processor.sync_domain_registry("repository", repository_dir)
            
            # Get all domains from layer config
            domains = self.config_processor.get_all_domains("repository", repository_dir)
            
            self.logger.info("Found domains for regeneration", extra={
                "total_domains": len(domains),
                "domains": [d.name for d in domains],
                "operation": "discover_domains"
            })
            
            generated_count = 0
            failed_count = 0
            
            for domain in domains:
                if domain.status in ["configured", "generated"]:
                    self.logger.debug("Regenerating domain repository", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "operation": "regenerate_domain"
                    })
                    
                    domain_result = self.generate_repository(domain.name)
                    if domain_result.success:
                        generated_count += 1
                        result.files_generated.extend(domain_result.files_generated)
                        result.files_modified.extend(domain_result.files_modified)
                    else:
                        failed_count += 1
                        result.errors.extend(domain_result.errors)
                        result.warnings.extend(domain_result.warnings)
                else:
                    result.add_skipped_file(f"Domain {domain.name} (status: {domain.status})")
                    self.logger.debug("Skipping domain with status", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "operation": "skip_domain"
                    })
            
            # Update result metadata
            result.metadata.update({
                "generated_count": generated_count,
                "failed_count": failed_count,
                "total_domains": len(domains)
            })
            
            if failed_count > 0:
                result.success = False
            
            self.logger.info("Repository regeneration completed", extra={
                "success": result.success,
                "generated_count": generated_count,
                "failed_count": failed_count,
                "total_domains": len(domains),
                "operation": "regenerate_all_repositories"
            })
            
            return result
    
    def create_blank_repository(self, domain_name: str) -> GenerationResult:
        """
        Create a blank repository with config files processed from templates.
        
        Args:
            domain_name: Name of domain to create repository for
            
        Returns:
            GenerationResult with operation details
        """
        result = GenerationResult(
            success=True,
            operation_type="create_blank_repository",
            metadata={"domain": domain_name}
        )
        
        with self.logger.timed_operation("create_blank_repository", {"domain": domain_name}):
            try:
                self.logger.debug("Starting blank repository creation", extra={
                    "domain": domain_name,
                    "operation": "create_blank_repository",
                    "phase": "start"
                })
                
                # Create repository directory
                repository_dir = self.target_dir / "app" / "repository" / domain_name
                repository_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.debug("Repository directory created", extra={
                    "domain": domain_name,
                    "path": str(repository_dir),
                    "operation": "create_directory"
                })
                
                # Use the template file that was already copied during initialization
                template_config_path = repository_dir / "repository.yaml"
                
                # Create template context
                context = TemplateContext(
                    domain=domain_name,
                    package_name=f"{domain_name.lower()}_repository",
                    plural_name=f"{domain_name}s",
                    description=f"Blank repository configuration for {domain_name} domain",
                    metadata={
                        'domain_name': domain_name,
                        'domain_name_plural': f"{domain_name}s",
                        'entity_name': domain_name.title()
                    }
                )
                
                self.logger.debug("Template context created for blank repository", extra={
                    "domain": domain_name,
                    "entity_name": domain_name.title(),
                    "domain_plural": f"{domain_name}s",
                    "operation": "create_blank_context"
                })
                
                if template_config_path.exists():
                    # Template file already exists from initialization - process it
                    self.logger.debug("Processing existing template config", extra={
                        "domain": domain_name,
                        "config_path": str(template_config_path),
                        "operation": "process_existing_template"
                    })
                    
                    try:
                        config_content = self.template_generator.generate_from_template(template_config_path, context)
                        template_config_path.write_text(config_content)
                        result.add_generated_file(str(template_config_path))
                        
                        self.logger.debug("Template config processed successfully", extra={
                            "domain": domain_name,
                            "config_path": str(template_config_path),
                            "config_size": len(config_content),
                            "operation": "process_template_config"
                        })
                    except Exception as template_error:
                        error_msg = f"Failed to process template config: {str(template_error)}"
                        result.add_error(error_msg)
                        return result
                else:
                    # Fallback: copy from template source and process
                    template_source = Path(__file__).parent.parent.parent / "app" / "repository" / "{{domain}}" / "repository.yaml"
                    
                    self.logger.debug("Using fallback template source", extra={
                        "domain": domain_name,
                        "template_source": str(template_source),
                        "operation": "fallback_template_source"
                    })
                    
                    if template_source.exists():
                        try:
                            config_content = self.template_generator.generate_from_template(template_source, context)
                            template_config_path.write_text(config_content)
                            result.add_generated_file(str(template_config_path))
                            
                            self.logger.debug("Fallback template processed successfully", extra={
                                "domain": domain_name,
                                "template_source": str(template_source),
                                "config_path": str(template_config_path),
                                "config_size": len(config_content),
                                "operation": "process_fallback_template"
                            })
                        except Exception as template_error:
                            error_msg = f"Failed to process fallback template: {str(template_error)}"
                            result.add_error(error_msg)
                            return result
                    else:
                        error_msg = f"Template source not found: {template_source}"
                        self.logger.error("Template source not found", extra={
                            "domain": domain_name,
                            "template_source": str(template_source),
                            "operation": "find_template_source"
                        })
                        result.add_error(error_msg)
                        return result
                
                # Add to layer config as blank domain
                layer_path = self.target_dir / "app" / "repository"
                self.config_processor.create_blank_domain("repository", layer_path, domain_name)
                
                self.logger.info("Blank repository created successfully", extra={
                    "domain": domain_name,
                    "repository_dir": str(repository_dir),
                    "config_file": str(template_config_path),
                    "operation": "create_blank_repository"
                })
                
                self.logger.info("Repository configuration ready", extra={
                    "domain": domain_name,
                    "config_location": str(repository_dir),
                    "next_step": "configure_repository",
                    "operation": "setup_complete"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Failed to create blank repository: {str(e)}"
                result.add_error(error_msg)
                self.logger.error("Failed to create blank repository", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "create_blank_repository"
                })
                return result
