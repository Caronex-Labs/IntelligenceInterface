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

from .models import Configuration
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