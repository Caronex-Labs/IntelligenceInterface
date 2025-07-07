"""
Ultra-Simple Interface Layer Generator.

Convention-based interface generation with validated configs using ConfigProcessor.
"""

from pathlib import Path
import logging

from ..utils import TemplateCodeGenerator, ConfigProcessor, ConfigProcessingError
from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import GenerationResult, TemplateContext
from ..types.models.config_models import InterfaceLayerConfig

logger = get_logger(__name__)


class InterfaceLayerGenerator:
    """Ultra-simple interface generator using conventions and validated configs."""

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize interface generator.
        
        Args:
            target_dir: Root of target project
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        # Template source is always at fixed location relative to this file
        template_base = Path(__file__).parent.parent.parent
        self.template_generator = TemplateCodeGenerator(template_base)
        self.config_processor = ConfigProcessor(template_base)
        
        self.logger.debug("Interface generator initialized", extra={
            "target_dir": str(self.target_dir),
            "template_base": str(template_base),
            "operation": "init"
        })

    def generate_interface(self, domain_name: str) -> GenerationResult:
        """
        Generate interface using validated configs and templates.
        
        Args:
            domain_name: Domain name (e.g., "Health")
            
        Returns:
            GenerationResult with detailed information about the operation
        """
        result = GenerationResult(
            success=True,
            operation_type="generate_interface",
            metadata={"domain": domain_name}
        )
        
        with self.logger.timed_operation("generate_interface", {"domain": domain_name}):
            try:
                self.logger.debug("Starting interface generation", extra={
                    "domain": domain_name,
                    "operation": "generate_interface",
                    "phase": "start"
                })
                
                # Load and validate interface configuration
                interface_dir = self.target_dir / "app" / "interface" / domain_name
                
                if not interface_dir.exists():
                    error_msg = f"Interface directory not found: {interface_dir}"
                    self.logger.error("Interface directory not found", extra={
                        "domain": domain_name,
                        "path": str(interface_dir),
                        "operation": "generate_interface"
                    })
                    result.add_error(error_msg)
                    return result
            
                # Load interface config using ConfigProcessor for validation
                try:
                    self.logger.debug("Loading interface configuration", extra={
                        "domain": domain_name,
                        "config_dir": str(interface_dir),
                        "operation": "load_config"
                    })
                    interface_config = self.config_processor.load_interface_config(interface_dir)
                    
                    self.logger.debug("Interface configuration loaded successfully", extra={
                        "domain": domain_name,
                        "api_config": {
                            "version": getattr(interface_config.api, 'version', None),
                            "prefix": getattr(interface_config.api, 'prefix', None),
                            "tags": getattr(interface_config.api, 'tags', [])
                        },
                        "auth_type": getattr(interface_config.authentication, 'type', None),
                        "middleware_count": len(getattr(interface_config.middleware, 'custom', [])) if interface_config.middleware else 0,
                        "endpoint_count": len(interface_config.endpoints) if interface_config.endpoints else 0,
                        "operation": "config_loaded"
                    })
                except ConfigProcessingError as e:
                    error_msg = f"Interface config validation failed: {str(e)}"
                    self.logger.error("Interface config validation failed", exc_info=True, extra={
                        "domain": domain_name,
                        "config_dir": str(interface_dir),
                        "operation": "validate_config"
                    })
                    result.add_error(error_msg)
                    return result
            
                # Create template context from validated config
                template_context = TemplateContext(
                    domain=domain_name,
                    metadata={
                        'domain_name': domain_name,
                        'entity_name': domain_name.title(),
                        'domain_name_plural': f"{domain_name}s",
                        'interface': interface_config.interface,
                        'api': interface_config.api,
                        'endpoints': interface_config.endpoints,
                        'auth': interface_config.authentication,
                        'middleware': interface_config.middleware
                    }
                )
                
                # Convert to dict for Jinja2 template processing
                context = template_context.model_dump()
                
                self.logger.debug("Template context created", extra={
                    "domain": domain_name,
                    "context_keys": list(context.keys()),
                    "entity_name": context['metadata']['entity_name'],
                    "operation": "create_context"
                })
                
                # Process all .j2 templates in the target directory
                templates_found = list(interface_dir.glob("*.j2"))
                self.logger.debug("Processing interface templates", extra={
                    "domain": domain_name,
                    "template_count": len(templates_found),
                    "templates": [t.name for t in templates_found],
                    "operation": "process_templates"
                })
                
                for template in templates_found:
                    self.logger.debug("Generating from template", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "template_path": str(template),
                        "operation": "generate_template"
                    })
                    
                    code = self.template_generator.generate_from_template(template, template_context)
                    output_file = interface_dir / template.name[:-3]  # Remove .j2
                    output_file.write_text(code)
                    
                    result.add_generated_file(str(output_file))
                    
                    self.logger.info("Interface file generated", extra={
                        "file": str(output_file),
                        "domain": domain_name,
                        "template": template.name,
                        "file_size": len(code),
                        "operation": "generate_file"
                    })
            
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "interface"
                self.config_processor.update_domain_status("interface", layer_path, domain_name, "generated")
                
                self.logger.info("Interface generation completed successfully", extra={
                    "domain": domain_name,
                    "files_generated": len(templates_found),
                    "operation": "generate_interface"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Interface generation failed: {str(e)}"
                self.logger.error("Interface generation failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "generate_interface"
                })
                result.add_error(error_msg)
                return result
    
    def get_from_config(self, config: InterfaceLayerConfig, domain_name: str) -> GenerationResult:
        """
        Generate interface from validated InterfaceLayerConfig object.
        
        Args:
            config: Validated InterfaceLayerConfig object
            domain_name: Domain name for the interface
            
        Returns:
            GenerationResult with detailed information about the operation
        """
        result = GenerationResult(
            success=True,
            operation_type="get_from_config",
            metadata={"domain": domain_name, "config_type": type(config).__name__}
        )
        
        with self.logger.timed_operation("get_from_config", {"domain": domain_name}):
            try:
                self.logger.debug("Starting interface generation from config object", extra={
                    "domain": domain_name,
                    "config_type": type(config).__name__,
                    "operation": "get_from_config"
                })
                
                interface_dir = self.target_dir / "app" / "interface" / domain_name
                interface_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.debug("Interface directory prepared", extra={
                    "domain": domain_name,
                    "interface_dir": str(interface_dir),
                    "operation": "prepare_directory"
                })
            
                # Create template context from config object
                template_context = TemplateContext(
                    domain=domain_name,
                    metadata={
                        'domain_name': domain_name,
                        'entity_name': domain_name.title(),
                        'domain_name_plural': f"{domain_name}s",
                        'interface': config.interface,
                        'api': config.api,
                        'endpoints': config.endpoints,
                        'auth': config.authentication,
                        'middleware': config.middleware
                    }
                )
                
                self.logger.debug("Template context created from config", extra={
                    "domain": domain_name,
                    "context_keys": list(template_context.metadata.keys()),
                    "api_endpoints": len(config.endpoints) if config.endpoints else 0,
                    "auth_enabled": bool(config.authentication),
                    "middleware_enabled": bool(config.middleware),
                    "operation": "create_context"
                })
                
                # Find and process templates from template source
                template_source = Path(__file__).parent.parent.parent / "app" / "interface" / "{{domain}}"
                
                self.logger.debug("Looking for templates in source", extra={
                    "domain": domain_name,
                    "template_source": str(template_source),
                    "operation": "find_templates"
                })
                
                # Process all .j2 templates
                templates_found = list(template_source.glob("*.j2"))
                self.logger.debug("Processing templates from source", extra={
                    "domain": domain_name,
                    "template_count": len(templates_found),
                    "templates": [t.name for t in templates_found],
                    "operation": "process_source_templates"
                })
                
                for template in templates_found:
                    self.logger.debug("Generating from source template", extra={
                        "domain": domain_name,
                        "template": template.name,
                        "template_path": str(template),
                        "operation": "generate_from_source"
                    })
                    
                    code = self.template_generator.generate_from_template(template, template_context)
                    output_file = interface_dir / template.name[:-3]  # Remove .j2
                    output_file.write_text(code)
                    
                    result.add_generated_file(str(output_file))
                    
                    self.logger.info("Interface file generated", extra={
                        "file": str(output_file),
                        "domain": domain_name,
                        "template": template.name,
                        "file_size": len(code),
                        "operation": "generate_file"
                    })
            
                # Update domain status in layer config
                layer_path = self.target_dir / "app" / "interface"
                self.config_processor.update_domain_status("interface", layer_path, domain_name, "generated")
                
                self.logger.info("Interface generation from config completed successfully", extra={
                    "domain": domain_name,
                    "files_generated": len(templates_found),
                    "operation": "get_from_config"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Interface generation from config failed: {str(e)}"
                self.logger.error("Interface generation from config failed", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "get_from_config"
                })
                result.add_error(error_msg)
                return result

    def regenerate_all_interfaces(self) -> GenerationResult:
        """Regenerate all existing interfaces in target project."""
        result = GenerationResult(
            success=True,
            operation_type="regenerate_all_interfaces"
        )
        
        with self.logger.timed_operation("regenerate_all_interfaces"):
            interface_dir = self.target_dir / "app" / "interface"
            
            self.logger.debug("Starting interface regeneration", extra={
                "interface_dir": str(interface_dir),
                "operation": "regenerate_all_interfaces"
            })
            
            if not interface_dir.exists():
                error_msg = f"No app/interface directory found: {interface_dir}"
                self.logger.error("No app/interface directory found", extra={
                    "interface_dir": str(interface_dir),
                    "operation": "regenerate_all_interfaces"
                })
                result.add_error(error_msg)
                return result
            
            # Sync domain registry first
            self.logger.debug("Syncing domain registry", extra={
                "layer": "interface",
                "layer_dir": str(interface_dir),
                "operation": "sync_registry"
            })
            self.config_processor.sync_domain_registry("interface", interface_dir)
            
            # Get all domains from layer config
            domains = self.config_processor.get_all_domains("interface", interface_dir)
            
            self.logger.info("Found domains for regeneration", extra={
                "total_domains": len(domains),
                "domain_names": [d.name for d in domains],
                "operation": "get_domains"
            })
            
            generated_count = 0
            failed_count = 0
            
            for domain in domains:
                if domain.status in ["configured", "generated"]:
                    self.logger.debug("Regenerating domain interface", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "operation": "regenerate_domain"
                    })
                    
                    domain_result = self.generate_interface(domain.name)
                    if domain_result.success:
                        generated_count += 1
                        result.files_generated.extend(domain_result.files_generated)
                        result.files_modified.extend(domain_result.files_modified)
                    else:
                        failed_count += 1
                        result.errors.extend(domain_result.errors)
                        result.warnings.extend(domain_result.warnings)
                else:
                    self.logger.debug("Skipping domain with status", extra={
                        "domain": domain.name,
                        "status": domain.status,
                        "operation": "skip_domain"
                    })
                    result.add_skipped_file(f"Domain {domain.name} (status: {domain.status})")
            
            if failed_count > 0:
                result.success = False
            
            result.metadata.update({
                "total_domains": len(domains),
                "generated_count": generated_count,
                "failed_count": failed_count
            })
            
            self.logger.info("Interface regeneration completed", extra={
                "total_domains": len(domains),
                "generated_count": generated_count,
                "failed_count": failed_count,
                "success": result.success,
                "operation": "regenerate_all_interfaces"
            })
            
            return result
    
    def create_blank_interface(self, domain_name: str) -> GenerationResult:
        """
        Create a blank interface with config files processed from templates.
        
        Args:
            domain_name: Name of domain to create interface for
            
        Returns:
            GenerationResult with detailed information about the operation
        """
        result = GenerationResult(
            success=True,
            operation_type="create_blank_interface",
            metadata={"domain": domain_name}
        )
        
        with self.logger.timed_operation("create_blank_interface", {"domain": domain_name}):
            try:
                self.logger.debug("Starting blank interface creation", extra={
                    "domain": domain_name,
                    "operation": "create_blank_interface"
                })
                
                # Create interface directory
                interface_dir = self.target_dir / "app" / "interface" / domain_name
                interface_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.debug("Interface directory created", extra={
                    "domain": domain_name,
                    "interface_dir": str(interface_dir),
                    "operation": "create_directory"
                })
                
                # Use the template file that was already copied during initialization
                template_config_path = interface_dir / "interface.yaml"
                
                # Create template context
                template_context = TemplateContext(
                    domain=domain_name,
                    metadata={
                        'domain_name': domain_name,
                        'domain_name_plural': f"{domain_name}s",
                        'entity_name': domain_name.title()
                    }
                )
                
                self.logger.debug("Template context created for blank interface", extra={
                    "domain": domain_name,
                    "context_keys": list(template_context.metadata.keys()),
                    "entity_name": template_context.metadata['entity_name'],
                    "operation": "create_context"
                })
                
                if template_config_path.exists():
                    # Template file already exists from initialization - process it
                    self.logger.debug("Processing existing template config", extra={
                        "domain": domain_name,
                        "config_path": str(template_config_path),
                        "operation": "process_existing_template"
                    })
                    config_content = self.template_generator.generate_from_template(template_config_path, template_context)
                    template_config_path.write_text(config_content)
                    result.add_generated_file(str(template_config_path))
                else:
                    # Fallback: copy from template source and process
                    template_source = Path(__file__).parent.parent.parent / "app" / "interface" / "{{domain}}" / "interface.yaml"
                    
                    self.logger.debug("Using fallback template source", extra={
                        "domain": domain_name,
                        "template_source": str(template_source),
                        "operation": "fallback_template"
                    })
                    
                    if template_source.exists():
                        config_content = self.template_generator.generate_from_template(template_source, template_context)
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
                layer_path = self.target_dir / "app" / "interface"
                self.config_processor.create_blank_domain("interface", layer_path, domain_name)
                
                self.logger.info("Blank interface created successfully", extra={
                    "domain": domain_name,
                    "interface_dir": str(interface_dir),
                    "config_file": str(template_config_path),
                    "operation": "create_blank_interface"
                })
                
                return result
                
            except Exception as e:
                error_msg = f"Failed to create blank interface: {str(e)}"
                self.logger.error("Failed to create blank interface", exc_info=True, extra={
                    "domain": domain_name,
                    "operation": "create_blank_interface"
                })
                result.add_error(error_msg)
                return result
