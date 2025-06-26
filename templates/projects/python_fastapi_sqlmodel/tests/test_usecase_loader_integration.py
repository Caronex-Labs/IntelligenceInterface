"""
Integration tests for UseCaseLoader with test fixtures.

This module validates that the UseCaseLoader implementation works correctly
with the created test fixtures and BDD scenarios.
"""

import pytest
from pathlib import Path
from cli.generate.config import UseCaseLoader, UseCaseDomainConfig
from cli.generate.config.exceptions import ConfigurationError


class TestUseCaseLoaderIntegration:
    """Test UseCaseLoader with real fixture files."""
    
    @pytest.fixture
    def usecase_loader(self):
        """Create a UseCaseLoader instance for testing."""
        return UseCaseLoader(strict_mode=True)
    
    @pytest.fixture
    def fixtures_path(self):
        """Get path to test fixtures directory."""
        return Path(__file__).parent / "fixtures" / "usecase"
    
    def test_load_user_management_config(self, usecase_loader, fixtures_path):
        """Test loading user management use case configuration."""
        usecase_file = fixtures_path / "user_usecase.yaml"
        business_rules_file = fixtures_path / "user_business_rules.yaml"
        
        # Load configuration from files
        config = usecase_loader.load_from_files(str(usecase_file), str(business_rules_file))
        
        # Validate loaded configuration
        assert isinstance(config, UseCaseDomainConfig)
        assert config.name == "UserManagement"
        assert config.usecase is not None
        assert config.business_rules is not None
        
        # Validate use case methods
        assert len(config.usecase.methods) == 3
        method_names = [method.name for method in config.usecase.methods]
        assert "create_user" in method_names
        assert "get_user_by_id" in method_names
        assert "update_user_profile" in method_names
        
        # Validate business rules
        assert len(config.business_rules.rules) == 4
        rule_names = [rule.name for rule in config.business_rules.rules]
        assert "email_uniqueness" in rule_names
        assert "password_strength" in rule_names
        assert "user_exists" in rule_names
        assert "profile_update_allowed" in rule_names
        
        # Validate dependency injection configuration
        assert config.usecase.dependency_injection is not None
        assert "EmailService" in config.usecase.dependency_injection.interface_mappings
        assert "ValidationService" in config.usecase.dependency_injection.interface_mappings
        
        # Validate error handling configuration
        assert config.usecase.error_handling is not None
        assert config.usecase.error_handling.aggregation_strategy == "collect_all_errors"
    
    def test_load_blog_management_config(self, usecase_loader, fixtures_path):
        """Test loading blog management use case configuration."""
        usecase_file = fixtures_path / "blog_usecase.yaml"
        business_rules_file = fixtures_path / "blog_business_rules.yaml"
        
        # Load configuration from files
        config = usecase_loader.load_from_files(str(usecase_file), str(business_rules_file))
        
        # Validate loaded configuration
        assert isinstance(config, UseCaseDomainConfig)
        assert config.name == "BlogManagement"
        assert config.usecase is not None
        assert config.business_rules is not None
        
        # Validate use case methods
        assert len(config.usecase.methods) == 3
        method_names = [method.name for method in config.usecase.methods]
        assert "create_post" in method_names
        assert "publish_post" in method_names
        assert "get_post_by_slug" in method_names
        
        # Validate business rules
        assert len(config.business_rules.rules) == 7
        rule_names = [rule.name for rule in config.business_rules.rules]
        assert "content_length_validation" in rule_names
        assert "title_uniqueness" in rule_names
        assert "post_exists" in rule_names
        
        # Validate service composition
        assert config.usecase.service_composition is not None
        assert config.usecase.service_composition.transaction_manager == "database_transaction_manager"
        assert config.usecase.service_composition.event_publisher == "blog_event_publisher"
    
    def test_load_ecommerce_config(self, usecase_loader, fixtures_path):
        """Test loading e-commerce use case configuration."""
        usecase_file = fixtures_path / "ecommerce_usecase.yaml"
        business_rules_file = fixtures_path / "ecommerce_business_rules.yaml"
        
        # Load configuration from files
        config = usecase_loader.load_from_files(str(usecase_file), str(business_rules_file))
        
        # Validate loaded configuration
        assert isinstance(config, UseCaseDomainConfig)
        assert config.name == "ECommerceCheckout"
        assert config.usecase is not None
        assert config.business_rules is not None
        
        # Validate complex dependency injection
        assert config.usecase.dependency_injection is not None
        interface_mappings = config.usecase.dependency_injection.interface_mappings
        assert "PaymentService" in interface_mappings
        assert "ShippingService" in interface_mappings
        assert interface_mappings["PaymentService"] == "stripe_payment_service"
        
        # Validate scoped dependencies
        scoped_deps = config.usecase.dependency_injection.scoped_dependencies
        assert "database_session" in scoped_deps
        assert "user_context" in scoped_deps
        assert "order_context" in scoped_deps
        
        # Validate business rules validation groups
        assert len(config.business_rules.validation_groups) == 5
        group_names = [group.name for group in config.business_rules.validation_groups]
        assert "pre_checkout_validation" in group_names
        assert "payment_validation" in group_names
        assert "inventory_validation" in group_names
    
    def test_load_from_strings(self, usecase_loader):
        """Test loading configuration from string content."""
        usecase_yaml = """
name: "TestUseCase"
description: "Test use case for string loading"
methods:
  - name: "test_method"
    input_schema: "TestRequest"
    output_schema: "TestResponse"
    transaction_boundary: true
dependencies:
  repositories: ["test_repository"]
  services: ["test_service"]
"""
        
        business_rules_yaml = """
rules:
  - name: "test_rule"
    type: "validation"
    condition: "test.is_valid()"
    error_message: "Test validation failed"
    severity: "error"
"""
        
        # Load configuration from strings
        config = usecase_loader.load_from_strings(usecase_yaml, business_rules_yaml)
        
        # Validate loaded configuration
        assert isinstance(config, UseCaseDomainConfig)
        assert config.name == "TestUseCase"
        assert config.usecase is not None
        assert config.business_rules is not None
        assert len(config.usecase.methods) == 1
        assert len(config.business_rules.rules) == 1
    
    def test_validation_error_handling(self, usecase_loader):
        """Test that validation errors are properly handled."""
        # Invalid use case configuration
        invalid_usecase_yaml = """
name: 123  # Should be string
methods: "not_a_list"  # Should be list
"""
        
        business_rules_yaml = """
rules:
  - name: "test_rule"
    type: "validation"
    condition: "test.is_valid()"
    error_message: "Test validation failed"
    severity: "error"
"""
        
        # Should raise validation error
        with pytest.raises(ConfigurationError):
            usecase_loader.load_from_strings(invalid_usecase_yaml, business_rules_yaml)
    
    def test_hierarchical_integration_readiness(self, usecase_loader, fixtures_path):
        """Test that configurations are ready for hierarchical merging."""
        usecase_file = fixtures_path / "user_usecase.yaml"
        business_rules_file = fixtures_path / "user_business_rules.yaml"
        
        # Load configuration
        config = usecase_loader.load_from_files(str(usecase_file), str(business_rules_file))
        
        # Validate integration points
        assert config.entity_dependencies is not None
        assert len(config.entity_dependencies) > 0
        assert "User" in config.entity_dependencies
        assert "UserProfile" in config.entity_dependencies
        
        assert config.repository_dependencies is not None
        assert len(config.repository_dependencies) > 0
        assert "user_repository" in config.repository_dependencies
        
        assert config.external_dependencies is not None
        assert len(config.external_dependencies) > 0
        assert "email_service" in config.external_dependencies
        assert "validation_service" in config.external_dependencies
        
        # Validate package name generation
        assert config.package is not None
        assert config.package == "user_management"  # PascalCase to snake_case conversion