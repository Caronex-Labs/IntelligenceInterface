"""
Config Processor Utility.

Centralized configuration loading and validation using Pydantic models.
Handles layer configs and domain-specific configs with proper validation.
"""

from pathlib import Path
from typing import List, Optional
import yaml
import logging

from .type_aliases import PathLike, YAMLContent
from ..types.models.internal_models import ValidationContext
from ..types.models.config_models import (
    EntityDomainConfig,
    InterfaceLayerConfig,
    UseCaseDomainConfig,
    RepositoryLayerConfig,
    ServiceConfig,
    LayerConfig,
    DomainInfo,
)
from .logging_utils import get_logger

logger = get_logger(__name__)


class ConfigProcessingError(Exception):
    """Exception raised when config processing fails."""
    pass


class ConfigProcessor:
    """
    Centralized configuration processor with Pydantic validation.
    
    Handles loading and validation of:
    - Layer-level configs (generic layer settings + domain tracking)
    - Domain-specific configs (entity, interface, usecase, repository, service)
    """

    def __init__(self, base_path: PathLike) -> None:
        """
        Initialize config processor.
        
        Args:
            base_path: Base path for config files (usually project root)
        """
        self.base_path = Path(base_path)
        self.logger = get_logger(__name__)
        
        self.logger.debug("ConfigProcessor initialized", extra={
            "base_path": str(self.base_path),
            "operation": "init"
        })

    def load_domain_config(self, domain_path: Path) -> EntityDomainConfig:
        """
        Load and validate domain configuration (domain.yaml + entities.yaml).
        
        Args:
            domain_path: Path to domain directory containing config files
            
        Returns:
            Validated EntityDomainConfig object
            
        Raises:
            ConfigProcessingError: If config loading or validation fails
        """
        with self.logger.timed_operation("load_domain_config", extra={"domain_path": str(domain_path)}):
            try:
                domain_dir = Path(domain_path)
                
                self.logger.debug("Loading domain configuration", extra={
                    "domain_path": str(domain_dir),
                    "operation": "load_domain_config",
                    "phase": "start"
                })
                
                if not domain_dir.exists():
                    self.logger.error("Domain directory not found", extra={
                        "domain_path": str(domain_dir),
                        "operation": "load_domain_config"
                    })
                    raise ConfigProcessingError(f"Domain directory not found: {domain_dir}")
                
                # Load domain.yaml
                domain_yaml = domain_dir / "domain.yaml"
                entities_yaml = domain_dir / "entities.yaml"
                
                domain_config = {}
                entities_config = {}
                
                if domain_yaml.exists():
                    self.logger.debug("Loading domain.yaml file", extra={
                        "file_path": str(domain_yaml),
                        "operation": "load_domain_config"
                    })
                    domain_config = self._load_yaml_file(domain_yaml)
                    self.logger.debug("Domain.yaml loaded successfully", extra={
                        "file_path": str(domain_yaml),
                        "config_keys": list(domain_config.keys()) if domain_config else [],
                        "operation": "load_domain_config"
                    })
                else:
                    self.logger.warning("domain.yaml not found", extra={
                        "domain_path": str(domain_dir),
                        "file_path": str(domain_yaml),
                        "operation": "load_domain_config"
                    })
                
                if entities_yaml.exists():
                    self.logger.debug("Loading entities.yaml file", extra={
                        "file_path": str(entities_yaml),
                        "operation": "load_domain_config"
                    })
                    entities_config = self._load_yaml_file(entities_yaml)
                    self.logger.debug("Entities.yaml loaded successfully", extra={
                        "file_path": str(entities_yaml),
                        "entity_count": len(entities_config.get('entities', [])) if entities_config else 0,
                        "operation": "load_domain_config"
                    })
                else:
                    self.logger.warning("entities.yaml not found", extra={
                        "domain_path": str(domain_dir),
                        "file_path": str(entities_yaml),
                        "operation": "load_domain_config"
                    })
                
                # Merge domain and entities configs
                self.logger.debug("Merging domain and entities configurations", extra={
                    "domain_config_keys": list(domain_config.keys()) if domain_config else [],
                    "entities_config_keys": list(entities_config.keys()) if entities_config else [],
                    "operation": "load_domain_config"
                })
                merged_config = self._merge_domain_configs(domain_config, entities_config)
                
                # Validate with Pydantic model
                self.logger.debug("Validating merged configuration with Pydantic model", extra={
                    "merged_config_keys": list(merged_config.keys()),
                    "operation": "load_domain_config"
                })
                validated_config = EntityDomainConfig(**merged_config)
                
                self.logger.info("Domain configuration loaded and validated successfully", extra={
                    "domain_path": str(domain_dir),
                    "entity_count": len(validated_config.entities) if validated_config.entities else 0,
                    "operation": "load_domain_config"
                })
                
                return validated_config
                
            except Exception as e:
                self.logger.error("Failed to load domain config", exc_info=True, extra={
                    "domain_path": str(domain_path),
                    "error_type": type(e).__name__,
                    "operation": "load_domain_config"
                })
                raise ConfigProcessingError(f"Failed to load domain config from {domain_path}: {e}")

    def load_interface_config(self, interface_path: Path) -> InterfaceLayerConfig:
        """
        Load and validate interface configuration (interface.yaml).
        
        Args:
            interface_path: Path to interface.yaml file or directory containing it
            
        Returns:
            Validated InterfaceLayerConfig object
            
        Raises:
            ConfigProcessingError: If config loading or validation fails
        """
        with self.logger.timed_operation("load_interface_config", extra={"interface_path": str(interface_path)}):
            try:
                self.logger.debug("Loading interface configuration", extra={
                    "interface_path": str(interface_path),
                    "operation": "load_interface_config",
                    "config_type": "interface"
                })
                
                config_file = self._resolve_config_file(interface_path, "interface.yaml")
                config_data = self._load_yaml_file(config_file)
                
                self.logger.debug("Interface config file loaded", extra={
                    "config_file": str(config_file),
                    "config_keys": list(config_data.keys()) if config_data else [],
                    "operation": "load_interface_config"
                })
                
                # Validate with Pydantic model
                validated_config = InterfaceLayerConfig(**config_data)
                
                self.logger.info("Interface configuration loaded and validated successfully", extra={
                    "config_file": str(config_file),
                    "operation": "load_interface_config"
                })
                
                return validated_config
                
            except Exception as e:
                self.logger.error("Failed to load interface config", exc_info=True, extra={
                    "interface_path": str(interface_path),
                    "error_type": type(e).__name__,
                    "operation": "load_interface_config"
                })
                raise ConfigProcessingError(f"Failed to load interface config from {interface_path}: {e}")

    def load_usecase_config(self, usecase_path: Path) -> UseCaseDomainConfig:
        """
        Load and validate usecase configuration (usecase.yaml + business-rules.yaml).
        
        Args:
            usecase_path: Path to usecase directory containing config files
            
        Returns:
            Validated UseCaseDomainConfig object
            
        Raises:
            ConfigProcessingError: If config loading or validation fails
        """
        with self.logger.timed_operation("load_usecase_config", extra={"usecase_path": str(usecase_path)}):
            try:
                usecase_dir = Path(usecase_path)
                
                self.logger.debug("Loading usecase configuration", extra={
                    "usecase_path": str(usecase_dir),
                    "operation": "load_usecase_config",
                    "config_type": "usecase"
                })
                
                if not usecase_dir.exists():
                    self.logger.error("UseCase directory not found", extra={
                        "usecase_path": str(usecase_dir),
                        "operation": "load_usecase_config"
                    })
                    raise ConfigProcessingError(f"UseCase directory not found: {usecase_dir}")
                
                # Load usecase.yaml and business-rules.yaml
                usecase_yaml = usecase_dir / "usecase.yaml"
                business_rules_yaml = usecase_dir / "business-rules.yaml"
                
                usecase_config = {}
                business_rules_config = {}
                
                if usecase_yaml.exists():
                    self.logger.debug("Loading usecase.yaml file", extra={
                        "file_path": str(usecase_yaml),
                        "operation": "load_usecase_config"
                    })
                    usecase_config = self._load_yaml_file(usecase_yaml)
                    self.logger.debug("Usecase.yaml loaded successfully", extra={
                        "file_path": str(usecase_yaml),
                        "config_keys": list(usecase_config.keys()) if usecase_config else [],
                        "operation": "load_usecase_config"
                    })
                else:
                    self.logger.error("usecase.yaml not found", extra={
                        "usecase_path": str(usecase_dir),
                        "file_path": str(usecase_yaml),
                        "operation": "load_usecase_config"
                    })
                    raise ConfigProcessingError(f"usecase.yaml not found in {usecase_dir}")
                
                if business_rules_yaml.exists():
                    self.logger.debug("Loading business-rules.yaml file", extra={
                        "file_path": str(business_rules_yaml),
                        "operation": "load_usecase_config"
                    })
                    business_rules_config = self._load_yaml_file(business_rules_yaml)
                    self.logger.debug("Business-rules.yaml loaded successfully", extra={
                        "file_path": str(business_rules_yaml),
                        "config_keys": list(business_rules_config.keys()) if business_rules_config else [],
                        "operation": "load_usecase_config"
                    })
                else:
                    self.logger.warning("business-rules.yaml not found", extra={
                        "usecase_path": str(usecase_dir),
                        "file_path": str(business_rules_yaml),
                        "operation": "load_usecase_config"
                    })
                
                # Merge usecase and business rules configs
                self.logger.debug("Merging usecase and business rules configurations", extra={
                    "usecase_config_keys": list(usecase_config.keys()) if usecase_config else [],
                    "business_rules_config_keys": list(business_rules_config.keys()) if business_rules_config else [],
                    "operation": "load_usecase_config"
                })
                merged_config = self._merge_usecase_configs(usecase_config, business_rules_config)
                
                # Validate with Pydantic model
                self.logger.debug("Validating merged usecase configuration", extra={
                    "merged_config_keys": list(merged_config.keys()),
                    "operation": "load_usecase_config"
                })
                validated_config = UseCaseDomainConfig(**merged_config)
                
                self.logger.info("UseCase configuration loaded and validated successfully", extra={
                    "usecase_path": str(usecase_dir),
                    "operation": "load_usecase_config"
                })
                
                return validated_config
                
            except Exception as e:
                self.logger.error("Failed to load usecase config", exc_info=True, extra={
                    "usecase_path": str(usecase_path),
                    "error_type": type(e).__name__,
                    "operation": "load_usecase_config"
                })
                raise ConfigProcessingError(f"Failed to load usecase config from {usecase_path}: {e}")

    def load_repository_config(self, repo_path: Path) -> RepositoryLayerConfig:
        """
        Load and validate repository configuration (repository.yaml).
        
        Args:
            repo_path: Path to repository.yaml file or directory containing it
            
        Returns:
            Validated RepositoryLayerConfig object
            
        Raises:
            ConfigProcessingError: If config loading or validation fails
        """
        with self.logger.timed_operation("load_repository_config", extra={"repo_path": str(repo_path)}):
            try:
                self.logger.debug("Loading repository configuration", extra={
                    "repo_path": str(repo_path),
                    "operation": "load_repository_config",
                    "config_type": "repository"
                })
                
                config_file = self._resolve_config_file(repo_path, "repository.yaml")
                config_data = self._load_yaml_file(config_file)
                
                self.logger.debug("Repository config file loaded", extra={
                    "config_file": str(config_file),
                    "config_keys": list(config_data.keys()) if config_data else [],
                    "operation": "load_repository_config"
                })
                
                # Validate with Pydantic model
                validated_config = RepositoryLayerConfig(**config_data)
                
                self.logger.info("Repository configuration loaded and validated successfully", extra={
                    "config_file": str(config_file),
                    "operation": "load_repository_config"
                })
                
                return validated_config
                
            except Exception as e:
                self.logger.error("Failed to load repository config", exc_info=True, extra={
                    "repo_path": str(repo_path),
                    "error_type": type(e).__name__,
                    "operation": "load_repository_config"
                })
                raise ConfigProcessingError(f"Failed to load repository config from {repo_path}: {e}")

    def load_service_config(self, service_path: Path) -> ServiceConfig:
        """
        Load and validate service configuration (service.yaml).
        
        Args:
            service_path: Path to service.yaml file or directory containing it
            
        Returns:
            Validated ServiceConfig object
            
        Raises:
            ConfigProcessingError: If config loading or validation fails
        """
        with self.logger.timed_operation("load_service_config", extra={"service_path": str(service_path)}):
            try:
                self.logger.debug("Loading service configuration", extra={
                    "service_path": str(service_path),
                    "operation": "load_service_config",
                    "config_type": "service"
                })
                
                config_file = self._resolve_config_file(service_path, "service.yaml")
                config_data = self._load_yaml_file(config_file)
                
                self.logger.debug("Service config file loaded", extra={
                    "config_file": str(config_file),
                    "config_keys": list(config_data.keys()) if config_data else [],
                    "operation": "load_service_config"
                })
                
                # Validate with Pydantic model
                validated_config = ServiceConfig(**config_data)
                
                self.logger.info("Service configuration loaded and validated successfully", extra={
                    "config_file": str(config_file),
                    "operation": "load_service_config"
                })
                
                return validated_config
                
            except Exception as e:
                self.logger.error("Failed to load service config", exc_info=True, extra={
                    "service_path": str(service_path),
                    "error_type": type(e).__name__,
                    "operation": "load_service_config"
                })
                raise ConfigProcessingError(f"Failed to load service config from {service_path}: {e}")

    def load_layer_config(self, layer: str, layer_path: Path) -> LayerConfig:
        """
        Load and validate layer configuration (layer_config.yaml).
        
        Args:
            layer: Layer name (domain, interface, usecase, repository, service)
            layer_path: Path to layer directory containing layer_config.yaml
            
        Returns:
            Validated LayerConfig object
            
        Raises:
            ConfigProcessingError: If config loading or validation fails
        """
        with self.logger.timed_operation("load_layer_config", extra={"layer": layer, "layer_path": str(layer_path)}):
            try:
                config_file = layer_path / "layer_config.yaml"
                
                self.logger.debug("Loading layer configuration", extra={
                    "layer": layer,
                    "layer_path": str(layer_path),
                    "config_file": str(config_file),
                    "operation": "load_layer_config"
                })
                
                if not config_file.exists():
                    # Create empty layer config if it doesn't exist
                    self.logger.info("Creating empty layer config", extra={
                        "layer": layer,
                        "config_file": str(config_file),
                        "operation": "load_layer_config",
                        "action": "create_empty"
                    })
                    empty_config = {
                        "layer": {
                            "name": layer,
                            "description": f"{layer.title()} layer configuration"
                        },
                        "domains": [],
                        "generation": {},
                        "metadata": {}
                    }
                    validated_config = LayerConfig(**empty_config)
                    
                    self.logger.debug("Empty layer config created", extra={
                        "layer": layer,
                        "config_structure": list(empty_config.keys()),
                        "operation": "load_layer_config"
                    })
                    
                    return validated_config
                
                config_data = self._load_yaml_file(config_file)
                
                self.logger.debug("Layer config file loaded", extra={
                    "layer": layer,
                    "config_file": str(config_file),
                    "config_keys": list(config_data.keys()) if config_data else [],
                    "domain_count": len(config_data.get('domains', [])) if config_data else 0,
                    "operation": "load_layer_config"
                })
                
                # Validate with Pydantic model
                validated_config = LayerConfig(**config_data)
                
                self.logger.info("Layer configuration loaded and validated successfully", extra={
                    "layer": layer,
                    "config_file": str(config_file),
                    "domain_count": len(validated_config.domains),
                    "operation": "load_layer_config"
                })
                
                return validated_config
                
            except Exception as e:
                self.logger.error("Failed to load layer config", exc_info=True, extra={
                    "layer": layer,
                    "layer_path": str(layer_path),
                    "error_type": type(e).__name__,
                    "operation": "load_layer_config"
                })
                raise ConfigProcessingError(f"Failed to load layer config for {layer} from {layer_path}: {e}")

    # Domain management methods
    def get_all_domains(self, layer: str, layer_path: Path) -> List[DomainInfo]:
        """
        Get all domains for a specific layer.
        
        Args:
            layer: Layer name
            layer_path: Path to layer directory
            
        Returns:
            List of DomainInfo objects
        """
        try:
            self.logger.debug("Getting all domains for layer", extra={
                "layer": layer,
                "layer_path": str(layer_path),
                "operation": "get_all_domains"
            })
            
            layer_config = self.load_layer_config(layer, layer_path)
            domains = layer_config.domains
            
            self.logger.debug("Retrieved domains for layer", extra={
                "layer": layer,
                "domain_count": len(domains),
                "domain_names": [d.name for d in domains],
                "operation": "get_all_domains"
            })
            
            return domains
        except ConfigProcessingError as e:
            self.logger.warning("Failed to get domains for layer", extra={
                "layer": layer,
                "layer_path": str(layer_path),
                "error": str(e),
                "operation": "get_all_domains"
            })
            return []

    def create_blank_domain(self, layer: str, layer_path: Path, domain_name: str) -> bool:
        """
        Create a blank domain entry in layer config.
        
        Args:
            layer: Layer name
            layer_path: Path to layer directory
            domain_name: Name of domain to create
            
        Returns:
            True if successful
        """
        with self.logger.timed_operation("create_blank_domain", extra={
            "layer": layer, 
            "domain_name": domain_name,
            "layer_path": str(layer_path)
        }):
            try:
                self.logger.debug("Creating blank domain", extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "layer_path": str(layer_path),
                    "operation": "create_blank_domain"
                })
                
                layer_config = self.load_layer_config(layer, layer_path)
                
                # Check if domain already exists
                existing_domain = next((d for d in layer_config.domains if d.name == domain_name), None)
                if existing_domain:
                    self.logger.warning("Domain already exists in layer", extra={
                        "layer": layer,
                        "domain_name": domain_name,
                        "existing_status": existing_domain.status,
                        "operation": "create_blank_domain"
                    })
                    return False
                
                # Add new blank domain
                new_domain = DomainInfo(
                    name=domain_name,
                    status="blank",
                    config_files=[],
                    description=f"Blank {domain_name} domain for user configuration"
                )
                layer_config.domains.append(new_domain)
                
                self.logger.debug("New blank domain created", extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "domain_status": new_domain.status,
                    "operation": "create_blank_domain"
                })
                
                # Save updated config
                self._save_layer_config(layer_path, layer_config)
                
                self.logger.info("Blank domain created successfully", extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "total_domains": len(layer_config.domains),
                    "operation": "create_blank_domain"
                })
                
                return True
                
            except Exception as e:
                self.logger.error("Failed to create blank domain", exc_info=True, extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "layer_path": str(layer_path),
                    "error_type": type(e).__name__,
                    "operation": "create_blank_domain"
                })
                return False

    def update_domain_status(self, layer: str, layer_path: Path, domain_name: str, status: str) -> bool:
        """
        Update domain status in layer config.
        
        Args:
            layer: Layer name
            layer_path: Path to layer directory
            domain_name: Name of domain to update
            status: New status (blank, configured, generated)
            
        Returns:
            True if successful
        """
        with self.logger.timed_operation("update_domain_status", extra={
            "layer": layer,
            "domain_name": domain_name,
            "new_status": status,
            "layer_path": str(layer_path)
        }):
            try:
                self.logger.debug("Updating domain status", extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "new_status": status,
                    "layer_path": str(layer_path),
                    "operation": "update_domain_status"
                })
                
                layer_config = self.load_layer_config(layer, layer_path)
                
                # Find and update domain
                domain = next((d for d in layer_config.domains if d.name == domain_name), None)
                if not domain:
                    self.logger.warning("Domain not found in layer", extra={
                        "layer": layer,
                        "domain_name": domain_name,
                        "available_domains": [d.name for d in layer_config.domains],
                        "operation": "update_domain_status"
                    })
                    return False
                
                old_status = domain.status
                domain.status = status
                
                self.logger.debug("Domain status updated", extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "old_status": old_status,
                    "new_status": status,
                    "operation": "update_domain_status"
                })
                
                # Save updated config
                self._save_layer_config(layer_path, layer_config)
                
                self.logger.info("Domain status updated successfully", extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "old_status": old_status,
                    "new_status": status,
                    "operation": "update_domain_status"
                })
                
                return True
                
            except Exception as e:
                self.logger.error("Failed to update domain status", exc_info=True, extra={
                    "layer": layer,
                    "domain_name": domain_name,
                    "new_status": status,
                    "layer_path": str(layer_path),
                    "error_type": type(e).__name__,
                    "operation": "update_domain_status"
                })
                return False

    def sync_domain_registry(self, layer: str, layer_path: Path) -> bool:
        """
        Sync layer config domains list with actual filesystem.
        
        Args:
            layer: Layer name
            layer_path: Path to layer directory
            
        Returns:
            True if successful
        """
        with self.logger.timed_operation("sync_domain_registry", extra={
            "layer": layer,
            "layer_path": str(layer_path)
        }):
            try:
                self.logger.debug("Starting domain registry synchronization", extra={
                    "layer": layer,
                    "layer_path": str(layer_path),
                    "operation": "sync_domain_registry"
                })
                
                layer_config = self.load_layer_config(layer, layer_path)
                original_domain_count = len(layer_config.domains)
                
                # Scan filesystem for actual domains
                actual_domains = []
                app_layer_path = layer_path
                
                self.logger.debug("Scanning filesystem for domains", extra={
                    "layer": layer,
                    "scan_path": str(app_layer_path),
                    "operation": "sync_domain_registry"
                })
                
                for item in app_layer_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.') and item.name != "{{domain}}":
                        self.logger.debug("Processing domain directory", extra={
                            "layer": layer,
                            "domain_name": item.name,
                            "domain_path": str(item),
                            "operation": "sync_domain_registry"
                        })
                        
                        # Check if domain has config files
                        config_files = []
                        status = "blank"
                        
                        # Layer-specific config file patterns
                        if layer == "domain":
                            if (item / "domain.yaml").exists():
                                config_files.append("domain.yaml")
                            if (item / "entities.yaml").exists():
                                config_files.append("entities.yaml")
                        elif layer == "interface":
                            if (item / "interface.yaml").exists():
                                config_files.append("interface.yaml")
                        elif layer == "usecase":
                            if (item / "usecase.yaml").exists():
                                config_files.append("usecase.yaml")
                            if (item / "business-rules.yaml").exists():
                                config_files.append("business-rules.yaml")
                        elif layer == "repository":
                            if (item / "repository.yaml").exists():
                                config_files.append("repository.yaml")
                        elif layer == "service":
                            if (item / "service.yaml").exists():
                                config_files.append("service.yaml")
                        
                        # Determine status based on config files
                        if config_files:
                            status = "configured"
                        
                        domain_info = DomainInfo(
                            name=item.name,
                            status=status,
                            config_files=config_files
                        )
                        actual_domains.append(domain_info)
                        
                        self.logger.debug("Domain processed", extra={
                            "layer": layer,
                            "domain_name": item.name,
                            "status": status,
                            "config_files": config_files,
                            "operation": "sync_domain_registry"
                        })
                
                # Update layer config with actual domains
                layer_config.domains = actual_domains
                
                self.logger.debug("Domain registry updated", extra={
                    "layer": layer,
                    "original_domain_count": original_domain_count,
                    "new_domain_count": len(actual_domains),
                    "domain_names": [d.name for d in actual_domains],
                    "operation": "sync_domain_registry"
                })
                
                # Save updated config
                self._save_layer_config(layer_path, layer_config)
                
                self.logger.info("Domain registry synchronized successfully", extra={
                    "layer": layer,
                    "original_domain_count": original_domain_count,
                    "synchronized_domain_count": len(actual_domains),
                    "operation": "sync_domain_registry"
                })
                
                return True
                
            except Exception as e:
                self.logger.error("Failed to sync domain registry", exc_info=True, extra={
                    "layer": layer,
                    "layer_path": str(layer_path),
                    "error_type": type(e).__name__,
                    "operation": "sync_domain_registry"
                })
                return False

    # Private helper methods
    def _load_yaml_file(self, file_path: Path) -> YAMLContent:
        """Load and parse YAML file."""
        try:
            self.logger.debug("Loading YAML file", extra={
                "file_path": str(file_path),
                "operation": "_load_yaml_file"
            })
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
                
            self.logger.debug("YAML file loaded successfully", extra={
                "file_path": str(file_path),
                "content_keys": list(content.keys()) if isinstance(content, dict) else [],
                "content_type": type(content).__name__,
                "operation": "_load_yaml_file"
            })
            
            return content
        except Exception as e:
            self.logger.error("Failed to load YAML file", exc_info=True, extra={
                "file_path": str(file_path),
                "error_type": type(e).__name__,
                "operation": "_load_yaml_file"
            })
            raise ConfigProcessingError(f"Failed to load YAML file {file_path}: {e}")

    def _resolve_config_file(self, path: Path, filename: str) -> Path:
        """Resolve config file path (file or directory containing file)."""
        path = Path(path)
        
        self.logger.debug("Resolving config file path", extra={
            "input_path": str(path),
            "filename": filename,
            "path_is_file": path.is_file(),
            "path_is_dir": path.is_dir(),
            "operation": "_resolve_config_file"
        })
        
        if path.is_file() and path.name == filename:
            self.logger.debug("Config file resolved as direct file", extra={
                "resolved_path": str(path),
                "filename": filename,
                "operation": "_resolve_config_file"
            })
            return path
        elif path.is_dir():
            config_file = path / filename
            if config_file.exists():
                self.logger.debug("Config file resolved in directory", extra={
                    "resolved_path": str(config_file),
                    "directory": str(path),
                    "filename": filename,
                    "operation": "_resolve_config_file"
                })
                return config_file
            else:
                self.logger.error("Config file not found in directory", extra={
                    "directory": str(path),
                    "filename": filename,
                    "operation": "_resolve_config_file"
                })
                raise ConfigProcessingError(f"{filename} not found in {path}")
        else:
            self.logger.error("Invalid config path", extra={
                "path": str(path),
                "filename": filename,
                "path_exists": path.exists(),
                "operation": "_resolve_config_file"
            })
            raise ConfigProcessingError(f"Invalid path: {path}")

    def _merge_domain_configs(self, domain_config: YAMLContent, entities_config: YAMLContent) -> YAMLContent:
        """Merge domain.yaml and entities.yaml configurations."""
        self.logger.debug("Merging domain configurations", extra={
            "domain_config_keys": list(domain_config.keys()) if domain_config else [],
            "entities_config_keys": list(entities_config.keys()) if entities_config else [],
            "operation": "_merge_domain_configs"
        })
        
        merged = {}
        
        # Start with domain config
        if 'domain' in domain_config:
            merged.update(domain_config['domain'])
            self.logger.debug("Added domain config section", extra={
                "added_keys": list(domain_config['domain'].keys()),
                "operation": "_merge_domain_configs"
            })
        
        # Add entities from entities config
        if 'entities' in entities_config:
            merged['entities'] = entities_config['entities']
            entity_count = len(entities_config['entities']) if isinstance(entities_config['entities'], list) else 0
            self.logger.debug("Added entities config section", extra={
                "entity_count": entity_count,
                "operation": "_merge_domain_configs"
            })
        else:
            merged['entities'] = []
            self.logger.debug("No entities found, using empty list", extra={
                "operation": "_merge_domain_configs"
            })
        
        # Add other domain-level configs
        for key in ['base_fields', 'mixins', 'relationships', 'sqlmodel_config']:
            if key in domain_config:
                merged[key] = domain_config[key]
                self.logger.debug("Added domain config key", extra={
                    "key": key,
                    "operation": "_merge_domain_configs"
                })
        
        self.logger.debug("Domain configurations merged successfully", extra={
            "merged_keys": list(merged.keys()),
            "final_entity_count": len(merged.get('entities', [])),
            "operation": "_merge_domain_configs"
        })
        
        return merged

    def _merge_usecase_configs(self, usecase_config: YAMLContent, business_rules_config: YAMLContent) -> YAMLContent:
        """Merge usecase.yaml and business-rules.yaml configurations."""
        self.logger.debug("Merging usecase configurations", extra={
            "usecase_config_keys": list(usecase_config.keys()) if usecase_config else [],
            "business_rules_config_keys": list(business_rules_config.keys()) if business_rules_config else [],
            "operation": "_merge_usecase_configs"
        })
        
        merged = dict(usecase_config)
        
        # Add business rules
        if 'business_rules' in business_rules_config:
            merged['business_rules'] = business_rules_config['business_rules']
            self.logger.debug("Added business rules section", extra={
                "business_rules_count": len(business_rules_config['business_rules']) if isinstance(business_rules_config['business_rules'], list) else 0,
                "operation": "_merge_usecase_configs"
            })
        
        # Merge other business rules config
        for key in ['validation', 'constraints', 'rules']:
            if key in business_rules_config:
                if key not in merged:
                    merged[key] = {}
                merged[key].update(business_rules_config[key])
                self.logger.debug("Merged business rules config key", extra={
                    "key": key,
                    "operation": "_merge_usecase_configs"
                })
        
        self.logger.debug("UseCase configurations merged successfully", extra={
            "merged_keys": list(merged.keys()),
            "operation": "_merge_usecase_configs"
        })
        
        return merged

    def _save_layer_config(self, layer_path: Path, layer_config: LayerConfig) -> None:
        """Save layer config to file."""
        config_file = layer_path / "layer_config.yaml"
        
        self.logger.debug("Saving layer config to file", extra={
            "config_file": str(config_file),
            "layer_name": layer_config.layer.name if layer_config.layer else "unknown",
            "domain_count": len(layer_config.domains),
            "operation": "_save_layer_config"
        })
        
        try:
            # Convert Pydantic model to dict
            config_dict = layer_config.model_dump()
            
            self.logger.debug("Layer config converted to dict", extra={
                "config_file": str(config_file),
                "config_keys": list(config_dict.keys()),
                "operation": "_save_layer_config"
            })
            
            # Write to YAML file
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info("Layer config saved successfully", extra={
                "config_file": str(config_file),
                "layer_name": layer_config.layer.name if layer_config.layer else "unknown",
                "domain_count": len(layer_config.domains),
                "operation": "_save_layer_config"
            })
            
        except Exception as e:
            self.logger.error("Failed to save layer config", exc_info=True, extra={
                "config_file": str(config_file),
                "error_type": type(e).__name__,
                "operation": "_save_layer_config"
            })
            raise
