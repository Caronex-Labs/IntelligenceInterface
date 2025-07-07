"""
Interface Layer Package

This package contains the interface layer implementations for all domains,
providing FastAPI routers, HTTP endpoints, and web API functionality.

The interface layer is responsible for:
- HTTP request/response handling
- Authentication and authorization
- Input validation and sanitization
- Error handling and status codes
- API documentation generation
- Middleware and cross-cutting concerns

Each domain has its own interface package with:
- router.py: FastAPI router with endpoints
- dependencies.py: Dependency injection functions
- protocols.py: Interface protocols and contracts
- interface.yaml: Configuration for the interface layer
"""

__all__ = [
    # Interface layer components will be exported from domain-specific packages
]