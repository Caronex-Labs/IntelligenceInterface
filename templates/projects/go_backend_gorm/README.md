# Go Hexagonal Architecture Template

A golden template for Go backend applications implementing the hexagonal architecture pattern (also known as ports and adapters) with PostgreSQL as the database. This template serves as the foundation for the GoHex boilerplate generator system.

## Project Structure

The project follows a structured hexagonal architecture:

```
.
├── cmd/
│   ├── api/          # Application entry points
│   └── standardize/  # Code generation tool
├── internal/         # Private application code
│   ├── di/           # Dependency injection setup
│   ├── core/         # Core domain entities and interfaces
│   │   ├── entity/   # Business entities
│   │   ├── models/   # Data models
│   │   ├── errors/   # Domain-specific errors
│   │   └── types/    # Shared types and constants
│   ├── interface/    # External-facing adapters
│   │   └── http/     # HTTP server, handlers, middleware
│   ├── repository/   # Data access implementations
│   │   └── postgres/ # PostgreSQL implementations
│   ├── usecase/      # Application use cases (business logic)
│   └── utils/        # Utility packages (config, logging)
└── test/             # Test helpers and utilities
```

## Features

- Clean separation of concerns through hexagonal architecture
- PostgreSQL database integration
- Dependency injection using samber/do
- Structured logging with Zap
- RESTful API endpoints
- Environment-based configuration
- Code generation for rapid development

## Getting Started

1. Clone this repository
2. Copy `.env.example` to `.env` and update the values
3. Run `go mod download` to download dependencies
4. Run `go run cmd/api/main.go` to start the server

## GoHex Boilerplate Generator

This template is designed to work with the GoHex boilerplate generator system, which provides tools for rapidly creating and extending Go backends while maintaining architectural consistency.

### Current Capabilities

The template includes code generation tool (`engine/main.go`) that can:

- Generate domain-specific code from templates
- Create entities, models, repositories, use cases, and handlers
- Maintain proper naming conventions and code structure

### Using the Standardize Tool

```bash
# Generate all files for a domain
go run cmd/standardize/main.go --domain user all

# Generate specific components
go run cmd/standardize/main.go --domain user entity
go run cmd/standardize/main.go --domain user model
go run cmd/standardize/main.go --domain user repository
go run cmd/standardize/main.go --domain user usecase
go run cmd/standardize/main.go --domain user handler
go run cmd/standardize/main.go --domain user di
```

## GoHex Vision: Configuration-Driven Architecture

The GoHex system (under development) extends this template with a powerful configuration-driven architecture:

### Project Configuration

Projects will use a central configuration file (`gohex.yaml` or `gohex.json`) that defines:

```yaml
version: "1.0"
name: "my-service"
description: "My awesome service"
module: "github.com/myorg/myservice"
template:
  version: "1.0.0"
  source: "github.com/gohex/template"
domains:
  - name: "user"
    config: "domains/user.yaml"
  - name: "product"
    config: "domains/product.yaml"
```

### Domain Configuration

Each domain will have its own configuration file:

```yaml
# domains/user.yaml
name: "user"
entities:
  - name: "User"
    fields:
      - name: "ID"
        type: "uuid.UUID"
        tags: 'json:"id" gorm:"primaryKey"'
      - name: "Email"
        type: "string"
        tags: 'json:"email" gorm:"uniqueIndex"'
        validations:
          - "required"
          - "email"
      - name: "Password"
        type: "string"
        tags: 'json:"-" gorm:"column:password_hash"'
    relationships:
      - type: "hasMany"
        entity: "Profile"
        foreignKey: "UserID"
```

### Code Preservation

The GoHex system will use special markers to preserve user code during regeneration:

```go
// @gohex:begin:custom
func (u *User) ValidatePassword(password string) bool {
    // Custom user code here
    return bcrypt.CompareHashAndPassword([]byte(u.Password), []byte(password)) == nil
}
// @gohex:end:custom
```

When templates are updated or configurations change, the system will:
1. Extract user code from marked regions
2. Regenerate code from templates
3. Re-insert preserved user code into the appropriate regions

### Regeneration Process

The regeneration process will:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Parse Config   │────▶│ Extract User    │────▶│ Generate New    │
│  Files          │     │ Code Regions    │     │ Code            │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐     ┌────────▼────────┐
│  Update         │◀────│ Re-insert User  │◀────│ Apply Template  │
│  References     │     │ Code            │     │ Changes         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Future Extensions

The GoHex system will be extended with:

### CLI Tool

A standalone CLI tool that can:
- Initialize new projects from the template
- Add/modify domains and entities
- Generate code from configurations
- Manage database migrations
- Generate API documentation

Example usage:
```bash
# Create new project
gohex new my-project

# Add a domain
gohex domain add user

# Add an entity with fields
gohex entity add user name:string email:string

# Generate OpenAPI documentation
gohex generate openapi
```

### MCP Server

An MCP (Model Context Protocol) server that provides:
- API endpoints for all CLI functionality
- Schema inference from natural language
- Automatic relationship detection
- Code quality suggestions
- Integration with AI assistants

This will enable AI agents to:
- Generate complete backend services from descriptions
- Extend existing services with new features
- Refactor and optimize code while preserving custom logic

## Contributing

Contributions to this template and the GoHex system are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
