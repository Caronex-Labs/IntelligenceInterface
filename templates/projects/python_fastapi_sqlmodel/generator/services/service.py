"""
Ultra-Simple Service Layer Generator.

Convention-based service generation with validated configs using ConfigProcessor.
"""

from pathlib import Path
import logging

from ..utils import TemplateCodeGenerator, ConfigProcessor, ConfigProcessingError
from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import GenerationResult, TemplateContext
from ..types.models.config_models import ServiceConfig

logger = get_logger(__name__)


class ServiceLayerGenerator:
    """Ultra-simple service generator using conventions and validated configs."""

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize service generator.
        
        Args:
            target_dir: Root of target project
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        # Template source is always at fixed location relative to this file
        template_base = Path(__file__).parent.parent.parent
        self.template_generator = TemplateCodeGenerator(template_base)
        self.config_processor = ConfigProcessor(template_base)
        
        self.logger.debug("ServiceLayerGenerator initialized", extra={
            "target_dir": str(self.target_dir),
            "template_base": str(template_base),
            "operation": "init"
        })

    def generate_service(self, service_name: str) -> GenerationResult:
        """
        Generate service using validated configs and templates.
        
        Args:
            service_name: Service name (e.g., "NotificationService")
            
        Returns:
            GenerationResult with detailed operation information
        """
        result = GenerationResult(
            success=True,
            operation_type="generate_service",
            metadata={"service_name": service_name}
        )
        
        self.logger.debug("Starting service generation", extra={
            "service": service_name,
            "operation": "generate_service",
            "phase": "start"
        })
        
        try:
            # Load and validate service configuration
            service_dir = self.target_dir / "app" / "service" / service_name
            
            if not service_dir.exists():
                error_msg = f"Service directory not found: {service_dir}"
                self.logger.error("Service directory not found", extra={
                    "service": service_name,
                    "path": str(service_dir),
                    "operation": "generate_service"
                })
                result.add_error(error_msg)
                return result
            
            self.logger.debug("Service directory found", extra={
                "service": service_name,
                "path": str(service_dir),
                "operation": "generate_service"
            })
            
            # Load service config using ConfigProcessor for validation
            try:
                service_config = self.config_processor.load_service_config(service_dir)
                self.logger.debug("Service config loaded successfully", extra={
                    "service": service_name,
                    "config_name": service_config.name,
                    "scope": service_config.scope,
                    "method_count": len(service_config.methods),
                    "dependency_count": len(service_config.dependencies),
                    "operation": "load_config"
                })
            except ConfigProcessingError as e:
                error_msg = f"Service config validation failed: {str(e)}"
                self.logger.error("Service config validation failed", exc_info=True, extra={
                    "service": service_name,
                    "operation": "validate_config"
                })
                result.add_error(error_msg)
                return result
            
            # Create template context from validated config
            context = TemplateContext(
                domain=service_name,
                package_name=service_config.package,
                description=service_config.description,
                metadata={
                    'service_name': service_name,
                    'service': service_config.name,
                    'service_description': service_config.description,
                    'service_package': service_config.package,
                    'service_scope': service_config.scope,
                    'methods': [method.model_dump() for method in service_config.methods],
                    'dependencies': service_config.dependencies
                }
            )
            
            self.logger.debug("Template context created", extra={
                "service": service_name,
                "scope": service_config.scope,
                "method_count": len(service_config.methods),
                "dependency_count": len(service_config.dependencies),
                "operation": "create_context"
            })
            
            # Process all .j2 templates in the target directory
            template_files = list(service_dir.glob("*.j2"))
            self.logger.debug("Found template files", extra={
                "service": service_name,
                "template_count": len(template_files),
                "templates": [t.name for t in template_files],
                "operation": "discover_templates"
            })
            
            for template in template_files:
                self.logger.debug("Processing template", extra={
                    "service": service_name,
                    "template": template.name,
                    "operation": "process_template"
                })
                
                try:
                    code = self.template_generator.generate_from_template(template, context)
                    output_file = service_dir / template.name[:-3]  # Remove .j2
                    output_file.write_text(code)
                    
                    result.add_generated_file(str(output_file))
                    
                    self.logger.info("Service file generated", extra={
                        "file": str(output_file),
                        "service": service_name,
                        "template": template.name,
                        "operation": "generate_file"
                    })
                except Exception as e:
                    error_msg = f"Failed to process template {template.name}: {str(e)}"
                    result.add_error(error_msg)
                    self.logger.error("Template processing failed", exc_info=True, extra={
                        "service": service_name,
                        "template": template.name,
                        "operation": "process_template"
                    })
            
            # Update service status in layer config
            try:
                layer_path = self.target_dir / "app" / "service"
                self.config_processor.update_domain_status("service", layer_path, service_name, "generated")
            except Exception as e:
                warning_msg = f"Failed to update service status: {str(e)}"
                result.add_warning(warning_msg)
                self.logger.warning("Failed to update service status", exc_info=True, extra={
                    "service": service_name,
                    "operation": "update_status"
                })
            
            self.logger.info("Service generation completed successfully", extra={
                "service": service_name,
                "files_generated": len(result.files_generated),
                "operation": "generate_service"
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Service generation failed: {str(e)}"
            result.add_error(error_msg)
            self.logger.error("Service generation failed", exc_info=True, extra={
                "service": service_name,
                "operation": "generate_service"
            })
            return result
    
    def get_from_config(self, config: ServiceConfig, service_name: str) -> GenerationResult:
        """
        Generate service from validated ServiceConfig object.
        
        Args:
            config: Validated ServiceConfig object
            service_name: Service name for the service
            
        Returns:
            GenerationResult with detailed operation information
        """
        result = GenerationResult(
            success=True,
            operation_type="get_from_config",
            metadata={"service_name": service_name, "config_name": config.name}
        )
        
        self.logger.debug("Starting service generation from config", extra={
            "service": service_name,
            "config_name": config.name,
            "scope": config.scope,
            "operation": "get_from_config",
            "phase": "start"
        })
        
        try:
            service_dir = self.target_dir / "app" / "service" / service_name
            service_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.debug("Service directory created", extra={
                "service": service_name,
                "path": str(service_dir),
                "operation": "create_directory"
            })
            
            # Create template context from config object
            context = TemplateContext(
                domain=service_name,
                package_name=config.package,
                description=config.description,
                metadata={
                    'service_name': service_name,
                    'service': config.name,
                    'service_description': config.description,
                    'service_package': config.package,
                    'service_scope': config.scope,
                    'methods': [method.model_dump() for method in config.methods],
                    'dependencies': config.dependencies
                }
            )
            
            self.logger.debug("Template context created from config", extra={
                "service": service_name,
                "scope": config.scope,
                "method_count": len(config.methods),
                "dependency_count": len(config.dependencies),
                "operation": "create_context"
            })
            
            # Find and process templates from template source
            template_source = Path(__file__).parent.parent.parent / "app" / "service" / "{{service_name}}"
            
            self.logger.debug("Template source located", extra={
                "service": service_name,
                "template_source": str(template_source),
                "operation": "locate_template_source"
            })
            
            # Process all .j2 templates
            template_files = list(template_source.glob("*.j2"))
            self.logger.debug("Found template files in source", extra={
                "service": service_name,
                "template_count": len(template_files),
                "templates": [t.name for t in template_files],
                "operation": "discover_source_templates"
            })
            
            for template in template_files:
                self.logger.debug("Processing template from source", extra={
                    "service": service_name,
                    "template": template.name,
                    "template_path": str(template),
                    "operation": "process_source_template"
                })
                
                try:
                    code = self.template_generator.generate_from_template(template, context)
                    output_file = service_dir / template.name[:-3]  # Remove .j2
                    output_file.write_text(code)
                    
                    result.add_generated_file(str(output_file))
                    
                    self.logger.info("Service file generated", extra={
                        "file": str(output_file),
                        "service": service_name,
                        "template": template.name,
                        "operation": "generate_file"
                    })
                except Exception as e:
                    error_msg = f"Failed to process template {template.name}: {str(e)}"
                    result.add_error(error_msg)
                    self.logger.error("Template processing failed", exc_info=True, extra={
                        "service": service_name,
                        "template": template.name,
                        "operation": "process_source_template"
                    })
            
            # Update service status in layer config
            try:
                layer_path = self.target_dir / "app" / "service"
                self.config_processor.update_domain_status("service", layer_path, service_name, "generated")
            except Exception as e:
                warning_msg = f"Failed to update service status: {str(e)}"
                result.add_warning(warning_msg)
                self.logger.warning("Failed to update service status", exc_info=True, extra={
                    "service": service_name,
                    "operation": "update_status"
                })
            
            self.logger.info("Service generation from config completed successfully", extra={
                "service": service_name,
                "files_generated": len(result.files_generated),
                "operation": "get_from_config"
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Service generation from config failed: {str(e)}"
            result.add_error(error_msg)
            self.logger.error("Service generation from config failed", exc_info=True, extra={
                "service": service_name,
                "operation": "get_from_config"
            })
            return result

    def regenerate_all_services(self) -> GenerationResult:
        """Regenerate all existing services in target project."""
        result = GenerationResult(
            success=True,
            operation_type="regenerate_all_services"
        )
        
        self.logger.debug("Starting regeneration of all services", extra={
            "operation": "regenerate_all_services",
            "phase": "start"
        })
        
        service_dir = self.target_dir / "app" / "service"
        
        if not service_dir.exists():
            error_msg = f"No app/service directory found: {service_dir}"
            self.logger.error("No app/service directory found", extra={
                "path": str(service_dir),
                "operation": "regenerate_all_services"
            })
            result.add_error(error_msg)
            return result
        
        self.logger.debug("Service directory found", extra={
            "path": str(service_dir),
            "operation": "regenerate_all_services"
        })
        
        try:
            # Sync domain registry first
            self.logger.debug("Syncing domain registry", extra={
                "layer": "service",
                "path": str(service_dir),
                "operation": "sync_registry"
            })
            self.config_processor.sync_domain_registry("service", service_dir)
            
            # Get all services from layer config
            services = self.config_processor.get_all_domains("service", service_dir)
            
            self.logger.info("Found services for regeneration", extra={
                "service_count": len(services),
                "services": [s.name for s in services],
                "operation": "discover_services"
            })
            
            generated_count = 0
            skipped_count = 0
            
            for service in services:
                if service.status in ["configured", "generated"]:
                    self.logger.debug("Regenerating service", extra={
                        "service": service.name,
                        "status": service.status,
                        "operation": "regenerate_service"
                    })
                    
                    service_result = self.generate_service(service.name)
                    if service_result.success:
                        generated_count += 1
                        result.files_generated.extend(service_result.files_generated)
                        result.files_modified.extend(service_result.files_modified)
                    else:
                        result.errors.extend(service_result.errors)
                        result.warnings.extend(service_result.warnings)
                        self.logger.warning("Service regeneration failed", extra={
                            "service": service.name,
                            "operation": "regenerate_service"
                        })
                else:
                    skipped_count += 1
                    result.add_skipped_file(f"service_{service.name}")
                    self.logger.debug("Skipping service regeneration", extra={
                        "service": service.name,
                        "status": service.status,
                        "reason": "status_not_eligible",
                        "operation": "skip_service"
                    })
            
            result.metadata.update({
                "total_services": len(services),
                "generated_count": generated_count,
                "skipped_count": skipped_count
            })
            
            self.logger.info("Service regeneration completed", extra={
                "total_services": len(services),
                "generated_count": generated_count,
                "skipped_count": skipped_count,
                "success": result.success,
                "operation": "regenerate_all_services"
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Service regeneration failed: {str(e)}"
            result.add_error(error_msg)
            self.logger.error("Service regeneration failed", exc_info=True, extra={
                "operation": "regenerate_all_services"
            })
            return result
    
    def create_blank_service(self, service_name: str) -> GenerationResult:
        """
        Create a blank service with config files processed from templates.
        
        Args:
            service_name: Name of service to create
            
        Returns:
            GenerationResult with detailed operation information
        """
        result = GenerationResult(
            success=True,
            operation_type="create_blank_service",
            metadata={"service_name": service_name}
        )
        
        self.logger.debug("Starting blank service creation", extra={
            "service": service_name,
            "operation": "create_blank_service",
            "phase": "start"
        })
        
        try:
            # Create service directory
            service_dir = self.target_dir / "app" / "service" / service_name
            service_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.debug("Service directory created", extra={
                "service": service_name,
                "path": str(service_dir),
                "operation": "create_directory"
            })
            
            # Use the template file that was already copied during initialization
            template_config_path = service_dir / "service.yaml"
            
            # Create template context
            context = TemplateContext(
                domain=service_name,
                description=f"Domain-agnostic service for {service_name}",
                package_name=f"app.service.{service_name.lower().replace('service', '')}_service",
                metadata={
                    'service_name': service_name,
                    'service_description': f"Domain-agnostic service for {service_name}",
                    'service_package': f"app.service.{service_name.lower().replace('service', '')}_service",
                    'service_scope': 'scoped'
                }
            )
            
            self.logger.debug("Template context created for blank service", extra={
                "service": service_name,
                "scope": context['service_scope'],
                "package": context['service_package'],
                "operation": "create_blank_context"
            })
            
            if template_config_path.exists():
                # Template file already exists from initialization - process it
                self.logger.debug("Processing existing template config", extra={
                    "service": service_name,
                    "template_path": str(template_config_path),
                    "operation": "process_existing_template"
                })
                
                try:
                    config_content = self.template_generator.generate_from_template(template_config_path, context)
                    template_config_path.write_text(config_content)
                    result.add_generated_file(str(template_config_path))
                    
                    self.logger.info("Service config generated from existing template", extra={
                        "service": service_name,
                        "config_file": str(template_config_path),
                        "operation": "generate_config"
                    })
                except Exception as e:
                    error_msg = f"Failed to process existing template: {str(e)}"
                    result.add_error(error_msg)
                    self.logger.error("Failed to process existing template", exc_info=True, extra={
                        "service": service_name,
                        "template_path": str(template_config_path),
                        "operation": "process_existing_template"
                    })
            else:
                # Fallback: copy from template source and process
                template_source = Path(__file__).parent.parent.parent / "app" / "service" / "{{service_name}}" / "service.yaml"
                
                self.logger.debug("Using fallback template source", extra={
                    "service": service_name,
                    "template_source": str(template_source),
                    "operation": "fallback_template"
                })
                
                if template_source.exists():
                    try:
                        config_content = self.template_generator.generate_from_template(template_source, context)
                        template_config_path.write_text(config_content)
                        result.add_generated_file(str(template_config_path))
                        
                        self.logger.info("Service config generated from template source", extra={
                            "service": service_name,
                            "config_file": str(template_config_path),
                            "template_source": str(template_source),
                            "operation": "generate_config"
                        })
                    except Exception as e:
                        error_msg = f"Failed to process template source: {str(e)}"
                        result.add_error(error_msg)
                        self.logger.error("Failed to process template source", exc_info=True, extra={
                            "service": service_name,
                            "template_source": str(template_source),
                            "operation": "process_template_source"
                        })
                else:
                    error_msg = f"Template source not found: {template_source}"
                    result.add_error(error_msg)
                    self.logger.error("Template source not found", extra={
                        "service": service_name,
                        "template_source": str(template_source),
                        "operation": "find_template_source"
                    })
            
            # Add to layer config as blank service
            try:
                layer_path = self.target_dir / "app" / "service"
                self.config_processor.create_blank_domain("service", layer_path, service_name)
            except Exception as e:
                warning_msg = f"Failed to update layer config: {str(e)}"
                result.add_warning(warning_msg)
                self.logger.warning("Failed to update layer config", exc_info=True, extra={
                    "service": service_name,
                    "operation": "update_layer_config"
                })
            
            self.logger.info("Blank service created successfully", extra={
                "service": service_name,
                "service_dir": str(service_dir),
                "config_file": str(template_config_path),
                "files_generated": len(result.files_generated),
                "operation": "create_blank_service"
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to create blank service: {str(e)}"
            result.add_error(error_msg)
            self.logger.error("Failed to create blank service", exc_info=True, extra={
                "service": service_name,
                "operation": "create_blank_service"
            })
            return result
