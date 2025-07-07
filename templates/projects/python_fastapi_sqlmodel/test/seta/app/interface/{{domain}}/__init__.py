"""
{{domain|title}} Interface Layer Package

This package implements the interface layer for {{domain|title}} operations,
providing FastAPI routers, dependencies, and HTTP endpoint implementations.

Generated from: app/interface/{{domain}}/__init__.py
"""

from .router import router, {{domain|title}}Router
from .dependencies import (
    get_{{domain}}_repository,
    get_{{domain}}_usecase,
    get_current_user,
    require_{{domain}}_permission,
    require_role,
)
from .protocols import (
    {{domain|title}}RouterProtocol,
    AuthenticationProtocol,
    AuthorizationProtocol,
    MiddlewareProtocol,
    RateLimitingProtocol,
    CachingProtocol,
    ValidationProtocol,
    MetricsProtocol,
)

__all__ = [
    # Router exports
    "router",
    "{{domain|title}}Router",
    
    # Dependency exports
    "get_{{domain}}_repository",
    "get_{{domain}}_usecase", 
    "get_current_user",
    "require_{{domain}}_permission",
    "require_role",
    
    # Protocol exports
    "{{domain|title}}RouterProtocol",
    "AuthenticationProtocol",
    "AuthorizationProtocol",
    "MiddlewareProtocol",
    "RateLimitingProtocol",
    "CachingProtocol",
    "ValidationProtocol",
    "MetricsProtocol",
]