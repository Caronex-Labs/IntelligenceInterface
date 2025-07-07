# Interface Layer

The Interface Layer implements the HTTP API interface using FastAPI, providing REST endpoints, authentication,
authorization, and comprehensive error handling.

## Architecture

The interface layer follows Clean Architecture principles and is organized by domain:

```
app/interface/
├── __init__.py                 # Interface layer package
├── README.md                   # This documentation
└── {domain}/                   # Domain-specific interface
    ├── __init__.py            # Domain interface package
    ├── router.py.j2           # FastAPI router template
    ├── dependencies.py.j2     # Dependency injection template
    ├── protocols.py.j2        # Interface protocols template
    └── interface.yaml         # Interface configuration
```

## Key Components

### Router (`router.py.j2`)

- FastAPI router with CRUD endpoints
- HTTP method implementations (GET, POST, PUT, DELETE)
- Request/response model integration
- Error handling and status codes
- OpenAPI documentation generation

### Dependencies (`dependencies.py.j2`)

- Dependency injection functions
- Authentication and authorization
- Rate limiting and caching
- Request validation and metrics

### Protocols (`protocols.py.j2`)

- Interface contracts and protocols
- Authentication and authorization interfaces
- Middleware and validation protocols
- Metrics and caching interfaces

### Configuration (`interface.yaml`)

- Endpoint definitions and settings
- Authentication and authorization config
- Middleware and rate limiting settings
- OpenAPI documentation configuration

## Features

### REST API Endpoints

- **POST /** - Create new resource
- **GET /{id}** - Retrieve resource by ID
- **PUT /{id}** - Update existing resource
- **DELETE /{id}** - Delete resource
- **GET /** - List resources with filtering and pagination

### Authentication & Authorization

- JWT Bearer token authentication
- Role-based access control (RBAC)
- Permission-based authorization
- Resource ownership validation

### Error Handling

- Custom exception handlers
- Proper HTTP status codes
- Structured error responses
- Error logging and monitoring

### Middleware Support

- CORS configuration
- Request/response logging
- Compression
- Response time tracking
- Security headers

### Performance Features

- Response caching
- Rate limiting
- Request validation
- Metrics collection

### API Documentation

- Automatic OpenAPI schema generation
- Interactive Swagger UI
- Comprehensive endpoint documentation
- Request/response examples

## Usage

### Basic Router Usage

```python
from app.interface.user.router import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
```

### Dependency Injection

```python
from app.interface.user.dependencies import get_current_user, require_user_permission

@router.get("/protected")
async def protected_endpoint(
    current_user = Depends(get_current_user),
    _: None = Depends(require_user_permission("read"))
):
    return {"user": current_user}
```

### Custom Authentication

```python
from app.interface.user.protocols import AuthenticationProtocol

class CustomAuth(AuthenticationProtocol):
    async def authenticate_user(self, request, credentials):
        # Custom authentication logic
        pass
```

## Integration with Other Layers

### Use Case Integration

The interface layer depends on the use case layer for business logic:

```python
# Dependencies inject use case
usecase: UserUseCaseProtocol = Depends(get_user_usecase)

# Router methods call use case operations
result = await usecase.create_user(request)
```

### Error Translation

Domain exceptions are translated to HTTP responses:

```python
try:
    result = await usecase.operation()
except UserNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

## Configuration

### Interface Configuration (`interface.yaml`)

```yaml
interface:
  api:
    prefix: "/api/v1/users"
    tags: ["users"]
  
  authentication:
    enabled: true
    scheme: "Bearer"
  
  rate_limiting:
    enabled: true
    default_limit: 100
    default_window: 60
```

### Environment Variables

- `API_HOST`: API host (default: localhost)
- `API_PORT`: API port (default: 8000)
- `JWT_SECRET_KEY`: JWT signing key
- `CORS_ORIGINS`: Allowed CORS origins

## Testing

### Unit Testing

```python
from fastapi.testclient import TestClient
from app.interface.user.router import router

client = TestClient(router)

def test_create_user():
    response = client.post("/", json={"name": "Test User"})
    assert response.status_code == 201
```

### Integration Testing

```python
async def test_user_crud_flow():
    # Test full CRUD operations
    user = await create_user(test_data)
    retrieved = await get_user(user.id)
    updated = await update_user(user.id, update_data)
    await delete_user(user.id)
```

## Security Considerations

### Input Validation

- All inputs validated using Pydantic models
- SQL injection prevention
- XSS protection through proper encoding

### Authentication

- JWT tokens with expiration
- Secure token storage and transmission
- Token refresh mechanisms

### Authorization

- Fine-grained permission system
- Resource-level access control
- Role-based security

### Rate Limiting

- Per-client request limits
- Endpoint-specific limits
- Abuse prevention

## Monitoring and Observability

### Metrics Collection

- Request/response metrics
- Error rate tracking
- Performance monitoring
- Custom business metrics

### Logging

- Structured request/response logging
- Error logging with context
- Security event logging
- Performance logging

### Health Checks

- Service health endpoints
- Dependency health checks
- Readiness and liveness probes

## Best Practices

1. **Error Handling**: Always provide meaningful error messages and proper status codes
2. **Input Validation**: Validate all inputs at the API boundary
3. **Authentication**: Implement proper authentication for all non-public endpoints
4. **Documentation**: Keep OpenAPI documentation up to date
5. **Performance**: Use caching and rate limiting appropriately
6. **Security**: Follow OWASP guidelines for API security
7. **Testing**: Maintain comprehensive test coverage
8. **Monitoring**: Implement proper logging and metrics collection