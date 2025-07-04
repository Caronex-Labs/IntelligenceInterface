"""Tests for  domain exceptions - Generated from Enhanced Co-located Template.
This module contains comprehensive tests for the generated domain exceptions
in the TaskManager domain, following hexagonal architecture testing principles.
Generated from:
- domain.yaml: Base domain configuration
- entities.yaml: Entity-specific exception requirements
- test_exceptions.py.j2: This enhanced Jinja2 test template with best practices
Co-location Architecture:
- Test templates, configurations, and generated tests in same directory
- Tests generated alongside the actual exception code
- @pyhex preservation markers for custom test logic
Jinja2 Best Practices Applied:
- Macros for repeated exception test pattern generation
- Proper variable scoping with Jinja2 set tags
- Filters for text transformation (|upper, |lower)
- Tests for conditional logic (is defined, is not none)
- Template structure improvements with clear sections
"""
# Standard library imports
import pytest
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
# Third-party imports
from fastapi import HTTPException
from starlette import status
# Local imports - Generated exceptions
from .exceptions import (
ExceptionSeverity,
ExceptionCategory,
  ProjectExceptionContext,
    BaseProjectException,
    ProjectNotFoundError,
    ProjectValidationError,
    ProjectBusinessRuleError,
  TaskExceptionContext,
    BaseTaskException,
    TaskNotFoundError,
    TaskValidationError,
    TaskBusinessRuleError,
  TaskCommentExceptionContext,
    BaseTaskCommentException,
    TaskCommentNotFoundError,
    TaskCommentValidationError,
    TaskCommentBusinessRuleError,
create_not_found_error,
register_exception_handlers,
)
# @pyhex:begin:custom_imports
# Add your custom test imports here
# @pyhex:end:custom_imports
class TestExceptionEnums:
"""Test cases for exception enumeration classes."""
  def test_exceptionseverity_values(self):
  """Test ExceptionSeverity enum values."""
assert ExceptionSeverity.CRITICAL == "critical"assert ExceptionSeverity.ERROR == "error"assert ExceptionSeverity.WARNING == "warning"assert ExceptionSeverity.INFO == "info"assert ExceptionSeverity.DEBUG == "debug"  # Test all values are present
  expected_values = {
"critical", "error", "warning", "info", "debug"  }
  actual_values = { exceptionseverity.value for exceptionseverity in ExceptionSeverity }
  assert expected_values == actual_values

  def test_exceptioncategory_values(self):
  """Test ExceptionCategory enum values."""
assert ExceptionCategory.VALIDATION == "validation"assert ExceptionCategory.BUSINESS_RULE == "business_rule"assert ExceptionCategory.NOT_FOUND == "not_found"assert ExceptionCategory.AUTHORIZATION == "authorization"assert ExceptionCategory.INTEGRATION == "integration"assert ExceptionCategory.SYSTEM == "system"  # Test all values are present
  expected_values = {
"validation", "business_rule", "not_found", "authorization", "integration", "system"  }
  actual_values = { exceptioncategory.value for exceptioncategory in ExceptionCategory }
  assert expected_values == actual_values

class TestExceptionContext:
"""Test cases for ExceptionContext."""
def test_context_creation_minimal(self):
"""Test creating exception context with minimal data."""
context = ExceptionContext(
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
context = ExceptionContext(
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
ExceptionContext(
error_code="TEST_003",
message="Test message",
severity="invalid_severity"
)
# Test invalid category
with pytest.raises(ValueError):
ExceptionContext(
error_code="TEST_004",
message="Test message",
category="invalid_category"
)
class TestBaseException:
"""Test cases for BaseException."""
def test_base_exception_creation(self):
"""Test creating base exception."""
context = ExceptionContext(
error_code="BASE_001",
message="Base exception test"
)
exception = BaseException(context)
assert exception.context == context
assert str(exception) == "Base exception test"
assert exception.context.error_code == "BASE_001"
def test_base_exception_http_status(self):
"""Test base exception HTTP status code."""
context = ExceptionContext(
error_code="BASE_002",
message="Base exception test"
)
exception = BaseException(context)
assert exception.http_status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
def test_base_exception_to_http_exception(self):
"""Test converting base exception to HTTPException."""
context = ExceptionContext(
error_code="BASE_003",
message="Base exception test",
user_message="User-friendly message"
)
exception = BaseException(context)
http_exception = exception.to_http_exception()
assert isinstance(http_exception, HTTPException)
assert http_exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
assert "User-friendly message" in str(http_exception.detail)
  class TestProjectExceptions:
  """Test cases for Project specific exceptions."""
  def test_project_not_found_error(self):
  """Test ProjectNotFoundError."""
  entity_id = str(uuid4())
  exception = ProjectNotFoundError(entity_id)
  assert entity_id in str(exception)
  assert exception.http_status_code == status.HTTP_404_NOT_FOUND
  assert exception.context.category == ExceptionCategory.NOT_FOUND
  assert exception.context.error_code.startswith("PROJECT_NOT_FOUND")

  def test_project_not_found_http_conversion(self):
  """Test ProjectNotFoundError HTTP conversion."""
  entity_id = str(uuid4())
  exception = ProjectNotFoundError(entity_id)
  http_exception = exception.to_http_exception()
  assert isinstance(http_exception, HTTPException)
  assert http_exception.status_code == status.HTTP_404_NOT_FOUND
  assert entity_id in str(http_exception.detail)
  def test_project_validation_error(self):
  """Test ProjectValidationError."""
  field_errors = {"name": "Name is required", "email": "Invalid email format"}
  exception = ProjectValidationError(field_errors)
  assert exception.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  assert exception.context.category == ExceptionCategory.VALIDATION
  assert exception.context.error_code.startswith("PROJECT_VALIDATION")
  assert exception.context.details == field_errors
  def test_project_validation_error_single_field(self):
  """Test ProjectValidationError with single field."""
  exception = ProjectValidationError("name", "Name is required")
  assert exception.context.details == {"name": "Name is required"}
  assert "name" in str(exception)
  assert "Name is required" in str(exception)
  def test_project_business_rule_error(self):
  """Test ProjectBusinessRuleError."""
  rule_name = "unique_email_rule"
  rule_description = "Email must be unique"
  exception = ProjectBusinessRuleError(rule_name, rule_description)
  assert exception.http_status_code == status.HTTP_409_CONFLICT
  assert exception.context.category == ExceptionCategory.BUSINESS_RULE
  assert exception.context.error_code.startswith("PROJECT_BUSINESS_RULE")
  assert rule_name in str(exception)
  assert rule_description in str(exception)
  def test_project_business_rule_http_conversion(self):
  """Test ProjectBusinessRuleError HTTP conversion."""
  rule_name = "test_rule"
  rule_description = "Test business rule violation"
  exception = ProjectBusinessRuleError(rule_name, rule_description)
  http_exception = exception.to_http_exception()
  assert isinstance(http_exception, HTTPException)
  assert http_exception.status_code == status.HTTP_409_CONFLICT
  assert rule_name in str(http_exception.detail)
  # @pyhex:begin:custom_project_exception_tests
  # Add your custom Project exception tests here
  # @pyhex:end:custom_project_exception_tests
  class TestTaskExceptions:
  """Test cases for Task specific exceptions."""
  def test_task_not_found_error(self):
  """Test TaskNotFoundError."""
  entity_id = str(uuid4())
  exception = TaskNotFoundError(entity_id)
  assert entity_id in str(exception)
  assert exception.http_status_code == status.HTTP_404_NOT_FOUND
  assert exception.context.category == ExceptionCategory.NOT_FOUND
  assert exception.context.error_code.startswith("TASK_NOT_FOUND")

  def test_task_not_found_http_conversion(self):
  """Test TaskNotFoundError HTTP conversion."""
  entity_id = str(uuid4())
  exception = TaskNotFoundError(entity_id)
  http_exception = exception.to_http_exception()
  assert isinstance(http_exception, HTTPException)
  assert http_exception.status_code == status.HTTP_404_NOT_FOUND
  assert entity_id in str(http_exception.detail)
  def test_task_validation_error(self):
  """Test TaskValidationError."""
  field_errors = {"name": "Name is required", "email": "Invalid email format"}
  exception = TaskValidationError(field_errors)
  assert exception.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  assert exception.context.category == ExceptionCategory.VALIDATION
  assert exception.context.error_code.startswith("TASK_VALIDATION")
  assert exception.context.details == field_errors
  def test_task_validation_error_single_field(self):
  """Test TaskValidationError with single field."""
  exception = TaskValidationError("name", "Name is required")
  assert exception.context.details == {"name": "Name is required"}
  assert "name" in str(exception)
  assert "Name is required" in str(exception)
  def test_task_business_rule_error(self):
  """Test TaskBusinessRuleError."""
  rule_name = "unique_email_rule"
  rule_description = "Email must be unique"
  exception = TaskBusinessRuleError(rule_name, rule_description)
  assert exception.http_status_code == status.HTTP_409_CONFLICT
  assert exception.context.category == ExceptionCategory.BUSINESS_RULE
  assert exception.context.error_code.startswith("TASK_BUSINESS_RULE")
  assert rule_name in str(exception)
  assert rule_description in str(exception)
  def test_task_business_rule_http_conversion(self):
  """Test TaskBusinessRuleError HTTP conversion."""
  rule_name = "test_rule"
  rule_description = "Test business rule violation"
  exception = TaskBusinessRuleError(rule_name, rule_description)
  http_exception = exception.to_http_exception()
  assert isinstance(http_exception, HTTPException)
  assert http_exception.status_code == status.HTTP_409_CONFLICT
  assert rule_name in str(http_exception.detail)
  # @pyhex:begin:custom_task_exception_tests
  # Add your custom Task exception tests here
  # @pyhex:end:custom_task_exception_tests
  class TestTaskCommentExceptions:
  """Test cases for TaskComment specific exceptions."""
  def test_taskcomment_not_found_error(self):
  """Test TaskCommentNotFoundError."""
  entity_id = str(uuid4())
  exception = TaskCommentNotFoundError(entity_id)
  assert entity_id in str(exception)
  assert exception.http_status_code == status.HTTP_404_NOT_FOUND
  assert exception.context.category == ExceptionCategory.NOT_FOUND
  assert exception.context.error_code.startswith("TASKCOMMENT_NOT_FOUND")

  def test_taskcomment_not_found_http_conversion(self):
  """Test TaskCommentNotFoundError HTTP conversion."""
  entity_id = str(uuid4())
  exception = TaskCommentNotFoundError(entity_id)
  http_exception = exception.to_http_exception()
  assert isinstance(http_exception, HTTPException)
  assert http_exception.status_code == status.HTTP_404_NOT_FOUND
  assert entity_id in str(http_exception.detail)
  def test_taskcomment_validation_error(self):
  """Test TaskCommentValidationError."""
  field_errors = {"name": "Name is required", "email": "Invalid email format"}
  exception = TaskCommentValidationError(field_errors)
  assert exception.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  assert exception.context.category == ExceptionCategory.VALIDATION
  assert exception.context.error_code.startswith("TASKCOMMENT_VALIDATION")
  assert exception.context.details == field_errors
  def test_taskcomment_validation_error_single_field(self):
  """Test TaskCommentValidationError with single field."""
  exception = TaskCommentValidationError("name", "Name is required")
  assert exception.context.details == {"name": "Name is required"}
  assert "name" in str(exception)
  assert "Name is required" in str(exception)
  def test_taskcomment_business_rule_error(self):
  """Test TaskCommentBusinessRuleError."""
  rule_name = "unique_email_rule"
  rule_description = "Email must be unique"
  exception = TaskCommentBusinessRuleError(rule_name, rule_description)
  assert exception.http_status_code == status.HTTP_409_CONFLICT
  assert exception.context.category == ExceptionCategory.BUSINESS_RULE
  assert exception.context.error_code.startswith("TASKCOMMENT_BUSINESS_RULE")
  assert rule_name in str(exception)
  assert rule_description in str(exception)
  def test_taskcomment_business_rule_http_conversion(self):
  """Test TaskCommentBusinessRuleError HTTP conversion."""
  rule_name = "test_rule"
  rule_description = "Test business rule violation"
  exception = TaskCommentBusinessRuleError(rule_name, rule_description)
  http_exception = exception.to_http_exception()
  assert isinstance(http_exception, HTTPException)
  assert http_exception.status_code == status.HTTP_409_CONFLICT
  assert rule_name in str(http_exception.detail)
  # @pyhex:begin:custom_taskcomment_exception_tests
  # Add your custom TaskComment exception tests here
  # @pyhex:end:custom_taskcomment_exception_tests
class TestExceptionHelpers:
"""Test cases for exception helper functions."""
def test_create_not_found_error_function(self):
"""Test create_not_found_error helper function."""
entity_type = "TestEntity"
entity_id = str(uuid4())
exception = create_not_found_error(entity_type, entity_id)
assert isinstance(exception, BaseException)
assert exception.context.category == ExceptionCategory.NOT_FOUND
assert entity_type in str(exception)
assert entity_id in str(exception)
def test_create_not_found_error_with_criteria(self):
"""Test create_not_found_error with search criteria."""
entity_type = "TestEntity"
criteria = {"name": "test_name", "status": "active"}
exception = create_not_found_error(entity_type, criteria=criteria)
assert isinstance(exception, BaseException)
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
"""Integration tests for all exceptions in TaskManager domain."""
def test_all_exceptions_inherit_base(self):
"""Test that all exceptions inherit from base exception."""
  assert issubclass(ProjectNotFoundError, BaseException)
  assert issubclass(ProjectValidationError, BaseException)
  assert issubclass(ProjectBusinessRuleError, BaseException)
  assert issubclass(TaskNotFoundError, BaseException)
  assert issubclass(TaskValidationError, BaseException)
  assert issubclass(TaskBusinessRuleError, BaseException)
  assert issubclass(TaskCommentNotFoundError, BaseException)
  assert issubclass(TaskCommentValidationError, BaseException)
  assert issubclass(TaskCommentBusinessRuleError, BaseException)
def test_all_exceptions_have_http_status(self):
"""Test that all exceptions have appropriate HTTP status codes."""
  # Create sample exceptions for Project
  not_found = ProjectNotFoundError("test-id")
  validation = ProjectValidationError({"field": "error"})
  business_rule = ProjectBusinessRuleError("rule", "description")
  # Verify HTTP status codes for Project
  assert not_found.http_status_code == status.HTTP_404_NOT_FOUND
  assert validation.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  assert business_rule.http_status_code == status.HTTP_409_CONFLICT
  # Create sample exceptions for Task
  not_found = TaskNotFoundError("test-id")
  validation = TaskValidationError({"field": "error"})
  business_rule = TaskBusinessRuleError("rule", "description")
  # Verify HTTP status codes for Task
  assert not_found.http_status_code == status.HTTP_404_NOT_FOUND
  assert validation.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  assert business_rule.http_status_code == status.HTTP_409_CONFLICT
  # Create sample exceptions for TaskComment
  not_found = TaskCommentNotFoundError("test-id")
  validation = TaskCommentValidationError({"field": "error"})
  business_rule = TaskCommentBusinessRuleError("rule", "description")
  # Verify HTTP status codes for TaskComment
  assert not_found.http_status_code == status.HTTP_404_NOT_FOUND
  assert validation.http_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  assert business_rule.http_status_code == status.HTTP_409_CONFLICT
def test_exception_context_consistency(self):
"""Test that all exceptions have consistent context structure."""
  exceptions = [
  ProjectNotFoundError("test-id"),
  ProjectValidationError({"field": "error"}),
  ProjectBusinessRuleError("rule", "description")
  ]
  for exception in exceptions:
  assert hasattr(exception, 'context')
  assert isinstance(exception.context, ExceptionContext)
  assert exception.context.error_code is not None
  assert exception.context.message is not None
  assert exception.context.correlation_id is not None
  exceptions = [
  TaskNotFoundError("test-id"),
  TaskValidationError({"field": "error"}),
  TaskBusinessRuleError("rule", "description")
  ]
  for exception in exceptions:
  assert hasattr(exception, 'context')
  assert isinstance(exception.context, ExceptionContext)
  assert exception.context.error_code is not None
  assert exception.context.message is not None
  assert exception.context.correlation_id is not None
  exceptions = [
  TaskCommentNotFoundError("test-id"),
  TaskCommentValidationError({"field": "error"}),
  TaskCommentBusinessRuleError("rule", "description")
  ]
  for exception in exceptions:
  assert hasattr(exception, 'context')
  assert isinstance(exception.context, ExceptionContext)
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