"""
Configuration loading engine with PyYAML integration and comprehensive error handling.

This module provides the core configuration loading functionality, including safe YAML parsing,
type validation through Pydantic models, and descriptive error messages for all failure modes.
"""

import os
import logging
from pathlib import Path
from typing import Union, Dict, Any, Optional
import yaml
from pydantic import ValidationError

from .models import Configuration, EntityDomainConfig, EntityConfig, UseCaseDomainConfig, UseCaseConfig, BusinessRulesConfig
from .exceptions import ConfigurationError, ConfigurationValidationError, ConfigurationFileError

logger = logging.getLogger(__name__)


class ConfigurationLoader:
    """
    Core configuration loading engine.
    
    Provides safe YAML loading, type validation, and comprehensive error handling
    for template generation configuration files.
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize configuration loader.
        
        Args:
            strict_mode: If True, reject unknown fields and apply strict validation
        """
        self.strict_mode = strict_mode
        logger.info("ConfigurationLoader initialized with strict_mode=%s", strict_mode)
    
    def load_from_file(self, file_path: Union[str, Path]) -> Configuration:
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            Validated Configuration object
            
        Raises:
            ConfigurationFileError: If file cannot be read
            ConfigurationValidationError: If YAML is invalid or validation fails
            ConfigurationError: For other configuration-related errors
        """
        file_path = Path(file_path)
        logger.info("Loading configuration from file: %s", file_path)
        
        # Validate file exists and is readable
        if not file_path.exists():
            error_msg = f"Configuration file not found: {file_path}"
            logger.error(error_msg)
            raise ConfigurationFileError(
                error_msg,
                file_path=str(file_path),
                suggestion="Ensure the file path is correct and the file exists"
            )
        
        if not file_path.is_file():
            error_msg = f"Path is not a file: {file_path}"
            logger.error(error_msg)
            raise ConfigurationFileError(
                error_msg,
                file_path=str(file_path),
                suggestion="Ensure the path points to a file, not a directory"
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug("Successfully read file content (%d characters)", len(content))
        except IOError as e:
            error_msg = f"Failed to read configuration file: {e}"
            logger.error(error_msg)
            raise ConfigurationFileError(
                error_msg,
                file_path=str(file_path),
                suggestion="Check file permissions and ensure the file is readable"
            ) from e
        
        return self.load_from_string(content, source_file=str(file_path))
    
    def load_from_string(self, yaml_content: str, source_file: Optional[str] = None) -> Configuration:
        """
        Load configuration from YAML string.
        
        Args:
            yaml_content: YAML content as string
            source_file: Optional source file path for error reporting
            
        Returns:
            Validated Configuration object
            
        Raises:
            ConfigurationValidationError: If YAML is invalid or validation fails
            ConfigurationError: For other configuration-related errors
        """
        source_info = f" from {source_file}" if source_file else ""
        logger.info("Loading configuration from YAML string%s", source_info)
        
        # Parse YAML content
        try:
            yaml_data = yaml.safe_load(yaml_content)
            logger.debug("Successfully parsed YAML content")
        except yaml.YAMLError as e:
            error_msg = f"Invalid YAML syntax{source_info}: {e}"
            logger.error(error_msg)
            
            # Extract line number if available
            line_number = None
            if hasattr(e, 'problem_mark') and e.problem_mark:
                line_number = e.problem_mark.line + 1
            
            raise ConfigurationValidationError(
                error_msg,
                source_file=source_file,
                line_number=line_number,
                suggestion="Check YAML syntax - ensure proper indentation and quote matching"
            ) from e
        
        if yaml_data is None:
            error_msg = f"Empty YAML content{source_info}"
            logger.error(error_msg)
            raise ConfigurationValidationError(
                error_msg,
                source_file=source_file,
                suggestion="Provide valid YAML configuration content"
            )
        
        return self.load_from_dict(yaml_data, source_file=source_file)
    
    def load_from_dict(self, config_dict: Dict[str, Any], source_file: Optional[str] = None) -> Configuration:
        """
        Load configuration from dictionary.
        
        Args:
            config_dict: Configuration data as dictionary
            source_file: Optional source file path for error reporting
            
        Returns:
            Validated Configuration object
            
        Raises:
            ConfigurationValidationError: If validation fails
            ConfigurationError: For other configuration-related errors
        """
        source_info = f" from {source_file}" if source_file else ""
        logger.info("Loading configuration from dictionary%s", source_info)
        
        if not isinstance(config_dict, dict):
            error_msg = f"Configuration must be a dictionary, got {type(config_dict).__name__}{source_info}"
            logger.error(error_msg)
            raise ConfigurationValidationError(
                error_msg,
                source_file=source_file,
                suggestion="Ensure YAML root element is a mapping (key-value pairs)"
            )
        
        # Validate configuration using Pydantic model
        try:
            configuration = Configuration(**config_dict)
            logger.info("Successfully loaded and validated configuration%s", source_info)
            
            # Log configuration summary
            self._log_configuration_summary(configuration)
            
            return configuration
            
        except ValidationError as e:
            error_msg = f"Configuration validation failed{source_info}"
            logger.error(error_msg)
            
            # Create detailed error message from Pydantic validation errors
            validation_errors = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                error_detail = error['msg']
                error_type = error['type']
                
                validation_errors.append({
                    'field': field_path,
                    'error': error_detail,
                    'type': error_type,
                    'input': error.get('input')
                })
            
            raise ConfigurationValidationError(
                error_msg,
                source_file=source_file,
                validation_errors=validation_errors,
                suggestion=self._generate_validation_suggestion(validation_errors)
            ) from e
        
        except Exception as e:
            error_msg = f"Unexpected error loading configuration{source_info}: {e}"
            logger.error(error_msg, exc_info=True)
            raise ConfigurationError(error_msg) from e
    
    def validate_configuration(self, configuration: Configuration) -> bool:
        """
        Perform additional validation on loaded configuration.
        
        Args:
            configuration: Configuration object to validate
            
        Returns:
            True if validation passes
            
        Raises:
            ConfigurationValidationError: If validation fails
        """
        logger.info("Performing additional configuration validation")
        
        try:
            # Validate entity relationships reference valid entities
            entity_names = {entity.name for entity in configuration.entities}
            
            for entity in configuration.entities:
                for relationship in entity.relationships:
                    if relationship.entity not in entity_names:
                        raise ConfigurationValidationError(
                            f"Entity '{entity.name}' references unknown entity '{relationship.entity}' in relationship",
                            suggestion=f"Ensure entity '{relationship.entity}' is defined in entities list"
                        )
            
            # Validate endpoint operations are supported
            supported_operations = {'create', 'get_by_id', 'list', 'update', 'delete', 'search'}
            for endpoint in configuration.endpoints:
                if endpoint.operation not in supported_operations:
                    logger.warning(
                        "Endpoint operation '%s' may not be supported. Supported operations: %s",
                        endpoint.operation, supported_operations
                    )
            
            logger.info("Configuration validation completed successfully")
            return True
            
        except Exception as e:
            logger.error("Configuration validation failed: %s", e)
            raise
    
    def _log_configuration_summary(self, configuration: Configuration) -> None:
        """Log a summary of the loaded configuration."""
        logger.info("Configuration Summary:")
        logger.info("  Domain: %s (%s)", configuration.domain.name, configuration.domain.plural)
        logger.info("  Entities: %d", len(configuration.entities))
        for entity in configuration.entities:
            logger.info("    - %s (%d fields, %d relationships)", 
                       entity.name, len(entity.fields), len(entity.relationships))
        logger.info("  Endpoints: %d", len(configuration.endpoints))
        logger.info("  Metadata: %d items", len(configuration.metadata))
    
    def _generate_validation_suggestion(self, validation_errors: list) -> str:
        """Generate helpful suggestion based on validation errors."""
        if not validation_errors:
            return "Check configuration format and required fields"
        
        # Common validation error patterns and suggestions
        error_types = {error['type'] for error in validation_errors}
        
        if 'missing' in error_types:
            missing_fields = [error['field'] for error in validation_errors if error['type'] == 'missing']
            return f"Required fields are missing: {', '.join(missing_fields)}"
        
        if 'type_error' in error_types:
            return "Check field types - ensure strings are quoted, numbers are unquoted, and booleans are true/false"
        
        if 'value_error' in error_types:
            return "Check field values - ensure they meet validation requirements"
        
        return "Review configuration structure and field requirements"


def load_configuration(file_path: Union[str, Path], strict_mode: bool = True) -> Configuration:
    """
    Convenience function to load configuration from file.
    
    Args:
        file_path: Path to YAML configuration file
        strict_mode: If True, apply strict validation
        
    Returns:
        Validated Configuration object
    """
    loader = ConfigurationLoader(strict_mode=strict_mode)
    return loader.load_from_file(file_path)


def load_configuration_from_string(yaml_content: str, strict_mode: bool = True) -> Configuration:
    """
    Convenience function to load configuration from YAML string.
    
    Args:
        yaml_content: YAML content as string
        strict_mode: If True, apply strict validation
        
    Returns:
        Validated Configuration object
    """
    loader = ConfigurationLoader(strict_mode=strict_mode)
    return loader.load_from_string(yaml_content)


class EntityDomainLoader:
    """
    Specialized loader for entity domain configurations with separate domain and entity files.
    
    Loads domain.yaml and entities.yaml files separately and merges them into a unified
    EntityDomainConfig that supports advanced features like mixins, base fields, and
    domain-level relationship definitions.
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize entity domain loader.
        
        Args:
            strict_mode: If True, reject unknown fields and apply strict validation
        """
        self.strict_mode = strict_mode
        self.loader = ConfigurationLoader(strict_mode=strict_mode)
        logger.info("EntityDomainLoader initialized with strict_mode=%s", strict_mode)
    
    def load_from_files(self, domain_file: Union[str, Path], entities_file: Union[str, Path]) -> EntityDomainConfig:
        """
        Load entity domain configuration from separate domain and entity files.
        
        Args:
            domain_file: Path to domain.yaml file with base configuration
            entities_file: Path to entities.yaml file with entity definitions
            
        Returns:
            Validated EntityDomainConfig object
            
        Raises:
            ConfigurationFileError: If files cannot be read
            ConfigurationValidationError: If validation fails
        """
        logger.info("Loading entity domain configuration from separate files")
        logger.info("  Domain file: %s", domain_file)
        logger.info("  Entities file: %s", entities_file)
        
        # Load domain configuration
        domain_dict = self._load_yaml_file(domain_file, "domain")
        
        # Load entities configuration  
        entities_dict = self._load_yaml_file(entities_file, "entities")
        
        # Merge configurations
        merged_config = self._merge_configurations(domain_dict, entities_dict, 
                                                 str(domain_file), str(entities_file))
        
        # Validate merged configuration
        try:
            entity_domain_config = EntityDomainConfig(**merged_config)
            logger.info("Successfully loaded and validated entity domain configuration")
            
            # Log configuration summary
            self._log_entity_domain_summary(entity_domain_config)
            
            return entity_domain_config
            
        except ValidationError as e:
            error_msg = f"Entity domain configuration validation failed"
            logger.error(error_msg)
            
            # Create detailed error message from Pydantic validation errors
            validation_errors = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                error_detail = error['msg']
                error_type = error['type']
                
                validation_errors.append({
                    'field': field_path,
                    'error': error_detail,
                    'type': error_type,
                    'input': error.get('input')
                })
            
            raise ConfigurationValidationError(
                error_msg,
                source_file=f"{domain_file}, {entities_file}",
                validation_errors=validation_errors,
                suggestion=self._generate_entity_domain_suggestion(validation_errors)
            ) from e
    
    def load_from_strings(self, domain_yaml: str, entities_yaml: str) -> EntityDomainConfig:
        """
        Load entity domain configuration from YAML strings.
        
        Args:
            domain_yaml: Domain configuration as YAML string
            entities_yaml: Entities configuration as YAML string
            
        Returns:
            Validated EntityDomainConfig object
            
        Raises:
            ConfigurationValidationError: If validation fails
        """
        logger.info("Loading entity domain configuration from YAML strings")
        
        # Load domain configuration
        domain_dict = self._parse_yaml_string(domain_yaml, "domain")
        
        # Load entities configuration
        entities_dict = self._parse_yaml_string(entities_yaml, "entities")
        
        # Merge configurations
        merged_config = self._merge_configurations(domain_dict, entities_dict, "domain_string", "entities_string")
        
        # Validate merged configuration
        try:
            entity_domain_config = EntityDomainConfig(**merged_config)
            logger.info("Successfully loaded and validated entity domain configuration from strings")
            
            return entity_domain_config
            
        except ValidationError as e:
            error_msg = "Entity domain configuration validation failed"
            logger.error(error_msg)
            
            validation_errors = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                validation_errors.append({
                    'field': field_path,
                    'error': error['msg'],
                    'type': error['type'],
                    'input': error.get('input')
                })
            
            raise ConfigurationValidationError(
                error_msg,
                validation_errors=validation_errors,
                suggestion=self._generate_entity_domain_suggestion(validation_errors)
            ) from e
    
    def validate_entity_domain_config(self, config: EntityDomainConfig) -> bool:
        """
        Perform additional validation on entity domain configuration.
        
        Args:
            config: EntityDomainConfig object to validate
            
        Returns:
            True if validation passes
            
        Raises:
            ConfigurationValidationError: If validation fails
        """
        logger.info("Performing additional entity domain configuration validation")
        
        try:
            # Validate mixin references
            if config.mixins:
                mixin_names = {mixin.name for mixin in config.mixins}
                for entity in config.entities:
                    for mixin_name in entity.mixins:
                        if mixin_name not in mixin_names:
                            raise ConfigurationValidationError(
                                f"Entity '{entity.name}' references unknown mixin '{mixin_name}'",
                                suggestion=f"Ensure mixin '{mixin_name}' is defined in mixins list"
                            )
            
            # Validate domain relationships reference valid entities
            if config.relationships:
                entity_names = {entity.name for entity in config.entities}
                for domain_rel in config.relationships:
                    if domain_rel.from_entity not in entity_names:
                        raise ConfigurationValidationError(
                            f"Domain relationship '{domain_rel.name}' references unknown from_entity '{domain_rel.from_entity}'",
                            suggestion=f"Ensure entity '{domain_rel.from_entity}' is defined in entities list"
                        )
                    if domain_rel.to_entity not in entity_names:
                        raise ConfigurationValidationError(
                            f"Domain relationship '{domain_rel.name}' references unknown to_entity '{domain_rel.to_entity}'",
                            suggestion=f"Ensure entity '{domain_rel.to_entity}' is defined in entities list"
                        )
            
            # Validate SQLModel field configurations
            if config.sqlmodel_config:
                for entity in config.entities:
                    for field in entity.fields:
                        if field.sqlmodel_field:
                            # Basic validation of SQLModel field expressions
                            if not field.sqlmodel_field.startswith('Field('):
                                logger.warning(
                                    "SQLModel field expression '%s' in entity '%s' field '%s' should start with 'Field('",
                                    field.sqlmodel_field, entity.name, field.name
                                )
            
            logger.info("Entity domain configuration validation completed successfully")
            return True
            
        except Exception as e:
            logger.error("Entity domain configuration validation failed: %s", e)
            raise
    
    def _load_yaml_file(self, file_path: Union[str, Path], file_type: str) -> Dict[str, Any]:
        """Load YAML file and return parsed dictionary."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            error_msg = f"Configuration file not found: {file_path}"
            logger.error(error_msg)
            raise ConfigurationFileError(
                error_msg,
                file_path=str(file_path),
                suggestion=f"Create {file_type}.yaml file with required configuration"
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return self._parse_yaml_string(content, file_type)
                
        except IOError as e:
            error_msg = f"Failed to read {file_type} configuration file: {file_path}"
            logger.error(error_msg)
            raise ConfigurationFileError(
                error_msg,
                file_path=str(file_path),
                suggestion="Check file permissions and ensure file is readable"
            ) from e
    
    def _parse_yaml_string(self, yaml_content: str, source_type: str) -> Dict[str, Any]:
        """Parse YAML string and return dictionary."""
        if not yaml_content.strip():
            error_msg = f"Empty {source_type} configuration"
            logger.error(error_msg)
            raise ConfigurationValidationError(
                error_msg,
                suggestion=f"Add configuration content to {source_type}.yaml file"
            )
        
        try:
            # Safe YAML loading to prevent code injection
            parsed_data = yaml.safe_load(yaml_content)
            
            if parsed_data is None:
                error_msg = f"Empty or invalid {source_type} configuration"
                logger.error(error_msg)
                raise ConfigurationValidationError(
                    error_msg,
                    suggestion=f"Ensure {source_type}.yaml contains valid YAML content"
                )
            
            if not isinstance(parsed_data, dict):
                error_msg = f"{source_type.title()} configuration must be a dictionary, got {type(parsed_data).__name__}"
                logger.error(error_msg)
                raise ConfigurationValidationError(
                    error_msg,
                    suggestion="Ensure YAML root element is a mapping (key-value pairs)"
                )
            
            logger.info("Successfully parsed %s configuration (%d top-level keys)", source_type, len(parsed_data))
            return parsed_data
            
        except yaml.YAMLError as e:
            error_msg = f"YAML syntax error in {source_type} configuration"
            logger.error(error_msg)
            raise ConfigurationValidationError(
                error_msg,
                suggestion="Check YAML syntax - ensure proper indentation and quoting"
            ) from e
    
    def _merge_configurations(self, domain_dict: Dict[str, Any], entities_dict: Dict[str, Any], 
                            domain_source: str, entities_source: str) -> Dict[str, Any]:
        """Merge domain and entities configurations into unified configuration."""
        logger.info("Merging domain and entities configurations")
        
        # Start with domain configuration as base
        merged_config = domain_dict.copy()
        
        # Add entities from entities.yaml
        if 'entities' in entities_dict:
            merged_config['entities'] = entities_dict['entities']
            logger.info("Added %d entities from entities configuration", len(entities_dict['entities']))
        else:
            logger.warning("No entities found in entities configuration")
            merged_config['entities'] = []
        
        # Merge endpoints if present in entities.yaml
        if 'endpoints' in entities_dict:
            if 'endpoints' in merged_config:
                merged_config['endpoints'].extend(entities_dict['endpoints'])
            else:
                merged_config['endpoints'] = entities_dict['endpoints']
            logger.info("Merged endpoints from entities configuration")
        
        # Merge metadata if present in entities.yaml
        if 'metadata' in entities_dict:
            if 'metadata' in merged_config:
                merged_config['metadata'].update(entities_dict['metadata'])
            else:
                merged_config['metadata'] = entities_dict['metadata']
            logger.info("Merged metadata from entities configuration")
        
        logger.info("Configuration merging completed successfully")
        return merged_config
    
    def _log_entity_domain_summary(self, config: EntityDomainConfig) -> None:
        """Log a summary of the loaded entity domain configuration."""
        logger.info("Entity Domain Configuration Summary:")
        logger.info("  Domain: %s (%s)", config.name, config.plural)
        logger.info("  Package: %s", config.package)
        logger.info("  Base fields: %d", len(config.base_fields))
        logger.info("  Mixins: %d", len(config.mixins))
        for mixin in config.mixins:
            logger.info("    - %s (%d fields)", mixin.name, len(mixin.fields))
        logger.info("  Domain relationships: %d", len(config.relationships))
        logger.info("  Entities: %d", len(config.entities))
        for entity in config.entities:
            logger.info("    - %s (%d fields, %d relationships, mixins: %s)", 
                       entity.name, len(entity.fields), len(entity.relationships), 
                       ', '.join(entity.mixins) if entity.mixins else 'none')
        logger.info("  Endpoints: %d", len(config.endpoints))
        logger.info("  SQLModel config: %s", "configured" if config.sqlmodel_config else "default")
    
    def _generate_entity_domain_suggestion(self, validation_errors: list) -> str:
        """Generate helpful suggestion based on entity domain validation errors."""
        if not validation_errors:
            return "Check entity domain configuration format and required fields"
        
        error_types = {error['type'] for error in validation_errors}
        error_fields = [error['field'] for error in validation_errors]
        
        if 'missing' in error_types:
            missing_fields = [error['field'] for error in validation_errors if error['type'] == 'missing']
            if 'name' in missing_fields:
                return "Domain name is required in domain.yaml"
            return f"Required fields are missing: {', '.join(missing_fields)}"
        
        if any('entities' in field for field in error_fields):
            return "Check entities.yaml format - ensure entities list is properly defined"
        
        if any('mixins' in field for field in error_fields):
            return "Check mixin definitions in domain.yaml - ensure all referenced mixins are defined"
        
        if any('relationships' in field for field in error_fields):
            return "Check relationship configurations - ensure all referenced entities exist"
        
        return "Review entity domain configuration structure and field requirements"


def load_entity_domain_configuration(domain_file: Union[str, Path], entities_file: Union[str, Path], 
                                   strict_mode: bool = True) -> EntityDomainConfig:
    """
    Convenience function to load entity domain configuration from separate files.
    
    Args:
        domain_file: Path to domain.yaml file
        entities_file: Path to entities.yaml file  
        strict_mode: If True, apply strict validation
        
    Returns:
        Validated EntityDomainConfig object
    """
    loader = EntityDomainLoader(strict_mode=strict_mode)
    return loader.load_from_files(domain_file, entities_file)


def load_entity_domain_from_strings(domain_yaml: str, entities_yaml: str, 
                                  strict_mode: bool = True) -> EntityDomainConfig:
    """
    Convenience function to load entity domain configuration from YAML strings.
    
    Args:
        domain_yaml: Domain configuration as YAML string
        entities_yaml: Entities configuration as YAML string
        strict_mode: If True, apply strict validation
        
    Returns:
        Validated EntityDomainConfig object
    """
    loader = EntityDomainLoader(strict_mode=strict_mode)
    return loader.load_from_strings(domain_yaml, entities_yaml)


class UseCaseLoader:
    """
    Specialized loader for use case configurations with separate usecase and business rules files.
    
    Loads usecase.yaml and business-rules.yaml files separately and merges them into a unified
    UseCaseDomainConfig that supports business logic orchestration, dependency injection patterns,
    and comprehensive business rule validation.
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize use case loader.
        
        Args:
            strict_mode: If True, reject unknown fields and apply strict validation
        """
        self.strict_mode = strict_mode
        self.loader = ConfigurationLoader(strict_mode=strict_mode)
        logger.info("UseCaseLoader initialized with strict_mode=%s", strict_mode)
    
    def load_from_files(self, usecase_file: Union[str, Path], business_rules_file: Union[str, Path]) -> UseCaseDomainConfig:
        """
        Load use case domain configuration from separate usecase and business rules files.
        
        Args:
            usecase_file: Path to usecase.yaml file with business logic configuration
            business_rules_file: Path to business-rules.yaml file with validation rules
            
        Returns:
            Validated UseCaseDomainConfig object
            
        Raises:
            ConfigurationFileError: If files cannot be read
            ConfigurationValidationError: If validation fails
        """
        logger.info("Loading use case domain configuration from separate files")
        logger.info("  Use case file: %s", usecase_file)
        logger.info("  Business rules file: %s", business_rules_file)
        
        # Load use case configuration
        usecase_dict = self._load_yaml_file(usecase_file, "usecase")
        
        # Load business rules configuration
        business_rules_dict = self._load_yaml_file(business_rules_file, "business_rules")
        
        # Merge configurations
        merged_config = self._merge_configurations(usecase_dict, business_rules_dict, 
                                                 str(usecase_file), str(business_rules_file))
        
        # Validate merged configuration
        try:
            usecase_domain_config = UseCaseDomainConfig(**merged_config)
            logger.info("Successfully loaded and validated use case domain configuration")
            
            # Log configuration summary
            self._log_usecase_domain_summary(usecase_domain_config)
            
            return usecase_domain_config
            
        except ValidationError as e:
            error_msg = f"Use case domain configuration validation failed"
            logger.error(error_msg)
            
            # Create detailed error message from Pydantic validation errors
            validation_errors = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                error_detail = error['msg']
                error_type = error['type']
                
                validation_errors.append({
                    'field': field_path,
                    'error': error_detail,
                    'type': error_type,
                    'input': error.get('input')
                })
            
            raise ConfigurationValidationError(
                error_msg,
                source_file=f"{usecase_file}, {business_rules_file}",
                validation_errors=validation_errors,
                suggestion=self._generate_usecase_domain_suggestion(validation_errors)
            ) from e
    
    def load_from_strings(self, usecase_yaml: str, business_rules_yaml: str) -> UseCaseDomainConfig:
        """
        Load use case domain configuration from YAML strings.
        
        Args:
            usecase_yaml: Use case configuration as YAML string
            business_rules_yaml: Business rules configuration as YAML string
            
        Returns:
            Validated UseCaseDomainConfig object
            
        Raises:
            ConfigurationValidationError: If validation fails
        """
        logger.info("Loading use case domain configuration from YAML strings")
        
        # Load use case configuration
        usecase_dict = self._parse_yaml_string(usecase_yaml, "usecase")
        
        # Load business rules configuration
        business_rules_dict = self._parse_yaml_string(business_rules_yaml, "business_rules")
        
        # Merge configurations
        merged_config = self._merge_configurations(usecase_dict, business_rules_dict, "usecase_string", "business_rules_string")
        
        # Validate merged configuration
        try:
            usecase_domain_config = UseCaseDomainConfig(**merged_config)
            logger.info("Successfully loaded and validated use case domain configuration from strings")
            
            return usecase_domain_config
            
        except ValidationError as e:
            error_msg = "Use case domain configuration validation failed"
            logger.error(error_msg)
            
            validation_errors = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                validation_errors.append({
                    'field': field_path,
                    'error': error['msg'],
                    'type': error['type'],
                    'input': error.get('input')
                })
            
            raise ConfigurationValidationError(
                error_msg,
                validation_errors=validation_errors,
                suggestion=self._generate_usecase_domain_suggestion(validation_errors)
            ) from e
    
    def validate_usecase_domain_config(self, config: UseCaseDomainConfig) -> bool:
        """
        Perform additional validation on use case domain configuration.
        
        Args:
            config: UseCaseDomainConfig object to validate
            
        Returns:
            True if validation passes
            
        Raises:
            ConfigurationValidationError: If validation fails
        """
        logger.info("Performing additional use case domain configuration validation")
        
        try:
            # Validate business rule references in use case methods
            if config.usecase and config.business_rules:
                rule_names = {rule.name for rule in config.business_rules.rules}
                for method in config.usecase.methods:
                    for rule_name in method.business_rules:
                        if rule_name not in rule_names:
                            raise ConfigurationValidationError(
                                f"Use case method '{method.name}' references unknown business rule '{rule_name}'",
                                suggestion=f"Ensure business rule '{rule_name}' is defined in business rules list"
                            )
            
            # Validate dependency injection interface mappings
            if config.usecase and config.usecase.dependency_injection:
                di_config = config.usecase.dependency_injection
                for interface, implementation in di_config.interface_mappings.items():
                    if not interface.endswith('Service') and not interface.endswith('Repository'):
                        logger.warning(
                            f"Interface '{interface}' does not follow naming convention (should end with 'Service' or 'Repository')"
                        )
            
            # Validate service composition configuration
            if config.usecase and config.usecase.service_composition:
                sc_config = config.usecase.service_composition
                required_services = ['transaction_manager', 'event_publisher']
                for service in required_services:
                    if not getattr(sc_config, service):
                        logger.warning(f"Service composition missing recommended service: {service}")
            
            # Validate business rule validation groups
            if config.business_rules and config.business_rules.validation_groups:
                rule_names = {rule.name for rule in config.business_rules.rules}
                for group in config.business_rules.validation_groups:
                    for rule_name in group.rules:
                        if rule_name not in rule_names:
                            raise ConfigurationValidationError(
                                f"Validation group '{group.name}' references unknown rule '{rule_name}'",
                                suggestion=f"Ensure rule '{rule_name}' is defined in business rules list"
                            )
            
            logger.info("Use case domain configuration validation completed successfully")
            return True
            
        except Exception as e:
            logger.error("Use case domain configuration validation failed: %s", e)
            raise
    
    def _load_yaml_file(self, file_path: Union[str, Path], file_type: str) -> Dict[str, Any]:
        """Load YAML file and return parsed dictionary."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            error_msg = f"Configuration file not found: {file_path}"
            logger.error(error_msg)
            raise ConfigurationFileError(
                error_msg,
                file_path=str(file_path),
                suggestion=f"Create {file_type}.yaml file with required configuration"
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return self._parse_yaml_string(content, file_type)
                
        except IOError as e:
            error_msg = f"Failed to read {file_type} configuration file: {file_path}"
            logger.error(error_msg)
            raise ConfigurationFileError(
                error_msg,
                file_path=str(file_path),
                suggestion="Check file permissions and ensure file is readable"
            ) from e
    
    def _parse_yaml_string(self, yaml_content: str, source_type: str) -> Dict[str, Any]:
        """Parse YAML string and return dictionary."""
        if not yaml_content.strip():
            error_msg = f"Empty {source_type} configuration"
            logger.error(error_msg)
            raise ConfigurationValidationError(
                error_msg,
                suggestion=f"Add configuration content to {source_type}.yaml file"
            )
        
        try:
            # Safe YAML loading to prevent code injection
            parsed_data = yaml.safe_load(yaml_content)
            
            if parsed_data is None:
                error_msg = f"Empty or invalid {source_type} configuration"
                logger.error(error_msg)
                raise ConfigurationValidationError(
                    error_msg,
                    suggestion=f"Ensure {source_type}.yaml contains valid YAML content"
                )
            
            if not isinstance(parsed_data, dict):
                error_msg = f"{source_type.title()} configuration must be a dictionary, got {type(parsed_data).__name__}"
                logger.error(error_msg)
                raise ConfigurationValidationError(
                    error_msg,
                    suggestion="Ensure YAML root element is a mapping (key-value pairs)"
                )
            
            logger.info("Successfully parsed %s configuration (%d top-level keys)", source_type, len(parsed_data))
            return parsed_data
            
        except yaml.YAMLError as e:
            error_msg = f"YAML syntax error in {source_type} configuration"
            logger.error(error_msg)
            raise ConfigurationValidationError(
                error_msg,
                suggestion="Check YAML syntax - ensure proper indentation and quoting"
            ) from e
    
    def _merge_configurations(self, usecase_dict: Dict[str, Any], business_rules_dict: Dict[str, Any], 
                            usecase_source: str, business_rules_source: str) -> Dict[str, Any]:
        """Merge use case and business rules configurations into unified configuration."""
        logger.info("Merging use case and business rules configurations")
        
        # Start with use case configuration as base
        merged_config = usecase_dict.copy()
        
        # Add business rules from business-rules.yaml
        if 'rules' in business_rules_dict or 'validation_groups' in business_rules_dict or 'error_handling' in business_rules_dict:
            merged_config['business_rules'] = business_rules_dict
            logger.info("Added business rules configuration")
        else:
            logger.warning("No business rules found in business rules configuration")
        
        # Wrap usecase configuration if it's not already wrapped
        if 'usecase' not in merged_config and any(key in merged_config for key in ['methods', 'dependencies', 'service_composition']):
            # Move use case-specific keys into usecase wrapper
            usecase_config = {}
            usecase_keys = ['methods', 'dependencies', 'error_handling', 'service_composition', 'dependency_injection']
            
            for key in usecase_keys:
                if key in merged_config:
                    usecase_config[key] = merged_config.pop(key)
            
            # Ensure name is set for use case
            if 'name' not in usecase_config and 'name' in merged_config:
                usecase_config['name'] = merged_config['name']
            
            merged_config['usecase'] = usecase_config
            logger.info("Wrapped use case configuration")
        
        logger.info("Configuration merging completed successfully")
        return merged_config
    
    def _log_usecase_domain_summary(self, config: UseCaseDomainConfig) -> None:
        """Log a summary of the loaded use case domain configuration."""
        logger.info("Use Case Domain Configuration Summary:")
        logger.info("  Name: %s", config.name)
        logger.info("  Package: %s", config.package)
        
        if config.usecase:
            logger.info("  Use case: %s", config.usecase.name)
            logger.info("  Methods: %d", len(config.usecase.methods))
            for method in config.usecase.methods:
                logger.info("    - %s (transaction: %s, rules: %d)", 
                           method.name, method.transaction_boundary, len(method.business_rules))
            
            if hasattr(config.usecase.dependencies, 'services'):
                logger.info("  Service dependencies: %d", len(config.usecase.dependencies.services))
            elif isinstance(config.usecase.dependencies, list):
                logger.info("  Dependencies: %d", len(config.usecase.dependencies))
        
        if config.business_rules:
            logger.info("  Business rules: %d", len(config.business_rules.rules))
            for rule in config.business_rules.rules:
                logger.info("    - %s (%s, %s)", rule.name, rule.type, rule.severity)
            logger.info("  Validation groups: %d", len(config.business_rules.validation_groups))
        
        logger.info("  Entity dependencies: %d", len(config.entity_dependencies))
        logger.info("  Repository dependencies: %d", len(config.repository_dependencies))
        logger.info("  External dependencies: %d", len(config.external_dependencies))
    
    def _generate_usecase_domain_suggestion(self, validation_errors: list) -> str:
        """Generate helpful suggestion based on use case domain validation errors."""
        if not validation_errors:
            return "Check use case domain configuration format and required fields"
        
        error_types = {error['type'] for error in validation_errors}
        error_fields = [error['field'] for error in validation_errors]
        
        if 'missing' in error_types:
            missing_fields = [error['field'] for error in validation_errors if error['type'] == 'missing']
            if 'name' in missing_fields:
                return "Use case domain name is required in usecase.yaml"
            return f"Required fields are missing: {', '.join(missing_fields)}"
        
        if any('usecase' in field for field in error_fields):
            return "Check usecase.yaml format - ensure use case configuration is properly defined"
        
        if any('business_rules' in field for field in error_fields):
            return "Check business-rules.yaml format - ensure business rules are properly defined"
        
        if any('methods' in field for field in error_fields):
            return "Check use case methods configuration - ensure all method definitions are valid"
        
        if any('dependencies' in field for field in error_fields):
            return "Check dependency configurations - ensure all dependency references are valid"
        
        return "Review use case domain configuration structure and field requirements"


def load_usecase_domain_configuration(usecase_file: Union[str, Path], business_rules_file: Union[str, Path], 
                                    strict_mode: bool = True) -> UseCaseDomainConfig:
    """
    Convenience function to load use case domain configuration from separate files.
    
    Args:
        usecase_file: Path to usecase.yaml file
        business_rules_file: Path to business-rules.yaml file  
        strict_mode: If True, apply strict validation
        
    Returns:
        Validated UseCaseDomainConfig object
    """
    loader = UseCaseLoader(strict_mode=strict_mode)
    return loader.load_from_files(usecase_file, business_rules_file)


def load_usecase_domain_from_strings(usecase_yaml: str, business_rules_yaml: str, 
                                   strict_mode: bool = True) -> UseCaseDomainConfig:
    """
    Convenience function to load use case domain configuration from YAML strings.
    
    Args:
        usecase_yaml: Use case configuration as YAML string
        business_rules_yaml: Business rules configuration as YAML string
        strict_mode: If True, apply strict validation
        
    Returns:
        Validated UseCaseDomainConfig object
    """
    loader = UseCaseLoader(strict_mode=strict_mode)
    return loader.load_from_strings(usecase_yaml, business_rules_yaml)