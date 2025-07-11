"""Health domain exceptions - Generated from Co-located Template.

This module contains domain-specific exceptions for the Health domain following
hexagonal architecture principles with co-location pattern implementation.

Generated from:
- domain.yaml: Base exception configuration and error patterns
- entities.yaml: Entity-specific exception patterns
- exceptions.py.j2: This Jinja2 template

Co-location Architecture:
- Templates, configurations, and generated files in same directory
- Hierarchical configuration merging for complete exception context
- @pyhex preservation markers for custom exception logic
"""

# Standard library imports
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

# Third-party imports
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

# @pyhex:begin:custom_imports
# Add custom imports here - preserved during regeneration
# @pyhex:end:custom_imports


# Exception severity levels
class ExceptionSeverity(str, Enum):
    """Exception severity levels for logging and monitoring."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


# Exception categories for domain organization
class ExceptionCategory(str, Enum):
    """Exception categories for domain organization."""
    VALIDATION = "validation"
    BUSINESS_RULE = "business_rule"
    NOT_FOUND = "not_found"
    AUTHORIZATION = "authorization"
    INTEGRATION = "integration"
    SYSTEM = "system"


# Base Domain Exception Structure
class HealthExceptionContext(BaseModel):
    """Exception context for structured error information."""
    
    error_code: str = Field(..., description="Unique error code")
    error_message: str = Field(..., description="Human-readable error message")
    category: ExceptionCategory = Field(..., description="Exception category")
    severity: ExceptionSeverity = Field(default=ExceptionSeverity.ERROR, description="Exception severity")
    entity_type: Optional[str] = Field(None, description="Entity type if applicable")
    entity_id: Optional[str] = Field(None, description="Entity ID if applicable")
    field_name: Optional[str] = Field(None, description="Field name if applicable")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    
    # @pyhex:begin:custom_context_fields
    # Add custom context fields here - preserved during regeneration
    # @pyhex:end:custom_context_fields


class BaseHealthException(Exception):
    """Base exception class for Health domain.
    
    This base class provides structured error handling with error codes,
    severity levels, and context information following hexagonal architecture.
    """
    
    def __init__(
        self,
        error_code: str,
        error_message: str,
        category: ExceptionCategory,
        severity: ExceptionSeverity = ExceptionSeverity.ERROR,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        field_name: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize base domain exception.
        
        Args:
            error_code: Unique error code for this exception
            error_message: Human-readable error message
            category: Exception category
            severity: Exception severity level
            entity_type: Entity type if applicable
            entity_id: Entity ID if applicable
            field_name: Field name if applicable
            context_data: Additional context data
            **kwargs: Additional keyword arguments
        """
        super().__init__(error_message)
        
        self.context = HealthExceptionContext(
            error_code=error_code,
            error_message=error_message,
            category=category,
            severity=severity,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            context_data=context_data or {}
        )
        
        # Log exception based on severity
        self._log_exception()
        
        # @pyhex:begin:custom_init_logic
        # Add custom initialization logic here - preserved during regeneration
        # @pyhex:end:custom_init_logic
    
    def _log_exception(self):
        """Log exception based on severity level."""
        logger = logging.getLogger("Health.exceptions")
        
        log_data = {
            "error_code": self.context.error_code,
            "category": self.context.category.value,
            "entity_type": self.context.entity_type,
            "entity_id": self.context.entity_id,
            "field_name": self.context.field_name,
            "context_data": self.context.context_data
        }
        
        if self.context.severity == ExceptionSeverity.CRITICAL:
            logger.critical(self.context.error_message, extra=log_data)
        elif self.context.severity == ExceptionSeverity.ERROR:
            logger.error(self.context.error_message, extra=log_data)
        elif self.context.severity == ExceptionSeverity.WARNING:
            logger.warning(self.context.error_message, extra=log_data)
        elif self.context.severity == ExceptionSeverity.INFO:
            logger.info(self.context.error_message, extra=log_data)
        else:
            logger.debug(self.context.error_message, extra=log_data)
    
    def to_fastapi_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException.
        
        Returns:
            HTTPException: FastAPI-compatible exception
        """
        # Map domain exception categories to HTTP status codes
        status_code_map = {
            ExceptionCategory.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ExceptionCategory.VALIDATION: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ExceptionCategory.BUSINESS_RULE: status.HTTP_400_BAD_REQUEST,
            ExceptionCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
            ExceptionCategory.INTEGRATION: status.HTTP_502_BAD_GATEWAY,
            ExceptionCategory.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        
        status_code = status_code_map.get(
            self.context.category, 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        detail = {
            "error_code": self.context.error_code,
            "error_message": self.context.error_message,
            "category": self.context.category.value,
            "entity_type": self.context.entity_type,
            "entity_id": self.context.entity_id,
            "field_name": self.context.field_name,
            "context_data": self.context.context_data
        }
        
        # @pyhex:begin:custom_fastapi_conversion
        # Add custom FastAPI conversion logic here - preserved during regeneration
        # @pyhex:end:custom_fastapi_conversion
        
        return HTTPException(status_code=status_code, detail=detail)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary.
        
        Returns:
            Dict[str, Any]: Exception as dictionary
        """
        return self.context.dict()
    
    def __str__(self) -> str:
        """String representation of exception."""
        return f"[{self.context.error_code}] {self.context.error_message}"
    
    def __repr__(self) -> str:
        """Detailed string representation of exception."""
        return (
            f"{self.__class__.__name__}("
            f"error_code='{self.context.error_code}', "
            f"category='{self.context.category.value}', "
            f"entity_type='{self.context.entity_type}', "
            f"entity_id='{self.context.entity_id}')"
        )
    
    # @pyhex:begin:custom_base_methods
    # Add custom base exception methods here - preserved during regeneration
    # @pyhex:end:custom_base_methods


# Specific Domain Exception Classes
class HealthNotFoundError(BaseHealthException):
    """Exception raised when a Health entity is not found."""
    
    def __init__(
        self,
        entity_type: str,
        entity_id: Optional[str] = None,
        field_name: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize not found exception.
        
        Args:
            entity_type: Type of entity that was not found
            entity_id: ID of entity that was not found
            field_name: Field name if applicable
            context_data: Additional context data
        """
        error_code = "_NOT_FOUND"
        
        if entity_id:
            error_message = f"{entity_type} with ID '{entity_id}' not found"
        elif field_name:
            error_message = f"{entity_type} with {field_name} not found"
        else:
            error_message = f"{entity_type} not found"
        
        super().__init__(
            error_code=error_code,
            error_message=error_message,
            category=ExceptionCategory.NOT_FOUND,
            severity=ExceptionSeverity.WARNING,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            context_data=context_data
        )
        
        # @pyhex:begin:custom_not_found_init
        # Add custom not found initialization logic here - preserved during regeneration
        # @pyhex:end:custom_not_found_init


class HealthValidationError(BaseHealthException):
    """Exception raised when Health validation fails."""
    
    def __init__(
        self,
        field_name: str,
        field_value: Any,
        validation_rule: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize validation exception.
        
        Args:
            field_name: Name of field that failed validation
            field_value: Value that failed validation
            validation_rule: Validation rule that was violated
            entity_type: Entity type if applicable
            entity_id: Entity ID if applicable
            context_data: Additional context data
        """
        error_code = "_VALIDATION_ERROR"
        error_message = f"Validation failed for field '{field_name}': {validation_rule}"
        
        validation_context = {
            "field_value": str(field_value),
            "validation_rule": validation_rule,
            **(context_data or {})
        }
        
        super().__init__(
            error_code=error_code,
            error_message=error_message,
            category=ExceptionCategory.VALIDATION,
            severity=ExceptionSeverity.WARNING,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            context_data=validation_context
        )
        
        # @pyhex:begin:custom_validation_init
        # Add custom validation initialization logic here - preserved during regeneration
        # @pyhex:end:custom_validation_init


class HealthBusinessRuleError(BaseHealthException):
    """Exception raised when Health business rules are violated."""
    
    def __init__(
        self,
        rule_name: str,
        rule_description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize business rule exception.
        
        Args:
            rule_name: Name of business rule that was violated
            rule_description: Description of business rule violation
            entity_type: Entity type if applicable
            entity_id: Entity ID if applicable
            context_data: Additional context data
        """
        error_code = "_BUSINESS_RULE_ERROR"
        error_message = f"Business rule '{rule_name}' violated: {rule_description}"
        
        business_context = {
            "rule_name": rule_name,
            "rule_description": rule_description,
            **(context_data or {})
        }
        
        super().__init__(
            error_code=error_code,
            error_message=error_message,
            category=ExceptionCategory.BUSINESS_RULE,
            severity=ExceptionSeverity.ERROR,
            entity_type=entity_type,
            entity_id=entity_id,
            context_data=business_context
        )
        
        # @pyhex:begin:custom_business_rule_init
        # Add custom business rule initialization logic here - preserved during regeneration
        # @pyhex:end:custom_business_rule_init


class HealthAuthorizationError(BaseHealthException):
    """Exception raised when Health authorization fails."""
    
    def __init__(
        self,
        user_id: str,
        action: str,
        resource: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize authorization exception.
        
        Args:
            user_id: ID of user attempting action
            action: Action that was attempted
            resource: Resource being accessed
            entity_type: Entity type if applicable
            entity_id: Entity ID if applicable
            context_data: Additional context data
        """
        error_code = "_AUTHORIZATION_ERROR"
        error_message = f"User '{user_id}' not authorized to {action} {resource}"
        
        auth_context = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            **(context_data or {})
        }
        
        super().__init__(
            error_code=error_code,
            error_message=error_message,
            category=ExceptionCategory.AUTHORIZATION,
            severity=ExceptionSeverity.WARNING,
            entity_type=entity_type,
            entity_id=entity_id,
            context_data=auth_context
        )
        
        # @pyhex:begin:custom_authorization_init
        # Add custom authorization initialization logic here - preserved during regeneration
        # @pyhex:end:custom_authorization_init


class HealthIntegrationError(BaseHealthException):
    """Exception raised when Health integration fails."""
    
    def __init__(
        self,
        integration_name: str,
        operation: str,
        error_details: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize integration exception.
        
        Args:
            integration_name: Name of integration that failed
            operation: Operation that was attempted
            error_details: Details of integration error
            entity_type: Entity type if applicable
            entity_id: Entity ID if applicable
            context_data: Additional context data
        """
        error_code = "_INTEGRATION_ERROR"
        error_message = f"Integration '{integration_name}' failed during {operation}: {error_details}"
        
        integration_context = {
            "integration_name": integration_name,
            "operation": operation,
            "error_details": error_details,
            **(context_data or {})
        }
        
        super().__init__(
            error_code=error_code,
            error_message=error_message,
            category=ExceptionCategory.INTEGRATION,
            severity=ExceptionSeverity.ERROR,
            entity_type=entity_type,
            entity_id=entity_id,
            context_data=integration_context
        )
        
        # @pyhex:begin:custom_integration_init
        # Add custom integration initialization logic here - preserved during regeneration
        # @pyhex:end:custom_integration_init


class HealthSystemError(BaseHealthException):
    """Exception raised when Health system errors occur."""
    
    def __init__(
        self,
        system_component: str,
        error_details: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize system exception.
        
        Args:
            system_component: System component that failed
            error_details: Details of system error
            entity_type: Entity type if applicable
            entity_id: Entity ID if applicable
            context_data: Additional context data
        """
        error_code = "_SYSTEM_ERROR"
        error_message = f"System component '{system_component}' failed: {error_details}"
        
        system_context = {
            "system_component": system_component,
            "error_details": error_details,
            **(context_data or {})
        }
        
        super().__init__(
            error_code=error_code,
            error_message=error_message,
            category=ExceptionCategory.SYSTEM,
            severity=ExceptionSeverity.CRITICAL,
            entity_type=entity_type,
            entity_id=entity_id,
            context_data=system_context
        )
        
        # @pyhex:begin:custom_system_init
        # Add custom system initialization logic here - preserved during regeneration
        # @pyhex:end:custom_system_init


# @pyhex:begin:custom_exception_classes
# Add custom exception classes here - preserved during regeneration
# @pyhex:end:custom_exception_classes


# Exception Factory Functions
def create_not_found_error(
    entity_type: str,
    entity_id: Optional[str] = None,
    field_name: Optional[str] = None,
    context_data: Optional[Dict[str, Any]] = None
) -> HealthNotFoundError:
    """Factory function for creating not found errors.
    
    Args:
        entity_type: Type of entity that was not found
        entity_id: ID of entity that was not found
        field_name: Field name if applicable
        context_data: Additional context data
        
    Returns:
        HealthNotFoundError: Configured not found exception
    """
    # @pyhex:begin:custom_not_found_factory
    # Add custom not found factory logic here - preserved during regeneration
    # @pyhex:end:custom_not_found_factory
    
    return HealthNotFoundError(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        context_data=context_data
    )


def create_validation_error(
    field_name: str,
    field_value: Any,
    validation_rule: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    context_data: Optional[Dict[str, Any]] = None
) -> HealthValidationError:
    """Factory function for creating validation errors.
    
    Args:
        field_name: Name of field that failed validation
        field_value: Value that failed validation
        validation_rule: Validation rule that was violated
        entity_type: Entity type if applicable
        entity_id: Entity ID if applicable
        context_data: Additional context data
        
    Returns:
        HealthValidationError: Configured validation exception
    """
    # @pyhex:begin:custom_validation_factory
    # Add custom validation factory logic here - preserved during regeneration
    # @pyhex:end:custom_validation_factory
    
    return HealthValidationError(
        field_name=field_name,
        field_value=field_value,
        validation_rule=validation_rule,
        entity_type=entity_type,
        entity_id=entity_id,
        context_data=context_data
    )


def create_business_rule_error(
    rule_name: str,
    rule_description: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    context_data: Optional[Dict[str, Any]] = None
) -> HealthBusinessRuleError:
    """Factory function for creating business rule errors.
    
    Args:
        rule_name: Name of business rule that was violated
        rule_description: Description of business rule violation
        entity_type: Entity type if applicable
        entity_id: Entity ID if applicable
        context_data: Additional context data
        
    Returns:
        HealthBusinessRuleError: Configured business rule exception
    """
    # @pyhex:begin:custom_business_rule_factory
    # Add custom business rule factory logic here - preserved during regeneration
    # @pyhex:end:custom_business_rule_factory
    
    return HealthBusinessRuleError(
        rule_name=rule_name,
        rule_description=rule_description,
        entity_type=entity_type,
        entity_id=entity_id,
        context_data=context_data
    )


# @pyhex:begin:custom_factory_functions
# Add custom factory functions here - preserved during regeneration
# @pyhex:end:custom_factory_functions


# FastAPI Exception Handlers
async def handle_domain_exception(
    exception: BaseHealthException
) -> HTTPException:
    """Handle domain exceptions for FastAPI.
    
    Args:
        exception: Domain exception to handle
        
    Returns:
        HTTPException: FastAPI-compatible exception
    """
    # @pyhex:begin:custom_fastapi_handler
    # Add custom FastAPI exception handling here - preserved during regeneration
    # @pyhex:end:custom_fastapi_handler
    
    return exception.to_fastapi_exception()


def register_exception_handlers(app):
    """Register domain exception handlers with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(BaseHealthException)
    async def domain_exception_handler(request, exc: BaseHealthException):
        """Handle domain exceptions."""
        return await handle_domain_exception(exc)
    
    @app.exception_handler(HealthNotFoundError)
    async def not_found_exception_handler(request, exc: HealthNotFoundError):
        """Handle not found exceptions."""
        return await handle_domain_exception(exc)
    
    @app.exception_handler(HealthValidationError)
    async def validation_exception_handler(request, exc: HealthValidationError):
        """Handle validation exceptions."""
        return await handle_domain_exception(exc)
    
    @app.exception_handler(HealthBusinessRuleError)
    async def business_rule_exception_handler(request, exc: HealthBusinessRuleError):
        """Handle business rule exceptions."""
        return await handle_domain_exception(exc)
    
    # @pyhex:begin:custom_exception_handlers
    # Add custom exception handlers here - preserved during regeneration
    # @pyhex:end:custom_exception_handlers


# Utility Functions
def get_exception_hierarchy() -> Dict[str, List[str]]:
    """Get exception hierarchy for documentation and debugging.
    
    Returns:
        Dict[str, List[str]]: Exception hierarchy mapping
    """
    return {
        "BaseHealthException": [
            "HealthNotFoundError",
            "HealthValidationError", 
            "HealthBusinessRuleError",
            "HealthAuthorizationError",
            "HealthIntegrationError",
            "HealthSystemError"
        ]
    }


def validate_exception_context(context: HealthExceptionContext) -> List[str]:
    """Validate exception context for completeness.
    
    Args:
        context: Exception context to validate
        
    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []
    
    if not context.error_code:
        errors.append("error_code is required")
    
    if not context.error_message:
        errors.append("error_message is required")
    
    if not context.category:
        errors.append("category is required")
    
    # @pyhex:begin:custom_context_validation
    # Add custom context validation here - preserved during regeneration
    # @pyhex:end:custom_context_validation
    
    return errors


# @pyhex:begin:custom_utility_functions
# Add custom utility functions here - preserved during regeneration
# @pyhex:end:custom_utility_functions


# Export all exception classes and utilities
__all__ = [
    # Enums
    "ExceptionSeverity",
    "ExceptionCategory",
    
    # Context and Base Classes
    "HealthExceptionContext",
    "BaseHealthException",
    
    # Specific Exception Classes
    "HealthNotFoundError",
    "HealthValidationError",
    "HealthBusinessRuleError",
    "HealthAuthorizationError",
    "HealthIntegrationError",
    "HealthSystemError",
    
    # Factory Functions
    "create_not_found_error",
    "create_validation_error",
    "create_business_rule_error",
    
    # FastAPI Integration
    "handle_domain_exception",
    "register_exception_handlers",
    
    # Utility Functions
    "get_exception_hierarchy",
    "validate_exception_context",
    
    # @pyhex:begin:custom_exports
    # Add custom exports here - preserved during regeneration
    # @pyhex:end:custom_exports
]