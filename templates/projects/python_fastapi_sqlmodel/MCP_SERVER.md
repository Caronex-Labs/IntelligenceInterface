# FastAPI SQLModel Generator - MCP Server

This MCP (Model Context Protocol) server provides LLMs with direct access to the FastAPI SQLModel project generator CLI
tool functionality through strict data types and standardized interfaces.

## Overview

The MCP server wraps the existing CLI functionality and exposes it through MCP tools and resources, allowing LLMs to:

1. **Initialize complete FastAPI projects** with proper directory structure
2. **Generate domain code** from configuration using existing Pydantic models
3. **Validate configurations** before generation
4. **Access schemas and examples** for proper data structure understanding

## Key Design Principles

- **Single Source of Truth**: Reuses ALL existing Pydantic models from `cli/generate/config/models.py`
- **Strict Data Types**: No schema guessing - everything is strictly typed with Pydantic validation
- **Zero Duplication**: Only adds response models; all input models are imported from existing codebase

## Available Tools

### 1. `initialize_project`

Initialize a complete FastAPI SQLModel project with full directory structure.

**Parameters:**

- `project_name` (str): Name of the project to create
- `output_dir` (str): Directory where the project should be created
- `description` (str, optional): Project description
- `author` (str, optional): Project author
- `clean_existing` (bool): Whether to clean existing directory

**Returns:** `ProjectInitializationResult`

### 2. `generate_domain_from_config`

Generate domain code from EntityDomainConfig using existing Pydantic models.

**Parameters:**

- `domain_config` (EntityDomainConfig): Complete domain configuration
- `output_dir` (str): Output directory for generated code
- `clean_existing` (bool): Whether to clean existing output directory
- `validate_syntax` (bool): Whether to validate generated Python syntax
- `validate_imports` (bool): Whether to validate import statements

**Returns:** `GenerationResult`

### 3. `generate_usecase_domain`

Generate use case domain with business logic orchestration.

**Parameters:**

- `usecase_config` (UseCaseDomainConfig): Complete use case domain configuration
- `output_dir` (str): Output directory for generated code
- `clean_existing` (bool): Whether to clean existing output directory

**Returns:** `GenerationResult`

### 4. `validate_configuration`

Validate configuration objects for correctness.

**Parameters:**

- `config` (Union[Configuration, EntityDomainConfig, UseCaseDomainConfig]): Configuration to validate

**Returns:** `ValidationResult`

## Available Resources

### Schemas

- `schema://entity-domain-config` - JSON schema for EntityDomainConfig
- `schema://usecase-domain-config` - JSON schema for UseCaseDomainConfig
- `schema://configuration` - JSON schema for Configuration
- `schema://field-types` - Available field types, relationship types, etc.

### Examples

- `examples://entity-domain-simple` - Simple entity domain example
- `examples://entity-domain-advanced` - Advanced example with relationships

## Usage

### Starting the Server

```bash
# Install dependencies
uv add fastmcp

# Start the MCP server
uv run python mcp_server.py
```

### Example Configuration

```python
from cli.generate.config.models import EntityDomainConfig, EntityConfig, FieldConfig, FieldType

# Create domain configuration using existing models
config = EntityDomainConfig(
    name="Product",
    description="Product catalog domain",
    entities=[
        EntityConfig(
            name="Product",
            fields=[
                FieldConfig(
                    name="id",
                    type=FieldType.UUID,
                    required=True,
                    unique=True,
                    description="Unique product identifier"
                ),
                FieldConfig(
                    name="name",
                    type=FieldType.STR,
                    required=True,
                    description="Product name"
                ),
                FieldConfig(
                    name="price",
                    type=FieldType.FLOAT,
                    required=True,
                    description="Product price"
                )
            ]
        )
    ]
)

# Use through MCP tools
result = generate_domain_from_config(
    domain_config=config,
    output_dir="./generated",
    validate_syntax=True
)
```

## Configuration Models

The server uses existing Pydantic models from `cli/generate/config/models.py`:

### Core Models

- `EntityDomainConfig` - Complete domain configuration
- `UseCaseDomainConfig` - Use case domain with business logic
- `Configuration` - Legacy configuration format
- `EntityConfig` - Individual entity configuration
- `FieldConfig` - Entity field configuration
- `RelationshipConfig` - Entity relationship configuration

### Supporting Models

- `DomainConfig` - Domain metadata
- `EndpointConfig` - API endpoint configuration
- `BusinessRuleConfig` - Business rule configuration
- `UseCaseConfig` - Use case orchestration
- `MixinConfig` - Reusable field mixins
- `SQLModelConfig` - SQLModel-specific settings

### Enums

- `FieldType` - Available field types (str, int, UUID, etc.)
- `RelationshipType` - Relationship types (one_to_many, etc.)
- `HTTPMethod` - HTTP methods for endpoints
- `BusinessRuleType` - Types of business rules
- `BusinessRuleSeverity` - Rule severity levels

## Response Models

The server adds only three new models for MCP responses:

- `GenerationResult` - Result of generation operations
- `ValidationResult` - Result of validation operations
- `ProjectInitializationResult` - Result of project initialization

## Testing

```bash
# Run the demo to see usage examples
uv run python demo_mcp_usage.py

# Run basic tests
uv run python test_mcp_server.py
```

## Integration with Claude Code

This MCP server is designed to work seamlessly with Claude Code and other MCP-compatible LLMs:

1. **Schema Discovery**: LLMs can fetch JSON schemas to understand exact data structures
2. **Example Access**: Pre-built examples show proper usage patterns
3. **Strict Validation**: All inputs are validated through existing Pydantic models
4. **Error Handling**: Comprehensive error messages guide proper usage

## Architecture Benefits

- **No Schema Drift**: Uses existing validated models
- **Type Safety**: Full Pydantic validation on all inputs
- **Maintainability**: Single source of truth for all schemas
- **Extensibility**: Easy to add new tools using existing patterns
- **Reliability**: Leverages battle-tested CLI functionality

## Error Handling

All tools return structured error information:

```python
{
    "success": False,
    "errors": ["Configuration must include at least one entity"],
    "warnings": ["Domain name does not match any entity name"]
}
```

This enables LLMs to understand issues and retry with corrected configurations.