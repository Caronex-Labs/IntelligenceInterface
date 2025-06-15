# Dependency Injection Layer Documentation

## Purpose
The DI (Dependency Injection) layer provides configuration and registration of all components in the dependency injection container, enabling loose coupling and testability across the entire application.

## Responsibilities

### What DI Layer Does
- **Component Registration**: Register all domain components (repositories, use cases, handlers) in the DI container
- **Dependency Wiring**: Define how components depend on each other
- **Lifecycle Management**: Control when components are created and destroyed
- **Configuration**: Centralize component configuration and initialization

### What DI Layer Does NOT
- **Not Business Logic**: Contains no domain or application logic
- **Not Data Access**: Doesn't contain database or external service calls
- **Not HTTP Handling**: Doesn't process requests or responses

## Data Flow

```
Application Startup → DI Registration → Component Creation → Dependency Resolution
```

## Key Patterns

### 1. Registration Functions
Each domain provides a registration function that wires all its components:
```go
func Register{{.Domain}}(injector *do.Injector) {
    // Register all components for this domain
    repositoryPkg.Register{{.Entity}}Repository(injector)
    usecasePkg.Register{{.Entity}}UseCase(injector)
    handlersPkg.Register{{.Entity}}Handler(injector)
}
```

### 2. Dependency Chain
Components are registered in dependency order:
1. **Infrastructure**: Database, logger, config
2. **Repositories**: Data access layer
3. **Use Cases**: Business logic layer (depends on repositories)
4. **Handlers**: Interface layer (depends on use cases)

### 3. Interface-Based Registration
Components are registered by their interfaces, enabling easy testing and swapping:
```go
// Register interface, not concrete type
do.Provide(injector, func() I{{.Entity}}Repository {
    return New{{.Entity}}Repository(injector)
})
```

### 4. Dynamic Container Integration
Components are added to dynamic containers for runtime access:
```go
// Add to central repositories container
do.ProvideNamedValue(injector, "register_{{.EntitySnake}}_repository", func(r *repository.Repositories) {
    repo := do.MustInvoke[I{{.Entity}}Repository](injector)
    repository.AddField(r, "{{.Entity}}", repo)
})
```

## Architecture Benefits

1. **Loose Coupling**: Components depend on interfaces, not concrete implementations
2. **Testability**: Easy to inject mock dependencies for testing
3. **Modularity**: Domains can be added/removed by changing registration
4. **Configuration Centralization**: All wiring logic in one place per domain

## Template Variables Available

- `{{.Entity}}` - PascalCase entity name (e.g., "User")
- `{{.EntitySnake}}` - snake_case entity name (e.g., "user")
- `{{.Domain}}` - PascalCase domain name
- `{{.DomainSnake}}` - snake_case domain name

## Generated Structure

```go
// Main registration function for the domain
func Register{{.Domain}}(injector *do.Injector) {
    // Register repository
    repositoryPkg.Register{{.Entity}}Repository(injector)
    
    // Register use case
    usecasePkg.Register{{.Entity}}UseCase(injector)
    
    // Register handler
    handlersPkg.Register{{.Entity}}Handler(injector)
}
```

## Component Registration Flow

### 1. Repository Registration
```go
func Register{{.Entity}}Repository(injector *do.Injector) {
    // Register the repository implementation
    do.Provide(injector, New{{.Entity}}Repository)
    
    // Add to repositories container
    do.ProvideNamedValue(injector, "register_{{.EntitySnake}}_repository", func(r *repository.Repositories) {
        repo, err := do.Invoke[I{{.Entity}}Repository](injector)
        if err != nil {
            panic(err)
        }
        repository.AddField(r, "{{.Entity}}", repo)
    })
}
```

### 2. Use Case Registration
```go
func Register{{.Entity}}UseCase(injector *do.Injector) {
    // Register the use case implementation
    do.Provide(injector, New{{.Entity}}UseCase)
    
    // Add to use cases container
    do.ProvideNamedValue(injector, "register_{{.EntitySnake}}_usecase", func(uc *usecase.UseCases) {
        useCase, err := do.Invoke[*{{.Entity}}UseCase](injector)
        if err != nil {
            panic(err)
        }
        usecase.AddField(uc, "{{.Entity}}", useCase)
    })
}
```

### 3. Handler Registration
```go
func Register{{.Entity}}Handler(injector *do.Injector) {
    // Register the handler implementation
    do.Provide(injector, NewHandler)
    
    // Add to handlers container
    do.ProvideNamedValue(injector, "register_{{.EntitySnake}}_handler", func(h *handlers.Handlers) {
        handler, err := do.Invoke[*Handler](injector)
        if err != nil {
            panic(err)
        }
        handlers.AddField(h, "{{.Entity}}", handler)
    })
}
```

## Integration with Main Application

In the main application, domains are registered during startup:

```go
func main() {
    // Create dependency injector
    injector := do.New()

    // Register infrastructure components
    do.Provide(injector, utils.NewConfig)
    do.Provide(injector, utils.NewLogger)
    do.Provide(injector, postgres.NewDB)

    // Register core containers
    repository.RegisterRepositories(injector)
    usecase.RegisterUseCases(injector)
    handlers.RegisterHandlers(injector)

    // Register domain components
    user.RegisterUser(injector)          // Generated DI registration
    product.RegisterProduct(injector)    // Generated DI registration
    profile.RegisterProfile(injector)    // Generated DI registration

    // Start server
    server := httpServer.NewServer(injector)
    server.Start()
}
```

## Dynamic Container Pattern

The system uses a dynamic container pattern to allow runtime addition of components:

### Central Containers
```go
// Repository container
type Repositories struct {
    Health health.IHealthRepository  // Static component
    dynamicFields map[string]interface{}  // Dynamic components
}

// Use case container  
type UseCases struct {
    Health IHealthUseCase  // Static component
    dynamicFields map[string]interface{}  // Dynamic components
}

// Handler container
type Handlers struct {
    Health *health.Handler  // Static component
    dynamicFields map[string]interface{}  // Dynamic components
}
```

### Dynamic Field Management
```go
// Add component to container
func AddField(container interface{}, name string, value interface{}) {
    // Uses reflection to add field to dynamicFields map
}

// Get component from container
func GetField(container interface{}, name string) (interface{}, bool) {
    // First check static fields via reflection
    // Then check dynamicFields map
}
```

## Dependency Resolution

When a component needs dependencies, the DI container resolves them:

```go
func New{{.Entity}}UseCase(injector *do.Injector) (*{{.Entity}}UseCase, error) {
    // Get repositories container
    repositories := do.MustInvoke[*repository.Repositories](injector)
    
    // Get specific repository from container
    repoField, ok := repository.GetField(repositories, "{{.Entity}}")
    if !ok {
        return nil, fmt.Errorf("failed to get {{.EntitySnake}} repository")
    }
    
    // Type assertion to interface
    {{.EntitySnake}}Repo, ok := repoField.(repoPkg.I{{.Entity}}Repository)
    if !ok {
        return nil, fmt.Errorf("failed to cast repository to correct type")
    }

    // Get other dependencies
    logger := do.MustInvoke[*utils.Logger](injector)

    return &{{.Entity}}UseCase{
        {{.EntitySnake}}Repo: {{.EntitySnake}}Repo,
        logger:           logger,
    }, nil
}
```

## Testing Benefits

The DI pattern enables easy testing:

```go
func TestUserUseCase_Create(t *testing.T) {
    // Create test injector
    injector := do.New()
    
    // Register mock dependencies
    mockRepo := &MockUserRepository{}
    do.ProvideValue(injector, mockRepo)
    
    // Create use case with mocked dependencies
    useCase, err := NewUserUseCase(injector)
    require.NoError(t, err)
    
    // Test business logic
    err = useCase.Create(context.Background(), &User{})
    assert.NoError(t, err)
    assert.True(t, mockRepo.CreateCalled)
}
```

## Configuration Management

DI registration can be configured through environment or config files:

```go
func Register{{.Domain}}(injector *do.Injector) {
    config := do.MustInvoke[*utils.Config](injector)
    
    // Conditional registration based on config
    if config.Features.{{.Domain}}Enabled {
        repositoryPkg.Register{{.Entity}}Repository(injector)
        usecasePkg.Register{{.Entity}}UseCase(injector)
        handlersPkg.Register{{.Entity}}Handler(injector)
    }
}
```

This approach provides a flexible, testable, and maintainable dependency injection system that supports both static core components and dynamically generated domain components.
