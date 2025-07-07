# Use Case Template Flow - Co-location Architecture

This directory contains the Use Case Template Flow implementation, providing comprehensive business logic orchestration
templates with co-location architecture for optimal developer experience.

## Overview

The Use Case Template Flow implements the application layer of hexagonal architecture, coordinating business workflows
between domain entities and repositories while enforcing business rules and managing transaction boundaries.

### Key Features

- **Co-location Architecture**: Templates, configurations, and generated files in same directory
- **Hierarchical Configuration**: Inherits from core and repository layers
- **Business Logic Orchestration**: Complete workflow step implementation
- **FastAPI Integration**: Ready for dependency injection patterns
- **Comprehensive Error Handling**: Business rule violations and validation errors
- **@pyhex Preservation**: Custom business logic preserved during regeneration

## Directory Structure

```
app/usecase/
├── README.md                          # This file
├── __init__.py                        # Use case layer initialization
└── {{domain}}/                        # Co-located domain use case directory
    ├── __init__.py                    # Domain use case module initialization
    ├── usecase.yaml                   # Use case configuration and workflow patterns
    ├── business-rules.yaml            # Business logic rules and constraints
    ├── protocols.py.j2                # Template: Use case interfaces
    ├── usecase.py.j2                  # Template: Use case implementations
    ├── schemas.py.j2                  # Template: Use case-level schemas
    ├── protocols.py                   # Generated: Use case interfaces (output)
    ├── usecase.py                     # Generated: Use case implementations (output)
    └── schemas.py                     # Generated: Use case schemas (output)
```

## Configuration Files

### usecase.yaml

Defines use case-specific workflow patterns and validation configuration:

```yaml
name: "{{domain.name|title}}UseCase"
description: "{{domain.description}} use case orchestration"
package: "app.usecase.{{domain.name}}"

methods:
  - name: "create_{{domain.name}}"
    description: "Create a new {{domain.name}} with business validation"
    input_schema: "Create{{domain.name|title}}Request"
    output_schema: "{{domain.name|title}}Response"
    transaction_boundary: true
    dependencies:
      repositories: ["{{domain.name}}_repository"]
      services: ["validation_service"]
    business_rules: ["{{domain.name}}_validation", "business_constraints"]
    orchestration_steps:
      - "validate_{{domain.name}}_data"
      - "check_business_rules"
      - "create_{{domain.name}}_record"
      - "publish_{{domain.name}}_created_event"

dependencies:
  repositories: ["{{domain.name}}_repository"]
  services: ["validation_service", "event_publisher", "logger"]

error_handling:
  aggregation_strategy: "collect_all_errors"
  early_termination: false
  custom_exceptions:
    - rule: "{{domain.name}}_validation"
      exception: "{{domain.name|title}}ValidationError"

service_composition:
  transaction_manager: "database_transaction_manager"
  event_publisher: "domain_event_publisher"
  cache_manager: "redis_cache_manager"

dependency_injection:
  interface_mappings:
    "{{domain.name|title}}Repository": "sqlmodel_{{domain.name}}_repository"
    "ValidationService": "pydantic_validation_service"
  scoped_dependencies:
    - "database_session"
    - "user_context"
  singleton_dependencies:
    - "cache_manager"
    - "logger"
```

### business-rules.yaml

Defines domain-specific business logic rules and constraints:

```yaml
rules:
  - name: "{{domain.name}}_validation"
    type: "validation"
    condition: "{{domain.name}}.is_valid() and {{domain.name}}.data_integrity_check()"
    error_message: "{{domain.name|title}} validation failed"
    severity: "error"
    context: "{{domain.name}}_operations"
    description: "Validates {{domain.name}} data integrity and format requirements"

  - name: "{{domain.name}}_exists"
    type: "constraint"
    condition: "{{domain.name}}_repository.exists({{domain.name}}.id)"
    error_message: "{{domain.name|title}} not found"
    severity: "error"
    context: "{{domain.name}}_retrieval"

validation_groups:
  - name: "{{domain.name}}_creation_validation"
    description: "Validation rules for {{domain.name}} creation"
    rules: ["{{domain.name}}_validation", "business_constraints"]
    execution_order: ["{{domain.name}}_validation", "business_constraints"]

error_handling:
  aggregation_strategy: "collect_all_errors"
  early_termination: false
  custom_exceptions:
    - rule: "{{domain.name}}_validation"
      exception: "{{domain.name|title}}ValidationError"
```

## Generated Templates

### protocols.py.j2

Generates use case interfaces and protocols:

- **{{domain.name|title}}UseCaseProtocol**: Main use case interface
- **{{domain.name|title}}BusinessRulesProtocol**: Business rules validation interface
- **{{domain.name|title}}EventProtocol**: Domain event publishing interface

Key features:

- Abstract method definitions for all business operations
- Comprehensive documentation with business rules and orchestration steps
- Type-safe interfaces for dependency injection
- Error handling specifications

### usecase.py.j2

Generates use case implementations with business logic orchestration:

- **{{domain.name|title}}UseCase**: Main use case implementation
- **{{domain.name|title}}BusinessRules**: Business rules validation implementation

Key features:

- Complete CRUD operation implementations
- Business logic orchestration with transaction management
- Repository coordination and service integration
- Event publishing and error handling
- @pyhex preservation markers for custom logic

### schemas.py.j2

Generates use case-level validation and data transfer objects:

- **Request Schemas**: Create, Update, Delete, Get, List operations
- **Response Schemas**: Formatted responses with computed properties
- **Error Schemas**: Structured error responses and validation details
- **Business Rule Schemas**: Validation results and rule violations

Key features:

- Comprehensive input validation with Pydantic
- Pagination and filtering support
- Business rule violation reporting
- FastAPI integration-ready schemas

## Integration with Configuration Loader

The use case templates integrate seamlessly with the existing configuration loader:

```python
from cli.generate.config import UseCaseLoader

# Load configuration
loader = UseCaseLoader(strict_mode=True)
config = loader.load_from_files("usecase.yaml", "business-rules.yaml")

# Access configuration for template generation
usecase_methods = config.usecase.methods
business_rules = config.business_rules.rules
dependency_injection = config.usecase.dependency_injection
```

## Hierarchical Configuration Merging

Use case configurations inherit from core and repository layers:

1. **Core Layer**: Base entity and domain-level settings
2. **Repository Layer**: Data access patterns and database configuration
3. **Use Case Layer**: Business logic workflows and validation rules
4. **Interface Layer**: API patterns and endpoint configuration

Configuration merging follows precedence rules with use case-specific overrides.

## FastAPI Integration

Generated use cases integrate seamlessly with FastAPI dependency injection:

```python
from fastapi import Depends
from app.usecase.user import UserUseCase, UserUseCaseProtocol

async def get_user_usecase(
    repository: UserRepository = Depends(get_user_repository)
) -> UserUseCaseProtocol:
    return UserUseCase(repository, business_rules, event_publisher)

@router.post("/users/", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    use_case: UserUseCaseProtocol = Depends(get_user_usecase)
) -> UserResponse:
    return await use_case.create_user(request)
```

## Business Logic Orchestration

Use cases coordinate complex business workflows:

1. **Input Validation**: Validate request data and business constraints
2. **Business Rules**: Apply domain-specific validation rules
3. **Repository Operations**: Coordinate data access and persistence
4. **Event Publishing**: Publish domain events for integration
5. **Error Handling**: Transform business errors to appropriate responses

### Orchestration Steps

Each use case method can define orchestration steps:

```yaml
orchestration_steps:
  - "validate_user_data"
  - "check_business_rules"
  - "create_user_record"
  - "publish_user_created_event"
```

These steps are implemented as private methods in the use case class, allowing for granular testing and customization.

## Error Handling and Business Rules

The system provides comprehensive error handling:

- **Validation Errors**: Input validation and data integrity checks
- **Business Rule Violations**: Domain-specific constraint violations
- **Authorization Errors**: Permission and security constraint failures
- **System Errors**: Infrastructure and external service failures

Business rules support different types:

- **validation**: Data format and integrity rules
- **constraint**: Business logic constraints
- **security**: Authorization and permission rules

## Testing and Quality Assurance

The use case templates support comprehensive testing:

- **Unit Tests**: Individual use case method testing with mocked dependencies
- **Integration Tests**: Cross-layer testing with real repository implementations
- **Business Rule Tests**: Validation rule testing with various scenarios
- **BDD Tests**: Behavior-driven testing with Gherkin scenarios

## Development Workflow

1. **Configure**: Define use case workflows in `usecase.yaml`
2. **Define Rules**: Specify business rules in `business-rules.yaml`
3. **Generate**: Run template generation to create implementation files
4. **Customize**: Add custom logic using @pyhex preservation markers
5. **Test**: Validate implementation with comprehensive test suites
6. **Integrate**: Wire up with FastAPI dependency injection

## Code Preservation

The @pyhex preservation system allows custom code to survive template regeneration:

```python
# @pyhex:begin:custom:create_user_validation
# Custom validation logic here
if user.email.endswith('@banned-domain.com'):
    raise UserValidationError("Email domain not allowed")
# @pyhex:end:custom:create_user_validation
```

Preservation markers are strategically placed throughout templates for:

- Custom imports and dependencies
- Additional validation logic
- Custom business methods
- Error handling extensions
- Integration-specific code

## Performance and Scalability

The generated use cases support:

- **Async Operations**: Full async/await support throughout
- **Transaction Management**: Proper transaction boundaries for data consistency
- **Caching Integration**: Redis caching for frequently accessed data
- **Event-Driven Architecture**: Domain event publishing for loose coupling
- **Monitoring**: Structured logging and metrics collection

## Best Practices

1. **Single Responsibility**: Each use case method has a clear, single purpose
2. **Dependency Injection**: All dependencies injected through constructor
3. **Transaction Boundaries**: Clearly defined transaction scopes
4. **Error Propagation**: Consistent error handling and propagation
5. **Business Rule Separation**: Business rules isolated and testable
6. **Event Publishing**: Domain events for integration and audit trails

## Troubleshooting

Common issues and solutions:

- **Configuration Validation Errors**: Check YAML syntax and required fields
- **Template Generation Failures**: Verify all placeholder variables are defined
- **Dependency Injection Issues**: Ensure all dependencies are properly registered
- **Business Rule Failures**: Check rule conditions and validation context
- **Transaction Errors**: Verify transaction boundaries and rollback handling

For detailed troubleshooting, see the test suite and BDD scenarios for examples of correct usage patterns.