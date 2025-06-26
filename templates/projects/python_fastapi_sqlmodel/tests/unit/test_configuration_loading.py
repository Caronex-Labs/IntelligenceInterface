"""
Unit tests for configuration loading functionality.

These tests provide comprehensive coverage of the configuration loading system,
including all edge cases and error conditions defined in the BDD scenarios.
"""

import tempfile
import logging
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

from cli.generate.config import (
    Configuration,
    ConfigurationLoader,
    load_configuration,
    load_configuration_from_string,
    ConfigurationError,
    ConfigurationValidationError,
    ConfigurationFileError,
    DomainConfig,
    EntityConfig,
    FieldConfig,
    FieldType,
)


class TestConfigurationModels:
    """Test Pydantic configuration models."""
    
    def test_field_config_validation(self):
        """Test field configuration validation."""
        # Valid field
        field = FieldConfig(
            name="user_name",
            type=FieldType.STR,
            required=True,
            index=True
        )
        assert field.name == "user_name"
        assert field.type == FieldType.STR
        assert field.required is True
        
    def test_field_config_invalid_name(self):
        """Test field name validation."""
        with pytest.raises(ValueError, match="not a valid Python identifier"):
            FieldConfig(name="123invalid", type=FieldType.STR)
        
        with pytest.raises(ValueError, match="should not start with underscore"):
            FieldConfig(name="_private", type=FieldType.STR)
    
    def test_entity_config_validation(self):
        """Test entity configuration validation."""
        fields = [
            FieldConfig(name="name", type=FieldType.STR, required=True),
            FieldConfig(name="email", type=FieldType.EMAIL, required=True),
        ]
        
        entity = EntityConfig(name="User", fields=fields)
        assert entity.name == "User"
        assert len(entity.fields) == 2
        assert entity.table_name == "user"  # Auto-generated
    
    def test_entity_config_invalid_name(self):
        """Test entity name validation."""
        fields = [FieldConfig(name="name", type=FieldType.STR)]
        
        with pytest.raises(ValueError, match="not a valid Python identifier"):
            EntityConfig(name="123Invalid", fields=fields)
            
        with pytest.raises(ValueError, match="should start with uppercase"):
            EntityConfig(name="invalidUser", fields=fields)
    
    def test_entity_config_duplicate_fields(self):
        """Test duplicate field name validation."""
        fields = [
            FieldConfig(name="name", type=FieldType.STR),
            FieldConfig(name="name", type=FieldType.EMAIL),  # Duplicate
        ]
        
        with pytest.raises(ValueError, match="duplicate field names"):
            EntityConfig(name="User", fields=fields)
    
    def test_domain_config_validation(self):
        """Test domain configuration validation."""
        domain = DomainConfig(name="User")
        assert domain.name == "User"
        assert domain.plural == "Users"  # Auto-generated
        assert domain.package == "user"  # Auto-generated
    
    def test_domain_config_custom_values(self):
        """Test domain configuration with custom values."""
        domain = DomainConfig(
            name="Category",
            plural="Categories",
            package="cat"
        )
        assert domain.plural == "Categories"
        assert domain.package == "cat"
    
    def test_configuration_validation(self):
        """Test full configuration validation."""
        config_data = {
            "domain": {"name": "User", "plural": "Users"},
            "entities": [
                {
                    "name": "User",
                    "fields": [
                        {"name": "name", "type": "str", "required": True},
                        {"name": "email", "type": "EmailStr", "required": True},
                    ]
                }
            ]
        }
        
        config = Configuration(**config_data)
        assert config.domain.name == "User"
        assert len(config.entities) == 1
        assert len(config.endpoints) == 5  # Default CRUD endpoints


class TestConfigurationLoader:
    """Test configuration loader functionality."""
    
    @pytest.fixture
    def loader(self):
        """Create configuration loader instance."""
        return ConfigurationLoader(strict_mode=True)
    
    @pytest.fixture
    def valid_yaml_config(self):
        """Valid YAML configuration for testing."""
        return """
domain:
  name: "User"
  plural: "Users"
entities:
  - name: "User"
    fields:
      - name: "name"
        type: "str"
        required: true
        index: true
      - name: "email"
        type: "EmailStr"
        required: true
        unique: true
      - name: "created_at"
        type: "datetime"
        default: "datetime.utcnow"
"""
    
    @pytest.fixture
    def temp_config_file(self, valid_yaml_config):
        """Create temporary configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(valid_yaml_config)
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        temp_path.unlink(missing_ok=True)
    
    def test_load_from_string_success(self, loader, valid_yaml_config):
        """Test successful loading from YAML string."""
        config = loader.load_from_string(valid_yaml_config)
        
        assert config.domain.name == "User"
        assert config.domain.plural == "Users"
        assert len(config.entities) == 1
        assert config.entities[0].name == "User"
        assert len(config.entities[0].fields) == 3
    
    def test_load_from_file_success(self, loader, temp_config_file):
        """Test successful loading from file."""
        config = loader.load_from_file(temp_config_file)
        
        assert config.domain.name == "User"
        assert len(config.entities) == 1
    
    def test_load_from_file_not_found(self, loader):
        """Test loading from non-existent file."""
        non_existent_path = Path("/non/existent/config.yaml")
        
        with pytest.raises(ConfigurationFileError) as exc_info:
            loader.load_from_file(non_existent_path)
        
        assert "not found" in str(exc_info.value)
        assert str(non_existent_path) in str(exc_info.value)
        assert exc_info.value.suggestion is not None
    
    def test_load_invalid_yaml_syntax(self, loader):
        """Test loading invalid YAML syntax."""
        invalid_yaml = """
domain:
  name: "User"
  plural: "Users"
entities:
  - name: "User"
    fields:
      - name: "email"
        type: "EmailStr
        required: true  # Missing closing quote above
"""
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_from_string(invalid_yaml)
        
        assert "YAML syntax" in str(exc_info.value)
        assert exc_info.value.suggestion is not None
    
    def test_load_missing_required_fields(self, loader):
        """Test loading configuration with missing required fields."""
        missing_required = """
domain:
  plural: "Users"  # Missing required 'name' field
entities: []
"""
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_from_string(missing_required)
        
        assert exc_info.value.validation_errors is not None
        assert len(exc_info.value.validation_errors) > 0
    
    def test_load_invalid_field_types(self, loader):
        """Test loading configuration with invalid field types."""
        invalid_types = """
domain:
  name: 123  # Should be string
  plural: "Users"
entities:
  - name: "User"
    fields:
      - name: "age"
        type: "invalid_type"
        required: "yes"  # Should be boolean
"""
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_from_string(invalid_types)
        
        error_fields = exc_info.value.get_field_errors()
        assert len(error_fields) > 0
    
    def test_load_empty_content(self, loader):
        """Test loading empty YAML content."""
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_from_string("")
        
        assert "Empty" in str(exc_info.value)
    
    def test_load_non_dict_yaml(self, loader):
        """Test loading non-dictionary YAML."""
        non_dict_yaml = """
- item1
- item2
- item3
"""
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_from_string(non_dict_yaml)
        
        assert "dictionary" in str(exc_info.value)
    
    def test_validate_configuration(self, loader, valid_yaml_config):
        """Test additional configuration validation."""
        config = loader.load_from_string(valid_yaml_config)
        
        # Should pass validation
        assert loader.validate_configuration(config) is True
    
    def test_convenience_functions(self, temp_config_file, valid_yaml_config):
        """Test convenience loading functions."""
        # Test load_configuration
        config1 = load_configuration(temp_config_file)
        assert config1.domain.name == "User"
        
        # Test load_configuration_from_string
        config2 = load_configuration_from_string(valid_yaml_config)
        assert config2.domain.name == "User"
        
        # Configs should be equivalent
        assert config1.domain.name == config2.domain.name


class TestConfigurationLogging:
    """Test configuration loading logging."""
    
    @pytest.fixture
    def loader(self):
        """Create configuration loader with logging."""
        return ConfigurationLoader(strict_mode=True)
    
    @pytest.fixture
    def log_capture(self, caplog):
        """Capture logs for testing."""
        caplog.set_level(logging.INFO, logger="cli.generate.config")
        return caplog
    
    def test_successful_loading_logs(self, loader, log_capture):
        """Test logging for successful configuration loading."""
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
        
        config = loader.load_from_string(valid_config)
        
        # Check that info logs were recorded
        info_logs = [record for record in log_capture.records if record.levelname == "INFO"]
        assert len(info_logs) > 0
        
        # Check for specific log messages
        log_messages = [record.message for record in info_logs]
        assert any("Loading configuration" in msg for msg in log_messages)
        assert any("Successfully loaded" in msg for msg in log_messages)
    
    def test_validation_error_logs(self, loader, log_capture):
        """Test logging for validation errors."""
        invalid_config = """
domain:
  plural: "Products"  # Missing required name
entities: []
"""
        
        with pytest.raises(ConfigurationValidationError):
            loader.load_from_string(invalid_config)
        
        # Check that error logs were recorded
        error_logs = [record for record in log_capture.records if record.levelname == "ERROR"]
        assert len(error_logs) > 0
        
        # Check for specific error log content
        log_messages = [record.message for record in error_logs]
        assert any("validation failed" in msg for msg in log_messages)


class TestConfigurationRelationships:
    """Test configuration relationship validation."""
    
    def test_valid_relationships(self):
        """Test configuration with valid entity relationships."""
        config_data = {
            "domain": {"name": "Blog", "plural": "Blogs"},
            "entities": [
                {
                    "name": "User",
                    "fields": [
                        {"name": "name", "type": "str", "required": True},
                        {"name": "email", "type": "EmailStr", "required": True},
                    ],
                    "relationships": [
                        {"entity": "Post", "type": "one_to_many", "back_populates": "user"}
                    ]
                },
                {
                    "name": "Post",
                    "fields": [
                        {"name": "title", "type": "str", "required": True},
                        {"name": "content", "type": "str", "required": True},
                        {"name": "user_id", "type": "int", "required": True},
                    ],
                    "relationships": [
                        {"entity": "User", "type": "many_to_one", "back_populates": "posts"}
                    ]
                }
            ]
        }
        
        config = Configuration(**config_data)
        loader = ConfigurationLoader()
        
        # Should pass validation including relationship validation
        assert loader.validate_configuration(config) is True
    
    def test_invalid_relationship_reference(self):
        """Test configuration with invalid relationship reference."""
        config_data = {
            "domain": {"name": "Blog"},
            "entities": [
                {
                    "name": "User",
                    "fields": [{"name": "name", "type": "str", "required": True}],
                    "relationships": [
                        {"entity": "NonExistentEntity", "type": "one_to_many"}
                    ]
                }
            ]
        }
        
        config = Configuration(**config_data)
        loader = ConfigurationLoader()
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.validate_configuration(config)
        
        assert "unknown entity" in str(exc_info.value)
        assert "NonExistentEntity" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])