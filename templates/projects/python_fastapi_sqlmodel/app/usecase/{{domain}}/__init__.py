"""
{{domain.name|title}} Use Case Module - Co-location Architecture

This module contains business logic orchestration for the {{domain.name}} domain,
implementing use cases that coordinate repositories, services, and business rules.

Generated Files:
- protocols.py: Use case interfaces and protocols
- usecase.py: Use case implementations with business logic
- schemas.py: Use case-level validation and data transfer objects

Configuration Files:
- usecase.yaml: Use case configuration and workflow patterns
- business-rules.yaml: Business logic rules and constraints

Architecture:
Follows hexagonal architecture with clean separation between
business logic, repositories, and external services.
"""

from .protocols import *  # noqa: F401, F403
from .usecase import *  # noqa: F401, F403
from .schemas import *  # noqa: F401, F403

__all__ = [
    # Protocols
    "{{domain.name|title}}UseCaseProtocol",
    
    # Use Cases
    "{{domain.name|title}}UseCase",
    
    # Schemas
    "Create{{domain.name|title}}Request",
    "Update{{domain.name|title}}Request",
    "Delete{{domain.name|title}}Request",
    "Get{{domain.name|title}}Request",
    "List{{domain.name_plural|title}}Request",
    "{{domain.name|title}}Response",
    "List{{domain.name_plural|title}}Response",
    "DeleteResponse",
]