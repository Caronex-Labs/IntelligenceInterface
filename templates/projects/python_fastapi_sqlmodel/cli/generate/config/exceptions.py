"""
Configuration-specific exceptions with detailed error information.

This module defines custom exceptions for configuration loading and validation,
providing structured error information for better debugging and user experience.
"""

from typing import Optional, List, Dict, Any


class ConfigurationError(Exception):
    """Base exception for configuration-related errors."""
    
    def __init__(
        self, 
        message: str, 
        source_file: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            source_file: Optional source file path
            suggestion: Optional suggestion for fixing the error
        """
        self.message = message
        self.source_file = source_file
        self.suggestion = suggestion
        
        # Build full error message
        full_message = message
        if source_file:
            full_message += f" (file: {source_file})"
        if suggestion:
            full_message += f"\nSuggestion: {suggestion}"
            
        super().__init__(full_message)


class ConfigurationFileError(ConfigurationError):
    """Exception raised when configuration file cannot be read."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        """
        Initialize configuration file error.
        
        Args:
            message: Error message
            file_path: Path to the problematic file
            suggestion: Optional suggestion for fixing the error
        """
        self.file_path = file_path
        super().__init__(message, source_file=file_path, suggestion=suggestion)


class ConfigurationValidationError(ConfigurationError):
    """Exception raised when configuration validation fails."""
    
    def __init__(
        self,
        message: str,
        source_file: Optional[str] = None,
        line_number: Optional[int] = None,
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        suggestion: Optional[str] = None
    ):
        """
        Initialize configuration validation error.
        
        Args:
            message: Error message
            source_file: Optional source file path
            line_number: Optional line number where error occurred
            validation_errors: Optional list of detailed validation errors
            suggestion: Optional suggestion for fixing the error
        """
        self.line_number = line_number
        self.validation_errors = validation_errors or []
        
        # Enhance message with line number and validation details
        enhanced_message = message
        if line_number:
            enhanced_message += f" (line {line_number})"
        
        if self.validation_errors:
            enhanced_message += "\nValidation errors:"
            for error in self.validation_errors:
                field = error.get('field', 'unknown')
                error_msg = error.get('error', 'validation failed')
                enhanced_message += f"\n  - {field}: {error_msg}"
        
        super().__init__(enhanced_message, source_file=source_file, suggestion=suggestion)
    
    def get_field_errors(self) -> Dict[str, str]:
        """
        Get validation errors grouped by field.
        
        Returns:
            Dictionary mapping field paths to error messages
        """
        field_errors = {}
        for error in self.validation_errors:
            field = error.get('field', 'unknown')
            error_msg = error.get('error', 'validation failed')
            field_errors[field] = error_msg
        return field_errors
    
    def has_field_error(self, field_path: str) -> bool:
        """
        Check if a specific field has validation errors.
        
        Args:
            field_path: Path to the field (e.g., "domain.name")
            
        Returns:
            True if field has validation errors
        """
        return field_path in self.get_field_errors()


class ConfigurationSchemaError(ConfigurationError):
    """Exception raised when configuration schema is invalid."""
    
    def __init__(
        self,
        message: str,
        schema_path: Optional[str] = None,
        source_file: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        """
        Initialize configuration schema error.
        
        Args:
            message: Error message
            schema_path: Path within the schema where error occurred
            source_file: Optional source file path
            suggestion: Optional suggestion for fixing the error
        """
        self.schema_path = schema_path
        
        enhanced_message = message
        if schema_path:
            enhanced_message += f" (schema path: {schema_path})"
            
        super().__init__(enhanced_message, source_file=source_file, suggestion=suggestion)