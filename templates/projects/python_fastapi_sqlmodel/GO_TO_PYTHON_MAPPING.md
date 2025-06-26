# Go Backend Template → Python FastAPI SQLModel Complete Mapping

## Executive Summary
Complete 1:1 architectural mapping from sophisticated Go hexagonal backend template to Python FastAPI SQLModel equivalent, preserving all advanced patterns while leveraging Python's modern async ecosystem.

## 1. ARCHITECTURE LAYER MAPPING

### Go → Python Layer Translation
```
Go Backend Template Structure:
internal/
├── core/
│   ├── entity/{{DOMAIN}}/          → app/domain/{{domain}}/
│   └── models/{{DOMAIN}}/          → app/repository/{{domain}}/models.py
├── repository/{{DOMAIN}}/          → app/repository/{{domain}}/
├── usecase/{{DOMAIN}}/             → app/usecase/{{domain}}/
├── interface/http/handlers/{{DOMAIN}}/ → app/interface/http/{{domain}}/
└── di/{{DOMAIN}}/                  → app/interface/di/{{domain}}/

Python FastAPI SQLModel Structure (Go-Style with Co-location):
app/
├── domain/{{domain}}/              # Pure business entities (Pydantic)
│   ├── entities.py.j2              # Template: Pure business entities
│   ├── exceptions.py.j2            # Template: Domain-specific exceptions
│   ├── domain.yaml                 # Config: Domain-level settings
│   └── entities.yaml               # Config: Entity-specific configuration
├── usecase/{{domain}}/             # Use case orchestration (Go-style naming)
│   ├── protocols.py.j2             # Template: Use case interfaces
│   ├── usecase.py.j2               # Template: Use case implementations
│   ├── schemas.py.j2               # Template: Use case-level schemas
│   ├── usecase.yaml                # Config: Use case configuration
│   └── business-rules.yaml         # Config: Business logic rules
├── repository/{{domain}}/          # Data access layer (Go-style naming)
│   ├── protocols.py.j2             # Template: Repository interfaces
│   ├── repository.py.j2            # Template: Repository implementations
│   ├── models.py.j2                # Template: SQLModel database entities
│   ├── repository.yaml             # Config: Repository configuration
│   └── database.yaml               # Config: Database-specific settings
├── interface/                      # Interface layer (Go-style naming)
│   ├── http/{{domain}}/            # FastAPI HTTP handlers
│   │   ├── schemas.py.j2           # Template: API request/response schemas
│   │   ├── handlers.py.j2          # Template: FastAPI route handlers
│   │   ├── dependencies.py.j2      # Template: Endpoint dependencies
│   │   ├── api.yaml                # Config: API endpoint configuration
│   │   └── validation.yaml         # Config: Request/response validation
│   └── di/{{domain}}/              # Dependency injection
└── infrastructure/                 # Infrastructure concerns
    ├── database/                   # Database configuration
    └── config/                     # Application configuration
```

## 2. TECHNOLOGY STACK MAPPING

### Core Dependencies Translation
| Go Component | Python Equivalent | Implementation Notes |
|--------------|-------------------|---------------------|
| **HTTP Framework** | | |
| `net/http` + Gin | `fastapi` | Modern async with auto-docs |
| **ORM/Database** | | |
| `gorm.io/gorm` | `sqlmodel` + `sqlalchemy` | Type-safe async ORM |
| `github.com/lib/pq` | `asyncpg` | High-performance async PostgreSQL |
| **Dependency Injection** | | |
| `github.com/samber/do` | `dependency-injector` | Professional DI container |
| **Configuration** | | |
| `gopkg.in/yaml.v3` | `pydantic-settings` + `PyYAML` | Type-safe config validation with hierarchical merging |
| **Validation** | | |
| Manual validation | `pydantic` built-in | Automatic request/response validation |
| **UUID Generation** | | |
| `github.com/google/uuid` | `uuid` (stdlib) + `pydantic.UUID4` | Built-in UUID support |
| **Logging** | | |
| Custom logger | `structlog` | Structured logging with context |
| **Testing** | | |
| `testing` + `testify` | `pytest` + `pytest-asyncio` | Async test support |

## 3. TEMPLATE SYSTEM MAPPING

### Template Engine Translation
| Go Template | Python Equivalent | Enhancement |
|-------------|-------------------|-------------|
| `text/template` | `jinja2` | More powerful templating |
| Custom functions | Jinja2 filters | Better ecosystem integration |
| `{{.Domain}}` placeholders | `{{domain}}` placeholders | Same pattern, lowercase convention |

### Template Function Mapping
```python
# Go Template Functions → Jinja2 Filters
"toSnakeCase"   → "to_snake_case"     # UserAccount → user_account
"toPascalCase"  → "to_pascal_case"    # user_account → UserAccount  
"pluralize"     → "pluralize"         # user → users
"default"       → "default"           # value|default("fallback")
"printf"        → "format"            # "Hello {}""|format(name)
"eq"/"ne"       → "==" / "!="         # {% if user == admin %}
"contains"      → "in"                # {% if "admin" in roles %}
```

### Placeholder System Enhancement
```yaml
# Go placeholders
{{.Domain}}        # "User" 
{{.DomainSnake}}   # "user"
{{.Entity}}        # "User"
{{.EntitySnake}}   # "user" 
{{.Entities}}      # "Users"
{{.EntitiesSnake}} # "users"

# Python equivalent (enhanced)
{{domain}}         # "User"
{{domain_snake}}   # "user" 
{{domain_plural}}  # "Users"
{{domain_plural_snake}} # "users"
{{table_name}}     # "users" (explicit database name)
{{module_name}}    # "app" (Python package name)
```

## 4. CO-LOCATION ARCHITECTURE

### Template and Configuration Co-location Strategy
Unlike the Go template system where templates are centralized, the Python implementation uses co-location for improved developer experience:

#### Co-location Benefits
- **Immediate Context**: Templates, configs, and generated files in same directory
- **Easier Maintenance**: Changes to domain logic update templates and configs together  
- **Intuitive Organization**: Developers see complete layer context at once
- **Reduced Cognitive Load**: No need to navigate between template and config directories

#### File Organization Pattern
```
app/{{domain}}/
├── layer_name/
│   ├── *.py.j2              # Jinja2 templates (co-located)
│   ├── *.yaml               # Configuration files (co-located)
│   └── *.py                 # Generated Python files (output)
```

### Configuration Merging Architecture

#### Hierarchical Configuration Strategy
The generation tool merges YAML configurations hierarchically:

```
Domain Level (app/domain/{{domain}}/domain.yaml)
    ↓ (inherits + overrides)
Use Case Level (app/usecase/{{domain}}/usecase.yaml)
    ↓ (inherits + overrides)  
Repository Level (app/repository/{{domain}}/repository.yaml)
    ↓ (inherits + overrides)
Interface Level (app/interface/http/{{domain}}/api.yaml)
```

#### Configuration Processing Pipeline
```python
def merge_configurations(domain_path: str) -> Dict[str, Any]:
    """Merge hierarchical YAML configurations for template generation."""
    
    # 1. Load base domain configuration
    base_config = load_yaml(f"{domain_path}/domain/domain.yaml")
    
    # 2. Layer-specific configurations
    layers = ["usecase", "repository", "interface/http"]
    
    # 3. Merge configurations with override capability
    for layer in layers:
        layer_config = load_yaml(f"{domain_path}/{layer}/*.yaml")
        base_config = deep_merge(base_config, layer_config)
    
    # 4. Validate merged configuration
    return validate_configuration(base_config)
```

#### Configuration File Examples

**Domain Configuration** (`app/domain/user/domain.yaml`):
```yaml
domain:
  name: "user"
  description: "User management domain"
  package: "app.domain.user"
  
entity:
  base_class: "BaseEntity"
  mixins: ["TimestampMixin", "SoftDeleteMixin"]
  
validation:
  email_unique: true
  password_complexity: true
```

**Repository Configuration** (`app/repository/user/repository.yaml`):
```yaml
repository:
  connection: "primary_db"
  table_prefix: "users"
  soft_delete: true
  
database:
  indexes:
    - fields: ["email"]
      unique: true
    - fields: ["created_at"]
      type: "btree"
      
performance:
  connection_pool_size: 20
  query_timeout: 30
```

**API Configuration** (`app/interface/http/user/api.yaml`):
```yaml
api:
  base_path: "/api/v1/users"
  version: "1.0"
  
authentication:
  required: true
  method: "jwt"
  
rate_limiting:
  requests_per_minute: 100
  burst_size: 20
  
endpoints:
  create_user:
    method: "POST"
    path: "/"
    request_model: "CreateUserRequest"
    response_model: "UserResponse"
    status_code: 201
```

#### Development Workflow with Co-location
1. **Domain Modeling**: Define entities and business rules in `domain/` layer
2. **Data Access**: Configure repository patterns in `repository/` layer  
3. **Business Logic**: Define use cases and workflows in `usecase/` layer
4. **API Interface**: Configure endpoints and validation in `interface/` layer
5. **Generation**: Tool merges all configurations and generates from co-located templates

## 5. CONFIGURATION SCHEMA MAPPING

### YAML Configuration Translation
```yaml
# Go Configuration → Python Configuration
version: "1.0"                    # Same
domain: "user"                    # Same
description: "User management"    # Same
module: "go_backend_gorm"        → package_name: "app"

# Enhanced Python configuration
entity:
  name: "User"
  base_class: "BaseEntity"        # Python-specific inheritance
  pydantic_config:                # Pydantic-specific settings
    str_strip_whitespace: true
    validate_assignment: true
  fields:
    - name: "email"
      type: "EmailStr"             # Pydantic email validation
      description: "User email"
      unique: true
      index: true

models:
  - name: "User"
    table_name: "users"
    inherit_from: "TimestampMixin"  # SQLModel mixins
    sqlmodel_config:                # SQLModel-specific settings
      table: true
      schema_extra:
        example:
          email: "user@example.com"
    fields:
      - name: "email"
        type: "str"
        sa_column_kwargs:           # SQLAlchemy column arguments
          unique: true
          index: true
        field_info:                 # Pydantic field info
          description: "User email address"
          example: "user@example.com"

repository:
  interface_name: "UserRepositoryProtocol"  # Python Protocol
  implementation_name: "UserRepository"
  base_class: "BaseRepository"              # Generic base
  async_methods: true                       # Python async/await
  custom_methods:
    - name: "get_by_email"
      parameters:
        - name: "email"
          type: "str"
      returns: "Optional[User]"
      query_method: "select"                # SQLAlchemy query method

use_case:
  interface_name: "UserServiceProtocol"     # Python Protocol  
  implementation_name: "UserService"
  base_class: "BaseService"
  async_methods: true
  business_methods:
    - name: "authenticate_user"
      parameters:
        - name: "email"
          type: "EmailStr"
        - name: "password"
          type: "str"
      returns: "AuthResult"
      transactional: true
      validation_schema: "AuthRequest"

handlers:
  router_name: "user_router"
  base_path: "/api/v1/users"
  tags: ["users"]
  dependencies:                             # FastAPI dependencies
    - "get_current_user"
    - "rate_limiter"
  endpoints:
    - method: "POST"
      path: "/"
      function_name: "create_user"
      request_model: "CreateUserRequest"
      response_model: "UserResponse"
      status_code: 201
      dependencies: ["validate_admin"]      # Endpoint-specific deps
```

## 5. CODE GENERATION MAPPING

### Template Processing Pipeline
```python
# Go Process → Python Process
1. YAML Load (yaml.v3)          → PyYAML + Pydantic validation
2. Config Processing            → Pydantic model transformation  
3. Template Data Creation       → Jinja2 context preparation
4. Template Execution           → Jinja2 rendering with filters
5. File Generation              → Python file output with formatting
6. Code Preservation            → @pyhex marker processing
```

### Python Code Generation Architecture
```python
# cmd/generate/main.py (equivalent to cmd/standardize/main.go)
from pathlib import Path
import click
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError

from .config_processor import ConfigProcessor
from .template_generator import TemplateGenerator

@click.command()
@click.option('--config', required=True, type=click.Path(exists=True))
@click.option('--output', default='./generated', type=click.Path())
def generate(config: str, output: str):
    """Generate FastAPI SQLModel application from YAML configuration."""
    try:
        processor = ConfigProcessor()
        domain_config = processor.load_config(config)
        template_data = processor.create_template_data(domain_config)
        
        generator = TemplateGenerator(output_dir=Path(output))
        generator.generate_all_files(template_data)
        
        click.echo("✅ Generation completed successfully!")
    except ValidationError as e:
        click.echo(f"❌ Configuration validation error: {e}")
    except Exception as e:
        click.echo(f"❌ Generation failed: {e}")

# config_processor.py (equivalent to config_processor.go)
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import yaml

class DomainConfig(BaseModel):
    version: str = "1.0"
    domain: str
    description: Optional[str]
    package_name: str = "app"
    entity: EntityConfig
    models: List[ModelConfig] = []
    repository: RepositoryConfig = RepositoryConfig()
    use_case: UseCaseConfig = UseCaseConfig()
    handlers: HandlersConfig = HandlersConfig()
    generation: GenerationConfig = GenerationConfig()

    @validator('domain')
    def domain_must_be_snake_case(cls, v):
        if not v.islower() or ' ' in v:
            raise ValueError('Domain must be snake_case')
        return v

class ConfigProcessor:
    def load_config(self, config_path: str) -> DomainConfig:
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        return DomainConfig(**raw_config)
    
    def create_template_data(self, config: DomainConfig) -> TemplateData:
        return TemplateData(
            domain=to_pascal_case(config.domain),
            domain_snake=config.domain,
            domain_plural=pluralize(to_pascal_case(config.domain)),
            domain_plural_snake=pluralize(config.domain),
            package_name=config.package_name,
            entity_config=self._process_entity_config(config.entity),
            # ... other processing
        )
```

## 6. LAYER IMPLEMENTATION MAPPING

### 6.1 Entity Layer (Domain) Translation

#### Go Entity Pattern:
```go
package user

type User struct {
    ID        uuid.UUID `json:"id"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

func FromUserModel(model *modelsPkg.User) *User { /* ... */ }
func (u *User) ToUserModel() *modelsPkg.User { /* ... */ }
```

#### Python Entity Equivalent:
```python
# app/domain/user/entities.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class User(BaseModel):
    """Pure business entity - no infrastructure dependencies."""
    
    id: UUID = Field(description="Unique identifier")
    email: EmailStr = Field(description="User email address")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        # @pyhex:begin:custom:pydantic_config
        str_strip_whitespace = True
        validate_assignment = True
        # @pyhex:end:custom:pydantic_config
    
    @classmethod
    def from_model(cls, model: "UserModel") -> "User":
        """Convert from SQLModel to domain entity."""
        return cls(
            id=model.id,
            email=model.email,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def to_model(self) -> "UserModel":
        """Convert to SQLModel for persistence."""
        from app.infrastructure.database.models.user import UserModel
        return UserModel(
            id=self.id,
            email=self.email,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    # @pyhex:begin:custom:business_methods
    def is_email_verified(self) -> bool:
        """Check if user email is verified."""
        # Custom business logic here
        return True
    # @pyhex:end:custom:business_methods
```

### 6.2 Model Layer (Database) Translation

#### Go Model Pattern:
```go
type User struct {
    ID        uuid.UUID `gorm:"type:uuid;primaryKey" json:"id"`
    Email     string    `gorm:"uniqueIndex;not null" json:"email"`
    CreatedAt time.Time `gorm:"type:timestamp;default:now()" json:"created_at"`
    UpdatedAt time.Time `gorm:"type:timestamp;default:now()" json:"updated_at"`
}
```

#### Python Model Equivalent:
```python
# app/infrastructure/database/models/user/models.py
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import String
from typing import Optional

class UserModel(SQLModel, table=True):
    """Database model for User entity."""
    
    __tablename__ = "users"
    
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier"
    )
    email: str = Field(
        sa_column=String(255),
        unique=True,
        index=True,
        description="User email address"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # @pyhex:begin:custom:fields
    # Add custom database fields here
    # @pyhex:end:custom:fields
    
    def __repr__(self) -> str:
        return f"UserModel(id={self.id}, email={self.email})"
    
    # @pyhex:begin:custom:methods
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    # @pyhex:end:custom:methods
```

### 6.3 Repository Layer Translation

#### Go Repository Pattern:
```go
type IUserRepository interface {
    Create(ctx context.Context, user *entity.User) error
    GetByID(ctx context.Context, id uuid.UUID) (*entity.User, error)
    // ...
}

type UserRepository struct {
    db     *postgres.DB
    logger *utils.Logger
}
```

#### Python Repository Equivalent (Go-Style Structure):
```python
# app/repository/user/protocols.py
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.user.entities import User

class UserRepositoryProtocol(ABC):
    """Repository interface for User domain operations."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        ...
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by ID."""
        ...
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email."""
        ...
    
    @abstractmethod
    async def list_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[User]:
        """List users with pagination and filtering."""
        ...
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user."""
        ...
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID."""
        ...

# app/repository/user/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID

from .protocols import UserRepositoryProtocol
from app.domain.user.entities import User
from .models import UserModel

class UserRepository(UserRepositoryProtocol):
    """SQLModel implementation of UserRepository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        model = user.to_model()
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return User.from_model(model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by ID."""
        statement = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.exec(statement)
        model = result.first()
        return User.from_model(model) if model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email."""
        statement = select(UserModel).where(UserModel.email == email)
        result = await self.session.exec(statement)
        model = result.first()
        return User.from_model(model) if model else None
    
    async def list_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[User]:
        """List users with pagination and filtering."""
        statement = select(UserModel).offset(skip).limit(limit)
        
        if filters:
            for key, value in filters.items():
                if hasattr(UserModel, key):
                    statement = statement.where(getattr(UserModel, key) == value)
        
        result = await self.session.exec(statement)
        models = result.all()
        return [User.from_model(model) for model in models]
    
    async def update(self, user: User) -> User:
        """Update existing user."""
        model = user.to_model()
        model.update_timestamp()
        await self.session.merge(model)
        await self.session.commit()
        await self.session.refresh(model)
        return User.from_model(model)
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID."""
        statement = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.exec(statement)
        await self.session.commit()
        return result.rowcount > 0
    
    # @pyhex:begin:custom:methods
    async def search_by_name(self, name_query: str) -> List[User]:
        """Search users by name pattern."""
        # Custom query implementation
        pass
    # @pyhex:end:custom:methods

# app/repository/user/models.py
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import String
from typing import Optional

class UserModel(SQLModel, table=True):
    """Database model for User entity."""
    
    __tablename__ = "users"
    
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier"
    )
    email: str = Field(
        sa_column=String(255),
        unique=True,
        index=True,
        description="User email address"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # @pyhex:begin:custom:fields
    # Add custom database fields here
    # @pyhex:end:custom:fields
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    # @pyhex:begin:custom:methods
    # Add custom model methods here
    # @pyhex:end:custom:methods
```

### 6.4 Use Case Layer Translation

#### Go UseCase Pattern:
```go
type IUserUseCase interface {
    Create(ctx context.Context, user *entity.User) error
    AuthenticateUser(ctx context.Context, email, password string) (*entity.User, error)
}

type UserUseCase struct {
    userRepo IUserRepository
    logger   *utils.Logger
}
```

#### Python UseCase Equivalent (Go-Style Structure):
```python
# app/usecase/user/protocols.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.user.entities import User

class UserUseCaseProtocol(ABC):
    """UseCase interface for User business operations."""
    
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user with business validation."""
        ...
    
    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        ...
    
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID with business logic."""
        ...

# app/usecase/user/usecase.py
import structlog
from typing import Optional
from uuid import UUID

from .protocols import UserUseCaseProtocol
from app.domain.user.entities import User
from app.repository.user.protocols import UserRepositoryProtocol

logger = structlog.get_logger()

class UserUseCase(UserUseCaseProtocol):
    """User business logic use case."""
    
    def __init__(self, user_repository: UserRepositoryProtocol):
        self.user_repository = user_repository
    
    async def create_user(self, user: User) -> User:
        """Create a new user with business validation."""
        logger.info("Creating user", email=user.email)
        
        # Business validation
        existing_user = await self.user_repository.get_by_email(user.email)
        if existing_user:
            raise ValueError(f"User with email {user.email} already exists")
        
        # @pyhex:begin:custom:create_validation
        # Add custom creation validation here
        # @pyhex:end:custom:create_validation
        
        created_user = await self.user_repository.create(user)
        logger.info("User created successfully", user_id=created_user.id)
        return created_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        logger.info("Authenticating user", email=email)
        
        user = await self.user_repository.get_by_email(email)
        if not user:
            logger.warning("Authentication failed - user not found", email=email)
            return None
        
        # @pyhex:begin:custom:password_verification
        # Add password verification logic here
        password_valid = True  # Placeholder
        # @pyhex:end:custom:password_verification
        
        if not password_valid:
            logger.warning("Authentication failed - invalid password", email=email)
            return None
        
        logger.info("User authenticated successfully", user_id=user.id)
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID with business logic."""
        logger.debug("Retrieving user by ID", user_id=user_id)
        
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning("User not found", user_id=user_id)
            return None
        
        # @pyhex:begin:custom:user_retrieval_logic
        # Add custom user retrieval business logic here
        # @pyhex:end:custom:user_retrieval_logic
        
        return user
    
    # @pyhex:begin:custom:business_methods
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account (soft delete)."""
        # Custom business logic for user deactivation
        pass
    # @pyhex:end:custom:business_methods
```

### 6.5 Interface Layer (HTTP Handlers) Translation

#### Go Handler Pattern:
```go
type Handler struct {
    userUseCase IUserUseCase
    logger      *utils.Logger
}

func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
    mux.HandleFunc("/api/v1/users", h.handleUsers)
}
```

#### Python Interface Layer Equivalent (Go-Style Structure):
```python
# app/interface/http/user/schemas.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    """Request schema for creating a user."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password")

class UserResponse(BaseModel):
    """Response schema for user data."""
    id: UUID = Field(description="User unique identifier")
    email: EmailStr = Field(description="User email address")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

class AuthRequest(BaseModel):
    """Request schema for user authentication."""
    email: EmailStr = Field(description="User email")
    password: str = Field(description="User password")

# app/interface/http/user/handlers.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from uuid import UUID
import structlog

from .schemas import CreateUserRequest, UserResponse, AuthRequest
from app.usecase.user.protocols import UserUseCaseProtocol
from app.interface.di.dependencies import get_user_usecase

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    user_usecase: UserUseCaseProtocol = Depends(get_user_usecase)
) -> UserResponse:
    """Create a new user."""
    try:
        from app.domain.user.entities import User
        user = User(
            email=request.email,
            # Password handling would be added here
        )
        created_user = await user_usecase.create_user(user)
        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to create user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_usecase: UserUseCaseProtocol = Depends(get_user_usecase)
) -> UserResponse:
    """Get user by ID."""
    user = await user_usecase.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@router.post("/auth", response_model=UserResponse)
async def authenticate_user(
    request: AuthRequest,
    user_usecase: UserUseCaseProtocol = Depends(get_user_usecase)
) -> UserResponse:
    """Authenticate user."""
    user = await user_usecase.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

# @pyhex:begin:custom:endpoints
@router.post("/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    user_usecase: UserUseCaseProtocol = Depends(get_user_usecase)
):
    """Deactivate user account."""
    # Custom endpoint implementation
    pass
# @pyhex:end:custom:endpoints
```

### 6.6 Dependency Injection Translation

#### Go DI Pattern:
```go
func RegisterUser(injector *do.Injector) {
    repositoryPkg.RegisterUserRepository(injector)
    usecasePkg.RegisterUserUseCase(injector)
    handlersPkg.RegisterUserHandler(injector)
}
```

#### Python DI Equivalent (Go-Style Structure):
```python
# app/interface/di/containers.py
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

from app.repository.user.repository import UserRepository
from app.usecase.user.usecase import UserUseCase

class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container."""
    
    # Configuration
    config = providers.Configuration()
    
    # Database
    async_session = providers.Singleton(
        # AsyncSession configuration
    )
    
    # Repositories
    user_repository = providers.Factory(
        UserRepository,
        session=async_session
    )
    
    # Use Cases
    user_usecase = providers.Factory(
        UserUseCase,
        user_repository=user_repository
    )

# app/interface/di/dependencies.py
from dependency_injector.wiring import inject, Provide
from typing import Annotated
from fastapi import Depends

from .containers import ApplicationContainer
from app.usecase.user.protocols import UserUseCaseProtocol

@inject
async def get_user_usecase(
    user_usecase: UserUseCaseProtocol = Depends(Provide[ApplicationContainer.user_usecase])
) -> UserUseCaseProtocol:
    """Get user use case dependency."""
    return user_usecase
```

## 7. CODE PRESERVATION MAPPING

### Go @gohex → Python @pyhex
```python
# Go preservation markers
// @gohex:begin:custom:fields
// Custom fields here
// @gohex:end:custom:fields

# Python preservation markers  
# @pyhex:begin:custom:fields
# Custom fields here
# @pyhex:end:custom:fields

# Enhanced Python preservation categories
# @pyhex:begin:custom:imports
# @pyhex:begin:custom:fields
# @pyhex:begin:custom:methods
# @pyhex:begin:custom:business_logic
# @pyhex:begin:custom:validation
# @pyhex:begin:custom:endpoints
# @pyhex:begin:custom:dependencies
```

## 8. COMMAND LINE TOOL MAPPING

### Go CLI → Python CLI
```python
# cmd/generate/main.py (Click-based CLI)
import click
from pathlib import Path

@click.group()
def cli():
    """FastAPI SQLModel Code Generator."""
    pass

@cli.command()
@click.option('--config', required=True, type=click.Path(exists=True))
@click.option('--output', default='./generated', type=click.Path())
@click.option('--domain', help='Domain name override')
@click.option('--dry-run', is_flag=True, help='Show what would be generated')
def generate(config: str, output: str, domain: str, dry_run: bool):
    """Generate FastAPI application from YAML configuration."""
    # Implementation

@cli.command()
@click.argument('domain')
@click.argument('entity')
def scaffold(domain: str, entity: str):
    """Quick scaffold domain without full configuration."""
    # Legacy compatibility with Go version

if __name__ == '__main__':
    cli()
```

## 9. TESTING ARCHITECTURE MAPPING

### Go Testing → Python Testing
```python
# Go testing patterns → Python pytest patterns

# Repository testing
class TestUserRepository:
    """Test user repository implementation."""
    
    @pytest.fixture
    async def repository(self, async_session):
        return UserRepository(async_session)
    
    async def test_create_user(self, repository, sample_user):
        # Test implementation with async/await
        created_user = await repository.create(sample_user)
        assert created_user.id is not None

# Service testing with mocks
class TestUserService:
    """Test user service business logic."""
    
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock(spec=UserRepositoryProtocol)
    
    @pytest.fixture
    def service(self, mock_repository):
        return UserService(mock_repository)
    
    async def test_create_user_duplicate_email(self, service, mock_repository):
        # Test business logic validation
        mock_repository.get_by_email.return_value = User(...)
        
        with pytest.raises(ValueError, match="already exists"):
            await service.create_user(User(...))

# API testing with TestClient
class TestUserAPI:
    """Test user API endpoints."""
    
    @pytest.fixture
    def client(self, app_with_test_db):
        return TestClient(app_with_test_db)
    
    def test_create_user_success(self, client):
        response = client.post("/api/v1/users", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"
```

## 10. DEPLOYMENT & PRODUCTION MAPPING

### Go Deployment → Python Deployment
```dockerfile
# Dockerfile (Python equivalent)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY cmd/ ./cmd/

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml (Enhanced Python version)
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app/app  # Development hot reload

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Summary

This comprehensive mapping preserves all sophisticated patterns from the Go hexagonal backend template while leveraging Python's modern async ecosystem. The Python implementation provides:

1. **Type Safety**: Enhanced with Pydantic and SQLModel
2. **Async Performance**: Native async/await throughout 
3. **Auto Documentation**: FastAPI OpenAPI generation
4. **Modern Validation**: Built-in request/response validation
5. **Professional DI**: dependency-injector container
6. **Code Preservation**: @pyhex marker system
7. **Template Power**: Jinja2 with custom filters
8. **Testing Excellence**: pytest with async support

The mapping ensures Python developers get a template system as sophisticated as the Go original while feeling natural in the Python ecosystem.