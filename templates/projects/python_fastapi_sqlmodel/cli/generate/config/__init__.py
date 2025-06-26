"""
Configuration loading and validation module.

This module provides the core configuration loading functionality for the template generation system.
It includes type-safe YAML parsing, comprehensive validation, and structured error handling.

Main exports:
- Configuration: Core configuration model
- ConfigurationLoader: Main loading engine
- load_configuration: Convenience function for loading from file
- load_configuration_from_string: Convenience function for loading from string
- ConfigurationError: Base exception class
- ConfigurationValidationError: Validation-specific exception
- ConfigurationFileError: File-related exception
"""

from .models import (
    Configuration,
    DomainConfig,
    EntityConfig,
    FieldConfig,
    RelationshipConfig,
    EndpointConfig,
    FieldType,
    RelationshipType,
    HTTPMethod,
)

from .loader import (
    ConfigurationLoader,
    load_configuration,
    load_configuration_from_string,
)

from .exceptions import (
    ConfigurationError,
    ConfigurationValidationError,
    ConfigurationFileError,
    ConfigurationSchemaError,
)

__all__ = [
    # Models
    'Configuration',
    'DomainConfig', 
    'EntityConfig',
    'FieldConfig',
    'RelationshipConfig',
    'EndpointConfig',
    'FieldType',
    'RelationshipType',
    'HTTPMethod',
    
    # Loader
    'ConfigurationLoader',
    'load_configuration',
    'load_configuration_from_string',
    
    # Exceptions
    'ConfigurationError',
    'ConfigurationValidationError',
    'ConfigurationFileError',
    'ConfigurationSchemaError',
]