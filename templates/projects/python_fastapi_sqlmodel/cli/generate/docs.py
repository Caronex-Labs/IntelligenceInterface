"""
Documentation content for the FastAPI SQLModel generator.

This module contains the embedded documentation content to ensure it's available
when the package is installed anywhere.
"""

# This content is automatically generated from LLM_USAGE.md
# To update, copy the content from LLM_USAGE.md
LLM_USAGE_CONTENT = """# LLM Usage Guide: Python FastAPI SQLModel Generator

## Overview

This tool generates complete Python FastAPI applications with SQLModel integration using YAML configuration files. **Critical**: The tool uses strict Pydantic model validation and requires exact schema compliance.

## Quick Start

### NEW: Project Initialization (Complete Setup)

**Install the generator locally first (one-time setup):**
```bash
cd /path/to/template/directory
uv tool install -e .
```

**Then use from anywhere:**
```bash
# Initialize a new FastAPI project with complete structure
uv run fastapi-sqlmodel-generator init --project-name "My API" --output ./my-api

# Add description and author
uv run fastapi-sqlmodel-generator init \
  --project-name "My API" \
  --description "My awesome FastAPI application" \
  --author "Your Name" \
  --output ./my-api
```

**What this creates:**
- Complete project structure (app/, cli/, tests/, configs/, templates/)
- Ready-to-run FastAPI application with main.py, config.py, database.py
- pyproject.toml with modern uv dependency management (no requirements.txt)
- justfile with project commands
- Docker setup and CI/CD files
- All CLI tools for adding domains
- Template files for project-specific customization
- **Automatic dependency installation** with UV sync
- **Automatic test execution** for immediate validation
- Self-contained project ready for development

### Domain Generation (Add to Existing Project)
```bash
# Generate domain in existing project
uv run fastapi-sqlmodel-generator generate --config user.yaml --output ./app

# Generate with cleanup
uv run fastapi-sqlmodel-generator generate --config user.yaml --output ./app --clean
```

### Documentation Access
```bash
# Show complete usage guide (for agents and developers)
uv run fastapi-sqlmodel-generator docs
```

### Basic File Structure Options

**Option 1: Single File**
```
configs/
  user.yaml          # Complete domain + entities in one file
```

**Option 2: Split Files**
```
configs/
  user_domain.yaml    # Domain metadata only
  user_entities.yaml  # Entities definitions only
```

**Option 3: Fallback Names**
```
configs/
  domain.yaml         # Domain metadata
  entities.yaml       # Entities definitions
```

## Configuration Schema Reference

### Critical Schema Rules

1. **Field Types**: ONLY use these exact enum values:
   - `"str"`, `"int"`, `"float"`, `"bool"`, `"datetime"`, `"EmailStr"`
   - `"Optional[str]"`, `"Optional[int]"`, `"Optional[float]"`, `"Optional[bool]"`, `"Optional[datetime]"`
   - `"List[str]"`, `"List[int]"`

2. **Domain Names**: Must start with uppercase letter, be valid Python identifiers

3. **Field Names**: Must be valid Python identifiers, no leading underscores

4. **Required Structure**: Must match Pydantic models exactly

### FieldConfig Structure
```yaml
fields:
  - name: "field_name"              # Required: Valid Python identifier
    type: "str"                     # Required: Must be exact FieldType enum value
    required: true                  # Optional: Default true
    index: false                    # Optional: Default false  
    unique: false                   # Optional: Default false
    default: null                   # Optional: String expression or null
    description: "Field description" # Optional: Human readable text
    sqlmodel_field: "Field(...)"    # Optional: Custom SQLModel Field() expression
```

### EntityConfig Structure
```yaml
entities:
  - name: "EntityName"              # Required: PascalCase, valid identifier
    description: "Entity description" # Optional but recommended
    table_name: "table_name"        # Optional: Defaults to snake_case of name
    fields: []                      # Required: List of FieldConfig objects
    relationships: []               # Optional: List of RelationshipConfig objects
```

### DomainConfig Structure
```yaml
name: "DomainName"                  # Required: PascalCase, valid identifier
plural: "DomainNames"              # Optional: Auto-generated if not provided
description: "Domain description"   # Optional but recommended
package: "domain_name"             # Optional: Auto-generated snake_case if not provided
```

## Working Examples

### Example 1: Simple User Domain (Single File)

```yaml
# user.yaml
domain:
  name: "User"
  description: "User management domain"
  package: "user"
  plural: "Users"

entities:
  - name: "User"
    description: "User entity for authentication"
    table_name: "users"
    fields:
      - name: "id"
        type: "int"
        required: false
        description: "Primary key"
        sqlmodel_field: "Field(primary_key=True)"
      
      - name: "email"
        type: "EmailStr"
        required: true
        unique: true
        index: true
        description: "User email address"
        sqlmodel_field: "Field(unique=True, index=True)"
      
      - name: "name"
        type: "str"
        required: true
        description: "User full name"
        sqlmodel_field: "Field(min_length=1, max_length=200)"
      
      - name: "is_active"
        type: "bool"
        required: true
        default: "true"
        description: "Whether user is active"
        sqlmodel_field: "Field(default=True)"
      
      - name: "created_at"
        type: "datetime"
        required: false
        default: "datetime.utcnow"
        description: "Creation timestamp"
        sqlmodel_field: "Field(default_factory=datetime.utcnow)"
```

### Example 2: Split Configuration Files

**user_domain.yaml**
```yaml
domain:
  name: "User"
  description: "User management domain"
  package: "user"
  plural: "Users"
```

**user_entities.yaml**
```yaml
entities:
  - name: "User"
    description: "User entity"
    table_name: "users"
    fields:
      - name: "id"
        type: "int"
        required: false
        sqlmodel_field: "Field(primary_key=True)"
      
      - name: "email"
        type: "EmailStr"
        required: true
        unique: true
        index: true
        sqlmodel_field: "Field(unique=True, index=True)"
      
      - name: "name"
        type: "str"
        required: true
        sqlmodel_field: "Field(min_length=1, max_length=200)"
```

### Example 3: Entity with Relationships

```yaml
entities:
  - name: "User"
    description: "User entity"
    table_name: "users"
    fields:
      - name: "id"
        type: "int"
        required: false
        sqlmodel_field: "Field(primary_key=True)"
      - name: "email"
        type: "EmailStr"
        required: true
        unique: true
    relationships:
      - entity: "UserProfile"
        type: "one_to_one"
        back_populates: "user"
  
  - name: "UserProfile"
    description: "Extended user profile"
    table_name: "user_profiles"
    fields:
      - name: "id"
        type: "int"
        required: false
        sqlmodel_field: "Field(primary_key=True)"
      - name: "user_id"
        type: "int"
        required: true
        sqlmodel_field: "Field(foreign_key='users.id')"
      - name: "bio"
        type: "Optional[str]"
        required: false
    relationships:
      - entity: "User"
        type: "one_to_one"
        back_populates: "profile"
        foreign_key: "users.id"
```

## Configuration Models Reference

### Complete FieldConfig Model
```python
class FieldConfig(BaseModel):
    name: str                           # Field name (required)
    type: FieldType                     # Field type enum (required) 
    required: bool = True               # Whether field is required
    index: bool = False                 # Whether field should be indexed
    unique: bool = False                # Whether field should be unique
    default: Optional[str] = None       # Default value expression
    description: Optional[str] = None   # Field description
    sqlmodel_field: Optional[str] = None # SQLModel Field() expression
```

### Complete EntityConfig Model
```python
class EntityConfig(BaseModel):
    name: str                                    # Entity name (required)
    description: Optional[str] = None            # Entity description
    table_name: Optional[str] = None             # Database table name
    fields: List[FieldConfig]                    # Entity fields (required)
    relationships: List[RelationshipConfig] = [] # Entity relationships
```

### RelationshipConfig Model
```python
class RelationshipConfig(BaseModel):
    entity: str                              # Related entity name (required)
    type: RelationshipType                   # Relationship type (required)
    back_populates: Optional[str] = None     # Back-reference field name
    foreign_key: Optional[str] = None        # Foreign key field reference
```

### RelationshipType Enum
```python
class RelationshipType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many" 
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
```

### FieldType Enum (COMPLETE LIST)
```python
class FieldType(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DATETIME = "datetime"
    EMAIL = "EmailStr"
    OPTIONAL_STR = "Optional[str]"
    OPTIONAL_INT = "Optional[int]"
    OPTIONAL_FLOAT = "Optional[float]"
    OPTIONAL_BOOL = "Optional[bool]"
    OPTIONAL_DATETIME = "Optional[datetime]"
    LIST_STR = "List[str]"
    LIST_INT = "List[int]"
```

## Automatic Project Setup

### Enhanced Init Process

The `init` command now includes comprehensive automation:

1. **Project Structure Creation**: Complete directory hierarchy with all necessary files
2. **Dependency Installation**: Automatic `uv sync` to install all dependencies
3. **Test Validation**: Automatic test execution to verify generated code
4. **Template Copying**: Local template files for project-specific customization

### What Happens During Init

```bash
uv run fastapi-sqlmodel-generator init --project-name "My API" --output ./my-api
```

**Automated Steps:**
1. ✅ Create complete project structure
2. ✅ Generate core application files (main.py, config.py, database.py)
3. ✅ Copy CLI tools for domain generation
4. ✅ **Copy template files to `templates/` directory**
5. ✅ Create pyproject.toml with modern UV dependency management
6. ✅ **Automatically run `uv sync` to install dependencies**
7. ✅ **Automatically run `pytest` to validate generated code**
8. ✅ Generate project documentation and guides

### Benefits of Automation

- **Immediate Development Ready**: Project is instantly ready for coding
- **Validated Code Quality**: Tests confirm generated code works correctly
- **Template Customization**: Local templates enable project-specific modifications
- **Modern Tooling**: Uses UV for fast, reliable dependency management
- **No Manual Setup**: Zero manual configuration steps required

### Troubleshooting Automatic Setup

**If UV sync fails:**
- Ensure UV is installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Manually run: `cd your-project && uv sync`

**If tests fail:**
- Check test output for specific errors
- Manually run: `cd your-project && uv run pytest -v`
- Review generated code for issues

**If template copying fails:**
- Templates are copied to enhance customization but aren't required
- Project will still function without local templates

## Template Customization

### Overview

Every initialized project includes a `templates/` directory with customizable template files (.j2) and configuration files (.yaml). This enables project-specific modifications without changing the global template system.

### Template Directory Structure

```
templates/
├── CUSTOMIZATION_GUIDE.md     # Complete customization documentation
├── app/
│   ├── main.py.j2             # FastAPI application template
│   ├── config.py.j2           # Configuration template
│   ├── database.py.j2         # Database setup template
│   ├── domain/
│   │   └── {{domain}}/
│   │       ├── entities.py.j2
│   │       └── exceptions.py.j2
│   ├── repository/
│   │   └── {{domain}}/
│   │       ├── repository.py.j2
│   │       └── protocols.py.j2
│   ├── usecase/
│   │   └── {{domain}}/
│   │       ├── usecase.py.j2
│   │       └── schemas.py.j2
│   └── interface/
│       └── {{domain}}/
│           ├── router.py.j2
│           └── dependencies.py.j2
└── configs/
    └── {{domain}}/
        ├── domain.yaml
        ├── entities.yaml
        ├── repository.yaml
        ├── usecase.yaml
        ├── business-rules.yaml
        └── interface.yaml
```

### Customization Workflow

1. **Modify Templates**: Edit .j2 files to change generated code structure
2. **Update Configurations**: Modify .yaml files for project-specific defaults
3. **Regenerate Domains**: Use local templates for domain generation

```bash
# Generate domain using local templates
python cli/generate/cli_tool.py generate \
  --domain your_domain \
  --template-dir templates/ \
  --config configs/your_domain_entities.yaml
```

### Template Variables

Common variables available in templates:
- `{{app_name}}` - Application name
- `{{domain}}` - Domain name (e.g., "user", "product")
- `{{domain_plural}}` - Plural domain name
- `{{package_name}}` - Python package name
- `{{database_type}}` - Database type (sqlite, postgresql, mysql)

### Customization Examples

**Custom Entity Template:**
```jinja2
# templates/app/domain/{{domain}}/entities.py.j2
\"\"\"{{domain}} entities with custom audit fields.\"\"\"

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class {{domain}}(SQLModel, table=True):
    \"\"\"{{domain}} entity with custom audit trail.\"\"\"
    
    # Your custom base fields
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    created_by: str = Field(description="User who created this record")
    modified_by: Optional[str] = Field(default=None, description="User who last modified")
    
    # Domain-specific fields will be generated here
    {% for field in fields %}
    {{field.name}}: {{field.type}} = {{field.sqlmodel_field}}
    {% endfor %}
```

**Custom Configuration:**
```yaml
# templates/configs/{{domain}}/domain.yaml
audit_enabled: true
soft_delete: true
versioning: true
custom_base_fields:
  - created_by
  - modified_by
  - version
```

## Common Patterns

### UUID Primary Keys
```yaml
fields:
  - name: "id"
    type: "str"
    required: false
    description: "UUID primary key"
    sqlmodel_field: "Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))"
```

### Timestamps with Auto-Generation
```yaml
fields:
  - name: "created_at"
    type: "datetime"
    required: false
    default: "datetime.utcnow"
    description: "Creation timestamp"
    sqlmodel_field: "Field(default_factory=datetime.utcnow)"
  
  - name: "updated_at"
    type: "datetime"
    required: false
    default: "datetime.utcnow"
    description: "Last update timestamp"
    sqlmodel_field: "Field(default_factory=datetime.utcnow)"
```

### Soft Delete Pattern
```yaml
fields:
  - name: "deleted_at"
    type: "Optional[datetime]"
    required: false
    description: "Soft deletion timestamp"
    sqlmodel_field: "Field(default=None)"
  
  - name: "is_deleted"
    type: "bool"
    required: true
    default: "false"
    description: "Soft deletion flag"
    sqlmodel_field: "Field(default=False)"
```

### Email Validation
```yaml
fields:
  - name: "email"
    type: "EmailStr"
    required: true
    unique: true
    index: true
    description: "User email address"
    sqlmodel_field: "Field(unique=True, index=True)"
```

### String with Length Constraints
```yaml
fields:
  - name: "name"
    type: "str"
    required: true
    description: "User name"
    sqlmodel_field: "Field(min_length=1, max_length=200)"
```

### Numeric Constraints
```yaml
fields:
  - name: "price"
    type: "float"
    required: true
    description: "Product price"
    sqlmodel_field: "Field(gt=0)"  # Greater than 0
```

### Optional Fields with Defaults
```yaml
fields:
  - name: "bio"
    type: "Optional[str]"
    required: false
    description: "User biography"
    sqlmodel_field: "Field(default=None, max_length=500)"
```

## Complete Application Generation

### Multi-Domain Setup
```python
# Use the generator for complete apps
from cli.generate.generator import DomainGenerator

generator = DomainGenerator(output_dir=Path("./output"), clean_existing=True)

result = generator.generate_complete_application(
    app_name="my_app",
    domains=["user", "product", "order"],
    config_dir=Path("./configs"),
    output_dir=Path("./my_app")
)
```

### Expected Output Structure
```
my_app/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── database.py            # Database setup
│   ├── domain/
│   │   ├── user/
│   │   │   └── entities.py
│   │   └── product/
│   │       └── entities.py
│   ├── repository/
│   │   ├── user_repository.py
│   │   └── product_repository.py
│   ├── usecase/
│   │   ├── user_usecase.py
│   │   └── product_usecase.py
│   └── interface/
│       ├── user_handler.py
│       └── product_handler.py
├── cli/                        # Code generation tools
│   ├── generate/
│   ├── helpers/
│   └── validate/
├── templates/                  # Template customization
│   ├── CUSTOMIZATION_GUIDE.md
│   ├── app/
│   │   ├── domain/
│   │   ├── repository/
│   │   ├── usecase/
│   │   └── interface/
│   └── configs/
├── tests/
│   ├── test_user.py
│   └── test_product.py
├── pyproject.toml              # Modern Python packaging
├── .venv/                      # Auto-created virtual environment
├── uv.lock                     # Dependency lock file
├── docker-compose.yml
└── README.md
```

## Troubleshooting

### Common Validation Errors

#### "Input should be 'str', 'int'..." Error
**Cause**: Used unsupported field type (e.g., "json", "text", "varchar")
**Fix**: Use exact FieldType enum values only

**Wrong:**
```yaml
- name: "data"
  type: "json"  # ❌ Not supported
```

**Correct:**
```yaml
- name: "data"
  type: "str"   # ✅ Use str for JSON data
  sqlmodel_field: "Field(default='{}')"
```

#### "Extra inputs are not permitted" Error
**Cause**: Used configuration fields not defined in Pydantic models
**Fix**: Remove unsupported configuration keys

**Wrong:**
```yaml
domain:
  name: "User"
  custom_setting: true  # ❌ Not in DomainConfig model
```

**Correct:**
```yaml
domain:
  name: "User"          # ✅ Only use defined fields
  description: "User domain"
```

#### "Field required" Error
**Cause**: Missing required fields in configuration
**Fix**: Add all required fields for each model

**Wrong:**
```yaml
entities:
  - description: "User entity"  # ❌ Missing required 'name'
```

**Correct:**
```yaml
entities:
  - name: "User"               # ✅ Required field included
    description: "User entity"
```

#### "Domain name should start with uppercase" Error
**Cause**: Domain name doesn't follow PascalCase convention
**Fix**: Use PascalCase for domain names

**Wrong:**
```yaml
name: "user"  # ❌ Should be PascalCase
```

**Correct:**
```yaml
name: "User"  # ✅ PascalCase
```

### File Structure Issues

#### "Configuration file not found" Error
**Cause**: Incorrect file naming or missing files
**Fix**: Use correct naming conventions

**Expected File Patterns:**
1. `{domain_name}.yaml` (single file)
2. `{domain_name}_domain.yaml` + `{domain_name}_entities.yaml`
3. `domain.yaml` + `entities.yaml` (fallback)

### Relationship Configuration Issues

#### Invalid Relationship References
**Cause**: Referencing entity that doesn't exist
**Fix**: Ensure all referenced entities are defined

**Wrong:**
```yaml
relationships:
  - entity: "NonexistentEntity"  # ❌ Entity not defined
    type: "one_to_one"
```

**Correct:**
```yaml
# First define the entity
entities:
  - name: "UserProfile"
    # ... fields ...
  - name: "User" 
    relationships:
      - entity: "UserProfile"     # ✅ Entity exists
        type: "one_to_one"
```

## CLI Reference

### Command Line Options

**Available Commands:**
- `init` - Initialize a new FastAPI SQLModel project
- `generate` - Generate domain from configuration file  
- `docs` - Show complete LLM usage guide as text

**Generate Command Options:**
```bash
uv run fastapi-sqlmodel-generator generate [OPTIONS]

Required:
  --config, -c PATH     Path to YAML configuration file

Optional:
  --output, -o PATH     Output directory (default: ./generated)
  --clean              Clean existing output directory before generation
  --no-validate        Skip strict configuration validation
  --verbose, -v        Enable verbose output
  --dry-run           Validate configuration and show what would be generated
```

**Init Command Options:**
```bash
uv run fastapi-sqlmodel-generator init [OPTIONS]

Required:
  --project-name, -n    Name of the project to create

Optional:
  --output, -o PATH     Output directory (default: current directory)
  --description, -d     Project description  
  --author, -a         Project author
  --clean              Clean existing output directory before initialization
```

**Docs Command:**
```bash
uv run fastapi-sqlmodel-generator docs

# No options - displays complete usage guide as text
# Useful for agents to query documentation programmatically
```

### Examples
```bash
# Basic generation
uv run fastapi-sqlmodel-generator generate -c user.yaml

# Custom output directory
uv run fastapi-sqlmodel-generator generate -c user.yaml -o ./my_project

# Clean output first
uv run fastapi-sqlmodel-generator generate -c user.yaml -o ./my_project --clean

# Verbose output for debugging
uv run fastapi-sqlmodel-generator generate -c user.yaml -v

# Dry run to validate configuration
uv run fastapi-sqlmodel-generator generate -c user.yaml --dry-run

# Get output directory info
uv run fastapi-sqlmodel-generator generate -c user.yaml --info
```

### Environment Setup
```bash
# Install dependencies
uv sync

# Run with UV (recommended)
uv run fastapi-sqlmodel-generator generate --config user.yaml

# Alternative: Direct CLI tool (after local installation)
fastapi-sqlmodel-generator generate --config user.yaml
```

## Success Checklist

Before running generation, verify:

- [ ] Configuration files use exact FieldType enum values
- [ ] Domain names are PascalCase and valid Python identifiers
- [ ] Field names are valid Python identifiers (no leading underscores)
- [ ] All required fields are provided for each model
- [ ] Relationships reference existing entities only
- [ ] File naming follows expected patterns
- [ ] No "extra inputs" outside of defined Pydantic models
- [ ] SQLModel field expressions are valid (if used)

Following this guide exactly will prevent the common validation errors that cause generation failures.

## Complete Workflow Example

### 1. Initialize New Project
```bash
# Create new FastAPI project with automatic setup
uv run fastapi-sqlmodel-generator init \
  --project-name "Blog API" \
  --description "Blog management API with users and posts" \
  --author "Your Name" \
  --output ./blog-api

cd blog-api
# Dependencies are automatically installed and tests automatically run!
# Project is immediately ready for development
```

### 2. Add User Domain
Create `configs/user_domain.yaml`:
```yaml
name: "User"
description: "User management domain"
package: "user"
plural: "Users"
```

Create `configs/user_entities.yaml`:
```yaml
entities:
  - name: "User"
    description: "User entity"
    table_name: "users"
    fields:
      - name: "id"
        type: "str"
        required: false
        description: "UUID primary key"
        sqlmodel_field: "Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))"
      - name: "email"
        type: "EmailStr"
        required: true
        unique: true
        description: "User email"
      - name: "name"
        type: "str"
        required: true
        description: "User full name"
```

Generate domain:
```bash
uv run fastapi-sqlmodel-generator generate \
  --config configs/user_domain.yaml \
  --output ./app
```

### 3. Add Post Domain
Create `configs/post_domain.yaml` and `configs/post_entities.yaml` (similar structure)

Generate domain:
```bash
uv run fastapi-sqlmodel-generator generate \
  --config configs/post_domain.yaml \
  --output ./app
```

### 4. Run the Application
```bash
# Start development server
just dev

# Run tests
just test

# Check code quality
just lint
```

### 5. Access the API
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

This workflow creates a complete, production-ready FastAPI application with multiple domains, comprehensive testing, and proper project structure.

## Modern Python Packaging

### UV-First Approach

This template system uses modern Python packaging practices:

✅ **pyproject.toml only** - No requirements.txt files generated
✅ **UV dependency management** - Fast, reliable package management
✅ **Automatic lock files** - uv.lock ensures reproducible builds
✅ **Virtual environment isolation** - Auto-created .venv directory
✅ **Development dependencies** - Separated dev and production dependencies

### Why No requirements.txt?

- **Modern Standard**: pyproject.toml is the PEP 518 standard for Python packaging
- **Better Dependency Resolution**: UV provides superior dependency resolution
- **Lock File Support**: uv.lock ensures exact dependency versions across environments
- **Development Separation**: Clear separation of production and development dependencies
- **Tool Integration**: Better integration with modern Python tools

### Dependency Management Commands

```bash
# Add production dependency
uv add fastapi

# Add development dependency
uv add --dev pytest

# Install dependencies
uv sync

# Update dependencies
uv lock --upgrade

# Run commands in environment
uv run python main.py
uv run pytest
```

### Migration from requirements.txt

If migrating from older projects with requirements.txt:

```bash
# Convert requirements.txt to pyproject.toml
uv add $(cat requirements.txt)

# Remove old requirements file
rm requirements.txt
```

This ensures your project uses modern, efficient Python packaging practices.

## Agent Usage

### Programmatic Documentation Access

For AI agents and automated systems, the complete usage guide is available via:

```bash
uv run fastapi-sqlmodel-generator docs
```

This command returns the entire LLM_USAGE.md content as plain text, enabling agents to:

- Query comprehensive configuration schemas and validation rules
- Access complete examples for all entity patterns  
- Reference troubleshooting guides for common issues
- Understand the full workflow from project initialization to domain generation
- Get up-to-date CLI command syntax and options

### Agent Workflow Recommendations

1. **Start with docs**: Always run `uv run fastapi-sqlmodel-generator docs` to get current documentation
2. **Validate configs**: Use schemas and examples from docs to create valid YAML configurations
3. **Follow patterns**: Reference the documented patterns for UUIDs, timestamps, relationships, etc.
4. **Use dry-run**: Validate configurations with `--dry-run` before actual generation
5. **Check success**: Parse generation output to ensure all files were created successfully

### Agent-Friendly Features

- **Structured CLI output**: Clear success/failure indicators and file lists
- **Comprehensive error messages**: Detailed validation errors with fixes
- **Consistent return codes**: 0 for success, 1 for failure  
- **Verbose mode**: `--verbose` flag provides detailed operation logs
- **Programmatic validation**: `--dry-run` validates without generating files"""


def get_documentation() -> str:
    """Return the complete LLM usage documentation."""
    return LLM_USAGE_CONTENT