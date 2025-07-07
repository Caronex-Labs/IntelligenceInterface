"""
Use Case Layer - Business Logic Orchestration

This module provides the use case layer for business logic orchestration,
following hexagonal architecture principles with co-location patterns.

The use case layer is responsible for:
- Orchestrating business workflows
- Coordinating repository and service interactions
- Enforcing business rules and validation
- Managing transaction boundaries
- Handling business logic errors

Co-location Architecture:
Each domain has its use cases co-located with configurations and generated files
in app/usecase/{{domain}}/ for optimal developer experience.
"""

__version__ = "1.0.0"
__author__ = "Template System"