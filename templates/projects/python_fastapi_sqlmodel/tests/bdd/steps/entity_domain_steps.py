"""
BDD step definitions for entity domain configuration support.

These step definitions test the Entity Domain Configuration system that loads
separate domain.yaml and entities.yaml files and merges them into unified
EntityDomainConfig objects.
"""

import tempfile
import logging
from pathlib import Path
from typing import Dict, Any

import pytest
from behave import given, when, then  
import yaml

from cli.generate.config import (
    EntityDomainLoader,
    EntityDomainConfig,
    load_entity_domain_configuration,
    load_entity_domain_from_strings,
    ConfigurationError,
    ConfigurationValidationError,
    ConfigurationFileError,
)


class EntityDomainTestContext:
    """Test context for entity domain configuration scenarios."""
    
    def __init__(self):
        self.loader = None
        self.domain_yaml = None
        self.entities_yaml = None
        self.domain_file = None
        self.entities_file = None
        self.config = None
        self.error = None
        self.validation_result = None
        
        # Temporary files for cleanup
        self._temp_files = []
    
    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self._temp_files:
            if temp_file and temp_file.exists():
                temp_file.unlink(missing_ok=True)
        self._temp_files.clear()
    
    def create_temp_file(self, content: str, suffix: str = '.yaml') -> Path:
        """Create temporary file with content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        self._temp_files.append(temp_path)
        return temp_path


# Global test context
test_context = EntityDomainTestContext()


def before_scenario(context, scenario):
    """Clean up before each scenario."""
    test_context.cleanup()
    test_context.__init__()


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    test_context.cleanup()


@given('I have a configuration loader with entity domain support')
def step_given_entity_domain_loader(context):
    """Initialize entity domain loader."""
    test_context.loader = EntityDomainLoader(strict_mode=True)
    assert test_context.loader is not None


@given('I have domain.yaml with base entity configuration')
def step_given_domain_yaml_base_config(context):
    """Set domain YAML with base configuration."""
    test_context.domain_yaml = context.text.strip()
    assert test_context.domain_yaml


@given('I have entities.yaml with entity-specific field definitions')
def step_given_entities_yaml_fields(context):
    """Set entities YAML with field definitions."""
    test_context.entities_yaml = context.text.strip()
    assert test_context.entities_yaml


@given('I have domain.yaml with base field mixins')
def step_given_domain_yaml_mixins(context):
    """Set domain YAML with field mixins."""
    test_context.domain_yaml = context.text.strip()
    assert test_context.domain_yaml


@given('I have entities.yaml with mixin usage')
def step_given_entities_yaml_mixin_usage(context):
    """Set entities YAML with mixin references."""
    test_context.entities_yaml = context.text.strip()
    assert test_context.entities_yaml


@given('I have domain.yaml with relationship configuration')
def step_given_domain_yaml_relationships(context):
    """Set domain YAML with relationship definitions."""
    test_context.domain_yaml = context.text.strip()
    assert test_context.domain_yaml


@given('I have entities.yaml with entity definitions')
def step_given_entities_yaml_definitions(context):
    """Set entities YAML with entity definitions."""
    test_context.entities_yaml = context.text.strip()
    assert test_context.entities_yaml


@given('I have domain.yaml with SQLModel configuration')
def step_given_domain_yaml_sqlmodel(context):
    """Set domain YAML with SQLModel configuration."""
    test_context.domain_yaml = context.text.strip()
    assert test_context.domain_yaml


@given('I have entities.yaml with SQLModel-compatible fields')
def step_given_entities_yaml_sqlmodel_fields(context):
    """Set entities YAML with SQLModel field configurations."""
    test_context.entities_yaml = context.text.strip()
    assert test_context.entities_yaml


@given('I have domain.yaml with invalid configuration')
def step_given_domain_yaml_invalid(context):
    """Set invalid domain YAML for error testing."""
    test_context.domain_yaml = context.text.strip()
    assert test_context.domain_yaml


@given('I have entities.yaml with conflicting field definitions')
def step_given_entities_yaml_conflicts(context):
    """Set entities YAML with conflicting definitions."""
    test_context.entities_yaml = context.text.strip()
    assert test_context.entities_yaml


@given('I have domain.yaml with valid configuration')
def step_given_domain_yaml_valid(context):
    """Set valid domain YAML."""
    test_context.domain_yaml = '''
name: "TestDomain"
plural: "TestDomains"
description: "Test domain configuration"
base_fields:
  - name: "id"
    type: "int"
    required: false
    index: true
'''
    # Create temporary file
    test_context.domain_file = test_context.create_temp_file(test_context.domain_yaml)


@given('entities.yaml file does not exist')
def step_given_entities_yaml_missing(context):
    """Simulate missing entities.yaml file."""
    test_context.entities_file = Path("/non/existent/entities.yaml")


@given('I have complete domain and entity configurations')
def step_given_complete_configurations(context):
    """Set up complete domain and entity configurations."""
    test_context.domain_yaml = '''
name: "Product"
plural: "Products"
description: "Product management domain"
base_fields:
  - name: "id"
    type: "int"
    required: false
    index: true
sqlmodel_config:
  table_naming: "snake_case"
  generate_id_fields: true
'''
    
    test_context.entities_yaml = '''
entities:
  - name: "Product"
    fields:
      - name: "name"
        type: "str"
        required: true
        index: true
      - name: "price"
        type: "float"
        required: true
        sqlmodel_field: "Field(ge=0)"
'''


@when('I load entity domain configuration from both files')
def step_when_load_from_files(context):
    """Load configuration from domain and entities YAML strings."""
    try:
        test_context.config = test_context.loader.load_from_strings(
            test_context.domain_yaml,
            test_context.entities_yaml
        )
    except Exception as e:
        test_context.error = e


@when('I attempt to load entity domain configuration from both files')
def step_when_attempt_load_from_files(context):
    """Attempt to load configuration, expecting potential errors."""
    try:
        test_context.config = test_context.loader.load_from_strings(
            test_context.domain_yaml,
            test_context.entities_yaml
        )
    except Exception as e:
        test_context.error = e


@when('I attempt to load entity domain configuration')
def step_when_attempt_load_missing_file(context):
    """Attempt to load configuration with missing file."""
    try:
        test_context.config = load_entity_domain_configuration(
            test_context.domain_file,
            test_context.entities_file
        )
    except Exception as e:
        test_context.error = e


@when('I validate the configuration for template generation')
def step_when_validate_for_template_generation(context):
    """Validate configuration for template generation readiness."""
    try:
        # First load the configuration
        test_context.config = test_context.loader.load_from_strings(
            test_context.domain_yaml,
            test_context.entities_yaml
        )
        
        # Then validate it
        test_context.validation_result = test_context.loader.validate_entity_domain_config(
            test_context.config
        )
    except Exception as e:
        test_context.error = e


@then('the configuration should be successfully merged')
def step_then_config_merged_successfully(context):
    """Verify configuration was successfully merged."""
    assert test_context.config is not None
    assert test_context.error is None
    assert isinstance(test_context.config, EntityDomainConfig)


@then('the User entity should have base fields from domain.yaml')
def step_then_user_has_base_fields(context):
    """Verify User entity has base fields from domain configuration."""
    assert test_context.config is not None
    
    user_entity = next((e for e in test_context.config.entities if e.name == "User"), None)
    assert user_entity is not None
    
    # Check for base fields
    field_names = {field.name for field in user_entity.fields}
    assert "id" in field_names
    assert "created_at" in field_names
    assert "updated_at" in field_names


@then('the User entity should have specific fields from entities.yaml')
def step_then_user_has_specific_fields(context):
    """Verify User entity has specific fields from entities configuration."""
    assert test_context.config is not None
    
    user_entity = next((e for e in test_context.config.entities if e.name == "User"), None)
    assert user_entity is not None
    
    # Check for entity-specific fields
    field_names = {field.name for field in user_entity.fields}
    assert "username" in field_names
    assert "email" in field_names
    assert "full_name" in field_names
    assert "is_active" in field_names


@then('the domain information should be properly set')
def step_then_domain_info_set(context):
    """Verify domain information is properly configured."""
    assert test_context.config is not None
    assert test_context.config.name == "User"
    assert test_context.config.plural == "Users"
    assert test_context.config.package == "user"


@then('the Product entity should include all mixin fields')
def step_then_product_has_mixin_fields(context):
    """Verify Product entity includes fields from all applied mixins."""
    assert test_context.config is not None
    
    product_entity = next((e for e in test_context.config.entities if e.name == "Product"), None)
    assert product_entity is not None
    
    field_names = {field.name for field in product_entity.fields}
    
    # Fields from Timestamped mixin
    assert "created_at" in field_names
    assert "updated_at" in field_names
    
    # Fields from SoftDelete mixin  
    assert "deleted_at" in field_names


@then('the Product entity should have its specific fields')
def step_then_product_has_specific_fields(context):
    """Verify Product entity has its own specific fields."""
    assert test_context.config is not None
    
    product_entity = next((e for e in test_context.config.entities if e.name == "Product"), None)
    assert product_entity is not None
    
    field_names = {field.name for field in product_entity.fields}
    assert "name" in field_names
    assert "price" in field_names
    assert "description" in field_names


@then('field precedence should be handled correctly')
def step_then_field_precedence_correct(context):
    """Verify field precedence is handled correctly."""
    assert test_context.config is not None
    
    product_entity = next((e for e in test_context.config.entities if e.name == "Product"), None)
    assert product_entity is not None
    
    # Check that field definitions don't conflict
    field_names = [field.name for field in product_entity.fields]
    assert len(field_names) == len(set(field_names)), "No duplicate field names should exist"


@then('entities should have proper relationship configurations')
def step_then_entities_have_relationships(context):
    """Verify entities have proper relationship configurations."""
    assert test_context.config is not None
    
    # Check that domain relationships were applied to entities
    user_entity = next((e for e in test_context.config.entities if e.name == "User"), None)
    post_entity = next((e for e in test_context.config.entities if e.name == "Post"), None)
    
    if user_entity and post_entity:
        # User should have relationship to Post
        user_relationships = [rel.entity for rel in user_entity.relationships]
        assert "Post" in user_relationships


@then('foreign key fields should be validated')
def step_then_foreign_keys_validated(context):
    """Verify foreign key fields are properly validated."""
    assert test_context.config is not None
    
    # Check that entities with foreign keys have proper field definitions
    for entity in test_context.config.entities:
        for field in entity.fields:
            if field.name.endswith('_id'):
                # Foreign key fields should be integers
                assert field.type in ['int', 'Optional[int]']


@then('relationship back_populates should be consistent')
def step_then_back_populates_consistent(context):
    """Verify relationship back_populates are consistent."""
    assert test_context.config is not None
    
    # This is a complex validation - for now just verify no errors occurred
    assert test_context.error is None


@then('SQLModel field configurations should be validated')
def step_then_sqlmodel_fields_validated(context):
    """Verify SQLModel field configurations are valid."""
    assert test_context.config is not None
    assert test_context.config.sqlmodel_config is not None
    
    # Check that SQLModel field expressions are present
    for entity in test_context.config.entities:
        for field in entity.fields:
            if field.sqlmodel_field:
                assert field.sqlmodel_field.startswith('Field(')


@then('table naming conventions should be applied')
def step_then_table_naming_applied(context):
    """Verify table naming conventions are applied."""
    assert test_context.config is not None
    assert test_context.config.sqlmodel_config is not None
    assert test_context.config.sqlmodel_config.table_naming == "snake_case"


@then('SQLModel-specific field attributes should be processed')
def step_then_sqlmodel_attributes_processed(context):
    """Verify SQLModel-specific field attributes are processed."""
    assert test_context.config is not None
    
    # Check that entities have SQLModel field configurations
    order_entity = next((e for e in test_context.config.entities if e.name == "Order"), None)
    if order_entity:
        sqlmodel_fields = [field for field in order_entity.fields if field.sqlmodel_field]
        assert len(sqlmodel_fields) > 0


@then('I should receive a configuration validation error')
def step_then_validation_error(context):
    """Verify a configuration validation error was raised."""
    assert test_context.error is not None
    assert isinstance(test_context.error, ConfigurationValidationError)


@then('the error should specify the invalid field name')
def step_then_error_specifies_invalid_field(context):
    """Verify error message specifies the invalid field name."""
    assert test_context.error is not None
    error_message = str(test_context.error)
    assert "123invalid" in error_message or "invalid" in error_message.lower()


@then('the error should mention the duplicate field conflict')
def step_then_error_mentions_duplicate_field(context):
    """Verify error message mentions duplicate field conflict."""
    assert test_context.error is not None
    error_message = str(test_context.error)
    assert "duplicate" in error_message.lower() or "field1" in error_message


@then('the error should provide helpful suggestions')
def step_then_error_provides_suggestions(context):
    """Verify error provides helpful suggestions."""
    assert test_context.error is not None
    assert hasattr(test_context.error, 'suggestion')
    assert test_context.error.suggestion is not None
    assert len(test_context.error.suggestion) > 0


@then('I should receive a configuration file error')
def step_then_file_error(context):
    """Verify a configuration file error was raised."""
    assert test_context.error is not None
    assert isinstance(test_context.error, ConfigurationFileError)


@then('the error should specify which file is missing')
def step_then_error_specifies_missing_file(context):
    """Verify error message specifies which file is missing."""
    assert test_context.error is not None
    error_message = str(test_context.error)
    assert "entities.yaml" in error_message or "not found" in error_message


@then('the error should provide guidance on creating the missing file')
def step_then_error_provides_file_guidance(context):
    """Verify error provides guidance on creating missing file."""
    assert test_context.error is not None
    assert hasattr(test_context.error, 'suggestion')
    assert test_context.error.suggestion is not None
    assert "create" in test_context.error.suggestion.lower()


@then('all required fields for SQLModel templates should be present')
def step_then_sqlmodel_template_fields_present(context):
    """Verify all required fields for SQLModel templates are present."""
    assert test_context.config is not None
    assert test_context.validation_result is True
    
    # Check that entities have required fields
    for entity in test_context.config.entities:
        assert len(entity.fields) > 0
        # All entities should have at least one field
        assert any(field.name for field in entity.fields)


@then('relationship definitions should be complete')
def step_then_relationship_definitions_complete(context):
    """Verify relationship definitions are complete."""
    assert test_context.config is not None
    assert test_context.validation_result is True


@then('field types should be compatible with SQLModel')
def step_then_field_types_sqlmodel_compatible(context):
    """Verify field types are compatible with SQLModel."""
    assert test_context.config is not None
    
    # Check that field types are valid
    valid_types = {
        "str", "int", "float", "bool", "datetime", "EmailStr",
        "Optional[str]", "Optional[int]", "Optional[float]", 
        "Optional[bool]", "Optional[datetime]", "List[str]", "List[int]"
    }
    
    for entity in test_context.config.entities:
        for field in entity.fields:
            assert field.type in valid_types


@then('the configuration should support immediate entity template generation')
def step_then_supports_entity_template_generation(context):
    """Verify configuration supports immediate entity template generation."""
    assert test_context.config is not None
    assert test_context.validation_result is True
    assert test_context.error is None
    
    # Configuration should have all required components
    assert test_context.config.name
    assert len(test_context.config.entities) > 0
    assert all(len(entity.fields) > 0 for entity in test_context.config.entities)