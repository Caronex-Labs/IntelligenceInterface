"""
Project Validator for FastAPI SQLModel Generator.

Handles validation of configuration files, domain consistency,
and project structure validation.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import yaml
import json
from pydantic import ValidationError, BaseModel, Field

from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike, YAMLContent
from ..utils.config_processor import ConfigProcessor, ConfigProcessingError
from ..types.models.internal_models import ValidationContext
from ..types.models.config_models import (
    EntityDomainConfig,
    UseCaseDomainConfig,
    ServiceConfig,
    Configuration,
    LayerConfig,
    InterfaceLayerConfig,
    RepositoryLayerConfig
)

logger = get_logger(__name__)


class ValidationResult(BaseModel):
    """Result of validation operation with structured error reporting."""
    
    is_valid: bool = Field(..., description="Whether the validation passed")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    config_type: Optional[str] = Field(default=None, description="Type of configuration validated")
    file_path: Optional[str] = Field(default=None, description="Path to the validated file")
    validation_context: Optional[ValidationContext] = Field(default=None, description="Additional validation context")
    
    def add_error(self, message: str, line_number: Optional[int] = None) -> None:
        """Add an error message and mark validation as failed."""
        self.errors.append(message)
        self.is_valid = False
        if self.validation_context and line_number:
            self.validation_context.add_error(message, line_number)
    
    def add_warning(self, message: str, line_number: Optional[int] = None) -> None:
        """Add a warning message."""
        self.warnings.append(message)
        if self.validation_context and line_number:
            self.validation_context.add_warning(message, line_number)
    
    def merge_context(self, context: ValidationContext) -> None:
        """Merge validation context into this result."""
        self.errors.extend(context.errors)
        self.warnings.extend(context.warnings)
        if context.errors:
            self.is_valid = False
        if not self.validation_context:
            self.validation_context = context
    
    @property
    def error_count(self) -> int:
        """Number of validation errors."""
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """Number of validation warnings."""
        return len(self.warnings)
    
    @property
    def total_issues(self) -> int:
        """Total number of validation issues."""
        return len(self.errors) + len(self.warnings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for backward compatibility."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "config_type": self.config_type,
            "file_path": self.file_path
        }


class ProjectValidator:
    """
    Core project validation class.
    
    Validates configuration files, domain consistency,
    and project structure for correctness.
    """

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize project validator.
        
        Args:
            target_dir: Target project directory
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        # Initialize config processor for validation
        template_base = Path(__file__).parent.parent.parent
        self.config_processor = ConfigProcessor(template_base)
        
        self.logger.debug("ProjectValidator initialized", extra={
            "target_dir": str(self.target_dir),
            "operation": "init"
        })

    def validate_config(self, config_path: str, config_type: Optional[str] = None) -> ValidationResult:
        """
        Validate a configuration file.
        
        Args:
            config_path: Path to configuration file
            config_type: Expected config type ("entity-domain", "usecase", "service", "configuration")
            
        Returns:
            ValidationResult with validation details
        """
        self.logger.debug("Starting config validation", extra={
            "config_path": config_path,
            "config_type": config_type,
            "operation": "validate_config"
        })
        
        result = ValidationResult(is_valid=True, config_type=config_type, file_path=config_path)
        
        # Create validation context
        validation_context = ValidationContext(
            config_type=config_type or "unknown",
            file_path=config_path
        )
        result.validation_context = validation_context
        
        try:
            config_file = Path(config_path)
            
            # Check file exists
            if not config_file.exists():
                result.add_error(f"Configuration file not found: {config_path}")
                return result
            
            # Load config data
            try:
                with open(config_file, 'r') as f:
                    if config_file.suffix.lower() in ['.yaml', '.yml']:
                        config_data: YAMLContent = yaml.safe_load(f)
                    elif config_file.suffix.lower() == '.json':
                        config_data = json.load(f)
                    else:
                        result.add_error(f"Unsupported config file format: {config_file.suffix}")
                        return result
            except Exception as e:
                result.add_error(f"Failed to parse config file: {e}")
                return result
            
            # Validate config structure
            if not isinstance(config_data, dict):
                result.add_error("Configuration must be a dictionary/object")
                return result
            
            # Auto-detect config type if not provided
            if config_type is None:
                config_type = self._detect_config_type(config_data)
                result.config_type = config_type
                validation_context.config_type = config_type
            
            # Validate based on config type using Pydantic models
            with self.logger.timed_operation("config_validation", extra={
                "config_type": config_type,
                "config_path": config_path
            }):
                if config_type == "entity-domain":
                    try:
                        validated_config = EntityDomainConfig(**config_data)
                        self._validate_entity_domain_config(validated_config, result)
                    except ValidationError as e:
                        self._handle_pydantic_validation_error(e, result, "entity-domain")
                elif config_type == "usecase":
                    try:
                        validated_config = UseCaseDomainConfig(**config_data)
                        self._validate_usecase_config(validated_config, result)
                    except ValidationError as e:
                        self._handle_pydantic_validation_error(e, result, "usecase")
                elif config_type == "service":
                    try:
                        validated_config = ServiceConfig(**config_data)
                        self._validate_service_config(validated_config, result)
                    except ValidationError as e:
                        self._handle_pydantic_validation_error(e, result, "service")
                elif config_type == "configuration":
                    try:
                        validated_config = Configuration(**config_data)
                        self._validate_comprehensive_config(validated_config, result)
                    except ValidationError as e:
                        self._handle_pydantic_validation_error(e, result, "configuration")
                elif config_type == "layer":
                    try:
                        validated_config = LayerConfig(**config_data)
                        self._validate_layer_config(validated_config, result)
                    except ValidationError as e:
                        self._handle_pydantic_validation_error(e, result, "layer")
                elif config_type == "interface":
                    try:
                        validated_config = InterfaceLayerConfig(**config_data)
                        self._validate_interface_config(validated_config, result)
                    except ValidationError as e:
                        self._handle_pydantic_validation_error(e, result, "interface")
                elif config_type == "repository":
                    try:
                        validated_config = RepositoryLayerConfig(**config_data)
                        self._validate_repository_config(validated_config, result)
                    except ValidationError as e:
                        self._handle_pydantic_validation_error(e, result, "repository")
                else:
                    result.add_warning(f"Unknown config type: {config_type}, performing basic validation only")
                    self._validate_basic_structure(config_data, result)
            
            # Log validation result
            if result.is_valid:
                self.logger.info("Configuration validation successful", extra={
                    "config_path": config_path,
                    "config_type": config_type,
                    "warning_count": len(result.warnings),
                    "operation": "validate_config",
                    "phase": "complete"
                })
            else:
                self.logger.warning("Configuration validation failed", extra={
                    "config_path": config_path,
                    "config_type": config_type,
                    "error_count": len(result.errors),
                    "warning_count": len(result.warnings),
                    "operation": "validate_config",
                    "phase": "failed"
                })
            
            return result
            
        except Exception as e:
            self.logger.error("Configuration validation error", exc_info=True, extra={
                "config_path": config_path,
                "operation": "validate_config",
                "phase": "failed"
            })
            result.add_error(f"Validation error: {e}")
            return result

    def validate_domain(self, domain_name: str) -> ValidationResult:
        """
        Validate a domain's configuration and consistency.
        
        Args:
            domain_name: Name of domain to validate
            
        Returns:
            ValidationResult with validation details
        """
        self.logger.debug("Starting domain validation", extra={
            "domain_name": domain_name,
            "operation": "validate_domain"
        })
        
        result = ValidationResult(is_valid=True, config_type="domain", file_path=domain_name)
        
        # Create validation context for domain
        validation_context = ValidationContext(
            config_type="domain",
            file_path=domain_name
        )
        result.validation_context = validation_context
        
        try:
            with self.logger.timed_operation("domain_validation", extra={"domain_name": domain_name}):
                # Check domain directories exist
                domain_paths = {
                    "core": self.target_dir / "app" / "core" / domain_name,
                    "interface": self.target_dir / "app" / "interface" / domain_name,
                    "repository": self.target_dir / "app" / "repository" / domain_name,
                    "usecase": self.target_dir / "app" / "usecase" / domain_name,
                    "service": self.target_dir / "app" / "service" / domain_name
                }
                
                existing_layers = []
                for layer, path in domain_paths.items():
                    if path.exists():
                        existing_layers.append(layer)
                    else:
                        result.add_warning(f"Domain layer not found: {layer} at {path}")
                
                if not existing_layers:
                    result.add_error(f"No domain layers found for {domain_name}")
                    return result
                
                # Validate each layer's configuration
                for layer in existing_layers:
                    layer_result = self._validate_domain_layer(domain_name, layer)
                    result.errors.extend(layer_result.errors)
                    result.warnings.extend(layer_result.warnings)
                    if not layer_result.is_valid:
                        result.is_valid = False
                
                # Check layer dependencies
                dependency_result = self._validate_layer_dependencies(existing_layers)
                result.errors.extend(dependency_result.errors)
                result.warnings.extend(dependency_result.warnings)
                if not dependency_result.is_valid:
                    result.is_valid = False
            
            # Log validation result
            if result.is_valid:
                self.logger.info("Domain validation successful", extra={
                    "domain_name": domain_name,
                    "existing_layers": existing_layers,
                    "warning_count": len(result.warnings),
                    "operation": "validate_domain",
                    "phase": "complete"
                })
            else:
                self.logger.warning("Domain validation failed", extra={
                    "domain_name": domain_name,
                    "existing_layers": existing_layers,
                    "error_count": len(result.errors),
                    "warning_count": len(result.warnings),
                    "operation": "validate_domain",
                    "phase": "failed"
                })
            
            return result
            
        except Exception as e:
            self.logger.error("Domain validation error", exc_info=True, extra={
                "domain_name": domain_name,
                "operation": "validate_domain",
                "phase": "failed"
            })
            result.add_error(f"Domain validation error: {e}")
            return result

    def validate_project_structure(self) -> ValidationResult:
        """
        Validate overall project structure.
        
        Returns:
            ValidationResult with validation details
        """
        self.logger.debug("Starting project structure validation", extra={
            "target_dir": str(self.target_dir),
            "operation": "validate_project_structure"
        })
        
        result = ValidationResult(True)
        
        try:
            # Check basic project structure
            required_dirs = [
                "app",
                "app/core",
                "app/interface", 
                "app/repository",
                "app/usecase",
                "app/service"
            ]
            
            for dir_path in required_dirs:
                full_path = self.target_dir / dir_path
                if not full_path.exists():
                    result.add_error(f"Required directory missing: {dir_path}")
            
            # Check for project files
            expected_files = [
                "pyproject.toml",
                "justfile",
                ".gitignore"
            ]
            
            for file_path in expected_files:
                full_path = self.target_dir / file_path
                if not full_path.exists():
                    result.add_warning(f"Expected project file missing: {file_path}")
            
            self.logger.info("Project structure validation completed", extra={
                "target_dir": str(self.target_dir),
                "is_valid": result.is_valid,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
                "operation": "validate_project_structure",
                "phase": "complete"
            })
            
            return result
            
        except Exception as e:
            self.logger.error("Project structure validation error", exc_info=True, extra={
                "target_dir": str(self.target_dir),
                "operation": "validate_project_structure",
                "phase": "failed"
            })
            result.add_error(f"Project structure validation error: {e}")
            return result

    def _detect_config_type(self, config_data: YAMLContent) -> str:
        """Detect configuration type from data structure."""
        if "entities" in config_data or ("domain" in config_data and "entities" in str(config_data)):
            return "entity-domain"
        elif "use_case" in config_data or "business_rules" in config_data or "methods" in config_data:
            return "usecase"
        elif "service" in config_data and "name" in config_data.get("service", {}):
            return "service"
        elif "domains" in config_data or "comprehensive" in config_data:
            return "configuration"
        elif "layer" in config_data:
            return "layer"
        elif "interface" in config_data or "api" in config_data:
            return "interface"
        elif "repository" in config_data or "database" in config_data:
            return "repository"
        else:
            return "unknown"

    def _validate_entity_domain_config(self, config: EntityDomainConfig, result: ValidationResult) -> None:
        """Validate entity domain configuration using Pydantic model."""
        try:
            # Additional business logic validation beyond Pydantic
            if not config.entities:
                result.add_warning("Entity domain configuration has no entities defined")
            
            # Validate entity relationships
            entity_names = {entity.name for entity in config.entities}
            for entity in config.entities:
                for relationship in entity.relationships:
                    if relationship.entity not in entity_names:
                        result.add_error(f"Entity '{entity.name}' has relationship to undefined entity '{relationship.entity}'")
            
            # Validate domain-level relationships
            for domain_rel in config.relationships:
                if domain_rel.from_entity not in entity_names:
                    result.add_error(f"Domain relationship references undefined entity '{domain_rel.from_entity}'")
                if domain_rel.to_entity not in entity_names:
                    result.add_error(f"Domain relationship references undefined entity '{domain_rel.to_entity}'")
            
        except Exception as e:
            result.add_error(f"Entity domain config validation error: {e}")

    def _validate_usecase_config(self, config: UseCaseDomainConfig, result: ValidationResult) -> None:
        """Validate use case configuration using Pydantic model."""
        try:
            # Additional business logic validation beyond Pydantic
            if not config.methods:
                result.add_warning("Use case configuration has no methods defined")
            
            # Validate method dependencies
            method_names = {method.name for method in config.methods}
            for method in config.methods:
                if hasattr(method, 'orchestration_steps'):
                    for step in method.orchestration_steps:
                        if step not in method_names and not step.startswith('external_'):
                            result.add_warning(f"Method '{method.name}' references undefined orchestration step '{step}'")
            
        except Exception as e:
            result.add_error(f"Use case config validation error: {e}")

    def _validate_service_config(self, config: ServiceConfig, result: ValidationResult) -> None:
        """Validate service configuration using Pydantic model."""
        try:
            # Additional business logic validation beyond Pydantic
            if not config.methods:
                result.add_warning("Service configuration has no methods defined")
            
            # Validate service dependencies
            for dependency in config.dependencies:
                if not dependency.endswith('Service') and not dependency.endswith('Repository'):
                    result.add_warning(f"Service dependency '{dependency}' should follow naming convention (end with 'Service' or 'Repository')")
            
        except Exception as e:
            result.add_error(f"Service config validation error: {e}")

    def _validate_comprehensive_config(self, config: Configuration, result: ValidationResult) -> None:
        """Validate comprehensive configuration using Pydantic model."""
        try:
            # Additional business logic validation beyond Pydantic
            if not config.entities:
                result.add_error("Comprehensive configuration must have at least one entity")
            
            # Validate endpoint-entity consistency
            entity_names = {entity.name.lower() for entity in config.entities}
            domain_name = config.domain.name.lower()
            
            if domain_name not in entity_names:
                result.add_warning(f"Domain name '{config.domain.name}' does not match any entity name")
            
        except Exception as e:
            result.add_error(f"Comprehensive config validation error: {e}")

    def _validate_layer_config(self, config: LayerConfig, result: ValidationResult) -> None:
        """Validate layer configuration using Pydantic model."""
        try:
            # Additional business logic validation beyond Pydantic
            layer_name = config.layer.get('name', 'unknown')
            
            if not config.domains:
                result.add_warning(f"Layer '{layer_name}' has no domains configured")
            
            # Validate domain statuses
            for domain in config.domains:
                if domain.status == "error":
                    result.add_error(f"Domain '{domain.name}' in layer '{layer_name}' has error status")
                elif domain.status == "blank":
                    result.add_warning(f"Domain '{domain.name}' in layer '{layer_name}' is blank")
            
        except Exception as e:
            result.add_error(f"Layer config validation error: {e}")

    def _validate_interface_config(self, config: InterfaceLayerConfig, result: ValidationResult) -> None:
        """Validate interface layer configuration using Pydantic model."""
        try:
            # Additional business logic validation beyond Pydantic
            if not config.endpoints:
                result.add_warning("Interface configuration has no endpoints defined")
            
            # Validate endpoint paths
            paths = []
            for endpoint in config.endpoints:
                path = endpoint.get('path', '')
                if path in paths:
                    result.add_error(f"Duplicate endpoint path: {path}")
                paths.append(path)
            
        except Exception as e:
            result.add_error(f"Interface config validation error: {e}")

    def _validate_repository_config(self, config: RepositoryLayerConfig, result: ValidationResult) -> None:
        """Validate repository layer configuration using Pydantic model."""
        try:
            # Additional business logic validation beyond Pydantic
            if not config.repository:
                result.add_warning("Repository configuration is empty")
            
            # Validate database configuration
            if config.database and 'connection_string' not in config.database:
                result.add_warning("Repository database configuration missing connection_string")
            
        except Exception as e:
            result.add_error(f"Repository config validation error: {e}")

    def _handle_pydantic_validation_error(self, error: ValidationError, result: ValidationResult, config_type: str) -> None:
        """Handle Pydantic validation errors and add them to result."""
        for validation_error in error.errors():
            field = '.'.join(str(loc) for loc in validation_error['loc'])
            error_msg = f"{config_type.title()} config error in {field}: {validation_error['msg']}"
            
            # Try to extract line number if available
            line_number = None
            if 'ctx' in validation_error and 'line_number' in validation_error['ctx']:
                line_number = validation_error['ctx']['line_number']
            
            result.add_error(error_msg, line_number)

    def _validate_basic_structure(self, config_data: YAMLContent, result: ValidationResult) -> None:
        """Validate basic configuration structure."""
        if not config_data:
            result.add_error("Configuration is empty")
            return
        
        # Basic structure checks
        if not isinstance(config_data, dict):
            result.add_error("Configuration must be a dictionary")

    def _validate_domain_layer(self, domain_name: str, layer: str) -> ValidationResult:
        """Validate a specific domain layer."""
        result = ValidationResult(True)
        
        domain_path = self.target_dir / "app" / layer / domain_name
        
        # Check for configuration files
        config_files = {
            "core": ["domain.yaml", "entities.yaml"],
            "interface": ["interface.yaml"],
            "repository": ["repository.yaml"],
            "usecase": ["usecase.yaml", "business-rules.yaml"],
            "service": ["service.yaml"]
        }
        
        expected_configs = config_files.get(layer, [])
        for config_file in expected_configs:
            config_path = domain_path / config_file
            if not config_path.exists():
                result.add_warning(f"Expected config file missing: {layer}/{domain_name}/{config_file}")
        
        return result

    def _validate_layer_dependencies(self, layers: List[str]) -> ValidationResult:
        """Validate layer dependencies are satisfied."""
        result = ValidationResult(True)
        
        dependencies = {
            "repository": ["core"],
            "usecase": ["core", "repository"],
            "service": ["core", "repository", "usecase"],
            "interface": ["core", "repository", "usecase"]
        }
        
        for layer in layers:
            required_deps = dependencies.get(layer, [])
            for dep in required_deps:
                if dep not in layers:
                    result.add_warning(f"Layer {layer} requires {dep} but {dep} is not present")
        
        return result
