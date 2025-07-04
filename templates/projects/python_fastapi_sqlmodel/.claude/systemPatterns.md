# System Architecture Patterns

## Co-location Architecture Pattern

### Template and Configuration Co-location Strategy

**Core Innovation**: Templates (.j2), configurations (.yaml), and generated files (.py) are co-located in the same
directory structure for optimal developer experience.

#### Benefits of Co-location

- **Immediate Context**: Developers see templates, configs, and outputs together
- **Easier Maintenance**: Changes to domain logic update templates and configs in same location
- **Reduced Cognitive Load**: No navigation between separate template and config directories
- **Intuitive Organization**: Complete layer context visible at once

#### File Organization Pattern

```
app/{{domain}}/
├── layer_name/
│   ├── *.py.j2              # Jinja2 templates (co-located)
│   ├── *.yaml               # Configuration files (co-located)
│   └── *.py                 # Generated Python files (output)
```

### Hierarchical Configuration Merging

**Strategy**: YAML configurations merge hierarchically with override capability.

#### Configuration Hierarchy

```
Domain Level (app/domain/{{domain}}/domain.yaml)
    ↓ (inherits + overrides)
Use Case Level (app/usecase/{{domain}}/usecase.yaml)
    ↓ (inherits + overrides)  
Repository Level (app/repository/{{domain}}/repository.yaml)
    ↓ (inherits + overrides)
Interface Level (app/interface/http/{{domain}}/api.yaml)
```

#### Development Workflow

1. **Domain Modeling**: Define entities and business rules in `domain/` layer
2. **Data Access**: Configure repository patterns in `repository/` layer
3. **Business Logic**: Define use cases and workflows in `usecase/` layer
4. **API Interface**: Configure endpoints and validation in `interface/` layer
5. **Generation**: Tool merges all configurations and generates from co-located templates

## Hexagonal Architecture Implementation (Go-Style Structure)

### Core Principles

- **Domain-Centric Design**: Business logic isolated from external concerns
- **Dependency Inversion**: Dependencies point inward toward domain
- **Port and Adapter Pattern**: Clear interfaces between layers
- **Testability**: Each layer can be tested in isolation

### Layer Definitions

#### Domain Layer (`app/domain/{{domain}}/`) - Go-Style with Co-location

**Purpose**: Core business entities and domain logic
**Responsibilities**:

- Domain entities with business rules
- Value objects and domain services
- Domain events and aggregates
- Business invariants and constraints

**Co-located Files**:

```
app/domain/{{domain}}/
├── entities.py.j2           # Template: Pure business entities
├── exceptions.py.j2         # Template: Domain-specific exceptions
├── domain.yaml              # Config: Domain-level settings
├── entities.yaml            # Config: Entity-specific configuration
├── entities.py              # Generated: Business entities (output)
└── exceptions.py            # Generated: Domain exceptions (output)
```

**Patterns**:

```python
# Entity with business logic
class {{DOMAIN}}Entity:
    def __init__(self, ...):
        self._validate_business_rules()
    
    def business_operation(self):
        # Domain logic here
        pass
```

#### Use Case Layer (`app/usecase/{{domain}}/`) - Go-Style with Co-location

**Purpose**: Use cases and application services
**Responsibilities**:

- Orchestrate domain operations
- Transaction management
- Input/output coordination
- Application-specific business logic

**Co-located Files**:

```
app/usecase/{{domain}}/
├── protocols.py.j2          # Template: Use case interfaces
├── usecase.py.j2            # Template: Use case implementations
├── schemas.py.j2            # Template: Use case-level schemas
├── usecase.yaml             # Config: Use case configuration
├── business-rules.yaml      # Config: Business logic rules
├── protocols.py             # Generated: Use case interfaces (output)
├── usecase.py               # Generated: Use case implementations (output)
└── schemas.py               # Generated: Use case schemas (output)
```

**Patterns**:

```python
# Use case with dependency injection
class {{DOMAIN}}UseCase:
    def __init__(self, repository: {{DOMAIN}}Repository):
        self._repository = repository
    
    async def execute(self, request: {{DOMAIN}}Request) -> {{DOMAIN}}Response:
        # Use case logic here
        pass
```

#### Repository Layer (`app/repository/{{domain}}/`) - Go-Style with Co-location

**Purpose**: Data access and persistence
**Responsibilities**:

- Database persistence
- Query operations
- Transaction management
- Data mapping

**Co-located Files**:

```
app/repository/{{domain}}/
├── protocols.py.j2          # Template: Repository interfaces
├── repository.py.j2         # Template: Repository implementations
├── models.py.j2             # Template: SQLModel database entities
├── repository.yaml          # Config: Repository configuration
├── database.yaml            # Config: Database-specific settings
├── protocols.py             # Generated: Repository interfaces (output)
├── repository.py            # Generated: Repository implementations (output)
└── models.py                # Generated: SQLModel entities (output)
```

**Patterns**:

```python
# Repository implementation
class SQLModel{{DOMAIN}}Repository({{DOMAIN}}Repository):
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, entity: {{DOMAIN}}Entity) -> None:
        # Persistence logic here
        pass
```

#### Interface Layer (`app/interface/http/{{domain}}/`) - Go-Style with Co-location

**Purpose**: HTTP API and external interfaces
**Responsibilities**:

- FastAPI route handlers
- Request/response transformation
- Authentication and authorization
- Input validation

**Co-located Files**:

```
app/interface/http/{{domain}}/
├── schemas.py.j2            # Template: API request/response schemas
├── handlers.py.j2           # Template: FastAPI route handlers
├── dependencies.py.j2       # Template: Endpoint dependencies
├── api.yaml                 # Config: API endpoint configuration
├── validation.yaml          # Config: Request/response validation
├── schemas.py               # Generated: API schemas (output)
├── handlers.py              # Generated: Route handlers (output)
└── dependencies.py          # Generated: Dependencies (output)
```

**Patterns**:

```python
# FastAPI handler with dependency injection
@router.post("/{{domain}}/")
async def create_{{domain}}(
    request: Create{{DOMAIN}}Request,
    use_case: {{DOMAIN}}UseCase = Depends(get_{{domain}}_use_case)
) -> {{DOMAIN}}Response:
    return await use_case.execute(request)
```

## Code Generation Patterns

### Template Placeholder System

**Primary Placeholder**: `{{DOMAIN}}` - replaced with domain name
**Variations**:

- `{{DOMAIN}}` → `User` (PascalCase)
- `{{domain}}` → `user` (lowercase)
- `{{DOMAIN_PLURAL}}` → `Users` (PascalCase plural)
- `{{domain_plural}}` → `users` (lowercase plural)

### File Generation Strategy

**Template Location**: `templates/{{DOMAIN}}/`
**Output Location**: `src/{layer}/{{domain}}/`

**File Naming Patterns**:

```
templates/entity.py.jinja2 → src/domain/{{domain}}/entity.py
templates/repository.py.jinja2 → src/infrastructure/{{domain}}/repository.py
templates/use_case.py.jinja2 → src/application/{{domain}}/use_case.py
templates/handler.py.jinja2 → src/interface/{{domain}}/handler.py
```

### Code Preservation Strategy

**Preservation Markers**:

```python
# @pyhex:begin(custom_imports)
# Custom imports here
# @pyhex:end(custom_imports)

class {{DOMAIN}}Entity:
    # @pyhex:begin(custom_methods)
    # Custom business methods here
    # @pyhex:end(custom_methods)
```

**Preservation Process**:

1. Extract custom code blocks before regeneration
2. Generate new template content
3. Restore custom code blocks to designated regions
4. Validate and format final code

## SQLModel Integration Patterns

### Entity Definition Pattern

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class {{DOMAIN}}Base(SQLModel):
    """Base model for {{DOMAIN}} with common fields"""
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class {{DOMAIN}}({{DOMAIN}}Base, table=True):
    """{{DOMAIN}} entity for database persistence"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    related_entities: List["RelatedEntity"] = Relationship(back_populates="{{domain}}")

class {{DOMAIN}}Create({{DOMAIN}}Base):
    """Request model for creating {{DOMAIN}}"""
    pass

class {{DOMAIN}}Update(SQLModel):
    """Request model for updating {{DOMAIN}}"""
    name: Optional[str] = None
    description: Optional[str] = None

class {{DOMAIN}}Response({{DOMAIN}}Base):
    """Response model for {{DOMAIN}}"""
    id: int
    created_at: datetime
    updated_at: datetime
```

### Repository Pattern Implementation

```python
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

class {{DOMAIN}}Repository:
    """Repository interface for {{DOMAIN}}"""
    
    async def create(self, entity: {{DOMAIN}}Create) -> {{DOMAIN}}:
        raise NotImplementedError
    
    async def get_by_id(self, entity_id: int) -> Optional[{{DOMAIN}}]:
        raise NotImplementedError
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[{{DOMAIN}}]:
        raise NotImplementedError
    
    async def update(self, entity_id: int, updates: {{DOMAIN}}Update) -> Optional[{{DOMAIN}}]:
        raise NotImplementedError
    
    async def delete(self, entity_id: int) -> bool:
        raise NotImplementedError

class SQLModel{{DOMAIN}}Repository({{DOMAIN}}Repository):
    """SQLModel implementation of {{DOMAIN}}Repository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, entity: {{DOMAIN}}Create) -> {{DOMAIN}}:
        db_entity = {{DOMAIN}}(**entity.model_dump())
        self._session.add(db_entity)
        await self._session.commit()
        await self._session.refresh(db_entity)
        return db_entity
    
    async def get_by_id(self, entity_id: int) -> Optional[{{DOMAIN}}]:
        statement = select({{DOMAIN}}).where({{DOMAIN}}.id == entity_id)
        result = await self._session.exec(statement)
        return result.first()
    
    # ... other methods
```

## FastAPI Integration Patterns

### Router Structure

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

router = APIRouter(prefix="/{{domain}}", tags=["{{DOMAIN}}"])

@router.post("/", response_model={{DOMAIN}}Response, status_code=status.HTTP_201_CREATED)
async def create_{{domain}}(
    entity: {{DOMAIN}}Create,
    use_case: {{DOMAIN}}UseCase = Depends(get_{{domain}}_use_case)
) -> {{DOMAIN}}Response:
    """Create a new {{domain}}"""
    return await use_case.create(entity)

@router.get("/{entity_id}", response_model={{DOMAIN}}Response)
async def get_{{domain}}(
    entity_id: int,
    use_case: {{DOMAIN}}UseCase = Depends(get_{{domain}}_use_case)
) -> {{DOMAIN}}Response:
    """Get {{domain}} by ID"""
    entity = await use_case.get_by_id(entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{DOMAIN}} not found"
        )
    return entity

@router.get("/", response_model=List[{{DOMAIN}}Response])
async def list_{{domain_plural}}(
    skip: int = 0,
    limit: int = 100,
    use_case: {{DOMAIN}}UseCase = Depends(get_{{domain}}_use_case)
) -> List[{{DOMAIN}}Response]:
    """List {{domain_plural}} with pagination"""
    return await use_case.get_all(skip=skip, limit=limit)
```

### Dependency Injection Pattern

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_{{domain}}_repository(
    session: AsyncSession = Depends(get_session)
) -> {{DOMAIN}}Repository:
    """Get {{DOMAIN}} repository instance"""
    return SQLModel{{DOMAIN}}Repository(session)

async def get_{{domain}}_use_case(
    repository: {{DOMAIN}}Repository = Depends(get_{{domain}}_repository)
) -> {{DOMAIN}}UseCase:
    """Get {{DOMAIN}} use case instance"""
    return {{DOMAIN}}UseCase(repository)
```

## Configuration Management Patterns

### YAML Domain Configuration

```yaml
domain:
  name: "{{DOMAIN}}"
  plural: "{{DOMAIN_PLURAL}}"
  
entities:
  - name: "{{DOMAIN}}"
    fields:
      - name: "name"
        type: "str"
        required: true
        index: true
      - name: "description"
        type: "Optional[str]"
        required: false
      - name: "created_at"
        type: "datetime"
        default: "datetime.utcnow"
    
relationships:
  - entity: "RelatedEntity"
    type: "one_to_many"
    back_populates: "{{domain}}"

endpoints:
  - method: "POST"
    path: "/"
    operation: "create"
  - method: "GET"
    path: "/{id}"
    operation: "get_by_id"
  - method: "GET"
    path: "/"
    operation: "list"
  - method: "PUT"
    path: "/{id}"
    operation: "update"
  - method: "DELETE"
    path: "/{id}"
    operation: "delete"
```

## Quality Patterns

### Testing Strategy

```python
# Test structure for each layer
tests/
├── unit/
│   ├── domain/test_{{domain}}_entity.py
│   ├── application/test_{{domain}}_use_case.py
│   └── infrastructure/test_{{domain}}_repository.py
├── integration/
│   └── test_{{domain}}_api.py
└── fixtures/
    └── {{domain}}_fixtures.py
```

### Error Handling Pattern

```python
class {{DOMAIN}}Error(Exception):
    """Base exception for {{DOMAIN}} operations"""
    pass

class {{DOMAIN}}NotFoundError({{DOMAIN}}Error):
    """Raised when {{DOMAIN}} is not found"""
    pass

class {{DOMAIN}}ValidationError({{DOMAIN}}Error):
    """Raised when {{DOMAIN}} validation fails"""
    pass
```

### Logging Pattern

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)

class {{DOMAIN}}UseCase:
    async def create(self, entity: {{DOMAIN}}Create) -> {{DOMAIN}}:
        logger.info(f"Creating {{domain}}: {entity.name}")
        try:
            result = await self._repository.create(entity)
            logger.info(f"Created {{domain}} with ID: {result.id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create {{domain}}: {e}")
            raise
```

## Go Template Analysis Integration (2025-06-25)

### Sophisticated Template System Patterns Discovered

**Hexagonal Architecture Excellence**:

- **Pure Domain Entities**: Go entities are completely infrastructure-agnostic with conversion methods
- **Interface-First Design**: Every layer defines interfaces before implementations
- **Dependency Injection**: Dynamic component registration with reflection-based container
- **Configuration-Driven Generation**: YAML configuration controls all aspects of code generation

**Advanced Code Generation Intelligence**:

```go
// Template processing pipeline discovered
1. YAML Configuration → DomainConfig struct (with validation)
2. Config Processing → TemplateData (with case conversions and defaults)
3. Template Execution → Go text/template with custom functions
4. File Generation → Multi-layer code generation with preservation
5. DI Integration → Automatic component registration
```

**Template Function Intelligence**:

```go
// Custom template functions for Python mapping
toSnakeCase    → to_snake_case filter    # UserAccount → user_account
toPascalCase   → to_pascal_case filter   # user_account → UserAccount
pluralize      → pluralize filter        # user → users
default        → default filter          # value|default("fallback")
printf         → format filter           # "Hello {}"|format(name)
```

**Code Preservation Patterns**:

```go
// @gohex markers → @pyhex markers mapping
// @gohex:begin:custom:fields        → # @pyhex:begin:custom:fields
// Custom fields here                → # Custom fields here  
// @gohex:end:custom:fields          → # @pyhex:end:custom:fields
```

### Python FastAPI SQLModel Architecture Intelligence

**Technology Stack Superiority**:

- **Type Safety Enhancement**: Pydantic + SQLModel provides superior type validation vs Go
- **Async Performance**: Native async/await throughout entire stack
- **Auto Documentation**: FastAPI OpenAPI generation surpasses Go manual documentation
- **Modern Validation**: Built-in request/response validation vs manual Go validation

**Hexagonal Architecture Python Translation**:

```python
# Go layers → Python equivalents with enhancements
internal/core/entity/     → app/domain/           # Pydantic business entities
internal/core/models/     → app/infrastructure/database/models/  # SQLModel with relationships
internal/repository/      → app/infrastructure/repositories/     # Async protocols + implementations
internal/usecase/         → app/application/services/           # Business logic services
internal/interface/http/  → app/presentation/api/               # FastAPI routers
internal/di/              → app/infrastructure/di/              # dependency-injector
```

**Template System Enhancement Intelligence**:

```python
# Python template system advantages over Go
1. Jinja2 > Go text/template (more powerful, better ecosystem)
2. Pydantic config validation > manual Go validation  
3. Black auto-formatting > manual Go formatting
4. Click CLI > manual Go flag parsing
5. pytest + async > Go testing + manual async
```

**Code Generation Pipeline Intelligence**:

```python
# Enhanced Python pipeline
1. YAML → Pydantic models (with automatic validation)
2. Config processing → TemplateData (with intelligent defaults)
3. Jinja2 rendering → Python files (with custom filters)
4. Code preservation → @pyhex markers (with regex extraction)
5. Black formatting → Professional code output
6. DI integration → dependency-injector containers
```

### Implementation-Ready Architecture Specifications

**Complete Directory Structure**:

- Designed 14-layer Python template system mirroring Go sophistication
- 50+ template files covering all aspects of hexagonal architecture
- Complete CLI tool with scaffold, validate, and generate commands
- Comprehensive testing architecture with fixtures and async support

**Advanced Features Preserved**:

- Configuration-driven template selection (simple vs advanced templates)
- Smart default value injection at multiple configuration levels
- Relationship handling for complex domain models
- Business method generation with validation integration
- Middleware and dependency injection patterns
- Performance optimization patterns (caching, pagination, filtering)

**Template System Intelligence Evolution**:

- Complete architecture designed and implementation-ready
- All Go patterns successfully mapped to Python equivalents
- Enhanced capabilities through modern Python ecosystem
- Professional-grade code generation with preservation system

**Next Implementation Phase Intelligence**:

- Template file creation (50+ Jinja2 templates required)
- CLI tool implementation (Click-based with 5 core commands)
- Code preservation system (regex-based @pyhex marker processing)
- Testing framework integration (pytest + async + fixtures)
- Documentation generation (comprehensive guides and examples)