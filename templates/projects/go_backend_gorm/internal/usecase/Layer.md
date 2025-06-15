# UseCase Layer Documentation

## Purpose
The UseCase layer contains application business logic and orchestrates the flow between different domain components. This is where business workflows are implemented.

## Responsibilities

### What UseCases Are
- **Business Workflow Orchestration**: Coordinate multiple repositories and domain entities
- **Application Logic**: Implement business processes and workflows
- **Data Transformation Hub**: Convert between all layer types (entities, models, requests, responses)
- **Transaction Management**: Handle cross-repository transactions
- **Business Rule Enforcement**: Apply domain rules and validation

### What UseCases Are NOT
- **Not HTTP Handlers**: Don't handle HTTP requests directly
- **Not Data Access**: Don't contain SQL queries or database logic
- **Not Presentation Logic**: Don't format responses for specific clients

## Data Flow

```
Handler → UseCase → Entity (business logic) → Repository → Model → Database
Handler ← UseCase ← Entity (business logic) ← Repository ← Model ← Database
```

## Key Patterns

### 1. Interface-First Design
Every use case defines an interface for testability:
```go
type I{{.Entity}}UseCase interface {
    Create(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
    GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.{{.Entity}}, error)
    List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*entityPkg.{{.Entity}}, error)
    Update(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
    Delete(ctx context.Context, id uuid.UUID) error
}
```

### 2. Dependency Injection
Use cases receive repositories and other dependencies through DI:
```go
type {{.Entity}}UseCase struct {
    {{.EntitySnake}}Repo repoPkg.I{{.Entity}}Repository
    logger           *utils.Logger
    // Other dependencies (email service, event publisher, etc.)
}
```

### 3. Business Logic Orchestration
Use cases coordinate multiple operations:
- Validate business rules using entities
- Call multiple repositories if needed
- Handle cross-cutting concerns (logging, events)
- Manage transactions

### 4. Error Handling
Use cases translate repository errors into business-appropriate errors and handle business rule violations.

## Architecture Benefits

1. **Business Logic Centralization**: All business workflows in one place
2. **Testability**: Can mock repositories and test business logic in isolation
3. **Reusability**: Same use case can be called from HTTP, gRPC, CLI, etc.
4. **Transaction Management**: Coordinate operations across multiple repositories

## Template Variables Available

- `{{.Entity}}` - PascalCase entity name (e.g., "User")
- `{{.EntitySnake}}` - snake_case entity name (e.g., "user")
- `{{.Domain}}` - PascalCase domain name
- `{{.DomainSnake}}` - snake_case domain name
- `{{.Module}}` - Go module name

## Generated Structure

```go
// Interface definition
type I{{.Entity}}UseCase interface {
    Create(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
    GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.{{.Entity}}, error)
    List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*entityPkg.{{.Entity}}, error)
    Update(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
    Delete(ctx context.Context, id uuid.UUID) error
}

// Implementation
type {{.Entity}}UseCase struct {
    {{.EntitySnake}}Repo repoPkg.I{{.Entity}}Repository
    logger           *utils.Logger
}

// Constructor with dependency injection
func New{{.Entity}}UseCase(injector *do.Injector) (*{{.Entity}}UseCase, error)

// Business operations
func (uc *{{.Entity}}UseCase) Create(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error
func (uc *{{.Entity}}UseCase) GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.{{.Entity}}, error)
// ... other business operations
```

## Standard UseCase Operations

### Create
1. Validate business rules using entity methods
2. Check for business constraints (e.g., unique business identifiers)
3. Call repository to persist
4. Handle business-specific errors
5. Log business events

### Read (GetByID)
1. Call repository to retrieve
2. Apply business logic if needed (e.g., permission checks)
3. Return entity

### List
1. Validate filter parameters
2. Apply business logic to filters
3. Call repository with processed filters
4. Return entities

### Update
1. Retrieve existing entity
2. Validate business rules for update
3. Check business constraints
4. Call repository to update
5. Handle optimistic locking

### Delete
1. Check business rules for deletion (e.g., can't delete if has dependencies)
2. Perform soft delete or hard delete based on business rules
3. Handle cascading business logic

## Data Transformation Responsibilities

The UseCase layer is responsible for converting between layer types:

```go
// From HTTP Request to Entity (usually delegated to entity)
entity := entityPkg.From{{.Entity}}Request(request)

// Entity validation
if err := entity.ValidateAll(); err != nil {
    return fmt.Errorf("validation failed: %w", err)
}

// Business logic
if err := uc.applyBusinessRules(entity); err != nil {
    return err
}

// Call repository (repository handles entity → model conversion)
return uc.{{.EntitySnake}}Repo.Create(ctx, entity)
```

## Dynamic Registration

Use cases register themselves in the DI container:
```go
func Register{{.Entity}}UseCase(injector *do.Injector) {
    do.Provide(injector, New{{.Entity}}UseCase)
    
    // Add to use case container using reflection
    do.ProvideNamedValue(injector, "register_{{.EntitySnake}}_usecase", func(uc *usecase.UseCases) {
        useCase := do.MustInvoke[*{{.Entity}}UseCase](injector)
        usecase.AddField(uc, "{{.Entity}}", useCase)
    })
}
```

## Business Logic Examples

```go
func (uc *{{.Entity}}UseCase) Create(ctx context.Context, {{.EntitySnake}} *entityPkg.{{.Entity}}) error {
    // 1. Validate entity business rules
    if err := {{.EntitySnake}}.ValidateAll(); err != nil {
        return fmt.Errorf("validation failed: %w", err)
    }
    
    // 2. Apply business logic (example: check for duplicates)
    existing, err := uc.{{.EntitySnake}}Repo.GetByEmail(ctx, {{.EntitySnake}}.Email)
    if err == nil && existing != nil {
        return fmt.Errorf("{{.EntitySnake}} with email already exists")
    }
    
    // 3. Apply business rules (example: auto-activate new users)
    {{.EntitySnake}}.IsActive = true
    
    // 4. Persist
    if err := uc.{{.EntitySnake}}Repo.Create(ctx, {{.EntitySnake}}); err != nil {
        return fmt.Errorf("failed to create {{.EntitySnake}}: %w", err)
    }
    
    // 5. Business events (example: send welcome email)
    uc.logger.Info(fmt.Sprintf("Created new {{.EntitySnake}}: %s", {{.EntitySnake}}.ID))
    
    return nil
}
```

This layer ensures that all business logic is centralized, testable, and reusable across different interfaces (HTTP, gRPC, CLI, etc.).
