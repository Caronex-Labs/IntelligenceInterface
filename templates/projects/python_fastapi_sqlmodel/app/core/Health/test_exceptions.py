"""Tests for Health domain exceptions - Generated from Co-located Template.

This module contains comprehensive tests for the generated domain exceptions
in the Health domain, following hexagonal architecture testing principles.

Generated from:
- domain.yaml: Base domain configuration
- entities.yaml: Entity-specific exception requirements
- test_exceptions.py.j2: This Jinja2 test template

Co-location Architecture:
- Test templates, configurations, and generated tests in same directory
- Tests generated alongside the actual exception code
- @pyhex preservation markers for custom test logic
"""

# Standard library imports
import pytest
from uuid import uuid4

# Third-party imports
from fastapi import HTTPException
from starlette import status

# Local imports - Generated exceptions
from .exceptions import (
    ExceptionSeverity,
    ExceptionCategory,
    HealthExceptionContext,
    BaseHealthException,
    HealthCheckNotFoundError,
    HealthCheckValidationError,
    HealthCheckBusinessRuleError,
    create_not_found_error,
    register_exception_handlers,
)

# @pyhex:begin:custom_imports
# Add your custom test imports here
# @pyhex:end:custom_imports


class TestExceptionEnums:
    """Test cases for exception enumeration classes."""
    
    def test_exception_severity_values(self):
        """Test ExceptionSeverity enum values."""
        assert ExceptionSeverity.LOW == "low"
        assert ExceptionSeverity.MEDIUM == "medium"
        assert ExceptionSeverity.HIGH == "high"
        assert ExceptionSeverity.CRITICAL == "critical"
        
        # Test all values are present
        expected_severities = {"low", "medium", "high", "critical"}
        actual_severities = {severity.value for severity in ExceptionSeverity}
        assert expected_severities == actual_severities

    def test_exception_category_values(self):
        """Test ExceptionCategory enum values."""
        assert ExceptionCategory.VALIDATION == "validation"
        assert ExceptionCategory.BUSINESS_RULE == "business_rule"
        assert ExceptionCategory.NOT_FOUND == "not_found"
        assert ExceptionCategory.PERMISSION == "permission"
        assert ExceptionCategory.SYSTEM == "system"
        
        # Test all values are present
        expected_categories = {"validation", "business_rule", "not_found", "permission", "system"}
        actual_categories = {category.value for category in ExceptionCategory}
        assert expected_categories == actual_categories


class TestExceptionContext:
    """Test cases for HealthExceptionContext."""
    
    def test_context_creation_minimal(self):
        """Test creating exception context with minimal data."""
        context = HealthExceptionContext(
            error_code="TEST_001",
            message="Test error message"
        )
        
        assert context.error_code == "TEST_001"
        assert context.message == "Test error message"
        assert context.severity == ExceptionSeverity.MEDIUM  # Default
        assert context.category == ExceptionCategory.SYSTEM  # Default
        assert context.details == {}  # Default
        assert context.user_message is None  # Default
        assert context.correlation_id is not None  # Auto-generated

    def test_context_creation_complete(self):
        """Test creating exception context with complete data."""
        test_details = {"field": "test_field", "value": "test_value"}
        test_correlation_id = str(uuid4())
        
        context = HealthExceptionContext(
            error_code="TEST_002",
            message="Complete test error",
            severity=ExceptionSeverity.HIGH,
            category=ExceptionCategory.VALIDATION,
            details=test_details,
            user_message="User-friendly error message",
            correlation_id=test_correlation_id
        )
        
        assert context.error_code == "TEST_002"
        assert context.message == "Complete test error"
        assert context.severity == ExceptionSeverity.HIGH
        assert context.category == ExceptionCategory.VALIDATION
        assert context.details == test_details
        assert context.user_message == "User-friendly error message"
        assert context.correlation_id == test_correlation_id

    def test_context_validation(self):
        """Test exception context field validation."""
        # Test invalid severity
        with pytest.raises(ValueError):
            HealthExceptionContext(
                error_code="TEST_003",
                message="Test message",
                severity="invalid_severity"
            )
        
        # Test invalid category
        with pytest.raises(ValueError):
            HealthExceptionContext(
                error_code="TEST_004",
                message="Test message",
                category="invalid_category"
            )


class TestBaseHealthException:
    """Test cases for BaseHealthException."""
    
    def test_base_exception_creation(self):
        """Test creating base exception."""
        context = HealthExceptionContext(
            error_code="BASE_001",
            message="Base exception test"
        )
        
        exception = BaseHealthException(context)
        
        assert exception.context == context
        assert str(exception) == "Base exception test"
        assert exception.context.error_code == "BASE_001"

    def test_base_exception_http_status(self):
        """Test base exception HTTP status code."""
        context = HealthExceptionContext(
            error_code="BASE_002",
            message="Base exception test"
        )
        
        exception = BaseHealthException(context)
        assert exception.http_status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_base_exception_to_http_exception(self):
        """Test converting base exception to HTTPException."""
        context = HealthExceptionContext(
            error_code="BASE_003",
            message="Base exception test",
            user_message="User-friendly message"
        )
        
        exception = BaseHealthException(context)
        http_exception = exception.to_http_exception()
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "User-friendly message" in str(http_exception.detail)


class TestHealthCheckExceptions:
    """Test cases for HealthCheck specific exceptions."""
    
    def test_healthcheck_not_found_error(self):
        """Test HealthCheckNotFoundError."""
        entity_id = str(uuid4())
        exception = HealthCheckNotFoundError(entity_id)
        
        assert entity_id in str(exception)
        assert exception.http_status_code == status.HTTP_404_NOT_FOUND
        assert exception.context.category == ExceptionCategory.NOT_FOUND
        assert exception.context.error_code.startswith("HEALTHCHECK_NOT_FOUND")

    def test_healthcheck_not_found_http_conversion(self):
        """Test HealthCheckNotFoundError HTTP conversion."""
        entity_id = str(uuid4())
        exception = HealthCheckNotFoundError(entity_id)
        http_exception = exception.to_http_exception()
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_404_NOT_FOUND
        assert entity_id in str(http_exception.detail)

    def test_healthcheck_validation_error(self):
        """Test HealthCheckValidationError."""
        field_errors = {"name": "Name is required", "email": "Invalid email format"}
        exception = HealthCheckValidationError(field_errors)
        
        assert exception.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exception.context.category == ExceptionCategory.VALIDATION
        assert exception.context.error_code.startswith("HEALTHCHECK_VALIDATION")
        assert exception.context.details == field_errors

    def test_healthcheck_validation_error_single_field(self):
        """Test HealthCheckValidationError with single field."""
        exception = HealthCheckValidationError("name", "Name is required")
        
        assert exception.context.details == {"name": "Name is required"}
        assert "name" in str(exception)
        assert "Name is required" in str(exception)

    def test_healthcheck_business_rule_error(self):
        """Test HealthCheckBusinessRuleError."""
        rule_name = "unique_email_rule"
        rule_description = "Email must be unique"
        exception = HealthCheckBusinessRuleError(rule_name, rule_description)
        
        assert exception.http_status_code == status.HTTP_409_CONFLICT
        assert exception.context.category == ExceptionCategory.BUSINESS_RULE
        assert exception.context.error_code.startswith("HEALTHCHECK_BUSINESS_RULE")
        assert rule_name in str(exception)
        assert rule_description in str(exception)

    def test_healthcheck_business_rule_http_conversion(self):
        """Test HealthCheckBusinessRuleError HTTP conversion."""
        rule_name = "test_rule"
        rule_description = "Test business rule violation"
        exception = HealthCheckBusinessRuleError(rule_name, rule_description)
        http_exception = exception.to_http_exception()
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_409_CONFLICT
        assert rule_name in str(http_exception.detail)

    # @pyhex:begin:custom_healthcheck_exception_tests
    # Add your custom HealthCheck exception tests here
    # @pyhex:end:custom_healthcheck_exception_tests



class TestExceptionHelpers:
    """Test cases for exception helper functions."""
    
    def test_create_not_found_error_function(self):
        """Test create_not_found_error helper function."""
        entity_type = "TestEntity"
        entity_id = str(uuid4())
        
        exception = create_not_found_error(entity_type, entity_id)
        
        assert isinstance(exception, BaseHealthException)
        assert exception.context.category == ExceptionCategory.NOT_FOUND
        assert entity_type in str(exception)
        assert entity_id in str(exception)

    def test_create_not_found_error_with_criteria(self):
        """Test create_not_found_error with search criteria."""
        entity_type = "TestEntity"
        criteria = {"name": "test_name", "status": "active"}
        
        exception = create_not_found_error(entity_type, criteria=criteria)
        
        assert isinstance(exception, BaseHealthException)
        assert exception.context.details == criteria
        assert "name: test_name" in str(exception)
        assert "status: active" in str(exception)


class TestExceptionHandlerRegistration:
    """Test cases for exception handler registration."""
    
    def test_register_exception_handlers_callable(self):
        """Test that register_exception_handlers is callable."""
        # Note: Full testing would require FastAPI app instance
        # This test verifies the function exists and is callable
        assert callable(register_exception_handlers)
        
        # Mock FastAPI app for testing
        class MockApp:
            def __init__(self):
                self.exception_handlers = {}
            
            def add_exception_handler(self, exc_class, handler):
                self.exception_handlers[exc_class] = handler
        
        mock_app = MockApp()
        register_exception_handlers(mock_app)
        
        # Verify exception handlers were registered
        assert len(mock_app.exception_handlers) > 0


class TestExceptionIntegration:
    """Integration tests for all exceptions in Health domain."""
    
    def test_all_exceptions_inherit_base(self):
        """Test that all exceptions inherit from base exception."""
        assert issubclass(HealthCheckNotFoundError, BaseHealthException)
        assert issubclass(HealthCheckValidationError, BaseHealthException)
        assert issubclass(HealthCheckBusinessRuleError, BaseHealthException)

    def test_all_exceptions_have_http_status(self):
        """Test that all exceptions have appropriate HTTP status codes."""
        # Create sample exceptions
        not_found = HealthCheckNotFoundError("test-id")
        validation = HealthCheckValidationError({"field": "error"})
        business_rule = HealthCheckBusinessRuleError("rule", "description")
        
        # Verify HTTP status codes
        assert not_found.http_status_code == status.HTTP_404_NOT_FOUND
        assert validation.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert business_rule.http_status_code == status.HTTP_409_CONFLICT

    def test_exception_context_consistency(self):
        """Test that all exceptions have consistent context structure."""
        exceptions = [
            HealthCheckNotFoundError("test-id"),
            HealthCheckValidationError({"field": "error"}),
            HealthCheckBusinessRuleError("rule", "description")
        ]
        
        for exception in exceptions:
            assert hasattr(exception, 'context')
            assert isinstance(exception.context, HealthExceptionContext)
            assert exception.context.error_code is not None
            assert exception.context.message is not None
            assert exception.context.correlation_id is not None

    # @pyhex:begin:custom_integration_tests
    # Add your custom integration tests here
    # @pyhex:end:custom_integration_tests


# @pyhex:begin:custom_test_classes
# Add your custom test classes here
# @pyhex:end:custom_test_classes


if __name__ == "__main__":
    pytest.main([__file__])