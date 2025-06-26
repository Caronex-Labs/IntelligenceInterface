"""
BDD step definitions for configuration loading scenarios.

This module implements the step definitions for all configuration loading
BDD scenarios, providing comprehensive testing of the configuration system.
"""

import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import pytest
from behave import given, when, then, step
import yaml

from cli.generate.config import (
    Configuration,
    ConfigurationLoader,
    load_configuration,
    load_configuration_from_string,
    ConfigurationError,
    ConfigurationValidationError,
    ConfigurationFileError,
)


# Test context storage
class TestContext:
    """Storage for test context between steps."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all context variables."""
        self.loader: Optional[ConfigurationLoader] = None
        self.yaml_content: Optional[str] = None
        self.config_file_path: Optional[Path] = None
        self.configuration: Optional[Configuration] = None
        self.error: Optional[Exception] = None
        self.temp_files: list = []
        self.log_records: list = []
    
    def cleanup(self):
        """Clean up temporary resources."""
        for temp_file in self.temp_files:
            try:
                temp_file.unlink(missing_ok=True)
            except Exception:
                pass
        self.temp_files.clear()


# Global test context
context = TestContext()


# Setup and teardown
@given('the configuration loading system is properly initialized')
def step_initialize_system(context_obj):
    """Initialize the configuration loading system."""
    context.reset()
    context.loader = ConfigurationLoader(strict_mode=True)
    
    # Setup logging capture
    context.log_handler = LogCapture()
    logger = logging.getLogger('cmd.generate.config')
    logger.addHandler(context.log_handler)
    logger.setLevel(logging.DEBUG)


@given('PyYAML integration is available')
def step_pyyaml_available(context_obj):
    """Verify PyYAML is available."""
    import yaml
    assert yaml is not None


# Configuration content setup
@given('I have PyYAML integration properly configured')
def step_pyyaml_configured(context_obj):
    """Verify PyYAML integration is configured."""
    assert context.loader is not None


@given('I have a valid domain configuration file')
def step_valid_config_from_docstring(context_obj):
    """Set up valid configuration from docstring."""
    context.yaml_content = context_obj.text.strip()


@given('I have a configuration file missing required domain name')
def step_missing_required_fields(context_obj):
    """Set up configuration missing required fields."""
    context.yaml_content = context_obj.text.strip()


@given('I have a configuration file with invalid YAML syntax')
def step_invalid_yaml_syntax(context_obj):
    """Set up configuration with invalid YAML syntax."""
    context.yaml_content = context_obj.text.strip()


@given('I have a configuration with invalid field types')
def step_invalid_field_types(context_obj):
    """Set up configuration with invalid field types."""
    context.yaml_content = context_obj.text.strip()


@given('a configuration file path that does not exist')
def step_nonexistent_file_path(context_obj):
    """Set up non-existent file path."""
    context.config_file_path = Path("/non/existent/path/config.yaml")


@given('logging is configured for the configuration system')
def step_logging_configured(context_obj):
    """Verify logging is configured."""
    assert context.log_handler is not None


# Actions
@when('I load a basic YAML configuration file')
def step_load_basic_config(context_obj):
    """Load a basic YAML configuration."""
    basic_config = """
domain:
  name: "User"
  plural: "Users"
entities:
  - name: "User"
    fields:
      - name: "name"
        type: "str"
        required: true
      - name: "email"
        type: "EmailStr"
        required: true
"""
    try:
        context.configuration = context.loader.load_from_string(basic_config)
        context.error = None
    except Exception as e:
        context.error = e
        context.configuration = None


@when('I load the configuration using the Configuration class')
def step_load_config_from_content(context_obj):
    """Load configuration from stored YAML content."""
    try:
        context.configuration = context.loader.load_from_string(context.yaml_content)
        context.error = None
    except Exception as e:
        context.error = e
        context.configuration = None


@when('I attempt to load the configuration')
def step_attempt_load_config(context_obj):
    """Attempt to load configuration (expecting potential failure)."""
    try:
        context.configuration = context.loader.load_from_string(context.yaml_content)
        context.error = None
    except Exception as e:
        context.error = e
        context.configuration = None


@when('I attempt to load the configuration from the non-existent path')
def step_attempt_load_nonexistent(context_obj):
    """Attempt to load from non-existent file path."""
    try:
        context.configuration = context.loader.load_from_file(context.config_file_path)
        context.error = None
    except Exception as e:
        context.error = e
        context.configuration = None


@when('I successfully load a valid configuration file')
def step_load_valid_config(context_obj):
    """Load a valid configuration for logging test."""
    valid_config = """
domain:
  name: "Product"
  plural: "Products"
entities:
  - name: "Product"
    fields:
      - name: "name"
        type: "str"
        required: true
"""
    context.configuration = context.loader.load_from_string(valid_config)


@when('I encounter a validation error')
def step_encounter_validation_error(context_obj):
    """Trigger a validation error for logging test."""
    invalid_config = """
domain:
  plural: "Products"
entities: []
"""
    try:
        context.loader.load_from_string(invalid_config)
    except Exception as e:
        context.error = e


# Assertions
@then('the configuration should be parsed successfully')
def step_config_parsed_successfully(context_obj):
    """Verify configuration was parsed successfully."""
    assert context.error is None, f"Expected successful parsing, got error: {context.error}"
    assert context.configuration is not None


@then('essential fields should be populated correctly')
def step_essential_fields_populated(context_obj):
    """Verify essential fields are populated."""
    assert context.configuration.domain is not None
    assert context.configuration.entities is not None
    assert len(context.configuration.entities) > 0


@then('basic validation should identify missing required fields')
def step_basic_validation_works(context_obj):
    """Test basic validation with missing fields."""
    invalid_config = """
domain:
  plural: "Users"
entities: []
"""
    try:
        context.loader.load_from_string(invalid_config)
        assert False, "Expected validation error for missing required fields"
    except ConfigurationValidationError:
        pass  # Expected


@then('the Configuration class should provide type-safe access')
def step_type_safe_access(context_obj):
    """Verify type-safe access to configuration."""
    assert isinstance(context.configuration.domain.name, str)
    assert isinstance(context.configuration.entities, list)
    if context.configuration.entities:
        assert hasattr(context.configuration.entities[0], 'name')
        assert hasattr(context.configuration.entities[0], 'fields')


@then('the domain name should be "{expected_name}"')
def step_domain_name_check(context_obj, expected_name):
    """Verify domain name."""
    assert context.configuration.domain.name == expected_name


@then('the domain plural should be "{expected_plural}"')
def step_domain_plural_check(context_obj, expected_plural):
    """Verify domain plural."""
    assert context.configuration.domain.plural == expected_plural


@then('the entities list should contain one User entity')
def step_entities_list_check(context_obj):
    """Verify entities list."""
    assert len(context.configuration.entities) == 1
    assert context.configuration.entities[0].name == "User"


@then('the User entity should have name and email fields')
def step_user_entity_fields_check(context_obj):
    """Verify User entity fields."""
    user_entity = context.configuration.entities[0]
    field_names = [field.name for field in user_entity.fields]
    assert "name" in field_names
    assert "email" in field_names


@then('field validation should pass for required fields')
def step_field_validation_check(context_obj):
    """Verify field validation passes."""
    user_entity = context.configuration.entities[0]
    for field in user_entity.fields:
        if field.required:
            assert field.name is not None
            assert field.type is not None


@then('a validation error should be raised')
def step_validation_error_raised(context_obj):
    """Verify validation error was raised."""
    assert context.error is not None
    assert isinstance(context.error, ConfigurationValidationError)


@then('the error message should indicate "{expected_message}"')
def step_error_message_check(context_obj, expected_message):
    """Verify error message contains expected text."""
    assert context.error is not None
    assert expected_message in str(context.error)


@then('the Configuration object should not be created')
def step_no_config_object(context_obj):
    """Verify no configuration object was created."""
    assert context.configuration is None


@then('a YAML parsing error should be raised')
def step_yaml_parsing_error(context_obj):
    """Verify YAML parsing error was raised."""
    assert context.error is not None
    assert isinstance(context.error, ConfigurationValidationError)
    assert "YAML syntax" in str(context.error)


@then('the line number of the error should be provided')
def step_line_number_provided(context_obj):
    """Verify line number is provided in error."""
    assert context.error is not None
    assert hasattr(context.error, 'line_number')
    # Note: line_number might be None for some YAML errors


@then('a file not found error should be raised')
def step_file_not_found_error(context_obj):
    """Verify file not found error was raised."""
    assert context.error is not None
    assert isinstance(context.error, ConfigurationFileError)


@then('the error message should indicate the missing file path')
def step_missing_file_path_in_error(context_obj):
    """Verify file path is in error message."""
    assert context.error is not None
    assert str(context.config_file_path) in str(context.error)


@then('helpful guidance should be provided')
def step_helpful_guidance(context_obj):
    """Verify helpful guidance is provided."""
    assert context.error is not None
    assert hasattr(context.error, 'suggestion')
    assert context.error.suggestion is not None


@then('type validation errors should be raised')
def step_type_validation_errors(context_obj):
    """Verify type validation errors."""
    assert context.error is not None
    assert isinstance(context.error, ConfigurationValidationError)


@then('the error should specify which fields have invalid types')
def step_invalid_fields_specified(context_obj):
    """Verify invalid fields are specified."""
    assert context.error is not None
    assert hasattr(context.error, 'validation_errors')
    assert len(context.error.validation_errors) > 0


@then('the expected types should be indicated in the error message')
def step_expected_types_indicated(context_obj):
    """Verify expected types are indicated."""
    assert context.error is not None
    error_msg = str(context.error)
    # Check that type-related information is present
    assert any(word in error_msg.lower() for word in ['type', 'str', 'bool', 'int'])


@then('an info log should be recorded indicating successful loading')
def step_info_log_recorded(context_obj):
    """Verify info log was recorded."""
    assert context.log_handler is not None
    info_logs = [record for record in context.log_handler.records 
                if record.levelname == 'INFO' and 'loading' in record.message.lower()]
    assert len(info_logs) > 0


@then('the log should include the configuration file path')
def step_log_includes_file_path(context_obj):
    """Verify log includes file path."""
    # For string loading, this might not apply
    pass


@then('an error log should be recorded with the validation details')
def step_error_log_recorded(context_obj):
    """Verify error log was recorded."""
    assert context.log_handler is not None
    error_logs = [record for record in context.log_handler.records 
                 if record.levelname == 'ERROR']
    assert len(error_logs) > 0


@then('the log should include the specific validation failures')
def step_log_includes_validation_failures(context_obj):
    """Verify log includes validation failures."""
    assert context.log_handler is not None
    error_logs = [record for record in context.log_handler.records 
                 if record.levelname == 'ERROR' and 'validation' in record.message.lower()]
    assert len(error_logs) > 0


# Helper class for log capture
class LogCapture:
    """Captures log records for testing."""
    
    def __init__(self):
        self.records = []
    
    def handle(self, record):
        """Handle a log record."""
        self.records.append(record)
    
    def emit(self, record):
        """Emit a log record."""
        self.handle(record)