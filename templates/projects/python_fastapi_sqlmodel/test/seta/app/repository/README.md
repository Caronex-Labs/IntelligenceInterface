# Repository Layer - Hexagonal Architecture

The repository layer provides data access abstraction following hexagonal architecture principles and co-location
patterns.

## Architecture Overview

The repository layer sits between the use case layer and the database, implementing the Repository pattern with
async/await support for PostgreSQL operations.

### Co-location Pattern

```
app/repository/{{domain}}/
├── repository.yaml          # Repository configuration
├── repository.py.j2        # Repository implementation template
├── protocols.py.j2         # Repository interface protocols
├── test_repository.py.j2   # Repository tests template
└── __init__.py
```

## Repository Features

### Async Database Operations

- Full async/await support for PostgreSQL
- Connection pooling and session management
- Transaction handling with rollback support
- Query optimization and performance monitoring

### CRUD Operations

- Create: Async entity creation with validation
- Read: Single entity retrieval by ID or criteria
- Update: Partial and full entity updates
- Delete: Hard and soft delete support
- List: Paginated queries with filtering and sorting

### Advanced Query Methods

- Complex filtering with multiple criteria
- Relationship-based queries (joins)
- Aggregation and statistical queries
- Full-text search capabilities
- Custom query methods with @pyhex markers

### Database Session Management

- Automatic session lifecycle management
- Connection pooling configuration
- Transaction boundaries with proper cleanup
- Error handling and connection recovery

## Configuration Structure

Repository configuration inherits from core and entity layers:

```yaml
# repository.yaml
repository:
  name: "{{domain|title}}Repository"
  interface: "{{domain|title}}RepositoryProtocol"
  implementation: "SQLModel{{domain|title}}Repository"
  
async_operations:
  enabled: true
  session_management: "automatic"
  connection_pooling: true
  transaction_support: true

crud_operations:
  create:
    validation: true
    return_created: true
  read:
    soft_delete_aware: true
    eager_loading: false
  update:
    partial_updates: true
    optimistic_locking: false
  delete:
    soft_delete: true
    cascade_handling: true
  list:
    pagination: true
    filtering: true
    sorting: true
    max_page_size: 100

query_methods:
  - name: "find_by_email"
    description: "Find entity by email address"
    parameters: ["email: str"]
    return_type: "Optional[{{domain|title}}]"
    query_type: "single"
  - name: "find_active_entities"
    description: "Find all active entities"
    parameters: []
    return_type: "List[{{domain|title}}]"
    query_type: "list"
```

## Generated Repository Components

### Repository Protocol (Interface)

Defines the contract for repository operations:

- CRUD method signatures
- Custom query method interfaces
- Transaction management methods
- Type hints and documentation

### Repository Implementation

SQLModel-based implementation with:

- Async database operations
- Session dependency injection
- Error handling and logging
- Performance optimization
- @pyhex markers for custom methods

### Repository Tests

Comprehensive test suite including:

- CRUD operation tests
- Custom query method tests
- Transaction handling tests
- Error condition tests
- Performance and concurrency tests

## Integration Points

### Use Case Layer Integration

```python
# Dependency injection in use cases
class UserUseCase:
    def __init__(self, user_repository: UserRepositoryProtocol):
        self.user_repository = user_repository
    
    async def create_user(self, request: CreateUserRequest):
        user = User(**request.dict())
        return await self.user_repository.create(user)
```

### Database Session Integration

```python
# Session management with FastAPI
@app.post("/users")
async def create_user(
    request: CreateUserRequest,
    session: AsyncSession = Depends(get_db_session)
):
    repository = UserRepository(session)
    return await repository.create(User(**request.dict()))
```

## Quality Standards

- 100% async/await pattern compliance
- Comprehensive error handling
- Type hints on all methods
- Docstring coverage > 90%
- Test coverage > 95%
- Performance benchmarks for queries
- Connection pooling optimization

## Testing Strategy

Repository tests use:

- In-memory SQLite for unit tests
- PostgreSQL containers for integration tests
- Async test fixtures and helpers
- Transaction rollback for test isolation
- Performance benchmarking tests
- Concurrent operation tests

## Custom Query Extensions

Use @pyhex markers for domain-specific queries:

```python
# @pyhex:begin:custom_queries
async def find_users_by_complex_criteria(
    self,
    criteria: Dict[str, Any]
) -> List[User]:
    # Custom implementation preserved during regeneration
    pass
# @pyhex:end:custom_queries
```