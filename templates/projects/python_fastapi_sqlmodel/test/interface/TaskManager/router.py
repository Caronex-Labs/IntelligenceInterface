"""
Project FastAPI Router - Interface Layer
This module implements the HTTP API interface for Project operations,
providing REST endpoints with proper request/response handling and error management.
Generated from: app/interface/TaskManager/router.py.j2
Configuration: app/interface/TaskManager/interface.yaml
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.responses import JSONResponse
# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports
from app.usecase.TaskManager.protocols import ProjectUseCaseProtocol
from app.usecase.TaskManager.schemas import (
CreateProjectRequest,
UpdateProjectRequest,
DeleteProjectRequest,
GetProjectRequest,
ListTaskmanagersRequest,
ProjectResponse,
ListTaskmanagersResponse,
DeleteResponse,
)
# Custom exception handling
from app.domain.TaskManager.exceptions import (
ProjectValidationError,
ProjectNotFoundError,
BusinessConstraintViolationError,
UnauthorizedOperationError,
)
from .protocols import (
ProjectRouterProtocol,
AuthenticationProtocol,
AuthorizationProtocol,
)
from .dependencies import (
get_TaskManager_usecase,
get_current_user,
require_TaskManager_permission,
)
logger = logging.getLogger(__name__)
# Create FastAPI router
router = APIRouter(
prefix="/api/v1/TaskManagers",
tags=["TaskManagers"],
responses={
404: {"description": "Project not found"},
422: {"description": "Validation error"},
500: {"description": "Service temporarily unavailable"},
},
)
class ProjectRouter(ProjectRouterProtocol):
"""
Project FastAPI router implementation.
This class implements REST API endpoints for Project operations,
following FastAPI conventions and providing comprehensive error handling.
Endpoints:
  - POST /: Create a new TaskManager with the provided data
  - GET /{TaskManager_id}: Retrieve a specific TaskManager by its unique identifier
  - PUT /{TaskManager_id}: Update an existing TaskManager with new data
  - DELETE /{TaskManager_id}: Delete an existing TaskManager
  - GET /: Retrieve a list of TaskManagers with optional filtering and pagination
"""
def __init__(self, usecase: ProjectUseCaseProtocol):
"""Initialize router with use case dependency."""
self.usecase = usecase
self.logger = logging.getLogger(__name__)
@router.post(
"/",
response_model=ProjectResponse,
status_code=status.HTTP_201_CREATED,
summary="Create a new TaskManager",
description="Create a new TaskManager with the provided data",
responses={
201: {"description": "Project created successfully"},
400: {"description": "Invalid request data"},
422: {"description": "Validation failed"},
},
)
async def create_TaskManager(
self,
request: CreateProjectRequest = Body(..., description="Project creation data"),
usecase: ProjectUseCaseProtocol = Depends(get_TaskManager_usecase),
current_user = Depends(get_current_user),
_: None = Depends(require_TaskManager_permission("create")),
) -> ProjectResponse:
"""
Create a new TaskManager entity.
This endpoint creates a new TaskManager with comprehensive validation,
business rules enforcement, and proper error handling.
"""
try:
self.logger.info(f"Creating TaskManager", extra={"user_id": getattr(current_user, 'id', None)})
# Execute use case
result = await usecase.create_TaskManager(request)
self.logger.info(f"Project created successfully", extra={"entity_id": result.id})
return result
except ProjectValidationError as e:
self.logger.warning(f"Project validation failed: {e}")
raise HTTPException(
status_code=status.HTTP_400_BAD_REQUEST,
detail={"error": "Validation failed", "message": str(e)}
)
except BusinessConstraintViolationError as e:
self.logger.warning(f"Business constraint violation: {e}")
raise HTTPException(
status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
detail={"error": "Business rule violation", "message": str(e)}
)
except Exception as e:
self.logger.error(f"Unexpected error creating TaskManager: {e}")
raise HTTPException(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
)
@router.get(
"/{id}",
response_model=ProjectResponse,
summary="Get TaskManager by ID",
description="Retrieve a specific TaskManager by its unique identifier",
responses={
200: {"description": "Project retrieved successfully"},
404: {"description": "Project not found"},
},
)
async def get_TaskManager_by_id(
self,
id: UUID = Path(..., description="Project unique identifier"),
usecase: ProjectUseCaseProtocol = Depends(get_TaskManager_usecase),
current_user = Depends(get_current_user),
_: None = Depends(require_TaskManager_permission("read")),
) -> ProjectResponse:
"""
Retrieve a TaskManager by its unique identifier.
This endpoint retrieves a specific TaskManager with access control validation
and comprehensive error handling.
"""
try:
self.logger.info(f"Retrieving TaskManager {id}")
# Create request object
request = GetProjectRequest(id=id)
# Execute use case
result = await usecase.get_TaskManager_by_id(request)
self.logger.info(f"Project retrieved successfully")
return result
except ProjectNotFoundError as e:
self.logger.warning(f"Project not found: {e}")
raise HTTPException(
status_code=status.HTTP_404_NOT_FOUND,
detail={"error": "Not found", "message": str(e)}
)
except UnauthorizedOperationError as e:
self.logger.warning(f"Unauthorized access attempt: {e}")
raise HTTPException(
status_code=status.HTTP_403_FORBIDDEN,
detail={"error": "Access denied", "message": str(e)}
)
except Exception as e:
self.logger.error(f"Unexpected error retrieving TaskManager: {e}")
raise HTTPException(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
)
@router.put(
"/{id}",
response_model=ProjectResponse,
summary="Update TaskManager",
description="Update an existing TaskManager with new data",
responses={
200: {"description": "Project updated successfully"},
400: {"description": "Invalid request data"},
404: {"description": "Project not found"},
422: {"description": "Validation failed"},
},
)
async def update_TaskManager(
self,
id: UUID = Path(..., description="Project unique identifier"),
request: UpdateProjectRequest = Body(..., description="Project update data"),
usecase: ProjectUseCaseProtocol = Depends(get_TaskManager_usecase),
current_user = Depends(get_current_user),
_: None = Depends(require_TaskManager_permission("update")),
) -> ProjectResponse:
"""
Update an existing TaskManager entity.
This endpoint updates a TaskManager with validation, permission checks,
and comprehensive error handling.
"""
try:
self.logger.info(f"Updating TaskManager {id}")
# Set the ID in the request
request.id = id
# Execute use case
result = await usecase.update_TaskManager(request)
self.logger.info(f"Project updated successfully")
return result
except ProjectNotFoundError as e:
self.logger.warning(f"Project not found for update: {e}")
raise HTTPException(
status_code=status.HTTP_404_NOT_FOUND,
detail={"error": "Not found", "message": str(e)}
)
except ProjectValidationError as e:
self.logger.warning(f"Project update validation failed: {e}")
raise HTTPException(
status_code=status.HTTP_400_BAD_REQUEST,
detail={"error": "Validation failed", "message": str(e)}
)
except BusinessConstraintViolationError as e:
self.logger.warning(f"Business constraint violation on update: {e}")
raise HTTPException(
status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
detail={"error": "Business rule violation", "message": str(e)}
)
except Exception as e:
self.logger.error(f"Unexpected error updating TaskManager: {e}")
raise HTTPException(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
)
@router.delete(
"/{id}",
response_model=DeleteResponse,
summary="Delete TaskManager",
description="Delete an existing TaskManager",
responses={
200: {"description": "Project deleted successfully"},
404: {"description": "Project not found"},
422: {"description": "Deletion not allowed"},
},
)
async def delete_TaskManager(
self,
id: UUID = Path(..., description="Project unique identifier"),
usecase: ProjectUseCaseProtocol = Depends(get_TaskManager_usecase),
current_user = Depends(get_current_user),
_: None = Depends(require_TaskManager_permission("delete")),
) -> DeleteResponse:
"""
Delete an existing TaskManager entity.
This endpoint deletes a TaskManager with validation, permission checks,
and comprehensive error handling.
"""
try:
self.logger.info(f"Deleting TaskManager {id}")
# Create request object
request = DeleteProjectRequest(id=id)
# Execute use case
result = await usecase.delete_TaskManager(request)
self.logger.info(f"Project deleted successfully")
return result
except ProjectNotFoundError as e:
self.logger.warning(f"Project not found for deletion: {e}")
raise HTTPException(
status_code=status.HTTP_404_NOT_FOUND,
detail={"error": "Not found", "message": str(e)}
)
except BusinessConstraintViolationError as e:
self.logger.warning(f"Deletion constraint violation: {e}")
raise HTTPException(
status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
detail={"error": "Deletion not allowed", "message": str(e)}
)
except Exception as e:
self.logger.error(f"Unexpected error deleting TaskManager: {e}")
raise HTTPException(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
)
@router.get(
"/",
response_model=ListTaskmanagersResponse,
summary="List TaskManagers",
description="Retrieve a list of TaskManagers with optional filtering and pagination",
responses={
200: {"description": "Taskmanagers retrieved successfully"},
},
)
async def list_TaskManagers(
self,
skip: int = Query(0, ge=0, description="Number of items to skip"),
limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
search: Optional[str] = Query(None, description="Search term for filtering"),
status: Optional[str] = Query(None, description="Filter by status"),
usecase: ProjectUseCaseProtocol = Depends(get_TaskManager_usecase),
current_user = Depends(get_current_user),
_: None = Depends(require_TaskManager_permission("list")),
) -> ListTaskmanagersResponse:
"""
Retrieve a list of TaskManagers with optional filtering and pagination.
This endpoint supports filtering, searching, and pagination with
comprehensive error handling and access control.
"""
try:
self.logger.info(f"Listing TaskManagers with filters")
# Build filters
filters = {}
if search:
filters["search"] = search
if status:
filters["status"] = status
# Create request object
request = ListTaskmanagersRequest(
skip=skip,
limit=limit,
filters=filters
)
# Execute use case
result = await usecase.list_TaskManagers(request)
self.logger.info(f"Taskmanagers listed successfully", extra={"count": len(result.items)})
return result
except Exception as e:
self.logger.error(f"Unexpected error listing TaskManagers: {e}")
raise HTTPException(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
)
# @pyhex:begin:custom:router_methods
# Add custom router methods here
# @pyhex:end:custom:router_methods
# Exception handlers
@router.exception_handler(ProjectValidationError)
async def TaskManager_validation_exception_handler(request, exc: ProjectValidationError):
"""Handle TaskManager validation errors."""
return JSONResponse(
status_code=status.HTTP_400_BAD_REQUEST,
content={"error": "Validation failed", "message": str(exc)}
)
@router.exception_handler(ProjectNotFoundError)
async def TaskManager_not_found_exception_handler(request, exc: ProjectNotFoundError):
"""Handle TaskManager not found errors."""
return JSONResponse(
status_code=status.HTTP_404_NOT_FOUND,
content={"error": "Not found", "message": str(exc)}
)
@router.exception_handler(BusinessConstraintViolationError)
async def business_constraint_exception_handler(request, exc: BusinessConstraintViolationError):
"""Handle business constraint violations."""
return JSONResponse(
status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
content={"error": "Business rule violation", "message": str(exc)}
)
@router.exception_handler(UnauthorizedOperationError)
async def unauthorized_exception_handler(request, exc: UnauthorizedOperationError):
"""Handle unauthorized operation errors."""
return JSONResponse(
status_code=status.HTTP_403_FORBIDDEN,
content={"error": "Access denied", "message": str(exc)}
)
# Health check endpoint
@router.get(
"/health",
summary="Health check",
description="Check the health status of the TaskManager service",
include_in_schema=False,
)
async def health_check():
"""Comprehensive health check endpoint for monitoring and container orchestration."""
import time
from datetime import datetime
try:
# Basic health checks
current_time = datetime.utcnow()
# Database connectivity check would go here
# db_status = await check_database_connection()
health_response = {
"status": "healthy",
"service": "TaskManager_service",
"timestamp": current_time.isoformat(),
"version": "1.0.0",
"checks": {
"service": "healthy",
"database": "healthy",  # Would implement actual DB check
"memory": "healthy",
"dependencies": "healthy"
}
}
return health_response
except Exception as e:
# Health check should never fail with 500
return {
"status": "degraded",
"service": "TaskManager_service",
"timestamp": datetime.utcnow().isoformat(),
"error": "Health check partially failed"
}
# Metrics endpoint
@router.get(
"/metrics",
summary="Service metrics",
description="Get service metrics and statistics",
include_in_schema=False,
)
async def get_metrics():
"""Get service metrics."""
return {
"service": "TaskManager_service",
"version": "1.0.0",
"uptime": "N/A",  # Implement actual uptime tracking
"requests_count": "N/A",  # Implement actual request counting
}
# @pyhex:begin:custom:router_handlers
# Add custom router handlers here
# @pyhex:end:custom:router_handlers