# Entity Layer Documentation

## Purpose
The Entity layer contains Domain Transfer Objects (DTOs) that represent the core business entities in a pure, framework-agnostic way.

## Responsibilities

### What Entities Are
- **Pure Business Objects**: Entities represent the core business concepts without any infrastructure concerns
- **DTOs Between Layers**: Entities serve as the data transfer format between the usecase layer and other layers
- **Domain Logic Containers**: Entities can contain business validation and domain-specific methods
- **Framework Agnostic**: No dependencies on databases, HTTP frameworks, or external libraries

### What Entities Are NOT
- **Not Database Models**: Entities don't contain database-specific constraints or ORM tags
- **Not Request/Response Types**: Entities don't contain HTTP-specific serialization concerns
- **Not Infrastructure Aware**: Entities don't know about external systems or frameworks

## Data Flow

```
HTTP Request → Handler → UseCase → Entity → UseCase → Repository (converts to Model)
                                     ↓
HTTP Response ← Handler ← UseCase ← Entity ← UseCase ← Repository (converts from Model)
```

## Key Patterns

### 1. Conversion Methods
Every entity provides conversion methods to/from other layer types:
- `FromXXXModel(model)` - Convert from repository model to entity
- `ToXXXModel()` - Convert from entity to repository model
- `FromXXXRequest(request)` - Convert from HTTP request to entity
- `ToXXXResponse()` - Convert from entity to HTTP response

### 2. Business Validation
Entities contain business-level validation that applies regardless of the input source:
- Field-level validation methods
- Cross-field business rules
- Domain-specific constraints

### 3. Domain Methods
Entities can contain domain-specific behavior:
- Calculated properties
- Business rule enforcement
- State transitions

## Architecture Benefits

1. **Clean Separation**: Each layer has its own data types with specific concerns
2. **Testability**: Business logic can be tested without infrastructure dependencies
3. **Flexibility**: Can easily change database schema or API format without affecting business logic
4. **Maintainability**: Clear boundaries make the code easier to understand and modify

## Template Variables Available

- `{{.Entity}}` - PascalCase entity name (e.g., "User")
- `{{.EntitySnake}}` - snake_case entity name (e.g., "user")
- `{{.Domain}}` - PascalCase domain name
- `{{.DomainSnake}}` - snake_case domain name
- `{{.Module}}` - Go module name
- `{{.Fields}}` - Array of configured fields
- `{{.EntityConfig}}` - Full entity configuration

## Generated Structure

```go
type {{.Entity}} struct {
    ID        uuid.UUID // Always present
    // Configured fields based on EntityConfig.Fields
    CreatedAt time.Time // Always present
    UpdatedAt time.Time // Always present
}

// Conversion methods
func From{{.Entity}}Model(model) *{{.Entity}}
func (e *{{.Entity}}) To{{.Entity}}Model() *Model
func From{{.Entity}}Request(request) *{{.Entity}}
func (e *{{.Entity}}) To{{.Entity}}Response() interface{}

// Business validation (if fields have validations)
func (e *{{.Entity}}) ValidateField() error
func (e *{{.Entity}}) ValidateAll() error
```

## Configuration-Driven Features

The template uses configuration to generate:
- **Field Definitions**: Based on `EntityConfig.Fields`
- **Validation Methods**: Based on field validation rules
- **Business Logic Placeholders**: Marked sections for custom code
- **Conversion Logic**: Automatic mapping between field configurations
