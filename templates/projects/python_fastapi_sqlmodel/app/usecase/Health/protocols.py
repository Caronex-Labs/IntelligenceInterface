"""
Health Use Case Protocols - Co-location Architecture

This module defines the use case interfaces and protocols for Health business logic orchestration.
These protocols ensure clean separation between business logic and implementation details,
supporting dependency injection and testing patterns.

Generated from: app/usecase/Health/protocols.py.j2
Configuration: app/usecase/Health/usecase.yaml
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from uuid import UUID

# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports

from app.domain.Health.entities import Health
from .schemas import (
    CreateHealthRequest,
    UpdateHealthRequest,
    DeleteHealthRequest,
    GetHealthRequest,
    ListHealthchecksRequest,
    HealthResponse,
    ListHealthchecksResponse,
    DeleteResponse,
)


class HealthUseCaseProtocol(ABC):
    """
    Protocol for Health use case business logic operations.
    
    This protocol defines the interface for all Health business operations,
    ensuring consistent implementation across different use case implementations.
    
    Business Operations:
- create_Health: Create a new Health with comprehensive validation
- get_Health_by_id: Retrieve Health by ID with access control validation
- update_Health: Update Health with permission checks and audit logging
- delete_Health: Delete Health with validation and audit logging
    
    Dependencies:
- Health_repository: Repository for data access
- validation_service: Service for validation service operations
- audit_service: Service for audit service operations
    """

    # @pyhex:begin:custom:protocol_methods
    # Add custom protocol method signatures here
    # @pyhex:end:custom:protocol_methods

@abstractmethod
    async def create_Health(
        self,
        request: CreateHealthRequest,
        # Dependencies injected by framework    ) -> HealthResponse:
        """
        Create a new Health with comprehensive validation
        
Business Rules Applied:
- data_validation: Validates data validation
- business_constraints: Validates business constraints
        
Orchestration Steps:
1. Validate Health Data
2. Create Health Record
3. Publish Health Created Event
        
        Args:
            request: CreateHealthRequest containing create Health data
            
        Returns:
            HealthResponse: Result of create Health operation
            
        Raises:
ValidationError: When business rules validation fails
            AuthorizationError: When user lacks required permissions
            BusinessLogicError: When business constraints are violated
        """
        ...

@abstractmethod
    async def get_Health_by_id(
        self,
        request: GetHealthRequest,
        # Dependencies injected by framework    ) -> HealthResponse:
        """
        Retrieve Health by ID with access control validation
        
Business Rules Applied:
- Health_exists: Validates Health exists
- access_permitted: Validates access permitted
        
Orchestration Steps:
1. Validate Access Permissions
2. Retrieve Health Data
        
        Args:
            request: GetHealthRequest containing get Health by id data
            
        Returns:
            HealthResponse: Result of get Health by id operation
            
        Raises:
ValidationError: When business rules validation fails
            AuthorizationError: When user lacks required permissions
            BusinessLogicError: When business constraints are violated
        """
        ...

@abstractmethod
    async def update_Health(
        self,
        request: UpdateHealthRequest,
        # Dependencies injected by framework    ) -> HealthResponse:
        """
        Update Health with permission checks and audit logging
        
Business Rules Applied:
- Health_exists: Validates Health exists
- update_allowed: Validates update allowed
- data_integrity: Validates data integrity
        
Orchestration Steps:
1. Validate Update Permissions
2. Validate Update Data
3. Update Health Record
4. Publish Health Updated Event
        
        Args:
            request: UpdateHealthRequest containing update Health data
            
        Returns:
            HealthResponse: Result of update Health operation
            
        Raises:
ValidationError: When business rules validation fails
            AuthorizationError: When user lacks required permissions
            BusinessLogicError: When business constraints are violated
        """
        ...

@abstractmethod
    async def delete_Health(
        self,
        request: DeleteHealthRequest,
        # Dependencies injected by framework    ) -> DeleteResponse:
        """
        Delete Health with validation and audit logging
        
Business Rules Applied:
- Health_exists: Validates Health exists
- deletion_allowed: Validates deletion allowed
        
Orchestration Steps:
1. Validate Deletion Permissions
2. Delete Health Record
3. Publish Health Deleted Event
        
        Args:
            request: DeleteHealthRequest containing delete Health data
            
        Returns:
            DeleteResponse: Result of delete Health operation
            
        Raises:
ValidationError: When business rules validation fails
            AuthorizationError: When user lacks required permissions
            BusinessLogicError: When business constraints are violated
        """
        ...


    # @pyhex:begin:custom:additional_methods
    # Add custom method signatures here
    # @pyhex:end:custom:additional_methods


class HealthBusinessRulesProtocol(ABC):
    """
    Protocol for Health business rules validation.
    
    This protocol defines the interface for business rules validation,
    ensuring consistent rule enforcement across use case operations.
    
    Business Rules:
- data_validation: 
- Health_exists: 
- update_allowed: 
- access_permitted: 
- business_constraints: 
- deletion_allowed: 
- data_integrity: 
    """

@abstractmethod
    async def validate_data_validation(
        self,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> bool:
        """
        Validate data_validation business rule.
        
        Rule: Health_data.is_valid and Health_data.fields_are_complete
        Type: validation
        Severity: error
        
        Args:
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            bool: True if rule passes, False otherwise
            
        Raises:
            Data_ValidationValidationError: When health data validation failed - invalid or incomplete data
        """
        ...

@abstractmethod
    async def validate_Health_exists(
        self,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> bool:
        """
        Validate Health_exists business rule.
        
        Rule: Health.id exists in database
        Type: constraint
        Severity: error
        
        Args:
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            bool: True if rule passes, False otherwise
            
        Raises:
            Health_ExistsValidationError: When health not found in the system
        """
        ...

@abstractmethod
    async def validate_update_allowed(
        self,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> bool:
        """
        Validate update_allowed business rule.
        
        Rule: Health.can_be_updated and not Health.is_locked
        Type: business_logic
        Severity: error
        
        Args:
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            bool: True if rule passes, False otherwise
            
        Raises:
            Update_AllowedValidationError: When health update not allowed for this record
        """
        ...

@abstractmethod
    async def validate_access_permitted(
        self,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> bool:
        """
        Validate access_permitted business rule.
        
        Rule: user_context.can_access_Health(Health.id)
        Type: security
        Severity: error
        
        Args:
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            bool: True if rule passes, False otherwise
            
        Raises:
            Access_PermittedValidationError: When access denied to health information
        """
        ...

@abstractmethod
    async def validate_business_constraints(
        self,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> bool:
        """
        Validate business_constraints business rule.
        
        Rule: Health_data.meets_business_requirements
        Type: validation
        Severity: error
        
        Args:
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            bool: True if rule passes, False otherwise
            
        Raises:
            Business_ConstraintsValidationError: When health does not meet business requirements
        """
        ...

@abstractmethod
    async def validate_deletion_allowed(
        self,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> bool:
        """
        Validate deletion_allowed business rule.
        
        Rule: Health.can_be_deleted and not Health.has_dependencies
        Type: business_logic
        Severity: error
        
        Args:
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            bool: True if rule passes, False otherwise
            
        Raises:
            Deletion_AllowedValidationError: When health cannot be deleted due to constraints
        """
        ...

@abstractmethod
    async def validate_data_integrity(
        self,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> bool:
        """
        Validate data_integrity business rule.
        
        Rule: updated_data.maintains_referential_integrity
        Type: constraint
        Severity: error
        
        Args:
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            bool: True if rule passes, False otherwise
            
        Raises:
            Data_IntegrityValidationError: When data update would violate referential integrity constraints
        """
        ...


    @abstractmethod
    async def validate_group(
        self,
        group_name: str,
        context: Dict[str, Any],
        Health: Optional[Health] = None
    ) -> List[str]:
        """
        Validate a group of business rules.
        
        Available Groups:
- Health_creation: Comprehensive validation rules for Health creation process
- Health_access: Validation rules for Health access operations
- Health_modification: Validation rules for Health modification operations
- Health_deletion: Validation rules for Health deletion operations
        
        Args:
            group_name: Name of validation group to execute
            context: Validation context with required data
            Health: Optional Health entity for validation
            
        Returns:
            List[str]: List of validation errors (empty if all rules pass)
        """
        ...

    # @pyhex:begin:custom:business_rule_methods
    # Add custom business rule method signatures here
    # @pyhex:end:custom:business_rule_methods


class HealthEventProtocol(ABC):
    """
    Protocol for Health domain event publishing.
    
    This protocol defines the interface for publishing domain events
    during Health business operations.
    """

    @abstractmethod
    async def publish_Health_created(
        self,
        Health: Health,
        context: Dict[str, Any]
    ) -> None:
        """Publish Health created event."""
        ...

    @abstractmethod
    async def publish_Health_updated(
        self,
        Health: Health,
        changes: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """Publish Health updated event."""
        ...

    @abstractmethod
    async def publish_Health_deleted(
        self,
        Health_id: UUID,
        context: Dict[str, Any]
    ) -> None:
        """Publish Health deleted event."""
        ...

    # @pyhex:begin:custom:event_methods
    # Add custom event method signatures here
    # @pyhex:end:custom:event_methods


# @pyhex:begin:custom:protocols
# Add custom protocol definitions here
# @pyhex:end:custom:protocols