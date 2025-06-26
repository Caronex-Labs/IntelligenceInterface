#!/usr/bin/env python3
"""Entity Template Integration Test Script.

This script tests the integration between our actual entity and exception templates
with the enhanced ConfigurationMerger, validating the complete co-location workflow.
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


class EntityTemplateIntegrationTester:
    """Tests entity template integration with configuration merging."""
    
    def __init__(self):
        """Initialize the integration tester."""
        self.temp_dir = None
        self.merger = ConfigurationMerger()
        self.template_dir = Path(__file__).parent / "app" / "domain" / "{{domain}}"
    
    def setup_test_environment(self) -> Path:
        """Create test environment with realistic configuration."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="entity_template_test_"))
        
        # Copy actual template files to test directory
        domain_template_dir = self.temp_dir / "templates"
        domain_template_dir.mkdir()
        
        # Copy entity and exception templates
        if (self.template_dir / "entities.py.j2").exists():
            shutil.copy2(
                self.template_dir / "entities.py.j2",
                domain_template_dir / "entities.py.j2"
            )
        
        if (self.template_dir / "exceptions.py.j2").exists():
            shutil.copy2(
                self.template_dir / "exceptions.py.j2", 
                domain_template_dir / "exceptions.py.j2"
            )
        
        # Create realistic domain configuration matching our template requirements
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
                        "enabled": True,
                        "fields": ["id"]
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
                "default_factory": "uuid4",
                "description": "Unique identifier"
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
                },
                "optional_string": {
                    "python_type": "str",
                    "sqlmodel_type": "str"
                }
            },
            "timestamps": {
                "created_at": {
                    "type": "datetime",
                    "default_factory": "datetime.utcnow",
                    "description": "Creation timestamp"
                },
                "updated_at": {
                    "type": "datetime",
                    "default_factory": "datetime.utcnow", 
                    "description": "Last update timestamp"
                }
            },
            "integration": {
                "pydantic": {
                    "validate_assignment": True,
                    "use_enum_values": True,
                    "allow_population_by_field_name": True
                },
                "fastapi": {
                    "include_examples": True
                }
            },
            "generation": {
                "style": {
                    "use_type_hints": True
                }
            }
        }
        
        # Create entity configuration matching our template structure
        entity_config = {
            "entities": [
                {
                    "name": "User",
                    "description": "User business entity with complete domain modeling",
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
                            },
                            "example": "John Doe"
                        },
                        {
                            "name": "email",
                            "type": "email",
                            "description": "User email address",
                            "required": True,
                            "unique": True,
                            "example": "user@example.com"
                        },
                        {
                            "name": "status",
                            "type": "string",
                            "description": "User status",
                            "required": True,
                            "default": "active",
                            "validation": {
                                "choices": ["active", "inactive", "pending"]
                            },
                            "example": "active"
                        }
                    ],
                    "relationships": [
                        {
                            "name": "posts",
                            "type": "one_to_many",
                            "target_entity": "Post",
                            "back_populates": "user",
                            "cascade": "save-update"
                        }
                    ],
                    "validation": {
                        "business_rules": [
                            {
                                "name": "unique_email_validation",
                                "description": "Email must be unique",
                                "type": "unique_constraint",
                                "fields": ["email"]
                            }
                        ]
                    }
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
    
    def test_entity_template_rendering(self) -> bool:
        """Test that our actual entity template renders correctly with merged config."""
        print("🔍 Testing entity template rendering with merged configuration...")
        
        try:
            # Get merged configuration
            domain_path = self.temp_dir / "domain.yaml"
            entity_path = self.temp_dir / "entities.yaml"
            
            merged_config = self.merger.merge_domain_configurations(
                domain_path, entity_path
            )
            
            # Load and render entity template
            template_path = self.temp_dir / "templates" / "entities.py.j2"
            if not template_path.exists():
                print("❌ entities.py.j2 template not found")
                return False
            
            with template_path.open('r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            rendered = template.render(**merged_config)
            
            # Validate that key components are present
            expected_components = [
                "User domain entities - Generated from Co-located Template",
                "class UserBase(SQLModel",
                "class User(UserBase, table=True)",
                "class UserCreate(UserBase)",
                "class UserUpdate(SQLModel)",
                "class UserResponse(UserBase)",
                "@pyhex:begin:custom_imports",
                "@pyhex:end:custom_imports",
                "def create_user_from_dict",
                "def validate_user_business_rules"
            ]
            
            for component in expected_components:
                if component not in rendered:
                    print(f"❌ Missing expected component: {component}")
                    return False
            
            # Validate field generation
            if "name: str = Field(" not in rendered:
                print("❌ User name field not properly generated")
                return False
            
            if "email: EmailStr = Field(" not in rendered:
                print("❌ User email field not properly generated")
                return False
            
            # Validate relationship generation
            if "posts: List[\"Post\"] = Relationship(" not in rendered:
                print("❌ User posts relationship not properly generated")
                return False
            
            print("✅ Entity template rendering successful")
            print(f"📄 Generated entity template length: {len(rendered)} characters")
            return True
            
        except Exception as e:
            print(f"❌ Entity template rendering failed: {e}")
            return False
    
    def test_exception_template_rendering(self) -> bool:
        """Test that our actual exception template renders correctly with merged config."""
        print("🔍 Testing exception template rendering with merged configuration...")
        
        try:
            # Get merged configuration
            domain_path = self.temp_dir / "domain.yaml"
            entity_path = self.temp_dir / "entities.yaml"
            
            merged_config = self.merger.merge_domain_configurations(
                domain_path, entity_path
            )
            
            # Load and render exception template
            template_path = self.temp_dir / "templates" / "exceptions.py.j2"
            if not template_path.exists():
                print("❌ exceptions.py.j2 template not found")
                return False
            
            with template_path.open('r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            rendered = template.render(**merged_config)
            
            # Validate that key exception components are present
            expected_components = [
                "User domain exceptions - Generated from Co-located Template",
                "class ExceptionSeverity(str, Enum)",
                "class ExceptionCategory(str, Enum)",
                "class UserExceptionContext(BaseModel)",
                "class BaseUserException(Exception)",
                "class UserNotFoundError(BaseUserException)",
                "class UserValidationError(BaseUserException)",
                "class UserBusinessRuleError(BaseUserException)",
                "@pyhex:begin:custom_imports",
                "@pyhex:end:custom_imports",
                "def create_not_found_error",
                "def register_exception_handlers"
            ]
            
            for component in expected_components:
                if component not in rendered:
                    print(f"❌ Missing expected exception component: {component}")
                    return False
            
            # Validate error code generation
            if "USER_NOT_FOUND" not in rendered:
                print("❌ User-specific error codes not properly generated")
                return False
            
            # Validate FastAPI integration
            if "HTTPException" not in rendered or "status.HTTP_" not in rendered:
                print("❌ FastAPI integration not properly generated")
                return False
            
            print("✅ Exception template rendering successful")
            print(f"📄 Generated exception template length: {len(rendered)} characters")
            return True
            
        except Exception as e:
            print(f"❌ Exception template rendering failed: {e}")
            return False
    
    def test_co_location_workflow(self) -> bool:
        """Test the complete co-location workflow."""
        print("🔍 Testing complete co-location workflow...")
        
        try:
            # Create co-location directory structure
            user_domain_dir = self.temp_dir / "user_domain"
            user_domain_dir.mkdir()
            
            # Copy templates to co-location directory
            shutil.copy2(self.temp_dir / "domain.yaml", user_domain_dir / "domain.yaml")
            shutil.copy2(self.temp_dir / "entities.yaml", user_domain_dir / "entities.yaml")
            
            if (self.temp_dir / "templates" / "entities.py.j2").exists():
                shutil.copy2(
                    self.temp_dir / "templates" / "entities.py.j2",
                    user_domain_dir / "entities.py.j2"
                )
            
            if (self.temp_dir / "templates" / "exceptions.py.j2").exists():
                shutil.copy2(
                    self.temp_dir / "templates" / "exceptions.py.j2",
                    user_domain_dir / "exceptions.py.j2"
                )
            
            # Test configuration merging from co-location directory
            merged_config = self.merger.merge_domain_configurations(
                user_domain_dir / "domain.yaml",
                user_domain_dir / "entities.yaml"
            )
            
            # Generate both entity and exception files
            entity_template = Template((user_domain_dir / "entities.py.j2").read_text())
            exception_template = Template((user_domain_dir / "exceptions.py.j2").read_text())
            
            # Render templates
            entity_output = entity_template.render(**merged_config)
            exception_output = exception_template.render(**merged_config)
            
            # Write generated files to co-location directory
            (user_domain_dir / "entities.py").write_text(entity_output)
            (user_domain_dir / "exceptions.py").write_text(exception_output)
            
            # Validate co-location structure
            expected_files = [
                "domain.yaml",     # Configuration
                "entities.yaml",   # Configuration
                "entities.py.j2",  # Template
                "exceptions.py.j2", # Template
                "entities.py",     # Generated
                "exceptions.py"    # Generated
            ]
            
            for file_name in expected_files:
                if not (user_domain_dir / file_name).exists():
                    print(f"❌ Missing file in co-location structure: {file_name}")
                    return False
            
            print("✅ Co-location workflow successful")
            print(f"📁 Co-location directory: {user_domain_dir}")
            print(f"📂 Files created: {len(expected_files)}")
            return True
            
        except Exception as e:
            print(f"❌ Co-location workflow failed: {e}")
            return False
    
    def test_preservation_markers(self) -> bool:
        """Test that @pyhex preservation markers are correctly placed."""
        print("🔍 Testing @pyhex preservation markers...")
        
        try:
            domain_path = self.temp_dir / "domain.yaml"
            entity_path = self.temp_dir / "entities.yaml"
            
            merged_config = self.merger.merge_domain_configurations(
                domain_path, entity_path
            )
            
            # Test entity template preservation markers
            entity_template_path = self.temp_dir / "templates" / "entities.py.j2"
            if entity_template_path.exists():
                with entity_template_path.open('r') as f:
                    entity_content = f.read()
                
                template = Template(entity_content)
                rendered = template.render(**merged_config)
                
                # Count preservation markers
                begin_markers = rendered.count("# @pyhex:begin:")
                end_markers = rendered.count("# @pyhex:end:")
                
                if begin_markers != end_markers:
                    print(f"❌ Mismatched preservation markers: {begin_markers} begin, {end_markers} end")
                    return False
                
                if begin_markers < 10:  # Expect at least 10 preservation blocks
                    print(f"❌ Insufficient preservation markers: {begin_markers}")
                    return False
                
                print(f"✅ Entity preservation markers: {begin_markers} blocks")
            
            # Test exception template preservation markers
            exception_template_path = self.temp_dir / "templates" / "exceptions.py.j2"
            if exception_template_path.exists():
                with exception_template_path.open('r') as f:
                    exception_content = f.read()
                
                template = Template(exception_content)
                rendered = template.render(**merged_config)
                
                # Count preservation markers
                begin_markers = rendered.count("# @pyhex:begin:")
                end_markers = rendered.count("# @pyhex:end:")
                
                if begin_markers != end_markers:
                    print(f"❌ Mismatched exception preservation markers: {begin_markers} begin, {end_markers} end")
                    return False
                
                if begin_markers < 5:  # Expect at least 5 preservation blocks
                    print(f"❌ Insufficient exception preservation markers: {begin_markers}")
                    return False
                
                print(f"✅ Exception preservation markers: {begin_markers} blocks")
            
            return True
            
        except Exception as e:
            print(f"❌ Preservation marker test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all entity template integration tests."""
        print("🚀 Starting Entity Template Integration Tests")
        print("=" * 60)
        
        # Setup test environment
        test_dir = self.setup_test_environment()
        print(f"📁 Test environment created at: {test_dir}")
        
        tests = [
            self.test_entity_template_rendering,
            self.test_exception_template_rendering,
            self.test_preservation_markers,
            self.test_co_location_workflow,
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
            print("🎉 All entity template integration tests passed!")
            return True
        else:
            print("💥 Some entity template integration tests failed!")
            return False


def main():
    """Main test execution."""
    print("Entity Template Integration Test Suite")
    print("Testing actual entity/exception templates with ConfigurationMerger")
    print()
    
    tester = EntityTemplateIntegrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()