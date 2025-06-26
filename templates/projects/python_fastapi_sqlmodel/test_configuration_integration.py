#!/usr/bin/env python3
"""Configuration Merging Integration Test Script.

This script tests the integration between the enhanced ConfigurationMerger and
our entity templates, validating that hierarchical configuration merging works
correctly with the co-location architecture.
"""

import sys
import yaml
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

# Add the domain module to path for testing
sys.path.append(str(Path(__file__).parent / "app" / "domain"))

try:
    from configuration_merger import ConfigurationMerger, MergeResult
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the template root directory")
    sys.exit(1)


class ConfigurationIntegrationTester:
    """Tests configuration merging integration with entity templates."""
    
    def __init__(self):
        """Initialize the integration tester."""
        self.temp_dir = None
        self.merger = ConfigurationMerger()
        self.test_results = []
    
    def setup_test_environment(self) -> Path:
        """Create temporary test environment with sample configurations."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="config_integration_test_"))
        
        # Create domain configuration
        domain_config = {
            "domain": {
                "name": "user",
                "description": "User domain with hexagonal architecture",
                "package": "app.domain.user",
                "version": "1.0.0"
            },
            "entity": {
                "base_class": "BaseEntity",
                "abstract_base": True,
                "mixins": [
                    {
                        "name": "UUIDMixin",
                        "description": "UUID primary key generation",
                        "enabled": True
                    },
                    {
                        "name": "TimestampMixin",
                        "description": "Created/updated timestamp fields",
                        "enabled": True,
                        "fields": ["created_at", "updated_at"]
                    }
                ]
            },
            "primary_key": {
                "type": "UUID",
                "field_name": "id",
                "auto_generate": True,
                "default_factory": "uuid4"
            },
            "field_types": {
                "string": {
                    "python_type": "str",
                    "sqlmodel_type": "str"
                },
                "email": {
                    "python_type": "EmailStr",
                    "sqlmodel_type": "str",
                    "unique": True
                }
            },
            "timestamps": {
                "created_at": {
                    "type": "datetime",
                    "default_factory": "datetime.utcnow"
                },
                "updated_at": {
                    "type": "datetime", 
                    "default_factory": "datetime.utcnow"
                }
            }
        }
        
        # Create entity-specific configuration
        entity_config = {
            "entities": [
                {
                    "name": "User",
                    "description": "User business entity",
                    "table_name": "users",
                    "mixins": ["UUIDMixin", "TimestampMixin"],
                    "fields": [
                        {
                            "name": "name",
                            "type": "string",
                            "description": "User full name",
                            "required": True,
                            "validation": {
                                "min_length": 2,
                                "max_length": 100
                            }
                        },
                        {
                            "name": "email",
                            "type": "email",
                            "description": "User email address",
                            "required": True,
                            "unique": True
                        }
                    ],
                    "relationships": [
                        {
                            "name": "posts",
                            "type": "one_to_many",
                            "target_entity": "Post",
                            "back_populates": "user"
                        }
                    ]
                }
            ],
            "template_context": {
                "domain_name": "user",
                "features": {
                    "enable_soft_delete": False,
                    "enable_audit_log": True
                }
            }
        }
        
        # Write configuration files
        domain_path = self.temp_dir / "domain.yaml"
        entity_path = self.temp_dir / "entities.yaml"
        
        with domain_path.open('w') as f:
            yaml.dump(domain_config, f, default_flow_style=False)
        
        with entity_path.open('w') as f:
            yaml.dump(entity_config, f, default_flow_style=False)
        
        return self.temp_dir
    
    def test_basic_configuration_merging(self) -> bool:
        """Test basic domain.yaml + entities.yaml merging."""
        print("🔍 Testing basic configuration merging...")
        
        try:
            domain_path = self.temp_dir / "domain.yaml"
            entity_path = self.temp_dir / "entities.yaml"
            
            # Test the merge operation
            merged_config = self.merger.merge_domain_configurations(
                domain_path, entity_path
            )
            
            # Validate merged configuration structure
            required_sections = ["domain", "entities", "field_types", "timestamps"]
            for section in required_sections:
                if section not in merged_config:
                    print(f"❌ Missing required section: {section}")
                    return False
            
            # Validate that entities inherit from domain configuration
            entities = merged_config.get("entities", [])
            if not entities:
                print("❌ No entities found in merged configuration")
                return False
            
            user_entity = entities[0]
            if user_entity.get("name") != "User":
                print("❌ User entity not found or incorrect")
                return False
            
            # Validate field_types were inherited
            field_types = merged_config.get("field_types", {})
            if "string" not in field_types or "email" not in field_types:
                print("❌ Field types not properly inherited")
                return False
            
            print("✅ Basic configuration merging successful")
            return True
            
        except Exception as e:
            print(f"❌ Basic configuration merging failed: {e}")
            return False
    
    def test_hierarchical_configuration_merging(self) -> bool:
        """Test advanced hierarchical merging with multiple layers."""
        print("🔍 Testing hierarchical configuration merging...")
        
        try:
            # Create additional layer configurations for testing
            usecase_config = {
                "usecase": {
                    "patterns": ["CQRS", "Repository"],
                    "validation": {"strict_mode": True}
                },
                "business_rules": {
                    "user_validation": {
                        "email_unique": True,
                        "name_required": True
                    }
                }
            }
            
            repository_config = {
                "repository": {
                    "database": "postgresql",
                    "async_support": True,
                    "connection_pool": {"min_size": 5, "max_size": 20}
                }
            }
            
            # Write additional layer configs
            usecase_path = self.temp_dir / "usecase.yaml"
            repository_path = self.temp_dir / "repository.yaml"
            
            with usecase_path.open('w') as f:
                yaml.dump(usecase_config, f, default_flow_style=False)
            
            with repository_path.open('w') as f:
                yaml.dump(repository_config, f, default_flow_style=False)
            
            # Test hierarchical merging
            layer_paths = [
                self.temp_dir / "domain.yaml",
                self.temp_dir / "entities.yaml", 
                usecase_path,
                repository_path
            ]
            
            result = self.merger.merge_hierarchical_configurations(
                layer_paths, conflict_resolution_strategy="highest_precedence"
            )
            
            # Validate hierarchical merge result
            if not isinstance(result.merged_config, dict):
                print("❌ Hierarchical merge result is not a dictionary")
                return False
            
            # Check that all layers contributed to final config
            if "domain" not in result.merged_config:
                print("❌ Domain configuration missing from hierarchical merge")
                return False
            
            if "usecase" not in result.merged_config:
                print("❌ Use case configuration missing from hierarchical merge")
                return False
            
            if "repository" not in result.merged_config:
                print("❌ Repository configuration missing from hierarchical merge")
                return False
            
            # Validate performance metrics
            if not result.performance_metrics:
                print("❌ Performance metrics missing from hierarchical merge")
                return False
            
            execution_time = result.performance_metrics.get("execution_time", 0)
            if execution_time <= 0:
                print("❌ Invalid execution time in performance metrics")
                return False
            
            print("✅ Hierarchical configuration merging successful")
            print(f"  ⏱️ Execution time: {execution_time:.4f}s")
            print(f"  📊 Layers processed: {result.performance_metrics.get('layers_processed', 0)}")
            print(f"  🔑 Config keys: {result.performance_metrics.get('config_keys', 0)}")
            return True
            
        except Exception as e:
            print(f"❌ Hierarchical configuration merging failed: {e}")
            return False
    
    def test_template_generation_with_merged_config(self) -> bool:
        """Test template generation using merged configuration."""
        print("🔍 Testing template generation with merged configuration...")
        
        try:
            # Get merged configuration
            domain_path = self.temp_dir / "domain.yaml"
            entity_path = self.temp_dir / "entities.yaml"
            
            merged_config = self.merger.merge_domain_configurations(
                domain_path, entity_path
            )
            
            # Create a simple test template
            template_content = """\"\"\"{{domain.name|title}} domain entities - Generated from merged config.\"\"\"

from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

# Domain: {{domain.name}}
# Entities: {{entities|length}}

{% for entity in entities %}
class {{entity.name}}:
    \"\"\"{{entity.description}}\"\"\"
    
    def __init__(self):
        {% for field in entity.fields %}
        self.{{field.name}}: {{field_types[field.type].python_type}} = None  # {{field.description}}
        {% endfor %}
        {% for mixin in entity.mixins %}
        # Mixin: {{mixin}}
        {% endfor %}

{% endfor %}"""

            # Test template rendering
            template = Template(template_content)
            rendered = template.render(**merged_config)
            
            # Validate rendered content
            if "User domain entities" not in rendered:
                print("❌ Template rendering failed - domain title not found")
                return False
            
            if "class User:" not in rendered:
                print("❌ Template rendering failed - User class not found")
                return False
            
            if "self.name:" not in rendered or "self.email:" not in rendered:
                print("❌ Template rendering failed - entity fields not found")
                return False
            
            print("✅ Template generation with merged configuration successful")
            print("📄 Sample rendered content:")
            print("=" * 50)
            print(rendered[:500] + "..." if len(rendered) > 500 else rendered)
            print("=" * 50)
            return True
            
        except Exception as e:
            print(f"❌ Template generation with merged config failed: {e}")
            return False
    
    def test_configuration_validation(self) -> bool:
        """Test configuration validation after merging."""
        print("🔍 Testing configuration validation...")
        
        try:
            domain_path = self.temp_dir / "domain.yaml"
            entity_path = self.temp_dir / "entities.yaml"
            
            merged_config = self.merger.merge_domain_configurations(
                domain_path, entity_path
            )
            
            # Test validation
            validation_errors = self.merger.validate_merged_config(merged_config)
            
            if validation_errors:
                print(f"❌ Configuration validation failed: {validation_errors}")
                return False
            
            print("✅ Configuration validation successful")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def test_configuration_inheritance_overrides(self) -> bool:
        """Test that entity configurations properly override domain defaults."""
        print("🔍 Testing configuration inheritance and overrides...")
        
        try:
            domain_path = self.temp_dir / "domain.yaml"
            entity_path = self.temp_dir / "entities.yaml"
            
            merged_config = self.merger.merge_domain_configurations(
                domain_path, entity_path
            )
            
            # Check that entity-specific values override domain defaults
            entities = merged_config.get("entities", [])
            user_entity = entities[0] if entities else {}
            
            # Validate entity name from entities.yaml overrides any domain default
            if user_entity.get("name") != "User":
                print("❌ Entity name override failed")
                return False
            
            # Validate template_context from entities.yaml is present
            template_context = merged_config.get("template_context", {})
            if template_context.get("domain_name") != "user":
                print("❌ Template context not properly inherited")
                return False
            
            # Validate field_types from domain are inherited
            field_types = merged_config.get("field_types", {})
            if not field_types.get("email", {}).get("unique"):
                print("❌ Field type inheritance failed")
                return False
            
            print("✅ Configuration inheritance and overrides working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Configuration inheritance test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print("🚀 Starting Configuration Merging Integration Tests")
        print("=" * 60)
        
        # Setup test environment
        test_dir = self.setup_test_environment()
        print(f"📁 Test environment created at: {test_dir}")
        
        tests = [
            self.test_basic_configuration_merging,
            self.test_hierarchical_configuration_merging,
            self.test_configuration_validation,
            self.test_configuration_inheritance_overrides,
            self.test_template_generation_with_merged_config,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                failed += 1
            print()
        
        # Cleanup
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test environment")
        
        # Results
        print("=" * 60)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All configuration merging integration tests passed!")
            return True
        else:
            print("💥 Some integration tests failed!")
            return False


def main():
    """Main test execution."""
    print("Configuration Merging Integration Test Suite")
    print("Testing enhanced ConfigurationMerger with entity templates")
    print()
    
    tester = ConfigurationIntegrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()