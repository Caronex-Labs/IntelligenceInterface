"""
Health FastAPI Router - Interface Layer

This module implements the HTTP API interface for Health operations,
providing REST endpoints with proper request/response handling and error management.

Generated from: app/interface/Health/router.py.j2
Configuration: app/interface/Health/interface.yaml
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.responses import JSONResponse

# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports

from app.usecase.Health.protocols import HealthUseCaseProtocol
from app.usecase.Health.schemas import (
    CreateHealthRequest,
    UpdateHealthRequest,
    DeleteHealthRequest,
    GetHealthRequest,
    ListHealthchecksRequest,
    HealthResponse,
    ListHealthchecksResponse,
    DeleteResponse,
)

# Custom exception handling
from app.core.Health.exceptions import (
    HealthValidationError,
    HealthNotFoundError,
    BusinessConstraintViolationError,
    UnauthorizedOperationError,
)

from .protocols import (
    HealthRouterProtocol,
)
from .dependencies import (
    get_Health_usecase,
    get_current_user,
    require_Health_permission,
)

logger = logging.getLogger(__name__)

# Create FastAPI router
router = APIRouter(
    prefix="/api/v1/HealthChecks",
    tags=["HealthChecks"],
    responses={
        404: {"description": "Health not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)


class HealthRouter(HealthRouterProtocol):
    """
    Health FastAPI router implementation.
    
    This class implements REST API endpoints for Health operations,
    following FastAPI conventions and providing comprehensive error handling.
    
    Endpoints:
- POST /: Create a new Health with the provided data
- GET /{Health_id}: Retrieve a specific Health by its unique identifier
- PUT /{Health_id}: Update an existing Health with new data
- DELETE /{Health_id}: Delete an existing Health
- GET /: Retrieve a list of HealthChecks with optional filtering and pagination
    """

    def __init__(self, usecase: HealthUseCaseProtocol):
        """Initialize router with use case dependency."""
        self.usecase = usecase
        self.logger = logging.getLogger(__name__)

    @router.post(
        "/",
        response_model=HealthResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Create a new Health",
        description="Create a new Health with the provided data",
        responses={
            201: {"description": "Health created successfully"},
            400: {"description": "Invalid request data"},
            422: {"description": "Validation failed"},
        },
    )
    async def create_Health(
        self,
        request: CreateHealthRequest = Body(..., description="Health creation data"),
        usecase: HealthUseCaseProtocol = Depends(get_Health_usecase),
        current_user = Depends(get_current_user),
        _: None = Depends(require_Health_permission("create")),
    ) -> HealthResponse:
        """
        Create a new Health entity.
        
        This endpoint creates a new Health with comprehensive validation,
        business rules enforcement, and proper error handling.
        """
        try:
            self.logger.info("Creating Health", extra={"user_id": getattr(current_user, 'id', None)})
            
            # Execute use case
            result = await usecase.create_Health(request)
            
            self.logger.info("Health created successfully", extra={"Health_id": result.id})
            return result
            
        except HealthValidationError as e:
            self.logger.warning(f"Health validation failed: {e}")
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
            self.logger.error(f"Unexpected error creating Health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
            )

    @router.get(
        "/{id}",
        response_model=HealthResponse,
        summary="Get Health by ID",
        description="Retrieve a specific Health by its unique identifier",
        responses={
            200: {"description": "Health retrieved successfully"},
            404: {"description": "Health not found"},
        },
    )
    async def get_Health_by_id(
        self,
        id: UUID = Path(..., description="Health unique identifier"),
        usecase: HealthUseCaseProtocol = Depends(get_Health_usecase),
        current_user = Depends(get_current_user),
        _: None = Depends(require_Health_permission("read")),
    ) -> HealthResponse:
        """
        Retrieve a Health by its unique identifier.
        
        This endpoint retrieves a specific Health with access control validation
        and comprehensive error handling.
        """
        try:
            self.logger.info(f"Retrieving Health {id}")
            
            # Create request object
            request = GetHealthRequest(id=Health_id)
            
            # Execute use case
            result = await usecase.get_Health_by_id(request)
            
            self.logger.info("Health retrieved successfully")
            return result
            
        except HealthNotFoundError as e:
            self.logger.warning(f"Health not found: {e}")
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
            self.logger.error(f"Unexpected error retrieving Health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
            )

    @router.put(
        "/{id}",
        response_model=HealthResponse,
        summary="Update Health",
        description="Update an existing Health with new data",
        responses={
            200: {"description": "Health updated successfully"},
            400: {"description": "Invalid request data"},
            404: {"description": "Health not found"},
            422: {"description": "Validation failed"},
        },
    )
    async def update_Health(
        self,
        id: UUID = Path(..., description="Health unique identifier"),
        request: UpdateHealthRequest = Body(..., description="Health update data"),
        usecase: HealthUseCaseProtocol = Depends(get_Health_usecase),
        current_user = Depends(get_current_user),
        _: None = Depends(require_Health_permission("update")),
    ) -> HealthResponse:
        """
        Update an existing Health entity.
        
        This endpoint updates a Health with validation, permission checks,
        and comprehensive error handling.
        """
        try:
            self.logger.info(f"Updating Health {id}")
            
            # Set the ID in the request
            request.id = id
            
            # Execute use case
            result = await usecase.update_Health(request)
            
            self.logger.info("Health updated successfully")
            return result
            
        except HealthNotFoundError as e:
            self.logger.warning(f"Health not found for update: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not found", "message": str(e)}
            )
        except HealthValidationError as e:
            self.logger.warning(f"Health update validation failed: {e}")
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
            self.logger.error(f"Unexpected error updating Health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
            )

    @router.delete(
        "/{id}",
        response_model=DeleteResponse,
        summary="Delete Health",
        description="Delete an existing Health",
        responses={
            200: {"description": "Health deleted successfully"},
            404: {"description": "Health not found"},
            422: {"description": "Deletion not allowed"},
        },
    )
    async def delete_Health(
        self,
        id: UUID = Path(..., description="Health unique identifier"),
        usecase: HealthUseCaseProtocol = Depends(get_Health_usecase),
        current_user = Depends(get_current_user),
        _: None = Depends(require_Health_permission("delete")),
    ) -> DeleteResponse:
        """
        Delete an existing Health entity.
        
        This endpoint deletes a Health with validation, permission checks,
        and comprehensive error handling.
        """
        try:
            self.logger.info(f"Deleting Health {id}")
            
            # Create request object
            request = DeleteHealthRequest(id=Health_id)
            
            # Execute use case
            result = await usecase.delete_Health(request)
            
            self.logger.info("Health deleted successfully")
            return result
            
        except HealthNotFoundError as e:
            self.logger.warning(f"Health not found for deletion: {e}")
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
            self.logger.error(f"Unexpected error deleting Health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
            )

    @router.get(
        "/",
        response_model=ListHealthchecksResponse,
        summary="List HealthChecks",
        description="Retrieve a list of HealthChecks with optional filtering and pagination",
        responses={
            200: {"description": "Healthchecks retrieved successfully"},
        },
    )
    async def list_HealthChecks(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
        search: Optional[str] = Query(None, description="Search term for filtering"),
        status: Optional[str] = Query(None, description="Filter by status"),
        usecase: HealthUseCaseProtocol = Depends(get_Health_usecase),
        current_user = Depends(get_current_user),
        _: None = Depends(require_Health_permission("list")),
    ) -> ListHealthchecksResponse:
        """
        Retrieve a list of HealthChecks with optional filtering and pagination.
        
        This endpoint supports filtering, searching, and pagination with
        comprehensive error handling and access control.
        """
        try:
            self.logger.info("Listing HealthChecks with filters")
            
            # Build filters
            filters = {}
            if search:
                filters["search"] = search
            if status:
                filters["status"] = status
            
            # Create request object
            request = ListHealthchecksRequest(
                skip=skip,
                limit=limit,
                filters=filters
            )
            
            # Execute use case
            result = await usecase.list_HealthChecks(request)
            
            self.logger.info("Healthchecks listed successfully", extra={"count": len(result.items)})
            return result
            
        except Exception as e:
            self.logger.error(f"Unexpected error listing HealthChecks: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Service temporarily unavailable", "message": "Request could not be completed"}
            )

    # @pyhex:begin:custom:router_methods
    # Add custom router methods here
    # @pyhex:end:custom:router_methods


# Exception handlers
@router.exception_handler(HealthValidationError)
async def Health_validation_exception_handler(request, exc: HealthValidationError):
    """Handle Health validation errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation failed", "message": str(exc)}
    )


@router.exception_handler(HealthNotFoundError)
async def Health_not_found_exception_handler(request, exc: HealthNotFoundError):
    """Handle Health not found errors."""
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
    description="Check the health status of the Health service",
    include_in_schema=False,
)
async def health_check():
    """Comprehensive health check endpoint for monitoring and container orchestration."""
    from datetime import datetime
    
    try:
        # Basic health checks
        current_time = datetime.utcnow()
        
        # Database connectivity check would go here
        # db_status = await check_database_connection()
        
        health_response = {
            "status": "healthy",
            "service": "Health_service",
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
        
    except Exception:
        # Health check should never fail with 500
        return {
            "status": "degraded",
            "service": "Health_service", 
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
        "service": "Health_service",
        "version": "1.0.0",
        "uptime": "N/A",  # Implement actual uptime tracking
        "requests_count": "N/A",  # Implement actual request counting
    }


# @pyhex:begin:custom:router_handlers
# Add custom router handlers here
# @pyhex:end:custom:router_handlers