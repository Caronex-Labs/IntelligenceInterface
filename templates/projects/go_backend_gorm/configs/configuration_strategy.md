# Configuration Strategy for GoHex Engine

## Design Philosophy

**Opinionated but Flexible**: Provide battle-tested defaults that work for 90% of use cases, with clear extension points for the other 10%.

## Configuration Levels

### Level 1: Minimal Configuration (Recommended Start)
- **Goal**: Maximum value with minimal effort
- **Config Size**: 10-20 lines
- **Generated Code**: ~1000+ lines of production-ready code
- **Use Case**: MVP, prototypes, standard CRUD domains

```yaml
domain: "user"
entity:
  fields:
    - name: "Email"
      type: "string"
      unique: true
    - name: "Name"
      type: "string"
```

**What Gets Generated Automatically**:
- Complete hexagonal architecture structure
- Standard CRUD operations (Create, Read, Update, Delete)
- REST API endpoints with proper HTTP status codes
- Request/response validation
- Database models with GORM tags
- Error handling and logging
- Dependency injection wiring
- Basic tests

### Level 2: Standard Configuration (Common Customizations)
- **Goal**: Handle common real-world requirements
- **Config Size**: 50-100 lines
- **Generated Code**: ~1500+ lines
- **Use Case**: Production applications with typical business logic

```yaml
domain: "user"
entity:
  fields:
    - name: "Email"
      type: "string"
      unique: true
      validations: ["required", "email"]

repository:
  custom_methods:
    - name: "GetByEmail"
      parameters: [...]

endpoints:
  - method: "POST"
    path: "/auth/login"
    handler: "LoginUser"
```

**Additional Features**:
- Custom repository methods
- Business logic methods with placeholders
- Custom API endpoints
- Request/response types
- Authentication patterns

### Level 3: Full Configuration (Maximum Control)
- **Goal**: Handle complex domains with specific requirements
- **Config Size**: 200+ lines
- **Generated Code**: 2000+ lines with full customization
- **Use Case**: Complex domains, enterprise applications, special requirements

```yaml
# Complete control over every aspect
domain: "user"
entity: { ... }
models: { ... }
api: { ... }
repository: { ... }
use_case: { ... }
handlers: { ... }
generation: { ... }
features: { ... }
```

## Smart Defaults Strategy

### 1. Entity Layer Defaults
```yaml
# Automatic Standard Fields
- ID: uuid.UUID (primary key)
- CreatedAt: time.Time (auto-managed)
- UpdatedAt: time.Time (auto-managed)

# Automatic Methods
- FromModel() - converts database model to entity
- ToModel() - converts entity to database model
- ToResponse() - converts entity to API response
```

### 2. Model Layer Defaults
```yaml
# GORM Configuration
- UUID primary keys
- Automatic timestamps
- Proper indexes on unique fields
- JSON tags for API serialization
- Table naming: snake_case plural

# Standard Hooks
- BeforeCreate: Set UUID if empty
- BeforeUpdate: Update timestamp
```

### 3. Repository Layer Defaults
```yaml
# Standard CRUD Methods
- Create(ctx, entity) error
- GetByID(ctx, id) (*entity, error)
- List(ctx, filters, limit, offset) ([]*entity, error)
- Update(ctx, entity) error
- Delete(ctx, id) error

# Built-in Features
- Context support
- Error handling with proper types
- Logging with structured output
- Pagination support
- Basic filtering
```

### 4. Use Case Layer Defaults
```yaml
# Business Logic Methods (delegate to repository)
- Create, GetByID, List, Update, Delete

# Extension Points
- Validation hooks
- Authorization checks
- Audit logging
- Event publishing
```

### 5. Handler Layer Defaults
```yaml
# Standard REST Endpoints
- POST /api/v1/{domain}s - Create
- GET /api/v1/{domain}s/{id} - Get by ID
- GET /api/v1/{domain}s - List with filtering
- PUT /api/v1/{domain}s/{id} - Update
- DELETE /api/v1/{domain}s/{id} - Delete

# Built-in Features
- Request validation
- Error handling with proper HTTP status codes
- JSON encoding/decoding
- Query parameter parsing
- Path parameter extraction
```

## Configuration Inheritance

### Base Configuration (Always Applied)
```yaml
# These are built into every domain
generation:
  preserve_custom_code: true
  uuid_primary_key: true
  soft_delete: false
  generate_tests: true

database:
  orm: "gorm"
  migration_support: true
  
api:
  content_type: "application/json"
  error_handling: "structured"

logging:
  structured: true
  request_logging: true
  error_logging: true
```

### Domain-Specific Overrides
```yaml
# Users can override any default
generation:
  soft_delete: true  # Override for this domain

api:
  base_path: "/v2/users"  # Custom API version
```

## Extension Points

### 1. Custom Code Preservation
```go
// Markers in generated code
func (r *UserRepository) Create(ctx context.Context, user *User) error {
    // @gohex:begin:custom:validation
    // Add your custom validation here
    // @gohex:end:custom:validation
    
    return r.db.Create(user).Error
}
```

### 2. Plugin Architecture
```yaml
# Future: Plugin system for common patterns
plugins:
  - name: "audit_trail"
    enabled: true
  - name: "soft_delete"
    enabled: true
  - name: "multitenancy"
    enabled: false
```

### 3. Template Overrides
```yaml
# Advanced: Custom templates for specific files
templates:
  repository: "./custom/repository.go.tmpl"
  # Use custom template instead of built-in
```

## Configuration Validation

### Schema Validation
- YAML schema validation
- Type checking
- Required field validation
- Cross-reference validation (e.g., endpoint references valid use case method)

### Business Rule Validation
- Naming convention compliance
- Dependency order validation
- Database constraint validation
- API design best practices

## Migration Strategy

### Configuration Versioning
```yaml
version: "1.0"  # Configuration schema version
# Automatic migration between versions
```

### Backward Compatibility
- Old configuration files automatically upgraded
- Deprecation warnings for old patterns
- Migration guides for breaking changes

## Best Practices

### 1. Start Small, Grow Gradually
1. Begin with minimal configuration
2. Add custom methods as needed
3. Evolve to full configuration only when necessary

### 2. Leverage Defaults
- Trust the opinionated defaults
- Override only when you have specific requirements
- Document why you're overriding defaults

### 3. Configuration as Documentation
- Use descriptive names and descriptions
- Configuration file serves as domain documentation
- Clear intent over brevity

### 4. Version Control Configuration
- Store configuration alongside code
- Track changes to understand domain evolution
- Review configuration changes like code

## Implementation Phases

### Phase 1: Minimal Configuration Engine
- Support Level 1 (minimal) configuration
- Generate complete CRUD with defaults
- Basic custom method support

### Phase 2: Standard Configuration Features
- Add Level 2 (standard) configuration
- Custom endpoints and business logic
- Request/response customization

### Phase 3: Full Configuration Control
- Complete Level 3 (full) configuration
- Advanced features and plugins
- Template override system

### Phase 4: Advanced Features
- Plugin ecosystem
- Configuration UI/wizard
- Integration with existing projects

## Success Metrics

### Developer Experience
- Time to first working API: < 5 minutes
- Lines of config vs lines of generated code: 1:50+ ratio
- Developer satisfaction with generated code quality

### Code Quality
- Generated code passes linting and security scans
- Performance benchmarks meet standards
- Test coverage > 80% for generated code

### Flexibility
- % of real-world use cases handled by defaults: > 90%
- % of custom requirements handleable through configuration: > 95%
- Migration time for existing codebases: < 1 day per domain

This strategy ensures that our GoHex engine provides maximum value with minimal configuration while maintaining the flexibility to handle complex real-world requirements.