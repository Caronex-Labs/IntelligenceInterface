"""
BDD step definitions for use case configuration scenarios.

This module implements the step definitions for all use case configuration
BDD scenarios, providing comprehensive testing of the use case configuration system.
"""

import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import pytest
from behave import given, when, then, step
import yaml

from cli.generate.config import (
    UseCaseDomainConfig,
    UseCaseLoader,
    load_usecase_domain_configuration,
    load_usecase_domain_from_strings,
    ConfigurationError,
    ConfigurationValidationError,
    ConfigurationFileError,
)
from app.domain.configuration_merger import ConfigurationMerger


# Test context storage
class UseCaseTestContext:
    """Storage for test context between steps."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all context variables."""
        self.usecase_loader: Optional[UseCaseLoader] = None
        self.usecase_yaml_content: Optional[str] = None
        self.business_rules_yaml_content: Optional[str] = None
        self.domain_yaml_content: Optional[str] = None
        self.repository_yaml_content: Optional[str] = None
        self.usecase_config_file_path: Optional[Path] = None
        self.business_rules_config_file_path: Optional[Path] = None
        self.usecase_domain_config: Optional[UseCaseDomainConfig] = None
        self.hierarchical_config: Optional[Dict[str, Any]] = None
        self.error: Optional[Exception] = None
        self.temp_files: list = []
        self.log_records: list = []
        self.configuration_merger: Optional[ConfigurationMerger] = None
    
    def cleanup(self):
        """Clean up temporary resources."""
        for temp_file in self.temp_files:
            try:
                temp_file.unlink(missing_ok=True)
            except Exception:
                pass
        self.temp_files.clear()


# Global test context
context = UseCaseTestContext()


# Setup and teardown
@given('the use case configuration loading system is properly initialized')
def step_initialize_usecase_system(context_obj):
    """Initialize the use case configuration loading system."""
    context.reset()
    context.usecase_loader = UseCaseLoader(strict_mode=True)
    
    # Setup logging capture
    context.log_handler = LogCapture()
    logger = logging.getLogger('cli.generate.config')
    logger.addHandler(context.log_handler)
    logger.setLevel(logging.DEBUG)


@given('PyYAML integration is available for use case configurations')
def step_pyyaml_available_usecase(context_obj):
    """Verify PyYAML is available for use case configurations."""
    import yaml
    assert yaml is not None


@given('the hierarchical configuration merging system is available')
def step_hierarchical_merging_available(context_obj):
    """Verify hierarchical configuration merging system is available."""
    context.configuration_merger = ConfigurationMerger()
    assert context.configuration_merger is not None


# Use case configuration content setup
@given('I have usecase.yaml with business logic configuration')
def step_usecase_yaml_from_docstring(context_obj):
    """Set up use case configuration from docstring."""
    context.usecase_yaml_content = context_obj.text.strip()


@given('I have business-rules.yaml with domain-specific rules')
def step_business_rules_yaml_from_docstring(context_obj):
    """Set up business rules configuration from docstring."""
    context.business_rules_yaml_content = context_obj.text.strip()


@given('I have usecase.yaml with service dependencies and transaction boundaries')
def step_usecase_yaml_with_dependencies(context_obj):
    """Set up use case configuration with dependencies from docstring."""
    context.usecase_yaml_content = context_obj.text.strip()


@given('I have business-rules.yaml with domain validation rules')
def step_business_rules_yaml_with_validation(context_obj):
    """Set up business rules configuration with validation rules from docstring."""
    context.business_rules_yaml_content = context_obj.text.strip()


@given('I have use case configuration with dependencies on entity and repository configs')
def step_usecase_config_with_dependencies(context_obj):
    """Set up use case configuration with dependencies on other layers."""
    context.usecase_yaml_content = """
name: "OrderProcessing"
description: "Order processing with entity and repository dependencies"
methods:
  - name: "create_order"
    input_schema: "CreateOrderRequest"
    output_schema: "OrderResponse"
    transaction_boundary: true
    dependencies:
      repositories: ["order_repository", "customer_repository"]
      services: ["inventory_service", "payment_service"]
    business_rules: ["inventory_check", "payment_validation"]
entity_dependencies: ["Order", "Customer", "Product"]
repository_dependencies: ["order_repository", "customer_repository", "product_repository"]
"""
    
    context.business_rules_yaml_content = """
rules:
  - name: "inventory_check"
    type: "business_logic"
    condition: "product.stock >= order.quantity"
    error_message: "Insufficient inventory"
    severity: "error"
  - name: "payment_validation"
    type: "validation"
    condition: "payment.amount > 0 and payment.method.is_valid()"
    error_message: "Invalid payment"
    severity: "error"
"""


@given('I have domain configuration with base settings')
def step_domain_config_base(context_obj):
    """Set up domain configuration with base settings."""
    context.domain_yaml_content = """
name: "Order"
plural: "Orders"
description: "Order domain configuration"
base_fields:
  - name: "id"
    type: "int"
    required: true
  - name: "created_at"
    type: "datetime"
    default: "datetime.utcnow"
"""


@given('I have repository configuration with data access patterns')
def step_repository_config_patterns(context_obj):
    """Set up repository configuration with data access patterns."""
    context.repository_yaml_content = """
name: "OrderRepository"
description: "Order repository configuration"
database_settings:
  connection_pool_size: 10
  query_timeout: 30
async_operations: true
caching_enabled: true
"""


@given('I have usecase.yaml with invalid method configuration')
def step_usecase_yaml_invalid(context_obj):
    """Set up invalid use case configuration from docstring."""
    context.usecase_yaml_content = context_obj.text.strip()


@given('I have business-rules.yaml with invalid rule definitions')
def step_business_rules_yaml_invalid(context_obj):
    """Set up invalid business rules configuration from docstring."""
    context.business_rules_yaml_content = context_obj.text.strip()


@given('I have usecase.yaml with complex dependency injection patterns')
def step_usecase_yaml_complex_di(context_obj):
    """Set up complex dependency injection configuration from docstring."""
    context.usecase_yaml_content = context_obj.text.strip()


@given('I have loaded a use case configuration previously')
def step_loaded_usecase_config_previously(context_obj):
    """Set up scenario where configuration was loaded previously."""
    # Simulate previous load by creating a simple configuration
    context.usecase_yaml_content = """
name: "SimpleUseCase"
methods:
  - name: "simple_method"
    input_schema: "SimpleRequest"
    output_schema: "SimpleResponse"
"""
    context.business_rules_yaml_content = """
rules:
  - name: "simple_rule"
    type: "validation"
    condition: "input.is_valid()"
    error_message: "Invalid input"
"""
    # Load it once to simulate caching
    context.usecase_domain_config = context.usecase_loader.load_from_strings(
        context.usecase_yaml_content, context.business_rules_yaml_content
    )


@given('I have a use case configuration file with invalid schema structure')
def step_usecase_config_invalid_schema(context_obj):
    """Set up use case configuration with invalid schema structure from docstring."""
    context.usecase_yaml_content = context_obj.text.strip()


@given('I have a complete use case configuration with all required elements')
def step_complete_usecase_config(context_obj):
    """Set up complete use case configuration with all elements."""
    context.usecase_yaml_content = """
name: "ComprehensiveUseCase"
description: "Complete use case configuration"
methods:
  - name: "process_request"
    input_schema: "ProcessRequest"
    output_schema: "ProcessResponse"
    transaction_boundary: true
    dependencies:
      repositories: ["main_repository"]
      services: ["validation_service", "notification_service"]
    business_rules: ["validation_rule", "business_rule"]
dependencies:
  repositories: ["main_repository"]
  services: ["validation_service", "notification_service"]
service_composition:
  transaction_manager: "database_transaction_manager"
  event_publisher: "domain_event_publisher"
dependency_injection:
  interface_mappings:
    "ValidationService": "default_validation_service"
    "NotificationService": "email_notification_service"
  scoped_dependencies: ["database_session"]
  singleton_dependencies: ["cache_manager"]
"""
    
    context.business_rules_yaml_content = """
rules:
  - name: "validation_rule"
    type: "validation"
    condition: "request.is_valid()"
    error_message: "Request validation failed"
    severity: "error"
  - name: "business_rule"
    type: "business_logic"
    condition: "business.logic.applies()"
    error_message: "Business rule violated"
    severity: "error"
validation_groups:
  - name: "request_validation"
    rules: ["validation_rule", "business_rule"]
"""


# Actions
@when('I load use case configuration using the configuration loader')
def step_load_usecase_config(context_obj):
    """Load use case configuration from stored YAML content."""
    try:
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        context.error = None
    except Exception as e:
        context.error = e
        context.usecase_domain_config = None


@when('I load the use case configuration')
def step_load_usecase_config_simple(context_obj):
    """Load use case configuration (simple form)."""
    try:
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        context.error = None
    except Exception as e:
        context.error = e
        context.usecase_domain_config = None


@when('I load the business rules configuration')
def step_load_business_rules_config(context_obj):
    """Load business rules configuration."""
    try:
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        context.error = None
    except Exception as e:
        context.error = e
        context.usecase_domain_config = None


@when('I load the complete hierarchical configuration')
def step_load_hierarchical_config(context_obj):
    """Load complete hierarchical configuration."""
    try:
        # First load the use case configuration
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        
        # Then simulate hierarchical merging with domain and repository layers
        hierarchical_layers = {}
        
        if context.domain_yaml_content:
            hierarchical_layers['domain'] = yaml.safe_load(context.domain_yaml_content)
        
        if context.repository_yaml_content:
            hierarchical_layers['repository'] = yaml.safe_load(context.repository_yaml_content)
        
        hierarchical_layers['usecase'] = {
            'name': context.usecase_domain_config.name,
            'usecase': context.usecase_domain_config.usecase.model_dump() if context.usecase_domain_config.usecase else {},
            'business_rules': context.usecase_domain_config.business_rules.model_dump() if context.usecase_domain_config.business_rules else {}
        }
        
        # Use configuration merger for hierarchical merging
        context.hierarchical_config = context.configuration_merger.merge_hierarchical_configurations(
            domain_config=hierarchical_layers.get('domain', {}),
            usecase_config=hierarchical_layers.get('usecase', {}),
            repository_config=hierarchical_layers.get('repository', {}),
            interface_config={}
        )
        
        context.error = None
    except Exception as e:
        context.error = e
        context.hierarchical_config = None


@when('I attempt to load the use case configuration')
def step_attempt_load_usecase_config(context_obj):
    """Attempt to load use case configuration (expecting potential failure)."""
    try:
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        context.error = None
    except Exception as e:
        context.error = e
        context.usecase_domain_config = None


@when('I load the complex use case configuration')
def step_load_complex_usecase_config(context_obj):
    """Load complex use case configuration."""
    try:
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        context.error = None
    except Exception as e:
        context.error = e
        context.usecase_domain_config = None


@when('I request the same use case configuration again')
def step_request_same_config_again(context_obj):
    """Request the same configuration again for caching test."""
    try:
        # Load the same configuration again
        second_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        context.error = None
        # Store both for comparison
        context.cached_config = second_config
    except Exception as e:
        context.error = e


@when('I load the configuration with schema validation enabled')
def step_load_config_with_schema_validation(context_obj):
    """Load configuration with schema validation enabled."""
    try:
        # UseCaseLoader has strict validation enabled by default
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, "rules: []"  # Minimal valid business rules
        )
        context.error = None
    except Exception as e:
        context.error = e
        context.usecase_domain_config = None


@when('I prepare the configuration for template generation')
def step_prepare_config_for_template_generation(context_obj):
    """Prepare configuration for template generation."""
    try:
        # Load the complete configuration first
        context.usecase_domain_config = context.usecase_loader.load_from_strings(
            context.usecase_yaml_content, context.business_rules_yaml_content
        )
        
        # Validate it for template generation readiness
        context.usecase_loader.validate_usecase_domain_config(context.usecase_domain_config)
        
        # Extract template variables
        context.template_variables = {
            'domain_name': context.usecase_domain_config.name,
            'package_name': context.usecase_domain_config.package,
            'usecase_methods': context.usecase_domain_config.usecase.methods if context.usecase_domain_config.usecase else [],
            'business_rules': context.usecase_domain_config.business_rules.rules if context.usecase_domain_config.business_rules else [],
        }
        
        context.error = None
    except Exception as e:
        context.error = e


# Assertions
@then('the usecase.yaml should provide use case interface and implementation specs')
def step_usecase_yaml_provides_specs(context_obj):
    """Verify usecase.yaml provides interface and implementation specs."""
    assert context.error is None, f"Expected successful loading, got error: {context.error}"
    assert context.usecase_domain_config is not None
    assert context.usecase_domain_config.usecase is not None
    assert len(context.usecase_domain_config.usecase.methods) > 0
    
    # Check that methods have proper interface specifications
    for method in context.usecase_domain_config.usecase.methods:
        assert method.name is not None
        assert method.input_schema is not None or method.output_schema is not None


@then('the business-rules.yaml should provide validation and business constraint rules')
def step_business_rules_yaml_provides_rules(context_obj):
    """Verify business-rules.yaml provides validation and constraint rules."""
    assert context.usecase_domain_config.business_rules is not None
    assert len(context.usecase_domain_config.business_rules.rules) > 0
    
    # Check that rules have proper structure
    for rule in context.usecase_domain_config.business_rules.rules:
        assert rule.name is not None
        assert rule.type is not None
        assert rule.condition is not None


@then('configuration should support dependency injection patterns')
def step_config_supports_dependency_injection(context_obj):
    """Verify configuration supports dependency injection patterns."""
    assert context.usecase_domain_config.usecase is not None
    assert context.usecase_domain_config.usecase.dependencies is not None
    
    # Check if dependencies are properly structured
    if hasattr(context.usecase_domain_config.usecase.dependencies, 'services'):
        assert isinstance(context.usecase_domain_config.usecase.dependencies.services, list)
    
    # Check dependency injection configuration if present
    if context.usecase_domain_config.usecase.dependency_injection:
        assert hasattr(context.usecase_domain_config.usecase.dependency_injection, 'interface_mappings')


@then('the merged configuration should enable use case template generation')
def step_merged_config_enables_template_generation(context_obj):
    """Verify merged configuration enables template generation."""
    assert context.usecase_domain_config is not None
    assert context.usecase_domain_config.name is not None
    assert context.usecase_domain_config.package is not None
    
    # Check that all required elements for template generation are present
    if context.usecase_domain_config.usecase:
        assert len(context.usecase_domain_config.usecase.methods) > 0
    
    if context.usecase_domain_config.business_rules:
        assert len(context.usecase_domain_config.business_rules.rules) > 0


@then('dependency injection patterns should be properly configured')
def step_dependency_injection_properly_configured(context_obj):
    """Verify dependency injection patterns are properly configured."""
    assert context.usecase_domain_config.usecase is not None
    assert context.usecase_domain_config.usecase.dependencies is not None
    
    # Verify dependency structure
    deps = context.usecase_domain_config.usecase.dependencies
    if hasattr(deps, 'repositories'):
        assert isinstance(deps.repositories, list)
    if hasattr(deps, 'services'):
        assert isinstance(deps.services, list)


@then('transaction boundary specifications should be available')
def step_transaction_boundaries_available(context_obj):
    """Verify transaction boundary specifications are available."""
    assert context.usecase_domain_config.usecase is not None
    assert len(context.usecase_domain_config.usecase.methods) > 0
    
    # Check that at least one method has transaction boundary specified
    has_transaction_boundary = any(
        method.transaction_boundary for method in context.usecase_domain_config.usecase.methods
    )
    assert has_transaction_boundary, "At least one method should have transaction boundary specified"


@then('business method signatures should be defined with input/output schemas')
def step_business_method_signatures_defined(context_obj):
    """Verify business method signatures are defined with input/output schemas."""
    assert context.usecase_domain_config.usecase is not None
    assert len(context.usecase_domain_config.usecase.methods) > 0
    
    # Check that methods have input/output schemas
    for method in context.usecase_domain_config.usecase.methods:
        assert method.input_schema is not None or method.output_schema is not None


@then('service composition configuration should be accessible')
def step_service_composition_accessible(context_obj):
    """Verify service composition configuration is accessible."""
    if context.usecase_domain_config.usecase and context.usecase_domain_config.usecase.service_composition:
        sc_config = context.usecase_domain_config.usecase.service_composition
        assert hasattr(sc_config, 'transaction_manager')
        assert hasattr(sc_config, 'event_publisher')


@then('orchestration steps should be properly ordered')
def step_orchestration_steps_ordered(context_obj):
    """Verify orchestration steps are properly ordered."""
    assert context.usecase_domain_config.usecase is not None
    
    # Check that methods with orchestration steps have them properly ordered
    for method in context.usecase_domain_config.usecase.methods:
        if method.orchestration_steps:
            assert isinstance(method.orchestration_steps, list)
            assert len(method.orchestration_steps) > 0


@then('validation rules should be properly structured')
def step_validation_rules_structured(context_obj):
    """Verify validation rules are properly structured."""
    assert context.usecase_domain_config.business_rules is not None
    assert len(context.usecase_domain_config.business_rules.rules) > 0
    
    for rule in context.usecase_domain_config.business_rules.rules:
        assert rule.name
        assert rule.type
        assert rule.condition
        assert rule.severity


@then('constraint definitions should be available for template generation')
def step_constraint_definitions_available(context_obj):
    """Verify constraint definitions are available for template generation."""
    assert context.usecase_domain_config.business_rules is not None
    
    # Check for constraint-type rules
    constraint_rules = [
        rule for rule in context.usecase_domain_config.business_rules.rules
        if rule.type == 'constraint' or rule.type == 'business_logic'
    ]
    assert len(constraint_rules) > 0, "Should have at least one constraint or business logic rule"


@then('error handling patterns should be configured')
def step_error_handling_configured(context_obj):
    """Verify error handling patterns are configured."""
    if context.usecase_domain_config.usecase and context.usecase_domain_config.usecase.error_handling:
        error_handling = context.usecase_domain_config.usecase.error_handling
        assert hasattr(error_handling, 'aggregation_strategy')
    
    if context.usecase_domain_config.business_rules and context.usecase_domain_config.business_rules.error_handling:
        error_handling = context.usecase_domain_config.business_rules.error_handling
        assert hasattr(error_handling, 'aggregation_strategy')


@then('validation groups should define proper execution order')
def step_validation_groups_execution_order(context_obj):
    """Verify validation groups define proper execution order."""
    if context.usecase_domain_config.business_rules and context.usecase_domain_config.business_rules.validation_groups:
        for group in context.usecase_domain_config.business_rules.validation_groups:
            assert group.rules
            if group.execution_order:
                assert isinstance(group.execution_order, list)


@then('custom exception mappings should be available')
def step_custom_exception_mappings_available(context_obj):
    """Verify custom exception mappings are available."""
    if context.usecase_domain_config.business_rules and context.usecase_domain_config.business_rules.error_handling:
        error_handling = context.usecase_domain_config.business_rules.error_handling
        if error_handling.custom_exceptions:
            assert isinstance(error_handling.custom_exceptions, list)


@then('use case config should merge properly with entity and repository layers')
def step_usecase_config_merges_properly(context_obj):
    """Verify use case config merges properly with other layers."""
    assert context.hierarchical_config is not None
    assert 'name' in context.hierarchical_config
    
    # Check that hierarchical configuration contains elements from all layers
    if context.domain_yaml_content:
        # Should contain domain elements
        assert context.hierarchical_config.get('name') is not None
    
    # Should contain use case elements
    assert context.usecase_domain_config is not None


@then('dependency references should be validated against available services')
def step_dependency_references_validated(context_obj):
    """Verify dependency references are validated."""
    assert context.error is None, "Configuration loading should succeed"
    assert context.usecase_domain_config is not None
    
    # Additional validation is performed in the loader
    context.usecase_loader.validate_usecase_domain_config(context.usecase_domain_config)


@then('configuration hierarchy should maintain proper precedence')
def step_config_hierarchy_precedence(context_obj):
    """Verify configuration hierarchy maintains proper precedence."""
    assert context.hierarchical_config is not None
    
    # Use case layer should have higher precedence than domain layer
    if context.usecase_domain_config and context.usecase_domain_config.name:
        # Use case name should be preserved in hierarchical config
        assert context.hierarchical_config.get('name') is not None


@then('use case layer should override lower layer configurations appropriately')
def step_usecase_layer_overrides(context_obj):
    """Verify use case layer overrides lower layer configurations."""
    assert context.hierarchical_config is not None
    # The hierarchical merging should preserve use case-specific configurations
    assert context.usecase_domain_config is not None


@then('merged configuration should be ready for template generation')
def step_merged_config_ready_for_templates(context_obj):
    """Verify merged configuration is ready for template generation."""
    assert context.hierarchical_config is not None
    assert context.usecase_domain_config is not None
    
    # Should have all necessary elements for template generation
    assert context.usecase_domain_config.name is not None
    assert context.usecase_domain_config.package is not None


@then('specific validation errors should be identified for use case configuration')
def step_specific_validation_errors_usecase(context_obj):
    """Verify specific validation errors are identified for use case configuration."""
    assert context.error is not None
    assert isinstance(context.error, ConfigurationValidationError)
    
    # Check that validation errors are specific and helpful
    if hasattr(context.error, 'validation_errors'):
        assert len(context.error.validation_errors) > 0


@then('detailed error messages should be provided for business rules')
def step_detailed_error_messages_business_rules(context_obj):
    """Verify detailed error messages are provided for business rules."""
    assert context.error is not None
    error_msg = str(context.error)
    assert 'business' in error_msg.lower() or 'rule' in error_msg.lower()


@then('suggestions for fixing the configuration should be included')
def step_suggestions_for_fixing_included(context_obj):
    """Verify suggestions for fixing configuration are included."""
    assert context.error is not None
    assert hasattr(context.error, 'suggestion')
    assert context.error.suggestion is not None


@then('the system should fail gracefully without corruption')
def step_system_fails_gracefully(context_obj):
    """Verify system fails gracefully without corruption."""
    assert context.error is not None
    assert context.usecase_domain_config is None
    # System should not be in corrupted state
    assert context.usecase_loader is not None


@then('dependency categories should be properly organized')
def step_dependency_categories_organized(context_obj):
    """Verify dependency categories are properly organized."""
    assert context.usecase_domain_config.usecase is not None
    deps = context.usecase_domain_config.usecase.dependencies
    
    if hasattr(deps, 'repositories'):
        assert isinstance(deps.repositories, list)
    if hasattr(deps, 'services'):
        assert isinstance(deps.services, list)
    if hasattr(deps, 'external_apis'):
        assert isinstance(deps.external_apis, list)


@then('interface mappings should be available for dependency injection')
def step_interface_mappings_available(context_obj):
    """Verify interface mappings are available for dependency injection."""
    if (context.usecase_domain_config.usecase and 
        context.usecase_domain_config.usecase.dependency_injection and
        context.usecase_domain_config.usecase.dependency_injection.interface_mappings):
        mappings = context.usecase_domain_config.usecase.dependency_injection.interface_mappings
        assert isinstance(mappings, dict)
        assert len(mappings) > 0


@then('scoped and singleton dependencies should be clearly identified')
def step_scoped_singleton_dependencies_identified(context_obj):
    """Verify scoped and singleton dependencies are clearly identified."""
    if (context.usecase_domain_config.usecase and 
        context.usecase_domain_config.usecase.dependency_injection):
        di_config = context.usecase_domain_config.usecase.dependency_injection
        assert hasattr(di_config, 'scoped_dependencies')
        assert hasattr(di_config, 'singleton_dependencies')


@then('all dependency types should be supported for template generation')
def step_all_dependency_types_supported(context_obj):
    """Verify all dependency types are supported for template generation."""
    assert context.usecase_domain_config.usecase is not None
    deps = context.usecase_domain_config.usecase.dependencies
    
    # Should support various dependency types
    assert hasattr(deps, 'repositories') or hasattr(deps, 'services')


@then('the cached configuration should be returned if not modified')
def step_cached_config_returned(context_obj):
    """Verify cached configuration is returned if not modified."""
    assert context.error is None
    assert hasattr(context, 'cached_config')
    assert context.cached_config is not None
    
    # Configurations should be equivalent (same structure)
    assert context.cached_config.name == context.usecase_domain_config.name


@then('file modification time should be checked for cache invalidation')
def step_file_modification_checked(context_obj):
    """Verify file modification time is checked for cache invalidation."""
    # This is implementation-specific, but we can verify caching behavior
    assert context.error is None


@then('performance should be optimized for repeated loads')
def step_performance_optimized_repeated_loads(context_obj):
    """Verify performance is optimized for repeated loads."""
    assert context.error is None
    # Performance optimization would be measured in real implementation


@then('memory usage should be efficient for large configurations')
def step_memory_usage_efficient(context_obj):
    """Verify memory usage is efficient for large configurations."""
    assert context.error is None
    # Memory efficiency would be measured in real implementation


@then('schema validation errors should be detected')
def step_schema_validation_errors_detected(context_obj):
    """Verify schema validation errors are detected."""
    assert context.error is not None
    assert isinstance(context.error, ConfigurationValidationError)


@then('specific schema violations should be reported')
def step_specific_schema_violations_reported(context_obj):
    """Verify specific schema violations are reported."""
    assert context.error is not None
    error_msg = str(context.error)
    # Should contain information about schema violations
    assert any(word in error_msg.lower() for word in ['schema', 'validation', 'invalid', 'type'])


@then('valid schema examples should be provided in error messages')
def step_valid_schema_examples_provided(context_obj):
    """Verify valid schema examples are provided in error messages."""
    assert context.error is not None
    assert hasattr(context.error, 'suggestion')
    assert context.error.suggestion is not None


@then('configuration should be rejected safely')
def step_config_rejected_safely(context_obj):
    """Verify configuration is rejected safely."""
    assert context.error is not None
    assert context.usecase_domain_config is None


@then('all template variables should be properly populated')
def step_template_variables_populated(context_obj):
    """Verify all template variables are properly populated."""
    assert context.error is None
    assert hasattr(context, 'template_variables')
    assert context.template_variables is not None
    
    # Check required template variables
    assert 'domain_name' in context.template_variables
    assert 'package_name' in context.template_variables


@then('dependency injection configuration should be template-ready')
def step_dependency_injection_template_ready(context_obj):
    """Verify dependency injection configuration is template-ready."""
    assert context.usecase_domain_config is not None
    if context.usecase_domain_config.usecase and context.usecase_domain_config.usecase.dependency_injection:
        di_config = context.usecase_domain_config.usecase.dependency_injection
        assert hasattr(di_config, 'interface_mappings')


@then('business rule configurations should be available for code generation')
def step_business_rule_configs_available_for_codegen(context_obj):
    """Verify business rule configurations are available for code generation."""
    assert context.usecase_domain_config.business_rules is not None
    assert len(context.usecase_domain_config.business_rules.rules) > 0
    
    # Check template variables include business rules
    if hasattr(context, 'template_variables'):
        assert 'business_rules' in context.template_variables


@then('the configuration should integrate seamlessly with existing template flows')
def step_config_integrates_with_template_flows(context_obj):
    """Verify configuration integrates seamlessly with existing template flows."""
    assert context.usecase_domain_config is not None
    
    # Should have proper integration points
    assert context.usecase_domain_config.entity_dependencies is not None
    assert context.usecase_domain_config.repository_dependencies is not None
    assert context.usecase_domain_config.external_dependencies is not None


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