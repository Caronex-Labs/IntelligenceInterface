"""
Domain Manager for FastAPI SQLModel Generator.

Handles domain creation, configuration, and orchestration across layers.
Provides the core interface for domain-related operations.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..utils.config_processor import ConfigProcessor, ConfigProcessingError
from ..types.models.internal_models import GenerationResult
from ..types.models.config_models import EntityDomainConfig, LayerConfig
from ..services.core import CoreLayerGenerator
from ..services.interface import InterfaceLayerGenerator
from ..services.repository import RepositoryLayerGenerator
from ..services.usecase import UseCaseLayerGenerator
from ..services.service import ServiceLayerGenerator

logger = get_logger(__name__)


class DomainManager:
    """
    Core domain management class.
    
    Orchestrates domain creation across multiple layers and manages
    domain configurations following the hexagonal architecture pattern.
    """

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize domain manager.
        
        Args:
            target_dir: Target project directory
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        # Initialize services
        self.core_generator = CoreLayerGenerator(str(self.target_dir))
        self.interface_generator = InterfaceLayerGenerator(str(self.target_dir))
        self.repository_generator = RepositoryLayerGenerator(str(self.target_dir))
        self.usecase_generator = UseCaseLayerGenerator(str(self.target_dir))
        self.service_generator = ServiceLayerGenerator(str(self.target_dir))
        
        self.logger.debug("DomainManager initialized", extra={
            "target_dir": str(self.target_dir),
            "operation": "init"
        })

    def add_domain(self, name: str, layers: list[str]) -> GenerationResult:
        """
        Add a new domain to the project.
        
        Creates domain directories and configuration files for the specified layers.
        
        Args:
            name: Domain name (e.g., "User", "Product")
            layers: List of layers to create ("core", "interface", "repository", "usecase", "service")
            
        Returns:
            GenerationResult with details about the domain creation
        """
        result = GenerationResult(
            success=True,
            operation_type="add_domain",
            metadata={"domain_name": name, "layers": layers}
        )
        
        self.logger.debug("Starting domain addition", extra={
            "domain_name": name,
            "layers": layers,
            "target_dir": str(self.target_dir),
            "operation": "add_domain"
        })
        
        try:
            with self.logger.timed_operation("domain_addition", extra={"domain_name": name}):
                # Create domain directories and configs for each layer
                for layer in layers:
                    layer = layer.strip().lower()
                    
                    if layer == "core":
                        config_file = self._create_core_domain_config(name)
                        result.add_generated_file(str(config_file))
                    elif layer == "interface":
                        config_file = self._create_interface_domain_config(name)
                        result.add_generated_file(str(config_file))
                    elif layer == "repository":
                        self._create_repository_domain_config(name)
                    elif layer == "usecase":
                        config_file = self._create_usecase_domain_config(name)
                        result.add_generated_file(str(config_file))
                    elif layer == "service":
                        self._create_service_domain_config(name)
                    else:
                        result.add_warning(f"Unknown layer specified: {layer}")
                        self.logger.warning("Unknown layer specified", extra={
                            "layer": layer,
                            "domain_name": name,
                            "operation": "add_domain"
                        })
            
            self.logger.info("Domain added successfully", extra={
                "domain_name": name,
                "layers": layers,
                "operation": "add_domain",
                "phase": "complete"
            })
            return result
            
        except Exception as e:
            result.add_error(f"Domain addition failed: {str(e)}")
            self.logger.error("Domain addition failed", exc_info=True, extra={
                "domain_name": name,
                "layers": layers,
                "operation": "add_domain",
                "phase": "failed"
            })
            return result

    def generate_core(self, config_path: str) -> GenerationResult:
        """
        Generate core layer from configuration.
        
        Args:
            config_path: Path to domain configuration file
            
        Returns:
            GenerationResult with details about the core generation
        """
        result = GenerationResult(
            success=True,
            operation_type="generate_core",
            metadata={"config_path": config_path}
        )
        
        self.logger.debug("Starting core generation", extra={
            "config_path": config_path,
            "operation": "generate_core"
        })
        
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                result.add_error(f"Configuration file not found: {config_path}")
                return result
            
            # Extract domain name from config path or file content
            domain_name = self._extract_domain_name_from_config(config_path)
            result.metadata["domain_name"] = domain_name
            
            with self.logger.timed_operation("core_generation", extra={"domain_name": domain_name}):
                core_result = self.core_generator.get_from_config(config_path)
                
                # Merge results from core generator
                if core_result.success:
                    result.files_generated.extend(core_result.files_generated)
                    result.files_modified.extend(core_result.files_modified)
                    result.warnings.extend(core_result.warnings)
                else:
                    result.success = False
                    result.errors.extend(core_result.errors)
            
            if result.success:
                self.logger.info("Core layer generated successfully", extra={
                    "domain_name": domain_name,
                    "config_path": config_path,
                    "operation": "generate_core",
                    "phase": "complete"
                })
            else:
                self.logger.error("Core layer generation failed", extra={
                    "domain_name": domain_name,
                    "config_path": config_path,
                    "operation": "generate_core",
                    "phase": "failed"
                })
            
            return result
            
        except Exception as e:
            result.add_error(f"Core generation failed: {str(e)}")
            self.logger.error("Core generation failed", exc_info=True, extra={
                "config_path": config_path,
                "operation": "generate_core",
                "phase": "failed"
            })
            return result

    def generate_all_layers(self, config_path: str, clean: bool = False) -> GenerationResult:
        """
        Generate all layers from comprehensive configuration.
        
        Args:
            config_path: Path to comprehensive configuration file
            clean: Whether to clean existing output
            
        Returns:
            GenerationResult with details about all layer generation
        """
        result = GenerationResult(
            success=True,
            operation_type="generate_all_layers",
            metadata={"config_path": config_path, "clean": clean}
        )
        
        self.logger.debug("Starting comprehensive generation", extra={
            "config_path": config_path,
            "clean": clean,
            "operation": "generate_all_layers"
        })
        
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                result.add_error(f"Configuration file not found: {config_path}")
                return result
            
            # Load and validate comprehensive config using ConfigProcessor
            config_processor = ConfigProcessor(str(self.target_dir))
            try:
                entity_config = config_processor.load_entity_domain_config(config_path)
            except Exception as e:
                result.add_error(f"Failed to load configuration: {str(e)}")
                return result
            
            domain_name = entity_config.name
            result.metadata["domain_name"] = domain_name
            
            with self.logger.timed_operation("comprehensive_generation", extra={"domain_name": domain_name}):
                # Generate each layer in dependency order
                layers_generated = []
                
                # 1. Core layer (entities, exceptions)
                if self._has_core_config(entity_config):
                    core_result = self.core_generator.get_from_config(entity_config)
                    if core_result.success:
                        layers_generated.append("core")
                        result.files_generated.extend(core_result.files_generated)
                        result.files_modified.extend(core_result.files_modified)
                        result.warnings.extend(core_result.warnings)
                    else:
                        result.add_error("Core layer generation failed")
                        result.errors.extend(core_result.errors)
                        return result
                
                # 2. Repository layer (depends on core)
                if self._has_repository_config(entity_config):
                    repo_result = self.repository_generator.get_from_config(entity_config, domain_name)
                    if repo_result.success:
                        layers_generated.append("repository")
                        result.files_generated.extend(repo_result.files_generated)
                        result.files_modified.extend(repo_result.files_modified)
                        result.warnings.extend(repo_result.warnings)
                    else:
                        result.add_error("Repository layer generation failed")
                        result.errors.extend(repo_result.errors)
                        return result
                
                # 3. Use case layer (depends on repository)
                if self._has_usecase_config(entity_config):
                    usecase_result = self.usecase_generator.get_from_config(entity_config, domain_name)
                    if usecase_result.success:
                        layers_generated.append("usecase")
                        result.files_generated.extend(usecase_result.files_generated)
                        result.files_modified.extend(usecase_result.files_modified)
                        result.warnings.extend(usecase_result.warnings)
                    else:
                        result.add_error("Use case layer generation failed")
                        result.errors.extend(usecase_result.errors)
                        return result
                
                # 4. Service layer (depends on use case)
                if self._has_service_config(entity_config):
                    service_result = self.service_generator.get_from_config(entity_config, domain_name)
                    if service_result.success:
                        layers_generated.append("service")
                        result.files_generated.extend(service_result.files_generated)
                        result.files_modified.extend(service_result.files_modified)
                        result.warnings.extend(service_result.warnings)
                    else:
                        result.add_error("Service layer generation failed")
                        result.errors.extend(service_result.errors)
                        return result
                
                # 5. Interface layer (depends on all others)
                if self._has_interface_config(entity_config):
                    interface_result = self.interface_generator.get_from_config(entity_config, domain_name)
                    if interface_result.success:
                        layers_generated.append("interface")
                        result.files_generated.extend(interface_result.files_generated)
                        result.files_modified.extend(interface_result.files_modified)
                        result.warnings.extend(interface_result.warnings)
                    else:
                        result.add_error("Interface layer generation failed")
                        result.errors.extend(interface_result.errors)
                        return result
                
                result.metadata["layers_generated"] = layers_generated
            
            self.logger.info("All layers generated successfully", extra={
                "domain_name": domain_name,
                "layers_generated": layers_generated,
                "operation": "generate_all_layers",
                "phase": "complete"
            })
            return result
            
        except Exception as e:
            result.add_error(f"Comprehensive generation failed: {str(e)}")
            self.logger.error("Comprehensive generation failed", exc_info=True, extra={
                "config_path": config_path,
                "operation": "generate_all_layers",
                "phase": "failed"
            })
            return result

    def _create_core_domain_config(self, domain_name: str) -> Path:
        """Create core domain configuration files."""
        domain_dir = self.target_dir / "app" / "core" / domain_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic domain.yaml config
        config_file = domain_dir / "domain.yaml"
        if not config_file.exists():
            config_data = {
                "domain": {
                    "name": domain_name,
                    "description": f"{domain_name} domain configuration"
                },
                "entities": {
                    f"{domain_name}": {
                        "description": f"Main {domain_name} entity",
                        "fields": {
                            "id": {"type": "UUID", "primary_key": True},
                            "name": {"type": "str", "description": f"{domain_name} name"}
                        }
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
        
        self.logger.debug("Core domain config created", extra={
            "domain_name": domain_name,
            "config_file": str(config_file)
        })
        
        return config_file

    def _create_interface_domain_config(self, domain_name: str) -> Path:
        """Create interface domain configuration files."""
        domain_dir = self.target_dir / "app" / "interface" / domain_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic interface.yaml config
        config_file = domain_dir / "interface.yaml"
        if not config_file.exists():
            config_data = {
                "interface": {
                    "domain": domain_name,
                    "description": f"{domain_name} interface configuration"
                },
                "endpoints": {
                    f"/{domain_name.lower()}s": {
                        "methods": ["GET", "POST"],
                        "description": f"CRUD operations for {domain_name}"
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
        
        self.logger.debug("Interface domain config created", extra={
            "domain_name": domain_name,
            "config_file": str(config_file)
        })
        
        return config_file

    def _create_repository_domain_config(self, domain_name: str) -> None:
        """Create repository domain configuration files."""
        domain_dir = self.target_dir / "app" / "repository" / domain_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug("Repository domain config created", extra={
            "domain_name": domain_name,
            "domain_dir": str(domain_dir)
        })

    def _create_usecase_domain_config(self, domain_name: str) -> Path:
        """Create use case domain configuration files."""
        domain_dir = self.target_dir / "app" / "usecase" / domain_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic usecase.yaml config
        config_file = domain_dir / "usecase.yaml"
        if not config_file.exists():
            config_data = {
                "use_case": {
                    "domain": domain_name,
                    "description": f"{domain_name} use case configuration"
                },
                "business_rules": {
                    f"Create{domain_name}": {
                        "description": f"Create a new {domain_name}",
                        "validation": ["name_required", "unique_name"]
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
        
        self.logger.debug("Use case domain config created", extra={
            "domain_name": domain_name,
            "config_file": str(config_file)
        })
        
        return config_file

    def _create_service_domain_config(self, domain_name: str) -> None:
        """Create service domain configuration files."""
        domain_dir = self.target_dir / "app" / "service" / domain_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug("Service domain config created", extra={
            "domain_name": domain_name,
            "domain_dir": str(domain_dir)
        })

    def _extract_domain_name_from_config(self, config_path: str) -> str:
        """Extract domain name from configuration file."""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            return config_data.get('domain', {}).get('name', 'Unknown')
        except Exception:
            # Fallback to extracting from path
            return Path(config_path).parent.name

    def _has_core_config(self, config: EntityDomainConfig) -> bool:
        """Check if config has core layer configuration."""
        return len(config.entities) > 0 or config.name is not None

    def _has_repository_config(self, config: EntityDomainConfig) -> bool:
        """Check if config has repository layer configuration."""
        return len(config.entities) > 0

    def _has_usecase_config(self, config: EntityDomainConfig) -> bool:
        """Check if config has use case layer configuration."""
        # Check if there are business rules or use case methods defined
        return (hasattr(config, 'business_rules') and len(getattr(config, 'business_rules', [])) > 0) or \
               len(config.entities) > 0

    def _has_service_config(self, config: EntityDomainConfig) -> bool:
        """Check if config has service layer configuration."""
        # Check if there are service-specific configurations
        return hasattr(config, 'service') and getattr(config, 'service') is not None

    def _has_interface_config(self, config: EntityDomainConfig) -> bool:
        """Check if config has interface layer configuration."""
        return len(config.endpoints) > 0 or len(config.entities) > 0
