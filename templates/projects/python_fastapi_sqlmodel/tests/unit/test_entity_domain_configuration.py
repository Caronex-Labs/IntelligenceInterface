"""
Unit tests for entity domain configuration support.

These tests validate the EntityDomainLoader and EntityDomainConfig functionality,
including loading separate domain.yaml and entities.yaml files, configuration
merging, mixin application, and SQLModel-specific validation.
"""

import tempfile
import logging
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

from cli.generate.config import (
    EntityDomainLoader,
    EntityDomainConfig,
    load_entity_domain_configuration,
    load_entity_domain_from_strings,
    MixinConfig,
    DomainRelationshipConfig,
    SQLModelConfig,
    ConfigurationError,
    ConfigurationValidationError,
    ConfigurationFileError,
    FieldType,
    RelationshipType,
)


class TestEntityDomainConfig:
    """Test EntityDomainConfig model validation and defaults."""
    
    def test_basic_entity_domain_config(self):
        """Test basic entity domain configuration."""
        config_data = {
            "name": "User",
            "entities": [
                {
                    "name": "User",
                    "fields": [
                        {"name": "username", "type": "str", "required": True}
                    ]
                }
            ]
        }
        
        config = EntityDomainConfig(**config_data)
        assert config.name == "User"
        assert config.plural == "Users"  # Auto-generated
        assert config.package == "user"  # Auto-generated
        assert len(config.entities) == 1
        assert len(config.endpoints) == 5  # Default CRUD endpoints
    
    def test_base_fields_application(self):
        """Test that base fields are applied to all entities."""
        config_data = {
            "name": "Product",
            "base_fields": [
                {"name": "id", "type": "int", "required": False, "index": True},
                {"name": "created_at", "type": "datetime", "default": "datetime.utcnow"}
            ],
            "entities": [
                {
                    "name": "Product",
                    "fields": [
                        {"name": "name", "type": "str", "required": True}
                    ]
                }
            ]
        }
        
        config = EntityDomainConfig(**config_data)
        product_entity = config.entities[0]
        
        field_names = {field.name for field in product_entity.fields}
        assert "id" in field_names
        assert "created_at" in field_names
        assert "name" in field_names
    
    def test_mixin_application(self):
        """Test that mixins are applied to entities that reference them."""
        config_data = {
            "name": "Blog",
            "mixins": [
                {
                    "name": "Timestamped",
                    "fields": [
                        {"name": "created_at", "type": "datetime", "default": "datetime.utcnow"},
                        {"name": "updated_at", "type": "datetime", "default": "datetime.utcnow"}
                    ]
                }
            ],
            "entities": [
                {
                    "name": "Post",
                    "mixins": ["Timestamped"],
                    "fields": [
                        {"name": "title", "type": "str", "required": True}
                    ]
                }
            ]
        }
        
        config = EntityDomainConfig(**config_data)
        post_entity = config.entities[0]
        
        field_names = {field.name for field in post_entity.fields}
        assert "created_at" in field_names
        assert "updated_at" in field_names
        assert "title" in field_names
    
    def test_domain_relationships_application(self):
        """Test that domain relationships are applied to entities."""
        config_data = {
            "name": "Blog",
            "relationships": [
                {
                    "name": "user_posts",
                    "from_entity": "User",
                    "to_entity": "Post",
                    "type": "one_to_many",
                    "back_populates": "author"
                }
            ],
            "entities": [
                {
                    "name": "User",
                    "fields": [{"name": "username", "type": "str", "required": True}]
                },
                {
                    "name": "Post", 
                    "fields": [{"name": "title", "type": "str", "required": True}]
                }
            ]
        }
        
        config = EntityDomainConfig(**config_data)
        user_entity = next(e for e in config.entities if e.name == "User")
        
        assert len(user_entity.relationships) == 1
        assert user_entity.relationships[0].entity == "Post"
        assert user_entity.relationships[0].type == RelationshipType.ONE_TO_MANY


class TestMixinConfig:
    """Test MixinConfig model validation."""
    
    def test_valid_mixin_config(self):
        """Test valid mixin configuration."""
        mixin = MixinConfig(
            name="Timestamped",
            fields=[
                {"name": "created_at", "type": "datetime", "default": "datetime.utcnow"}
            ]
        )
        
        assert mixin.name == "Timestamped"
        assert len(mixin.fields) == 1
        assert mixin.fields[0].name == "created_at"
    
    def test_invalid_mixin_name(self):
        """Test invalid mixin name validation."""
        with pytest.raises(ValueError, match="not a valid Python identifier"):
            MixinConfig(
                name="123Invalid",
                fields=[{"name": "field1", "type": "str"}]
            )
        
        with pytest.raises(ValueError, match="should start with uppercase"):
            MixinConfig(
                name="invalidMixin",
                fields=[{"name": "field1", "type": "str"}]
            )


class TestSQLModelConfig:
    """Test SQLModelConfig model validation."""
    
    def test_valid_sqlmodel_config(self):
        """Test valid SQLModel configuration."""
        config = SQLModelConfig(
            table_naming="snake_case",
            field_naming="snake_case",
            generate_id_fields=True,
            timestamp_fields=["created_at", "updated_at"]
        )
        
        assert config.table_naming == "snake_case"
        assert config.field_naming == "snake_case"
        assert config.generate_id_fields is True
        assert len(config.timestamp_fields) == 2
    
    def test_invalid_naming_convention(self):
        """Test invalid naming convention validation."""
        with pytest.raises(ValueError, match="must be one of"):
            SQLModelConfig(table_naming="invalid_convention")


class TestEntityDomainLoader:
    """Test EntityDomainLoader functionality."""
    
    @pytest.fixture
    def loader(self):
        """Create entity domain loader instance."""
        return EntityDomainLoader(strict_mode=True)
    
    @pytest.fixture
    def sample_domain_yaml(self):
        """Sample domain.yaml content."""
        return """
name: "User"
plural: "Users"
description: "User management domain"
base_fields:
  - name: "id"
    type: "int"
    required: false
    index: true
  - name: "created_at"
    type: "datetime"
    default: "datetime.utcnow"
mixins:
  - name: "Timestamped"
    fields:
      - name: "created_at"
        type: "datetime"
        default: "datetime.utcnow"
      - name: "updated_at"
        type: "datetime"
        default: "datetime.utcnow"
sqlmodel_config:
  table_naming: "snake_case"
  generate_id_fields: true
"""
    
    @pytest.fixture
    def sample_entities_yaml(self):
        """Sample entities.yaml content.""" 
        return """
entities:
  - name: "User"
    description: "User entity"
    mixins: ["Timestamped"]
    fields:
      - name: "username"
        type: "str"
        required: true
        unique: true
        sqlmodel_field: "Field(unique=True)"
      - name: "email"
        type: "EmailStr"
        required: true
        unique: true
      - name: "full_name"
        type: "str"
        required: true
  - name: "Profile"
    description: "User profile"
    fields:
      - name: "bio"
        type: "Optional[str]"
        required: false
      - name: "user_id"
        type: "int"
        required: true
        sqlmodel_field: "Field(foreign_key='users.id')"
endpoints:
  - method: "POST"
    path: "/users/"
    operation: "create_user"
  - method: "GET"
    path: "/users/{id}"
    operation: "get_user"
metadata:
  entities_count: 2
"""
    
    def test_load_from_strings_success(self, loader, sample_domain_yaml, sample_entities_yaml):
        """Test successful loading from YAML strings."""
        config = loader.load_from_strings(sample_domain_yaml, sample_entities_yaml)
        
        assert config.name == "User"
        assert config.plural == "Users"
        assert len(config.entities) == 2
        assert len(config.mixins) == 1
        assert config.sqlmodel_config is not None
        
        # Check base fields were applied
        user_entity = next(e for e in config.entities if e.name == "User")
        field_names = {field.name for field in user_entity.fields}
        assert "id" in field_names
        assert "created_at" in field_names
        assert "username" in field_names
        
        # Check mixin fields were applied
        assert "updated_at" in field_names
        
        # Check endpoints were merged
        assert len(config.endpoints) == 2
        
        # Check metadata was merged
        assert config.metadata["entities_count"] == 2
    
    def test_load_from_files_success(self, loader, sample_domain_yaml, sample_entities_yaml):
        """Test successful loading from files."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as domain_file:
            domain_file.write(sample_domain_yaml)
            domain_path = Path(domain_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as entities_file:
            entities_file.write(sample_entities_yaml)
            entities_path = Path(entities_file.name)
        
        try:
            config = loader.load_from_files(domain_path, entities_path)
            
            assert config.name == "User"
            assert len(config.entities) == 2
            assert config.sqlmodel_config is not None
            
        finally:
            # Cleanup
            domain_path.unlink(missing_ok=True)
            entities_path.unlink(missing_ok=True)
    
    def test_load_missing_domain_file(self, loader):
        """Test error when domain file is missing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as entities_file:
            entities_file.write("entities: []")
            entities_path = Path(entities_file.name)
        
        non_existent_domain = Path("/non/existent/domain.yaml")
        
        try:
            with pytest.raises(ConfigurationFileError) as exc_info:
                loader.load_from_files(non_existent_domain, entities_path)
            
            assert "not found" in str(exc_info.value)
            assert str(non_existent_domain) in str(exc_info.value)
            
        finally:
            entities_path.unlink(missing_ok=True)
    
    def test_load_invalid_domain_yaml(self, loader):
        """Test error when domain YAML is invalid."""
        invalid_domain = """
name: 123  # Invalid - should be string
entities: []
"""
        
        valid_entities = """
entities:
  - name: "Test"
    fields:
      - name: "field1"
        type: "str"
"""
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_from_strings(invalid_domain, valid_entities)
        
        assert "validation failed" in str(exc_info.value)
    
    def test_load_missing_entities_in_entities_yaml(self, loader):
        """Test warning when entities.yaml has no entities."""
        domain_yaml = """
name: "Test"
"""
        
        entities_yaml = """
metadata:
  test: true
"""
        
        config = loader.load_from_strings(domain_yaml, entities_yaml)
        
        # Should still work but with empty entities list
        assert len(config.entities) == 0
    
    def test_validate_entity_domain_config_success(self, loader, sample_domain_yaml, sample_entities_yaml):
        """Test successful entity domain configuration validation."""
        config = loader.load_from_strings(sample_domain_yaml, sample_entities_yaml)
        
        result = loader.validate_entity_domain_config(config)
        assert result is True
    
    def test_validate_unknown_mixin_reference(self, loader):
        """Test validation error for unknown mixin reference."""
        domain_yaml = """
name: "Test"
mixins:
  - name: "KnownMixin"
    fields:
      - name: "field1"
        type: "str"
"""
        
        entities_yaml = """
entities:
  - name: "Test"
    mixins: ["UnknownMixin"]
    fields:
      - name: "field2"
        type: "str"
"""
        
        config = loader.load_from_strings(domain_yaml, entities_yaml)
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.validate_entity_domain_config(config)
        
        assert "unknown mixin" in str(exc_info.value)
        assert "UnknownMixin" in str(exc_info.value)
    
    def test_validate_unknown_entity_in_relationships(self, loader):
        """Test validation error for unknown entity in relationships."""
        domain_yaml = """
name: "Test"
relationships:
  - name: "test_rel"
    from_entity: "EntityA"
    to_entity: "UnknownEntity"
    type: "one_to_many"
"""
        
        entities_yaml = """
entities:
  - name: "EntityA"
    fields:
      - name: "field1"
        type: "str"
"""
        
        config = loader.load_from_strings(domain_yaml, entities_yaml)
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.validate_entity_domain_config(config)
        
        assert "unknown" in str(exc_info.value)
        assert "UnknownEntity" in str(exc_info.value)
    
    def test_convenience_functions(self, sample_domain_yaml, sample_entities_yaml):
        """Test convenience loading functions."""
        # Test load_entity_domain_from_strings
        config1 = load_entity_domain_from_strings(sample_domain_yaml, sample_entities_yaml)
        assert config1.name == "User"
        assert len(config1.entities) == 2
        
        # Test load_entity_domain_configuration with files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as domain_file:
            domain_file.write(sample_domain_yaml)
            domain_path = Path(domain_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as entities_file:
            entities_file.write(sample_entities_yaml)
            entities_path = Path(entities_file.name)
        
        try:
            config2 = load_entity_domain_configuration(domain_path, entities_path)
            assert config2.name == "User"
            assert len(config2.entities) == 2
            
            # Configs should be equivalent
            assert config1.name == config2.name
            assert len(config1.entities) == len(config2.entities)
            
        finally:
            domain_path.unlink(missing_ok=True)
            entities_path.unlink(missing_ok=True)


class TestEntityDomainConfigurationIntegration:
    """Integration tests using sample configuration files."""
    
    def test_load_user_domain_fixtures(self):
        """Test loading user domain fixture files."""
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "entity_domain"
        domain_file = fixtures_dir / "user_domain.yaml"
        entities_file = fixtures_dir / "user_entities.yaml"
        
        if domain_file.exists() and entities_file.exists():
            config = load_entity_domain_configuration(domain_file, entities_file)
            
            assert config.name == "User"
            assert config.plural == "Users"
            assert len(config.entities) == 2  # User and Profile
            assert len(config.mixins) >= 1  # At least Timestamped
            assert config.sqlmodel_config is not None
            
            # Check User entity
            user_entity = next(e for e in config.entities if e.name == "User")
            assert len(user_entity.fields) >= 3  # Should have base + specific fields
            
            # Check Profile entity
            profile_entity = next(e for e in config.entities if e.name == "Profile")
            assert len(profile_entity.fields) >= 2  # Should have mixin + specific fields
    
    def test_load_blog_domain_fixtures(self):
        """Test loading blog domain fixture files."""
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "entity_domain"
        domain_file = fixtures_dir / "blog_domain.yaml"
        entities_file = fixtures_dir / "blog_entities.yaml"
        
        if domain_file.exists() and entities_file.exists():
            config = load_entity_domain_configuration(domain_file, entities_file)
            
            assert config.name == "Blog"
            assert config.plural == "Blogs"
            assert len(config.entities) == 4  # User, Post, Comment, Tag
            assert len(config.mixins) >= 3  # Multiple mixins
            assert len(config.relationships) >= 3  # Multiple relationships
            
            # Check that relationships were applied
            user_entity = next(e for e in config.entities if e.name == "User")
            assert len(user_entity.relationships) >= 1
            
            # Check SQLModel field configurations
            post_entity = next(e for e in config.entities if e.name == "Post")
            sqlmodel_fields = [f for f in post_entity.fields if f.sqlmodel_field]
            assert len(sqlmodel_fields) >= 1


if __name__ == "__main__":
    pytest.main([__file__])