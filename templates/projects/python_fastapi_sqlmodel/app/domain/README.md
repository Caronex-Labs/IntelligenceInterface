# Domain Layer - Co-location Architecture

## Co-location Directory Structure

This directory implements the **co-location architecture pattern** where templates, configurations, and generated files
are organized together in the same directories for optimal developer experience.

### Directory Pattern: `app/domain/{{domain}}/`

```
app/domain/{{domain}}/
├── entities.py.j2           # Template: Pydantic business entities
├── exceptions.py.j2         # Template: Domain-specific exceptions
├── domain.yaml              # Config: Domain-level configuration
├── entities.yaml            # Config: Entity-specific configuration
├── entities.py              # Generated: Business entities (output)
└── exceptions.py            # Generated: Domain exceptions (output)
```

## Co-location Architecture Benefits

### 1. **Immediate Context Visibility**

- Developers see templates (.j2), configurations (.yaml), and generated files (.py) together
- No navigation between separate template and config directories
- Complete layer context visible at once

### 2. **Simplified Maintenance**

- Changes to domain logic update templates and configs in same location
- Related files are co-located for intuitive organization
- Reduced cognitive load for developers

### 3. **Optimal Developer Experience**

- Templates, configs, and outputs co-located in same directories
- Configuration changes immediately visible with affected templates
- Streamlined development workflow

## Hierarchical Configuration Merging

### Configuration Inheritance Strategy

```
Domain Level (domain.yaml)
    ↓ (inherits + overrides)
Entity Level (entities.yaml)
    ↓ (provides complete context)
Template Rendering (merged configuration)
```

### Configuration Processing Pipeline

1. **Load Base Configuration**: `domain.yaml` provides base entity settings
2. **Load Entity Configuration**: `entities.yaml` provides entity-specific overrides
3. **Deep Merge**: ConfigurationMerger creates complete template context
4. **Template Rendering**: Jinja2 templates use merged configuration

## File Naming Conventions

### Template Files (`.j2` extension)

- `entities.py.j2` - SQLModel entity template
- `exceptions.py.j2` - Domain exception template

### Configuration Files (`.yaml` extension)

- `domain.yaml` - Base domain configuration
- `entities.yaml` - Entity-specific configuration

### Generated Files (`.py` extension)

- `entities.py` - Generated SQLModel entities
- `exceptions.py` - Generated domain exceptions

## Go-Style Hexagonal Architecture

This domain layer follows **Go-style hexagonal architecture** with:

- **Domain Layer**: Pure business entities and domain logic (`app/domain/{{domain}}/`)
- **Use Case Layer**: Business logic orchestration (`app/usecase/{{domain}}/`)
- **Repository Layer**: Data access patterns (`app/repository/{{domain}}/`)
- **Interface Layer**: HTTP handlers and API (`app/interface/http/{{domain}}/`)

## Template System Integration

### Code Preservation

- **@pyhex preservation markers** allow custom business logic extension
- Custom code preserved during template regeneration
- Business logic extensions without breaking template updates

### SQLModel Integration

- Type-safe entities with Pydantic validation
- UUID primary keys and timestamp mixins
- FastAPI compatibility with automatic schema generation
- Async/await patterns for database operations

### Quality Standards

- Python best practices with type hints
- Hexagonal architecture compliance
- BDD-driven development with comprehensive scenarios
- Configuration-driven generation with validation

## Usage Patterns

### Development Workflow

1. **Modify Configuration**: Update `domain.yaml` or `entities.yaml`
2. **Template Processing**: ConfigurationMerger processes hierarchical configurations
3. **Code Generation**: Templates generate updated entities and exceptions
4. **Custom Logic**: Add business logic using @pyhex preservation markers
5. **Validation**: BDD scenarios ensure proper generation and integration

### Template Customization

1. **Domain-level**: Modify `domain.yaml` for base entity patterns
2. **Entity-level**: Customize `entities.yaml` for specific field definitions
3. **Template-level**: Extend `.j2` templates for advanced patterns
4. **Business Logic**: Use @pyhex markers for custom domain methods

This co-location architecture provides the foundation for sophisticated Python FastAPI SQLModel applications with
optimal developer experience and maintenance efficiency.