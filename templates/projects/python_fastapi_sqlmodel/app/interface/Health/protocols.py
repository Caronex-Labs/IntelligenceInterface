"""
Health Interface Layer Protocols

This module defines protocols (interfaces) for the Health interface layer,
ensuring proper dependency injection and interface segregation.

Generated from: app/interface/Health/protocols.py.j2
Configuration: app/interface/Health/interface.yaml
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from uuid import UUID
from fastapi import Request, Response

# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports

from app.usecase.Health.schemas import (
    CreateHealthRequest,
    UpdateHealthRequest,
    HealthResponse,
    ListHealthchecksResponse,
    DeleteResponse,
)


class HealthRouterProtocol(ABC):
    """
    Protocol for Health FastAPI router operations.
    
    This protocol defines the interface for Health HTTP operations,
    ensuring consistent implementation across different router implementations.
    """

    @abstractmethod
    async def create_Health(
        self,
        request: CreateHealthRequest,
        **kwargs
    ) -> HealthResponse:
        """Create a new Health entity."""
        pass

    @abstractmethod
    async def get_Health_by_id(
        self,
        Health_id: UUID,
        **kwargs
    ) -> HealthResponse:
        """Retrieve a Health by its unique identifier."""
        pass

    @abstractmethod
    async def update_Health(
        self,
        Health_id: UUID,
        request: UpdateHealthRequest,
        **kwargs
    ) -> HealthResponse:
        """Update an existing Health entity."""
        pass

    @abstractmethod
    async def delete_Health(
        self,
        Health_id: UUID,
        **kwargs
    ) -> DeleteResponse:
        """Delete an existing Health entity."""
        pass

    @abstractmethod
    async def list_HealthChecks(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        **kwargs
    ) -> ListHealthchecksResponse:
        """List HealthChecks with optional filtering and pagination."""
        pass


class AuthenticationProtocol(ABC):
    """
    Protocol for authentication operations.
    
    This protocol defines the interface for user authentication,
    supporting various authentication methods and providers.
    """

    @abstractmethod
    async def authenticate_user(
        self,
        request: Request,
        credentials: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a user with provided credentials."""
        pass

    @abstractmethod
    async def get_current_user(
        self,
        request: Request,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """Get current user from authentication token."""
        pass

    @abstractmethod
    async def validate_token(
        self,
        token: str
    ) -> bool:
        """Validate an authentication token."""
        pass

    @abstractmethod
    async def refresh_token(
        self,
        refresh_token: str
    ) -> Optional[Dict[str, str]]:
        """Refresh an expired authentication token."""
        pass

    @abstractmethod
    async def logout_user(
        self,
        request: Request,
        token: str
    ) -> bool:
        """Logout a user and invalidate their token."""
        pass


class AuthorizationProtocol(ABC):
    """
    Protocol for authorization operations.
    
    This protocol defines the interface for user authorization,
    supporting role-based and permission-based access control.
    """

    @abstractmethod
    async def check_permission(
        self,
        user: Dict[str, Any],
        resource: str,
        action: str
    ) -> bool:
        """Check if user has permission for specific action on resource."""
        pass

    @abstractmethod
    async def check_role(
        self,
        user: Dict[str, Any],
        required_role: str
    ) -> bool:
        """Check if user has required role."""
        pass

    @abstractmethod
    async def get_user_permissions(
        self,
        user: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get all permissions for a user."""
        pass

    @abstractmethod
    async def get_user_roles(
        self,
        user: Dict[str, Any]
    ) -> List[str]:
        """Get all roles for a user."""
        pass

    @abstractmethod
    async def check_resource_ownership(
        self,
        user: Dict[str, Any],
        resource_type: str,
        resource_id: UUID
    ) -> bool:
        """Check if user owns a specific resource."""
        pass


class MiddlewareProtocol(ABC):
    """
    Protocol for middleware operations.
    
    This protocol defines the interface for HTTP middleware,
    supporting request/response processing and modification.
    """

    @abstractmethod
    async def process_request(
        self,
        request: Request
    ) -> Optional[Request]:
        """Process incoming HTTP request."""
        pass

    @abstractmethod
    async def process_response(
        self,
        request: Request,
        response: Response
    ) -> Response:
        """Process outgoing HTTP response."""
        pass

    @abstractmethod
    async def handle_error(
        self,
        request: Request,
        error: Exception
    ) -> Optional[Response]:
        """Handle request processing errors."""
        pass


class RateLimitingProtocol(ABC):
    """
    Protocol for rate limiting operations.
    
    This protocol defines the interface for request rate limiting,
    supporting various rate limiting strategies and configurations.
    """

    @abstractmethod
    async def check_rate_limit(
        self,
        request: Request,
        identifier: str,
        limit: int,
        window: int
    ) -> bool:
        """Check if request is within rate limit."""
        pass

    @abstractmethod
    async def get_rate_limit_status(
        self,
        identifier: str
    ) -> Dict[str, Any]:
        """Get current rate limit status for identifier."""
        pass

    @abstractmethod
    async def reset_rate_limit(
        self,
        identifier: str
    ) -> bool:
        """Reset rate limit for identifier."""
        pass


class CachingProtocol(ABC):
    """
    Protocol for caching operations.
    
    This protocol defines the interface for response caching,
    supporting various caching strategies and backends.
    """

    @abstractmethod
    async def get_cached_response(
        self,
        cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached response by key."""
        pass

    @abstractmethod
    async def set_cached_response(
        self,
        cache_key: str,
        response: Dict[str, Any],
        ttl: int
    ) -> bool:
        """Set cached response with TTL."""
        pass

    @abstractmethod
    async def invalidate_cache(
        self,
        pattern: str
    ) -> bool:
        """Invalidate cache entries matching pattern."""
        pass

    @abstractmethod
    async def generate_cache_key(
        self,
        request: Request
    ) -> str:
        """Generate cache key for request."""
        pass


class ValidationProtocol(ABC):
    """
    Protocol for request validation operations.
    
    This protocol defines the interface for HTTP request validation,
    supporting custom validation rules and error handling.
    """

    @abstractmethod
    async def validate_request(
        self,
        request: Request,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate HTTP request against schema."""
        pass

    @abstractmethod
    async def validate_query_params(
        self,
        params: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate query parameters against rules."""
        pass

    @abstractmethod
    async def validate_headers(
        self,
        headers: Dict[str, str],
        required_headers: List[str]
    ) -> bool:
        """Validate required headers are present."""
        pass

    @abstractmethod
    async def sanitize_input(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sanitize input data for security."""
        pass


class MetricsProtocol(ABC):
    """
    Protocol for metrics collection operations.
    
    This protocol defines the interface for collecting and reporting
    API metrics and performance data.
    """

    @abstractmethod
    async def record_request(
        self,
        request: Request,
        response_time: float,
        status_code: int
    ) -> None:
        """Record API request metrics."""
        pass

    @abstractmethod
    async def record_error(
        self,
        request: Request,
        error: Exception
    ) -> None:
        """Record API error metrics."""
        pass

    @abstractmethod
    async def get_metrics_summary(
        self,
        time_range: str
    ) -> Dict[str, Any]:
        """Get metrics summary for time range."""
        pass

    @abstractmethod
    async def get_endpoint_metrics(
        self,
        endpoint: str,
        time_range: str
    ) -> Dict[str, Any]:
        """Get metrics for specific endpoint."""
        pass


# @pyhex:begin:custom:protocols
# Add custom interface protocols here
# @pyhex:end:custom:protocols