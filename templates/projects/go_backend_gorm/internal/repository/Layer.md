# Repository Layer Documentation

## Purpose
The Repository layer provides data access abstraction, isolating the domain and application layers from database implementation details.

## Responsibilities

### What Repositories Are
- **Data Access Abstraction**: Abstract interface between business logic and data storage
- **Model ↔ Entity Conversion**: Convert between database models and domain entities
- **Query Implementation**: Implement data retrieval and persistence operations
- **Database Operations**: Handle transactions, connections, and database-specific logic

### What Repositories Are NOT
- **Not Business Logic**: Repositories don't contain domain rules or business validation
- **Not Controllers**: Repositories don't handle HTTP requests or user input
- **Not Use Cases**: Repositories don't orchestrate business workflows

## Data Flow

```
UseCase → Repository Interface → Repository Implementation → Database Model → Database
UseCase ← Repository Interface ← Repository Implementation ← Database Model ← Database
```

## Key Patterns

### 1. Interface-First Design
Every repository starts with an interface defining the contract:
```go
type I{{.Entity}}Repository interface {
    Create(ctx context.Context, entity *{{.Entity}}) error
    GetByID(ctx context.Context, id uuid.UUID) (*{{.Entity}}, error)
    List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*{{.Entity}}, error)
    Update(ctx context.Context, entity *{{.Entity}}) error
    Delete(ctx context.Context, id uuid.UUID) error
}
```

### 2. Dependency Injection
Repositories are registered in the DI container and injected into use cases:
```go
func New{{.Entity}}Repository(injector *do.Injector) (I{{.Entity}}Repository, error)
```

### 3. Model Conversion
Repositories handle conversion between entities and models:
- Entity → Model (for persistence)
- Model → Entity (for retrieval)

### 4. Error Handling
Repositories translate database errors into domain-appropriate errors:
- `gorm.ErrRecordNotFound` → domain-specific not found error
- Database connection errors → infrastructure errors

## Architecture Benefits

1. **Testability**: Use cases can be tested with mock repositories
2. **Database Independence**: Can switch between PostgreSQL, MySQL, etc.
3. **Query Optimization**: Database-specific optimizations isolated in repository
4. **Transaction Management**: Centralized transaction handling

## Template Variables Available

- `{{.Entity}}` - PascalCase entity name (e.g., "User")
- `{{.EntitySnake}}` - snake_case entity name (e.g., "user")
- `{{.Domain}}` - PascalCase domain name
- `{{.DomainSnake}}` - snake_case domain name
- `{{.Module}}` - Go module name

## Generated Structure

```go
// Interface definition
type I{{.Entity}}Repository interface {
    Create(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
    GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.{{.Entity}}, error)
    List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*entityPkg.{{.Entity}}, error)
    Update(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
    Delete(ctx context.Context, id uuid.UUID) error
}

// Implementation
type {{.Entity}}Repository struct {
    db     *postgres.DB
    logger *utils.Logger
}

// Constructor with dependency injection
func New{{.Entity}}Repository(injector *do.Injector) (I{{.Entity}}Repository, error)

// CRUD operations with model conversion
func (r *{{.Entity}}Repository) Create(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
func (r *{{.Entity}}Repository) GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.{{.Entity}}, error)
// ... other CRUD methods
```

## Standard Repository Operations

### Create
- Convert entity to model
- Insert into database
- Handle unique constraint violations

### Read (GetByID)
- Query by primary key
- Convert model to entity
- Handle not found cases

### List
- Apply filters and pagination
- Convert models to entities
- Handle empty results

### Update
- Convert entity to model
- Update existing record
- Handle optimistic locking if needed

### Delete
- Soft delete (if configured) or hard delete
- Handle cascading deletes

## Dynamic Registration

Repositories register themselves in the DI container:
```go
func Register{{.Entity}}Repository(injector *do.Injector) {
    do.Provide(injector, New{{.Entity}}Repository)
    
    // Add to repository container using reflection
    do.ProvideNamedValue(injector, "register_{{.EntitySnake}}_repository", func(r *repository.Repositories) {
        repo := do.MustInvoke[I{{.Entity}}Repository](injector)
        repository.AddField(r, "{{.Entity}}", repo)
    })
}
```

This allows use cases to access repositories through the central `Repositories` container while maintaining type safety.

## Error Handling Patterns

```go
func (r *{{.Entity}}Repository) GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.{{.Entity}}, error) {
    var model modelsPkg.{{.Entity}}
    err := r.db.WithContext(ctx).First(&model, "id = ?", id).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, fmt.Errorf("{{.DomainSnake}} not found: %w", err)
        }
        return nil, err // Infrastructure error
    }
    
    entity := entityPkg.From{{.Entity}}Model(&model)
    return entity, nil
}
```
