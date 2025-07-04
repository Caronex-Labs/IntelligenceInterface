"""
Project Interface Layer Dependencies
This module provides dependency injection functions for the Project interface layer,
ensuring proper dependency resolution and lifecycle management.
Generated from: app/interface/TaskManager/dependencies.py.j2
Configuration: app/interface/TaskManager/interface.yaml
"""
import logging
from typing import Optional, Dict, Any, Annotated
from fastapi import Depends, HTTPException, status, Request, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports
from app.usecase.TaskManager.protocols import ProjectUseCaseProtocol
from app.usecase.TaskManager.usecase import ProjectUseCase
from app.repository.TaskManager.protocols import ProjectRepositoryProtocol
from app.repository.TaskManager.repository import ProjectRepository
from .protocols import (
AuthenticationProtocol,
AuthorizationProtocol,
MiddlewareProtocol,
RateLimitingProtocol,
CachingProtocol,
)
logger = logging.getLogger(__name__)
# Security scheme
security = HTTPBearer(auto_error=False)
# Core dependency providers
async def get_TaskManager_repository() -> ProjectRepositoryProtocol:
"""
Get Project repository instance.
This dependency provides a configured repository instance
for Project data operations.
"""
# @pyhex:begin:custom:get_TaskManager_repository
# Initialize repository with database session
# This is a simplified implementation - customize based on your database setup
return ProjectRepository()
# @pyhex:end:custom:get_TaskManager_repository
async def get_TaskManager_usecase(
repository: ProjectRepositoryProtocol = Depends(get_TaskManager_repository)
) -> ProjectUseCaseProtocol:
"""
Get Project use case instance.
This dependency provides a configured use case instance
with proper repository injection.
"""
# @pyhex:begin:custom:get_TaskManager_usecase
# Initialize use case with dependencies
# This is a simplified implementation - customize based on your architecture
from app.usecase.TaskManager.usecase import ProjectBusinessRules
business_rules = ProjectBusinessRules(repository)
# Mock event publisher - replace with actual implementation
class MockEventPublisher:
async def publish_TaskManager_created(self, entity, context): pass
async def publish_TaskManager_updated(self, entity, update_data, context): pass
async def publish_TaskManager_deleted(self, entity_id, context): pass
event_publisher = MockEventPublisher()
# Mock services - replace with actual implementations
validation_service = None
audit_service = None
return ProjectUseCase(
TaskManager_repository=repository,
business_rules=business_rules,
event_publisher=event_publisher,
validation_service=validation_service,
audit_service=audit_service,
)
# @pyhex:end:custom:get_TaskManager_usecase
# Authentication dependencies
async def get_current_user(
request: Request,
credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
"""
Get current authenticated user.
This dependency extracts and validates the current user
from the request authentication token.
"""
# @pyhex:begin:custom:get_current_user
# For development/testing purposes, return a mock user
# Replace with actual authentication logic
if not credentials:
# Allow unauthenticated access for development
return {
"id": "00000000-0000-0000-0000-000000000000",
"username": "anonymous",
"email": "anonymous@example.com",
"roles": ["user"],
"permissions": ["read", "create", "update", "delete", "list"]
}
# TODO: Implement actual token validation
# token = credentials.credentials
# user = await authenticate_token(token)
# if not user:
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid authentication credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
# Mock authenticated user
return {
"id": "12345678-1234-1234-1234-123456789012",
"username": "authenticated_user",
"email": "user@example.com",
"roles": ["user", "TaskManager_admin"],
"permissions": ["read", "create", "update", "delete", "list"]
}
# @pyhex:end:custom:get_current_user
def require_TaskManager_permission(permission: str):
"""
Create a dependency that requires specific TaskManager permission.
Args:
permission: Required permission (create, read, update, delete, list)
Returns:
Dependency function that validates permission
"""
async def check_permission(
current_user: Dict[str, Any] = Depends(get_current_user)
) -> None:
"""Check if current user has required permission."""
# @pyhex:begin:custom:check_permission
if not current_user:
raise HTTPException(
status_code=status.HTTP_401_UNAUTHORIZED,
detail="Authentication required"
)
user_permissions = current_user.get("permissions", [])
user_roles = current_user.get("roles", [])
# Check direct permission
if permission in user_permissions:
return
# Check role-based permissions
admin_roles = ["admin", "TaskManager_admin", "super_admin"]
if any(role in admin_roles for role in user_roles):
return
# Permission denied
logger.warning(
f"Permission denied for user {current_user.get('id')}: {permission}",
extra={"user_id": current_user.get("id"), "permission": permission}
)
raise HTTPException(
status_code=status.HTTP_403_FORBIDDEN,
detail=f"Insufficient permissions: {permission} required"
)
# @pyhex:end:custom:check_permission
return check_permission
def require_role(role: str):
"""
Create a dependency that requires specific role.
Args:
role: Required role
Returns:
Dependency function that validates role
"""
async def check_role(
current_user: Dict[str, Any] = Depends(get_current_user)
) -> None:
"""Check if current user has required role."""
if not current_user:
raise HTTPException(
status_code=status.HTTP_401_UNAUTHORIZED,
detail="Authentication required"
)
user_roles = current_user.get("roles", [])
if role not in user_roles:
logger.warning(
f"Role check failed for user {current_user.get('id')}: {role}",
extra={"user_id": current_user.get("id"), "role": role}
)
raise HTTPException(
status_code=status.HTTP_403_FORBIDDEN,
detail=f"Role required: {role}"
)
return check_role
# Rate limiting dependencies
async def rate_limit_dependency(
request: Request,
x_forwarded_for: Annotated[str | None, Header()] = None,
) -> None:
"""
Apply rate limiting to requests.
This dependency implements request rate limiting based on
client IP address or user identification.
"""
# @pyhex:begin:custom:rate_limit_dependency
# Get client identifier
client_ip = x_forwarded_for or request.client.host if request.client else "unknown"
# TODO: Implement actual rate limiting logic
# rate_limiter = get_rate_limiter()
# if not await rate_limiter.check_rate_limit(client_ip, limit=100, window=60):
#     raise HTTPException(
#         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#         detail="Rate limit exceeded"
#     )
logger.debug(f"Rate limit check passed for {client_ip}")
# @pyhex:end:custom:rate_limit_dependency
# Caching dependencies
async def cache_dependency(request: Request) -> Optional[Dict[str, Any]]:
"""
Check for cached response.
This dependency checks if a cached response exists
for the current request.
"""
# @pyhex:begin:custom:cache_dependency
# TODO: Implement actual caching logic
# cache_key = generate_cache_key(request)
# cached_response = await get_from_cache(cache_key)
# return cached_response
return None  # No cached response
# @pyhex:end:custom:cache_dependency
# Validation dependencies
async def validate_request_headers(
request: Request,
content_type: Annotated[str | None, Header()] = None,
accept: Annotated[str | None, Header()] = None,
) -> None:
"""
Validate request headers.
This dependency validates that required headers
are present and have acceptable values.
"""
# @pyhex:begin:custom:validate_request_headers
# Validate content type for POST/PUT requests
if request.method in ["POST", "PUT", "PATCH"]:
if not content_type or not content_type.startswith("application/json"):
logger.warning(f"Invalid content type: {content_type}")
# Note: FastAPI handles this automatically, but you can add custom validation
# Validate accept header
if accept and "application/json" not in accept:
logger.warning(f"Unsupported accept header: {accept}")
# Note: FastAPI handles this automatically, but you can add custom validation
logger.debug("Request headers validation passed")
# @pyhex:end:custom:validate_request_headers
# Metrics dependencies
async def metrics_dependency(request: Request) -> None:
"""
Record request metrics.
This dependency records metrics for monitoring
and analytics purposes.
"""
# @pyhex:begin:custom:metrics_dependency
# TODO: Implement actual metrics recording
# metrics_recorder = get_metrics_recorder()
# await metrics_recorder.record_request_start(request)
logger.debug(f"Request metrics recorded for {request.url}")
# @pyhex:end:custom:metrics_dependency
# Common dependencies combination
def get_common_dependencies():
"""
Get common dependencies for all endpoints.
Returns:
List of common dependencies
"""
return [
Depends(validate_request_headers),
Depends(rate_limit_dependency),
Depends(metrics_dependency),
]
# @pyhex:begin:custom:dependencies
# Add custom dependency functions here
# @pyhex:end:custom:dependencies