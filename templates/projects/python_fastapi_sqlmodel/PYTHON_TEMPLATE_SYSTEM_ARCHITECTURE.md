# Python FastAPI SQLModel Template System - Complete Architecture Design

## Executive Summary
Implementation-ready architecture for a sophisticated Python FastAPI SQLModel template system that rivals the Go backend template's capabilities while leveraging Python's modern async ecosystem.

## 1. DIRECTORY STRUCTURE DESIGN

### Complete Template System Layout
```
templates/projects/python_fastapi_sqlmodel/
├── pyproject.toml                    # Python project configuration
├── README.md                         # Template usage documentation
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore patterns
├── .pre-commit-config.yaml          # Pre-commit hooks
├── Dockerfile                        # Container configuration
├── docker-compose.yml               # Development environment
├── alembic.ini                      # Database migration config
│
├── cmd/                             # Code generation tools
│   └── generate/                    # Python equivalent of Go's standardize
│       ├── __init__.py
│       ├── main.py                  # Click CLI entry point
│       ├── config_processor.py     # Hierarchical YAML configuration processing
│       ├── template_generator.py   # Jinja2 template engine with co-location
│       ├── template_data.py         # Template data structures
│       ├── filters.py               # Jinja2 custom filters
│       ├── utils.py                 # Utility functions
│       └── config_merger.py         # Hierarchical YAML configuration merging
│
├── app/                             # Generated application template
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry
│   │
│   ├── domain/                      # Business entities layer (Go-style with co-location)
│   │   ├── __init__.py
│   │   ├── base.py                  # Base entity classes
│   │   └── {{domain}}/              # Domain-specific entities (co-located templates & configs)
│   │       ├── __init__.py
│   │       ├── entities.py.j2       # Template: Pydantic business entities
│   │       ├── exceptions.py.j2     # Template: Domain-specific exceptions
│   │       ├── domain.yaml          # Config: Domain-level configuration
│   │       ├── entities.yaml        # Config: Entity-specific configuration
│   │       ├── entities.py          # Generated: Business entities (output)
│   │       └── exceptions.py        # Generated: Domain exceptions (output)
│   │
│   ├── usecase/                     # Use cases layer (Go-style naming with co-location)
│   │   ├── __init__.py
│   │   ├── base.py                  # Base use case classes
│   │   └── {{domain}}/              # Domain-specific use cases (co-located templates & configs)
│   │       ├── __init__.py
│   │       ├── protocols.py.j2      # Template: Use case interfaces
│   │       ├── usecase.py.j2        # Template: Use case implementations
│   │       ├── schemas.py.j2        # Template: Use case-level schemas
│   │       ├── usecase.yaml         # Config: Use case configuration
│   │       ├── business-rules.yaml  # Config: Business logic rules
│   │       ├── protocols.py         # Generated: Use case interfaces (output)
│   │       ├── usecase.py           # Generated: Use case implementations (output)
│   │       └── schemas.py           # Generated: Use case schemas (output)
│   │
│   ├── repository/                  # Data access layer (Go-style naming with co-location)
│   │   ├── __init__.py
│   │   ├── base.py                  # Base repository classes
│   │   └── {{domain}}/              # Domain-specific repositories (co-located templates & configs)
│   │       ├── __init__.py
│   │       ├── protocols.py.j2      # Template: Repository interfaces
│   │       ├── repository.py.j2     # Template: Repository implementations
│   │       ├── models.py.j2         # Template: SQLModel database entities
│   │       ├── repository.yaml      # Config: Repository configuration
│   │       ├── database.yaml        # Config: Database-specific settings
│   │       ├── protocols.py         # Generated: Repository interfaces (output)
│   │       ├── repository.py        # Generated: Repository implementations (output)
│   │       └── models.py            # Generated: SQLModel entities (output)
│   │
│   ├── interface/                   # Interface layer (Go-style naming with co-location)
│   │   ├── __init__.py
│   │   ├── http/                    # HTTP interfaces
│   │   │   ├── __init__.py
│   │   │   ├── middleware.py        # HTTP middleware
│   │   │   ├── exception_handlers.py # Global exception handling
│   │   │   ├── router.py            # Main router configuration
│   │   │   └── {{domain}}/          # Domain-specific HTTP handlers (co-located templates & configs)
│   │   │       ├── __init__.py
│   │   │       ├── schemas.py.j2    # Template: API request/response schemas
│   │   │       ├── handlers.py.j2   # Template: FastAPI route handlers
│   │   │       ├── dependencies.py.j2 # Template: Endpoint-specific dependencies
│   │   │       ├── api.yaml         # Config: API endpoint configuration
│   │   │       ├── validation.yaml  # Config: Request/response validation
│   │   │       ├── schemas.py       # Generated: API schemas (output)
│   │   │       ├── handlers.py      # Generated: Route handlers (output)
│   │   │       └── dependencies.py  # Generated: Dependencies (output)
│   │   │
│   │   └── di/                      # Dependency injection
│   │       ├── __init__.py
│   │       ├── containers.py        # DI container configuration
│   │       ├── dependencies.py      # FastAPI dependencies
│   │       └── {{domain}}/          # Domain-specific DI
│   │           ├── __init__.py
│   │           └── providers.py.j2  # Domain DI providers
│   │
│   ├── infrastructure/              # Infrastructure concerns
│   │   ├── __init__.py
│   │   ├── database/                # Database configuration
│   │   │   ├── __init__.py
│   │   │   ├── session.py           # Database session management
│   │   │   └── migrations/          # Alembic migrations
│   │   │
│   │   └── config/                  # Application configuration
│   │       ├── __init__.py
│   │       └── settings.py          # Configuration settings
│   │
│   └── tests/                       # Test templates
│       ├── __init__.py
│       ├── conftest.py              # Test configuration
│       ├── unit/                    # Unit test templates
│       │   └── {{domain}}/
│       │       ├── test_entities.py.j2
│       │       ├── test_services.py.j2
│       │       └── test_repositories.py.j2
│       ├── integration/             # Integration test templates
│       │   └── {{domain}}/
│       │       └── test_api.py.j2
│       └── fixtures/                # Test data fixtures
│           └── {{domain}}/
│               └── fixtures.py.j2
│
├── configs/                         # Domain configuration examples
│   ├── user_domain.yaml            # Comprehensive example
│   ├── simple_domain.yaml          # Minimal example
│   ├── complex_domain.yaml         # Advanced relationships
│   └── schemas/                     # Configuration schemas
│       └── domain_config_schema.json
│
├── scripts/                         # Development scripts
│   ├── setup.sh                     # Environment setup
│   ├── test.sh                      # Test execution
│   ├── format.sh                    # Code formatting
│   └── generate_example.sh          # Example generation
│
└── docs/                            # Documentation
    ├── README.md                    # Getting started
    ├── configuration.md             # YAML configuration guide
    ├── architecture.md              # Architecture documentation
    ├── customization.md             # Template customization
    └── examples/                    # Usage examples
```

## 2. CONFIGURATION SCHEMA ARCHITECTURE

### Pydantic Configuration Models
```python
# cmd/generate/config_models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class FieldType(str, Enum):
    """Supported field types."""
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    DATETIME = "datetime"
    UUID = "UUID"
    EMAIL = "EmailStr"
    JSON = "Dict[str, Any]"
    OPTIONAL_STRING = "Optional[str]"
    LIST_STRING = "List[str]"

class ValidationRule(str, Enum):
    """Validation rules."""
    REQUIRED = "required"
    EMAIL = "email"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    REGEX = "regex"
    RANGE = "range"

class FieldConfig(BaseModel):
    """Individual field configuration."""
    name: str = Field(description="Field name")
    type: FieldType = Field(description="Field type")
    description: Optional[str] = Field(None, description="Field description")
    default: Optional[Any] = Field(None, description="Default value")
    nullable: bool = Field(False, description="Allow null values")
    unique: bool = Field(False, description="Unique constraint")
    index: bool = Field(False, description="Database index")
    validations: List[str] = Field(default_factory=list, description="Validation rules")
    
    @validator('name')
    def name_must_be_snake_case(cls, v):
        if not v.islower() or ' ' in v:
            raise ValueError('Field name must be snake_case')
        return v

class EntityConfig(BaseModel):
    """Domain entity configuration."""
    name: str = Field(description="Entity name (PascalCase)")
    description: Optional[str] = Field(None, description="Entity description")
    base_class: str = Field("BaseEntity", description="Base class to inherit from")
    fields: List[FieldConfig] = Field(default_factory=list, description="Entity fields")
    computed_fields: List[Dict[str, Any]] = Field(default_factory=list)
    custom_methods: List[Dict[str, Any]] = Field(default_factory=list)
    pydantic_config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('name')
    def name_must_be_pascal_case(cls, v):
        if not v[0].isupper():
            raise ValueError('Entity name must be PascalCase')
        return v

class ModelConfig(BaseModel):
    """Database model configuration."""
    name: str = Field(description="Model name")
    table_name: str = Field(description="Database table name")
    description: Optional[str] = Field(None)
    inherit_from: List[str] = Field(default_factory=list, description="Mixin classes")
    fields: List[FieldConfig] = Field(default_factory=list)
    indexes: List[Dict[str, Any]] = Field(default_factory=list)
    constraints: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    sqlmodel_config: Dict[str, Any] = Field(default_factory=dict)

class RepositoryConfig(BaseModel):
    """Repository configuration."""
    interface_name: Optional[str] = Field(None, description="Protocol name")
    implementation_name: Optional[str] = Field(None, description="Implementation class name")
    base_class: str = Field("BaseRepository", description="Base repository class")
    async_methods: bool = Field(True, description="Use async methods")
    standard_methods: Dict[str, bool] = Field(default_factory=dict)
    custom_methods: List[Dict[str, Any]] = Field(default_factory=list)
    pagination: Dict[str, Any] = Field(default_factory=dict)
    filtering: Dict[str, Any] = Field(default_factory=dict)
    caching: Dict[str, Any] = Field(default_factory=dict)

class ServiceConfig(BaseModel):
    """Service/Use case configuration."""
    interface_name: Optional[str] = Field(None)
    implementation_name: Optional[str] = Field(None)
    base_class: str = Field("BaseService")
    async_methods: bool = Field(True)
    standard_methods: Dict[str, bool] = Field(default_factory=dict)
    business_methods: List[Dict[str, Any]] = Field(default_factory=list)
    validation: Dict[str, Any] = Field(default_factory=dict)
    transactions: Dict[str, Any] = Field(default_factory=dict)
    logging: Dict[str, Any] = Field(default_factory=dict)

class APIConfig(BaseModel):
    """API/Router configuration."""
    router_name: Optional[str] = Field(None)
    base_path: str = Field(description="API base path")
    tags: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    middleware: List[str] = Field(default_factory=list)
    endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    openapi_config: Dict[str, Any] = Field(default_factory=dict)

class GenerationConfig(BaseModel):
    """Code generation configuration."""
    preserve_custom_code: bool = Field(True, description="Enable @pyhex markers")
    generate_tests: bool = Field(True, description="Generate test files")
    generate_migrations: bool = Field(True, description="Generate Alembic migrations")
    uuid_primary_key: bool = Field(True, description="Use UUID vs int primary keys")
    async_by_default: bool = Field(True, description="Generate async methods")
    include_examples: bool = Field(True, description="Include example implementations")
    format_code: bool = Field(True, description="Format generated code with black")

class DomainConfig(BaseModel):
    """Complete domain configuration."""
    version: str = Field("1.0", description="Configuration schema version")
    domain: str = Field(description="Domain name (snake_case)")
    description: Optional[str] = Field(None, description="Domain description")
    package_name: str = Field("app", description="Python package name")
    
    # Core configuration sections
    entity: EntityConfig = Field(description="Entity configuration")
    models: List[ModelConfig] = Field(default_factory=list, description="Database models")
    repository: RepositoryConfig = Field(default_factory=RepositoryConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    api: APIConfig = Field(description="API configuration")
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    
    # Optional features
    features: Dict[str, Any] = Field(default_factory=dict)
    custom_config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('domain')
    def domain_must_be_snake_case(cls, v):
        if not v.islower() or ' ' in v:
            raise ValueError('Domain must be snake_case')
        return v
```

## 3. TEMPLATE PROCESSING ENGINE ARCHITECTURE

### Core Template Processing Classes
```python
# cmd/generate/template_generator.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, List
import black
import structlog

from .template_data import TemplateData
from .filters import register_custom_filters

logger = structlog.get_logger()

class TemplateGenerator:
    """Jinja2-based template processing engine with co-location support."""
    
    def __init__(self, app_dir: Path, config_merger):
        self.app_dir = app_dir  # Points to app/ directory with co-located templates
        self.config_merger = config_merger
        self.env = self._setup_jinja_environment()
    
    def _setup_jinja_environment(self) -> Environment:
        """Configure Jinja2 environment with custom filters for co-located templates."""
        env = Environment(
            loader=FileSystemLoader(self.app_dir),  # Load from app/ directory
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Register custom filters
        register_custom_filters(env)
        
        return env
    
    def generate_all_files(self, domain: str) -> None:
        """Generate all files for a domain using co-located templates and configurations."""
        logger.info("Starting co-location code generation", domain=domain)
        
        # 1. Merge hierarchical configurations for the domain
        merged_config = self.config_merger.merge_domain_configs(domain)
        
        # 2. Generate files for each layer using co-located templates
        layers = [
            ("domain", self._generate_domain_layer),
            ("usecase", self._generate_usecase_layer),
            ("repository", self._generate_repository_layer),
            ("interface/http", self._generate_interface_layer),
        ]
        
        for layer_name, generator in layers:
            try:
                layer_path = self.app_dir / layer_name / domain
                generator(layer_path, merged_config)
            except Exception as e:
                logger.error("Layer generation failed", layer=layer_name, error=str(e))
                raise
        
        logger.info("Co-location code generation completed", domain=domain)
    
    def _generate_domain_layer(self, layer_path: Path, config: Dict[str, Any]) -> None:
        """Generate domain layer files from co-located templates."""
        templates = [
            ("entities.py.j2", "entities.py"),
            ("exceptions.py.j2", "exceptions.py"),
        ]
        
        for template_file, output_file in templates:
            self._generate_colocated_file(layer_path, template_file, output_file, config)
    
    def _generate_repository_layer(self, layer_path: Path, config: Dict[str, Any]) -> None:
        """Generate repository layer files from co-located templates (Go-style structure)."""
        templates = [
            ("protocols.py.j2", "protocols.py"),
            ("repository.py.j2", "repository.py"),
            ("models.py.j2", "models.py"),
        ]
        
        for template_file, output_file in templates:
            self._generate_colocated_file(layer_path, template_file, output_file, config)
    
    def _generate_usecase_layer(self, layer_path: Path, config: Dict[str, Any]) -> None:
        """Generate use case layer files from co-located templates (Go-style structure)."""
        templates = [
            ("protocols.py.j2", "protocols.py"),
            ("usecase.py.j2", "usecase.py"),
            ("schemas.py.j2", "schemas.py"),
        ]
        
        for template_file, output_file in templates:
            self._generate_colocated_file(layer_path, template_file, output_file, config)
    
    def _generate_interface_layer(self, layer_path: Path, config: Dict[str, Any]) -> None:
        """Generate interface layer files from co-located templates (Go-style structure)."""
        templates = [
            ("schemas.py.j2", "schemas.py"),
            ("handlers.py.j2", "handlers.py"),
            ("dependencies.py.j2", "dependencies.py"),
        ]
        
        for template_file, output_file in templates:
            self._generate_colocated_file(layer_path, template_file, output_file, config)
    
    def _generate_colocated_file(
        self, 
        layer_path: Path, 
        template_file: str, 
        output_file: str, 
        config: Dict[str, Any]
    ) -> None:
        """Generate a single file from co-located template with merged configuration."""
        template_path = layer_path / template_file
        output_path = layer_path / output_file
        
        if not template_path.exists():
            logger.warning("Template not found", template=str(template_path))
            return
        
        try:
            # Load template relative to layer directory
            relative_template = str(template_path.relative_to(self.app_dir))
            template = self.env.get_template(relative_template)
            
            # Render template with merged configuration
            rendered_content = template.render(**config)
            
            # Format Python code with black
            if output_file.endswith('.py'):
                rendered_content = black.format_str(rendered_content, mode=black.FileMode())
            
            # Write generated file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered_content, encoding='utf-8')
            
            logger.info("Generated file", template=template_file, output=str(output_path))
            
        except Exception as e:
            logger.error("File generation failed", template=template_file, error=str(e))
            raise
    
# Configuration Merger for Hierarchical YAML Processing

class ConfigurationMerger:
    """Hierarchical YAML configuration merging for co-located template system."""
    
    def __init__(self, app_dir: Path):
        self.app_dir = app_dir
        
    def merge_domain_configs(self, domain: str) -> Dict[str, Any]:
        """Merge all configuration files for a domain hierarchically."""
        merged_config = {}
        
        # Define layer hierarchy (parent → child inheritance)
        layers = [
            f"domain/{domain}",
            f"usecase/{domain}",
            f"repository/{domain}",
            f"interface/http/{domain}",
        ]
        
        for layer in layers:
            layer_path = self.app_dir / layer
            if layer_path.exists():
                layer_config = self._load_layer_configs(layer_path)
                merged_config = self._deep_merge(merged_config, layer_config)
        
        # Add computed values for template rendering
        merged_config.update({
            "domain": domain,
            "domain_snake": self._to_snake_case(domain),
            "domain_pascal": self._to_pascal_case(domain),
            "domain_plural": self._pluralize(domain),
        })
        
        return merged_config
    
    def _load_layer_configs(self, layer_path: Path) -> Dict[str, Any]:
        """Load all YAML configuration files from a layer directory."""
        layer_config = {}
        
        for yaml_file in layer_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
                layer_config = self._deep_merge(layer_config, file_config)
            except Exception as e:
                logger.warning("Failed to load config", file=str(yaml_file), error=str(e))
        
        return layer_config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries with override capability."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _to_snake_case(self, name: str) -> str:
        """Convert string to snake_case."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert string to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _pluralize(self, name: str) -> str:
        """Simple pluralization for domain names."""
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return name + 'es'
        else:
            return name + 's'

# cmd/generate/filters.py
from jinja2 import Environment
import inflect
import re

def register_custom_filters(env: Environment) -> None:
    """Register custom Jinja2 filters."""
    p = inflect.engine()
    
    def to_snake_case(text: str) -> str:
        """Convert PascalCase to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def to_pascal_case(text: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in text.split('_'))
    
    def to_camel_case(text: str) -> str:
        """Convert snake_case to camelCase."""
        words = text.split('_')
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def pluralize(text: str) -> str:
        """Pluralize a word."""
        return p.plural(text)
    
    def singularize(text: str) -> str:
        """Singularize a word."""
        return p.singular_noun(text) or text
    
    def python_type_hint(field_type: str, nullable: bool = False) -> str:
        """Convert field type to Python type hint."""
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'float': 'float',
            'boolean': 'bool',
            'datetime': 'datetime',
            'uuid': 'UUID',
            'email': 'EmailStr',
            'json': 'Dict[str, Any]',
        }
        
        python_type = type_mapping.get(field_type.lower(), field_type)
        
        if nullable:
            return f"Optional[{python_type}]"
        return python_type
    
    def sqlalchemy_type(field_type: str) -> str:
        """Convert field type to SQLAlchemy type."""
        type_mapping = {
            'string': 'String',
            'integer': 'Integer',
            'float': 'Float',
            'boolean': 'Boolean',
            'datetime': 'DateTime',
            'uuid': 'UUID',
            'text': 'Text',
            'json': 'JSON',
        }
        return type_mapping.get(field_type.lower(), 'String')
    
    # Register filters
    env.filters['to_snake_case'] = to_snake_case
    env.filters['to_pascal_case'] = to_pascal_case
    env.filters['to_camel_case'] = to_camel_case
    env.filters['pluralize'] = pluralize
    env.filters['singularize'] = singularize
    env.filters['python_type_hint'] = python_type_hint
    env.filters['sqlalchemy_type'] = sqlalchemy_type
```

## 4. CODE PRESERVATION SYSTEM

### @pyhex Marker Implementation
```python
# cmd/generate/code_preservation.py
import re
from pathlib import Path
from typing import Dict, List, Tuple
import structlog

logger = structlog.get_logger()

class CodePreservationManager:
    """Manages @pyhex code preservation markers."""
    
    MARKER_PATTERN = r'# @pyhex:begin:([a-zA-Z_:]+)\n(.*?)\n# @pyhex:end:\1'
    BEGIN_MARKER = "# @pyhex:begin:{}"
    END_MARKER = "# @pyhex:end:{}"
    
    def __init__(self):
        self.preserved_blocks: Dict[str, Dict[str, str]] = {}
    
    def extract_preserved_code(self, file_path: Path) -> Dict[str, str]:
        """Extract all preserved code blocks from a file."""
        if not file_path.exists():
            return {}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            blocks = {}
            
            matches = re.finditer(self.MARKER_PATTERN, content, re.DOTALL)
            for match in matches:
                block_name = match.group(1)
                block_content = match.group(2)
                blocks[block_name] = block_content
                logger.debug("Extracted preserved block", file=str(file_path), block=block_name)
            
            return blocks
            
        except Exception as e:
            logger.error("Failed to extract preserved code", file=str(file_path), error=str(e))
            return {}
    
    def inject_preserved_code(self, content: str, preserved_blocks: Dict[str, str]) -> str:
        """Inject preserved code blocks into generated content."""
        if not preserved_blocks:
            return content
        
        def replace_block(match):
            block_name = match.group(1)
            if block_name in preserved_blocks:
                preserved_content = preserved_blocks[block_name]
                return f"{self.BEGIN_MARKER.format(block_name)}\n{preserved_content}\n{self.END_MARKER.format(block_name)}"
            return match.group(0)  # Keep original if no preserved content
        
        # Replace placeholder blocks with preserved content
        result = re.sub(self.MARKER_PATTERN, replace_block, content, flags=re.DOTALL)
        
        logger.debug("Injected preserved code blocks", count=len(preserved_blocks))
        return result
    
    def create_preservation_regions(self, template_content: str) -> str:
        """Add preservation markers to template content."""
        # This method adds default preservation regions to templates
        # Implementation would depend on template structure
        return template_content

# Integration into template generator
class PreservationAwareTemplateGenerator(TemplateGenerator):
    """Template generator with code preservation support."""
    
    def __init__(self, template_dir: Path, output_dir: Path):
        super().__init__(template_dir, output_dir)
        self.preservation_manager = CodePreservationManager()
    
    def _generate_file(self, template_name: str, output_path: str, context: Dict[str, Any]) -> None:
        """Generate file with code preservation."""
        output_file = self.output_dir / output_path
        
        # Extract existing preserved code
        preserved_blocks = {}
        if output_file.exists():
            preserved_blocks = self.preservation_manager.extract_preserved_code(output_file)
        
        # Generate new content
        template = self.env.get_template(template_name)
        content = template.render(**context)
        
        # Inject preserved code
        if preserved_blocks:
            content = self.preservation_manager.inject_preserved_code(content, preserved_blocks)
        
        # Format and write
        if output_path.endswith('.py') and context.get('generation', {}).get('format_code', True):
            try:
                content = black.format_str(content, mode=black.FileMode())
            except black.InvalidInput as e:
                logger.warning("Black formatting failed", file=output_path, error=str(e))
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.debug("Generated file with preservation", path=output_path, preserved_blocks=len(preserved_blocks))
```

## 5. TEMPLATE EXAMPLES

### Entity Template (entity.py.j2)
```python
"""{{domain|to_pascal_case}} domain entities."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

from app.domain.base import BaseEntity

# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports

class {{domain|to_pascal_case}}(BaseEntity):
    """{{entity.description or (domain|to_pascal_case + ' business entity')}}."""
    
    # Standard fields
    id: UUID = Field(description="Unique identifier")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    # Domain-specific fields
    {%- for field in entity.fields %}
    {{field.name}}: {{field.type|python_type_hint(field.nullable)}} = Field(
        {%- if field.default %}default={{field.default}}, {% endif %}
        description="{{field.description or field.name}}"
    )
    {%- endfor %}
    
    # @pyhex:begin:custom:fields
    # Add custom fields here
    # @pyhex:end:custom:fields
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True
        validate_assignment = True
        # @pyhex:begin:custom:pydantic_config
        # Add custom Pydantic configuration here
        # @pyhex:end:custom:pydantic_config
    
    {%- for field in entity.fields %}
    {%- if field.validations %}
    
    @validator('{{field.name}}')
    def validate_{{field.name}}(cls, v):
        """Validate {{field.name}} field."""
        # @pyhex:begin:custom:{{field.name}}_validation
        {%- for validation in field.validations %}
        # TODO: Implement {{validation}} validation
        {%- endfor %}
        # @pyhex:end:custom:{{field.name}}_validation
        return v
    {%- endif %}
    {%- endfor %}
    
    @classmethod
    def from_model(cls, model: "{{domain|to_pascal_case}}Model") -> "{{domain|to_pascal_case}}":
        """Convert from SQLModel to domain entity."""
        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            {%- for field in entity.fields %}
            {{field.name}}=model.{{field.name}},
            {%- endfor %}
        )
    
    def to_model(self) -> "{{domain|to_pascal_case}}Model":
        """Convert to SQLModel for persistence."""
        from app.infrastructure.database.models.{{domain_snake}} import {{domain|to_pascal_case}}Model
        return {{domain|to_pascal_case}}Model(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            {%- for field in entity.fields %}
            {{field.name}}=self.{{field.name}},
            {%- endfor %}
        )
    
    # @pyhex:begin:custom:methods
    def example_business_method(self) -> str:
        """Example business method - implement your logic here."""
        return f"{{domain|to_pascal_case}} {self.id}"
    # @pyhex:end:custom:methods

# @pyhex:begin:custom:classes
# Add custom entity classes here
# @pyhex:end:custom:classes
```

### Repository Template (repository.py.j2)
```python
"""{{domain|to_pascal_case}} repository implementation."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from uuid import UUID
import structlog

from .protocols import {{domain|to_pascal_case}}RepositoryProtocol
from app.domain.{{domain_snake}}.entities import {{domain|to_pascal_case}}
from app.infrastructure.database.models.{{domain_snake}} import {{domain|to_pascal_case}}Model
from app.infrastructure.repositories.base import BaseRepository

# @pyhex:begin:custom:imports
# Add custom imports here
# @pyhex:end:custom:imports

logger = structlog.get_logger()

class {{domain|to_pascal_case}}Repository(BaseRepository, {{domain|to_pascal_case}}RepositoryProtocol):
    """SQLModel implementation of {{domain|to_pascal_case}}Repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model_class = {{domain|to_pascal_case}}Model
        self.entity_class = {{domain|to_pascal_case}}
    
    async def create(self, entity: {{domain|to_pascal_case}}) -> {{domain|to_pascal_case}}:
        """Create a new {{domain_snake}}."""
        logger.info("Creating {{domain_snake}}", entity_id=entity.id)
        
        # @pyhex:begin:custom:create_validation
        # Add custom create validation here
        # @pyhex:end:custom:create_validation
        
        model = entity.to_model()
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        result = {{domain|to_pascal_case}}.from_model(model)
        logger.info("Created {{domain_snake}}", entity_id=result.id)
        return result
    
    async def get_by_id(self, entity_id: UUID) -> Optional[{{domain|to_pascal_case}}]:
        """Retrieve {{domain_snake}} by ID."""
        logger.debug("Getting {{domain_snake}} by ID", entity_id=entity_id)
        
        statement = select({{domain|to_pascal_case}}Model).where({{domain|to_pascal_case}}Model.id == entity_id)
        result = await self.session.exec(statement)
        model = result.first()
        
        if not model:
            logger.debug("{{domain|to_pascal_case}} not found", entity_id=entity_id)
            return None
        
        return {{domain|to_pascal_case}}.from_model(model)
    
    async def list_{{domain_plural_snake}}(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[{{domain|to_pascal_case}}]:
        """List {{domain_plural_snake}} with pagination and filtering."""
        logger.debug("Listing {{domain_plural_snake}}", skip=skip, limit=limit, filters=filters)
        
        statement = select({{domain|to_pascal_case}}Model).offset(skip).limit(limit)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr({{domain|to_pascal_case}}Model, key):
                    statement = statement.where(getattr({{domain|to_pascal_case}}Model, key) == value)
        
        # @pyhex:begin:custom:list_filtering
        # Add custom filtering logic here
        # @pyhex:end:custom:list_filtering
        
        result = await self.session.exec(statement)
        models = result.all()
        
        return [{{domain|to_pascal_case}}.from_model(model) for model in models]
    
    async def update(self, entity: {{domain|to_pascal_case}}) -> {{domain|to_pascal_case}}:
        """Update existing {{domain_snake}}."""
        logger.info("Updating {{domain_snake}}", entity_id=entity.id)
        
        # @pyhex:begin:custom:update_validation
        # Add custom update validation here
        # @pyhex:end:custom:update_validation
        
        model = entity.to_model()
        model.updated_at = datetime.utcnow()
        
        await self.session.merge(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        result = {{domain|to_pascal_case}}.from_model(model)
        logger.info("Updated {{domain_snake}}", entity_id=result.id)
        return result
    
    async def delete(self, entity_id: UUID) -> bool:
        """Delete {{domain_snake}} by ID."""
        logger.info("Deleting {{domain_snake}}", entity_id=entity_id)
        
        statement = delete({{domain|to_pascal_case}}Model).where({{domain|to_pascal_case}}Model.id == entity_id)
        result = await self.session.exec(statement)
        await self.session.commit()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info("Deleted {{domain_snake}}", entity_id=entity_id)
        else:
            logger.warning("{{domain|to_pascal_case}} not found for deletion", entity_id=entity_id)
        
        return deleted
    
    # @pyhex:begin:custom:methods
    async def find_by_example_field(self, value: str) -> List[{{domain|to_pascal_case}}]:
        """Example custom query method."""
        # Implement custom query logic here
        pass
    # @pyhex:end:custom:methods
```

## 6. CLI TOOL ARCHITECTURE

### Click-based CLI Implementation
```python
# cmd/generate/main.py
import click
from pathlib import Path
import sys
import structlog
from typing import Optional

from .config_processor import ConfigProcessor
from .template_generator import PreservationAwareTemplateGenerator
from .utils import setup_logging

logger = structlog.get_logger()

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(verbose: bool, debug: bool):
    """FastAPI SQLModel Template Generator.
    
    Generate sophisticated Python backend applications from YAML configuration.
    """
    setup_logging(verbose=verbose, debug=debug)

@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True), 
              help='YAML configuration file path')
@click.option('--output', '-o', default='./generated', type=click.Path(),
              help='Output directory for generated code')
@click.option('--template-dir', type=click.Path(exists=True),
              help='Custom template directory (optional)')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without creating files')
@click.option('--preserve-code/--no-preserve-code', default=True,
              help='Enable/disable code preservation with @pyhex markers')
@click.option('--format-code/--no-format-code', default=True,
              help='Format generated code with black')
def generate(
    config: str, 
    output: str, 
    template_dir: Optional[str],
    dry_run: bool,
    preserve_code: bool,
    format_code: bool
):
    """Generate FastAPI application from YAML configuration."""
    try:
        config_path = Path(config)
        output_path = Path(output)
        
        # Load and validate configuration
        logger.info("Loading configuration", config=str(config_path))
        processor = ConfigProcessor()
        domain_config = processor.load_config(config_path)
        
        # Override generation settings from CLI
        domain_config.generation.preserve_custom_code = preserve_code
        domain_config.generation.format_code = format_code
        
        # Create template data
        template_data = processor.create_template_data(domain_config)
        
        if dry_run:
            logger.info("DRY RUN: Would generate files for domain", domain=template_data.domain)
            # Show what would be generated
            return
        
        # Determine template directory
        if template_dir:
            tmpl_dir = Path(template_dir)
        else:
            tmpl_dir = Path(__file__).parent / "templates"
        
        # Generate code
        logger.info("Starting code generation", domain=template_data.domain, output=str(output_path))
        generator = PreservationAwareTemplateGenerator(tmpl_dir, output_path)
        generator.generate_all_files(template_data)
        
        click.echo(f"✅ Successfully generated {template_data.domain} domain at {output_path}")
        
    except Exception as e:
        logger.error("Generation failed", error=str(e))
        click.echo(f"❌ Generation failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('domain')
@click.argument('entity', required=False)
@click.option('--output', '-o', default='./generated', type=click.Path())
def scaffold(domain: str, entity: Optional[str], output: str):
    """Quick scaffold a domain without full configuration.
    
    Creates a minimal domain structure for rapid prototyping.
    """
    try:
        entity_name = entity or domain.title()
        output_path = Path(output)
        
        # Create minimal configuration
        from .config_models import DomainConfig, EntityConfig, FieldConfig
        
        minimal_config = DomainConfig(
            domain=domain,
            description=f"Scaffolded {domain} domain",
            entity=EntityConfig(
                name=entity_name,
                description=f"{entity_name} entity",
                fields=[
                    FieldConfig(name="name", type="str", description=f"{entity_name} name"),
                ]
            )
        )
        
        # Generate with minimal config
        processor = ConfigProcessor()
        template_data = processor.create_template_data(minimal_config)
        
        tmpl_dir = Path(__file__).parent / "templates"
        generator = PreservationAwareTemplateGenerator(tmpl_dir, output_path)
        generator.generate_all_files(template_data)
        
        click.echo(f"✅ Scaffolded {domain} domain at {output_path}")
        click.echo(f"💡 Customize {output_path}/configs/{domain}_domain.yaml and regenerate for full configuration")
        
    except Exception as e:
        logger.error("Scaffolding failed", error=str(e))
        click.echo(f"❌ Scaffolding failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True))
def validate(config: str):
    """Validate YAML configuration file."""
    try:
        config_path = Path(config)
        processor = ConfigProcessor()
        domain_config = processor.load_config(config_path)
        
        click.echo(f"✅ Configuration is valid!")
        click.echo(f"Domain: {domain_config.domain}")
        click.echo(f"Entity: {domain_config.entity.name}")
        click.echo(f"Fields: {len(domain_config.entity.fields)}")
        
    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {e}", err=True)
        sys.exit(1)

@cli.command()
def init():
    """Initialize a new project with example configuration."""
    try:
        # Create example configuration files
        example_config = """# Example domain configuration
version: "1.0"
domain: "user"
description: "User management domain"

entity:
  name: "User"
  description: "User entity"
  fields:
    - name: "email"
      type: "email"
      description: "User email address"
      unique: true
      validations: ["required", "email"]
    - name: "first_name"
      type: "str"
      description: "User first name"
      validations: ["required", "min_length:2"]
    - name: "last_name"
      type: "str"
      description: "User last name"
      validations: ["required", "min_length:2"]

api:
  base_path: "/api/v1/users"
  tags: ["users"]
  
generation:
  preserve_custom_code: true
  generate_tests: true
  uuid_primary_key: true
"""
        
        config_dir = Path("configs")
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "user_domain.yaml"
        config_file.write_text(example_config)
        
        click.echo(f"✅ Initialized project with example configuration")
        click.echo(f"📝 Edit {config_file} and run: python -m cmd.generate generate -c {config_file}")
        
    except Exception as e:
        click.echo(f"❌ Initialization failed: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
```

## Summary

This Python FastAPI SQLModel template system architecture provides:

1. **Complete 1:1 Go Pattern Mapping**: All sophisticated Go patterns preserved
2. **Modern Python Stack**: FastAPI + SQLModel + Pydantic + async/await
3. **Sophisticated Code Generation**: Jinja2 with custom filters and preservation
4. **Type Safety**: Comprehensive Pydantic configuration validation
5. **Professional CLI**: Click-based with multiple commands and options
6. **Code Preservation**: @pyhex marker system for custom code
7. **Hexagonal Architecture**: Clean separation of concerns
8. **Testing Ready**: Comprehensive test templates and fixtures
9. **Production Ready**: Docker, dependencies, and deployment configs
10. **Developer Experience**: Black formatting, structured logging, comprehensive docs

The architecture is implementation-ready and provides a sophisticated foundation for rapid Python backend development.