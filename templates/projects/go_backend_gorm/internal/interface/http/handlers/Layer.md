# HTTP Handlers Layer Documentation

## Purpose
The HTTP Handlers layer provides the REST API interface, handling HTTP requests and responses while delegating business logic to use cases.

## Responsibilities

### What Handlers Are
- **HTTP Interface**: Handle HTTP requests and responses
- **Request Parsing**: Parse JSON, form data, URL parameters, and query strings
- **Response Formatting**: Format responses as JSON with appropriate HTTP status codes
- **Route Registration**: Register URL patterns and HTTP methods
- **Input Validation**: Validate HTTP-specific input (headers, content-type, etc.)

### What Handlers Are NOT
- **Not Business Logic**: Don't contain domain rules or business workflows
- **Not Data Access**: Don't call repositories directly
- **Not Entities**: Don't contain business data structures

## Data Flow

```
HTTP Request → Handler → UseCase (business logic) → Handler → HTTP Response
```

## Key Patterns

### 1. Thin Handler Pattern
Handlers should be thin - parse input, call use case, format response:
```go
func (h *Handler) CreateUser(w http.ResponseWriter, r *http.Request) {
    // 1. Parse request
    var request CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
        http.Error(w, "Invalid request", http.StatusBadRequest)
        return
    }
    
    // 2. Convert to entity (or let use case do it)
    entity := entityPkg.FromUserRequest(request)
    
    // 3. Call use case
    if err := h.userUseCase.Create(r.Context(), entity); err != nil {
        h.handleError(w, err)
        return
    }
    
    // 4. Format response
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(entity.ToUserResponse())
}
```

### 2. Dependency Injection
Handlers receive use cases through DI:
```go
type Handler struct {
    {{.EntitySnake}}UseCase usecasePkg.I{{.Entity}}UseCase
    logger              *utils.Logger
}
```

### 3. Route Registration
Handlers implement the `IHandler` interface and register their own routes:
```go
func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
    mux.HandleFunc("/api/v1/{{.EntitiesSnake}}", h.handle{{.Entities}})
    mux.HandleFunc("/api/v1/{{.EntitiesSnake}}/", h.handle{{.Entity}}ByID)
}
```

### 4. Error Handling
Handlers translate business errors into appropriate HTTP status codes:
- Validation errors → 400 Bad Request
- Not found → 404 Not Found
- Business rule violations → 422 Unprocessable Entity
- Internal errors → 500 Internal Server Error

## Architecture Benefits

1. **HTTP Separation**: HTTP concerns isolated from business logic
2. **Multiple Interfaces**: Same use cases can support HTTP, gRPC, CLI
3. **Testability**: Can test handlers with mock use cases
4. **API Versioning**: Easy to create v2 handlers using same use cases

## Template Variables Available

- `{{.Entity}}` - PascalCase entity name (e.g., "User")
- `{{.EntitySnake}}` - snake_case entity name (e.g., "user")
- `{{.Entities}}` - PascalCase plural name (e.g., "Users")
- `{{.EntitiesSnake}}` - snake_case plural name (e.g., "users")
- `{{.Domain}}` - PascalCase domain name
- `{{.DomainSnake}}` - snake_case domain name
- `{{.Module}}` - Go module name

## Generated Structure

```go
// Handler implementation
type Handler struct {
    {{.EntitySnake}}UseCase usecasePkg.I{{.Entity}}UseCase
    logger              *utils.Logger
}

// Constructor with dependency injection
func NewHandler(injector *do.Injector) (*Handler, error)

// Route registration
func (h *Handler) RegisterRoutes(mux *http.ServeMux)

// HTTP method handlers
func (h *Handler) handle{{.Entities}}(w http.ResponseWriter, r *http.Request)      // GET/POST /{{.EntitiesSnake}}
func (h *Handler) handle{{.Entity}}ByID(w http.ResponseWriter, r *http.Request)   // GET/PUT/DELETE /{{.EntitiesSnake}}/:id
```

## Standard HTTP Endpoints

### Collection Endpoints (`/api/v1/{{.EntitiesSnake}}`)

#### GET - List Entities
- Parse query parameters (limit, offset, filters)
- Call use case List method
- Return JSON array of entities

#### POST - Create Entity
- Parse JSON request body
- Convert to entity
- Call use case Create method
- Return created entity with 201 status

### Item Endpoints (`/api/v1/{{.EntitiesSnake}}/:id`)

#### GET - Get Entity by ID
- Parse ID from URL path
- Call use case GetByID method
- Return entity JSON or 404

#### PUT - Update Entity
- Parse ID from URL path
- Parse JSON request body
- Ensure ID matches
- Call use case Update method
- Return updated entity

#### DELETE - Delete Entity
- Parse ID from URL path
- Call use case Delete method
- Return 204 No Content

## Request/Response Handling

### Request Parsing
```go
// JSON body parsing
var entity entityPkg.{{.Entity}}
if err := json.NewDecoder(r.Body).Decode(&entity); err != nil {
    http.Error(w, "Invalid request body", http.StatusBadRequest)
    return
}

// URL parameter parsing
idStr := r.URL.Path[len("/api/v1/{{.EntitiesSnake}}/"):]
id, err := uuid.Parse(idStr)
if err != nil {
    http.Error(w, "Invalid ID", http.StatusBadRequest)
    return
}

// Query parameter parsing
query := r.URL.Query()
limit := 10 // default
if limitStr := query.Get("limit"); limitStr != "" {
    if l, err := strconv.Atoi(limitStr); err == nil && l > 0 {
        limit = l
    }
}
```

### Response Formatting
```go
// Success response
w.Header().Set("Content-Type", "application/json")
w.WriteHeader(http.StatusOK)
json.NewEncoder(w).Encode(entity.To{{.Entity}}Response())

// Error response
w.Header().Set("Content-Type", "application/json")
w.WriteHeader(http.StatusBadRequest)
json.NewEncoder(w).Encode(map[string]string{
    "error": "Validation failed",
    "message": err.Error(),
})
```

## Dynamic Registration

Handlers register themselves in the DI container:
```go
func Register{{.Entity}}Handler(injector *do.Injector) {
    do.Provide(injector, NewHandler)
    
    // Add to handler container using reflection
    do.ProvideNamedValue(injector, "register_{{.EntitySnake}}_handler", func(h *handlers.Handlers) {
        handler := do.MustInvoke[*Handler](injector)
        handlers.AddField(h, "{{.Entity}}", handler)
    })
}
```

The central `Handlers` container automatically registers routes for all handlers:
```go
func (h *Handlers) RegisterAllRoutes(mux *http.ServeMux) {
    // Automatically calls RegisterRoutes on all registered handlers
    for name, handler := range h.dynamicFields {
        if routeHandler, ok := handler.(interface{ RegisterRoutes(*http.ServeMux) }); ok {
            h.logger.Info("registering routes for " + name)
            routeHandler.RegisterRoutes(mux)
        }
    }
}
```

## Error Handling Patterns

```go
func (h *Handler) handleError(w http.ResponseWriter, err error) {
    h.logger.LogError(context.Background(), err, "handler error")
    
    // Map business errors to HTTP status codes
    switch {
    case strings.Contains(err.Error(), "not found"):
        http.Error(w, "Resource not found", http.StatusNotFound)
    case strings.Contains(err.Error(), "validation"):
        http.Error(w, err.Error(), http.StatusBadRequest)
    case strings.Contains(err.Error(), "already exists"):
        http.Error(w, err.Error(), http.StatusConflict)
    default:
        http.Error(w, "Internal server error", http.StatusInternalServerError)
    }
}
```

## Logging and Monitoring

Handlers log all requests with timing information:
```go
func (h *Handler) handle{{.Entities}}(w http.ResponseWriter, r *http.Request) {
    start := time.Now()
    ctx := r.Context()
    
    // ... handle request ...
    
    // Log request completion
    duration := time.Since(start)
    h.logger.LogRequest(ctx, r.Method, r.URL.Path, http.StatusOK, duration)
}
```

This provides a complete HTTP interface that delegates all business logic to use cases while handling HTTP-specific concerns like parsing, formatting, and status codes.
