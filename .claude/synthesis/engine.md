# Synthesis Engine Technical Specification

## Table of Contents
1. [Configuration Architecture](#configuration-architecture)
2. [Templating Engine Mechanics](#templating-engine-mechanics)
3. [CLI Interface Design](#cli-interface-design)
4. [Flow Abstraction System](#flow-abstraction-system)
5. [Code Preservation Technology](#code-preservation-technology)
6. [Future MCP Server Design](#future-mcp-server-design)

## Configuration Architecture

### Configuration Hierarchy

The synthesis engine implements a **three-tier configuration system** that balances simplicity with comprehensive control:

```yaml
# Level 1: Minimal Configuration (~50 lines)
version: "1.0"
domain: "user"
entity:
  fields:
    - name: "Email"
      type: "string"
      unique: true
    - name: "Name"
      type: "string"

# Level 2: Standard Configuration (~400 lines)
version: "1.0"
domain: "user"
entity:
  fields: [...]
  methods: [...]
  validation: [...]
model:
  table_name: "users"
  indexes: [...]
api:
  request_types: [...]
  response_types: [...]
repository:
  custom_queries: [...]
use_case:
  business_methods: [...]
handlers:
  endpoints: [...]

# Level 3: Full Configuration (enterprise)
# Complete control over every aspect of generation
```

### Configuration Structure

#### Core Configuration Types

```yaml
# Top-level configuration
version: string           # Configuration schema version
domain: string           # Domain name (e.g., "user", "product")

# Business Logic Layer
entity:
  name: string           # Entity name (defaults to PascalCase(domain))
  fields: []Field        # Business entity fields
  methods: []Method      # Business logic methods
  validation: []Rule     # Validation rules

# Database Layer  
model:
  table_name: string     # Database table name
  fields: []Field        # Database-specific fields
  indexes: []Index       # Database indexes
  relationships: []Rel   # Entity relationships

# API Layer
api:
  request_types: []Type  # HTTP request structures
  response_types: []Type # HTTP response structures
  
# Data Access Layer
repository:
  interface_name: string # Repository interface name
  custom_queries: []Query # Custom database queries
  
# Business Logic Layer
use_case:
  interface_name: string # UseCase interface name
  methods: []Method     # Business logic methods

# HTTP Interface Layer
handlers:
  endpoints: []Endpoint # HTTP API endpoints
  middleware: []string  # Applied middleware
```

#### Field Configuration

```yaml
fields:
  - name: string         # Field name
    type: string         # Go type (string, int, bool, time.Time, etc.)
    gorm_tags: string    # GORM database tags
    json_tags: string    # JSON serialization tags
    validation: string   # Validation rules
    unique: bool         # Unique constraint
    required: bool       # Required field
    default_value: any   # Default value
```

### Smart Defaults System

The engine applies **intelligent defaults** to minimize configuration complexity:

#### Automatic Field Generation
```yaml
# Minimal config:
domain: "user"
entity:
  fields:
    - name: "Email"
      type: "string"

# Automatically generates:
# - ID field (UUID primary key)
# - CreatedAt field (timestamp)
# - UpdatedAt field (timestamp)
# - DeletedAt field (soft delete)
```

#### Convention-Based Naming
- **Entity**: `User` (PascalCase of domain)
- **Model**: `UserModel` 
- **Repository**: `UserRepository` + `UserRepositoryImpl`
- **UseCase**: `UserUseCase` + `UserUseCaseImpl`
- **Handler**: `UserHandler`
- **Table**: `users` (snake_case plural)

#### Standard CRUD Operations
Every entity automatically receives:
- `Create(entity)` - Create new record
- `GetByID(id)` - Retrieve by primary key
- `GetAll()` - List all records
- `Update(entity)` - Update existing record
- `Delete(id)` - Soft delete record

### Configuration Validation

The engine performs comprehensive validation:

```go
type ConfigProcessor struct {
    validationRules map[string][]ValidationRule
}

// Validation checks:
// - Required fields present
// - Valid Go types specified
// - Consistent naming conventions
// - Valid GORM tags
// - Proper relationship definitions
// - Security rule compliance
```

## Templating Engine Mechanics

### Template Technology Stack

**Core Engine**: Go `text/template` with custom function library

**Custom Template Functions**:
```go
template.FuncMap{
    "toSnakeCase":  stringutil.ToSnakeCase,
    "toPascalCase": stringutil.ToPascalCase,
    "toCamelCase":  stringutil.ToCamelCase,
    "pluralize":    stringutil.Pluralize,
    "lower":        strings.ToLower,
    "upper":        strings.ToUpper,
    "printf":       fmt.Sprintf,
    "default":      templateutil.Default,
}
```

### Template Processing Pipeline

#### 1. Configuration Loading
```go
func (cp *ConfigProcessor) LoadConfig(configPath string) (*Config, error) {
    // Read YAML file
    data, err := os.ReadFile(configPath)
    
    // Parse YAML into Config struct
    var config Config
    err = yaml.Unmarshal(data, &config)
    
    // Apply defaults
    cp.applyDefaults(&config)
    
    // Validate configuration
    return &config, cp.validate(&config)
}
```

#### 2. Template Data Transformation
```go
type TemplateData struct {
    // Legacy compatibility
    Domain string
    Entity string
    
    // Configuration-driven
    EntityConfig    EntityConfig
    ModelConfig     ModelConfig
    RepositoryConfig RepositoryConfig
    UseCaseConfig   UseCaseConfig
    HandlerConfig   HandlerConfig
    
    // Computed values
    DomainSnake     string // user
    DomainPascal    string // User
    DomainPlural    string // users
    TableName       string // users
}
```

#### 3. Template Execution
```go
func (g *Generator) ExecuteTemplate(templatePath string, data TemplateData) ([]byte, error) {
    // Load template file
    tmpl, err := template.New("").Funcs(g.funcMap).ParseFiles(templatePath)
    
    // Execute template with data
    var buf bytes.Buffer
    err = tmpl.Execute(&buf, data)
    
    return buf.Bytes(), err
}
```

### Template Organization

#### Directory Structure
```
templates/
├── entity/
│   ├── entity.go.tmpl           # Business entity
│   └── entity_config.go.tmpl    # Configuration-driven entity
├── model/
│   └── model.go.tmpl            # Database model
├── repository/
│   ├── repository.go.tmpl       # Repository interface
│   └── repositories.go.tmpl     # Repository implementation
├── usecase/
│   ├── usecase.go.tmpl          # UseCase interface
│   └── usecases.go.tmpl         # UseCase implementation
└── handler/
    └── handler.go.tmpl          # HTTP handlers
```

#### Template Examples

**Entity Template (`entity.go.tmpl`)**:
```go
package {{.DomainSnake}}

import (
    "time"
{{- if .EntityConfig.HasValidation}}
    "github.com/go-playground/validator/v10"
{{- end}}
)

type {{.DomainPascal}} struct {
{{- range .EntityConfig.Fields}}
    {{.Name}} {{.Type}} `json:"{{.JsonTag}}"{{if .Validation}} validate:"{{.Validation}}"{{end}}`
{{- end}}
}

{{- range .EntityConfig.Methods}}
func ({{lower $.DomainPascal}} *{{$.DomainPascal}}) {{.Name}}({{.Parameters}}) {{.ReturnType}} {
    {{/* @gohex:begin:custom:{{.Name}} */}}
    // TODO: Implement {{.Name}}
    {{.DefaultImplementation}}
    {{/* @gohex:end:custom:{{.Name}} */}}
}
{{- end}}
```

**Repository Template (`repository.go.tmpl`)**:
```go
package {{.DomainSnake}}

import (
    "context"
    "{{.ModulePath}}/internal/core/entity/{{.DomainSnake}}"
)

type {{.DomainPascal}}Repository interface {
    Create(ctx context.Context, {{.DomainSnake}} *{{.DomainSnake}}.{{.DomainPascal}}) error
    GetByID(ctx context.Context, id string) (*{{.DomainSnake}}.{{.DomainPascal}}, error)
    Update(ctx context.Context, {{.DomainSnake}} *{{.DomainSnake}}.{{.DomainPascal}}) error
    Delete(ctx context.Context, id string) error
{{- range .RepositoryConfig.CustomQueries}}
    {{.Name}}(ctx context.Context{{if .Parameters}}, {{.Parameters}}{{end}}) {{.ReturnType}}
{{- end}}
}
```

### Code Generation Workflow

#### Complete Generation Process
```go
func (g *Generator) GenerateAll(config *Config) error {
    // 1. Prepare template data
    data := g.prepareTemplateData(config)
    
    // 2. Generate entity layer
    g.generateEntity(data)
    
    // 3. Generate model layer
    g.generateModel(data)
    
    // 4. Generate repository layer
    g.generateRepository(data)
    
    // 5. Generate usecase layer
    g.generateUseCase(data)
    
    // 6. Generate handler layer
    g.generateHandler(data)
    
    // 7. Generate dependency injection
    g.generateDI(data)
    
    // 8. Update project files
    g.updateGoMod(data)
    g.updateMain(data)
    
    return nil
}
```

## CLI Interface Design

### Command Structure

The synthesis engine provides a **dual-mode CLI interface**:

#### Configuration-Driven Mode (Recommended)
```bash
# Generate complete system from config
standardize --config user_domain.yaml

# Generate specific components
standardize --config user_domain.yaml --component entity
standardize --config user_domain.yaml --component repository
```

#### Legacy Command-Line Mode
```bash
# Generate all components
standardize --domain user --name User all

# Generate specific components
standardize --domain user --name User entity
standardize --domain user --name User repository usecase handler
```

### Available Commands

#### Component Generation
- `entity` - Generate business entity
- `model` - Generate database model
- `repository` - Generate data access layer
- `usecase` - Generate business logic layer
- `handler` - Generate HTTP API layer
- `di` - Generate dependency injection
- `all` - Generate complete system

#### Utility Commands
- `--validate` - Validate configuration without generation
- `--dry-run` - Show what would be generated
- `--help` - Display usage information
- `--version` - Show version information

### CLI Implementation

```go
type CommandHandler struct {
    configProcessor *ConfigProcessor
    generator       *Generator
}

func (ch *CommandHandler) HandleCommand(args []string) error {
    // Parse command line arguments
    cmd := ch.parseArgs(args)
    
    switch cmd.Mode {
    case "config":
        return ch.handleConfigMode(cmd)
    case "legacy":
        return ch.handleLegacyMode(cmd)
    default:
        return ch.showUsage()
    }
}

func (ch *CommandHandler) handleConfigMode(cmd *Command) error {
    // Load configuration
    config, err := ch.configProcessor.LoadConfig(cmd.ConfigPath)
    if err != nil {
        return err
    }
    
    // Generate components
    return ch.generator.Generate(config, cmd.Components)
}
```

### Developer Workflow Integration

#### Initial Setup
```bash
# Create new domain
standardize --config minimal_user.yaml

# This generates:
# - Complete hexagonal architecture
# - Working CRUD operations
# - Database migrations
# - API endpoints
# - Dependency injection
# - Basic tests
```

#### Iterative Development
```bash
# Add new fields to existing domain
# Edit user_domain.yaml, add fields
standardize --config user_domain.yaml

# Custom code is preserved
# New fields are added to all layers
# Existing customizations remain intact
```

## Flow Abstraction System

### Flow Definition

A **"flow"** represents a complete business capability that spans all architectural layers. In the context of a Go backend, a flow consists of:

- **Entity** - Business logic representation
- **Model** - Database persistence layer
- **Repository** - Data access interface and implementation  
- **UseCase** - Business logic orchestration
- **Handler** - HTTP API endpoints
- **DI** - Dependency injection wiring

### Flow Coordination

#### Type-Safe Layer Integration
```go
// Generated flow maintains type safety across layers:

// 1. Entity (Business Logic)
type User struct {
    ID    string `json:"id"`
    Email string `json:"email" validate:"required,email"`
    Name  string `json:"name" validate:"required"`
}

// 2. Model (Database)
type UserModel struct {
    ID        string    `gorm:"primaryKey;type:uuid"`
    Email     string    `gorm:"uniqueIndex;not null"`
    Name      string    `gorm:"not null"`
    CreatedAt time.Time `gorm:"autoCreateTime"`
    UpdatedAt time.Time `gorm:"autoUpdateTime"`
}

// 3. Repository (Data Access)
type UserRepository interface {
    Create(ctx context.Context, user *entity.User) error
    GetByEmail(ctx context.Context, email string) (*entity.User, error)
}

// 4. UseCase (Business Logic)
type UserUseCase interface {
    RegisterUser(ctx context.Context, req *RegisterUserRequest) error
    AuthenticateUser(ctx context.Context, email, password string) (*entity.User, error)
}

// 5. Handler (HTTP API)
type UserHandler struct {
    userUC UserUseCase
}
```

#### Automatic Interface Contracts
The synthesis engine ensures **interface consistency** across layers:

```yaml
# Configuration drives interface generation
use_case:
  methods:
    - name: "RegisterUser"
      parameters: "ctx context.Context, req *RegisterUserRequest"
      return_type: "error"
      
repository:
  custom_queries:
    - name: "GetByEmail" 
      parameters: "email string"
      return_type: "*entity.User, error"
```

### Flow Generation Process

#### 1. Configuration Analysis
```go
func (g *Generator) analyzeFlow(config *Config) *FlowDefinition {
    flow := &FlowDefinition{
        Domain: config.Domain,
        Layers: make(map[string]*LayerDefinition),
    }
    
    // Analyze entity requirements
    flow.Layers["entity"] = g.analyzeEntityLayer(config.Entity)
    
    // Analyze repository requirements  
    flow.Layers["repository"] = g.analyzeRepositoryLayer(config.Repository)
    
    // Analyze usecase requirements
    flow.Layers["usecase"] = g.analyzeUseCaseLayer(config.UseCase)
    
    return flow
}
```

#### 2. Cross-Layer Dependency Resolution
```go
func (g *Generator) resolveDependencies(flow *FlowDefinition) error {
    // Ensure entity types are available to repository
    g.linkEntityToRepository(flow)
    
    // Ensure repository interfaces are available to usecase
    g.linkRepositoryToUseCase(flow)
    
    // Ensure usecase interfaces are available to handler
    g.linkUseCaseToHandler(flow)
    
    return nil
}
```

#### 3. Coordinated Code Generation
```go
func (g *Generator) generateFlow(flow *FlowDefinition) error {
    // Generate in dependency order
    layers := []string{"entity", "model", "repository", "usecase", "handler", "di"}
    
    for _, layer := range layers {
        if err := g.generateLayer(flow, layer); err != nil {
            return err
        }
    }
    
    return nil
}
```

### Flow Abstractions

#### Endpoint Groups
```yaml
handlers:
  endpoint_groups:
    - name: "user_management"
      base_path: "/api/v1/users"
      endpoints:
        - method: "POST"
          path: ""
          handler: "CreateUser"
          middleware: ["auth", "validation"]
        - method: "GET"
          path: "/{id}"
          handler: "GetUser"
        - method: "PUT"
          path: "/{id}"
          handler: "UpdateUser"
          middleware: ["auth", "validation"]
```

#### Business Logic Flows
```yaml
use_case:
  business_flows:
    - name: "user_registration"
      steps:
        - validate_input
        - check_email_unique
        - hash_password
        - create_user
        - send_welcome_email
      error_handling: "rollback"
      
    - name: "user_authentication"
      steps:
        - validate_credentials
        - check_user_exists
        - verify_password
        - generate_jwt
      error_handling: "log_and_return"
```

#### Repository Patterns
```yaml
repository:
  patterns:
    - name: "audit_trail"
      fields: ["created_at", "updated_at", "created_by", "updated_by"]
      
    - name: "soft_delete"
      fields: ["deleted_at"]
      methods: ["SoftDelete", "Restore", "FindActive"]
      
    - name: "pagination"
      methods: ["FindWithPagination", "Count"]
```

## Code Preservation Technology

### Preservation Mechanisms

#### Custom Code Markers
The synthesis engine uses **special comment markers** to protect custom code during regeneration:

```go
func (u *UserUseCaseImpl) RegisterUser(ctx context.Context, req *RegisterUserRequest) error {
    {{/* @gohex:begin:custom:register-user-validation */}}
    // Custom validation logic - preserved across regenerations
    if err := u.validateBusinessRules(req); err != nil {
        return err
    }
    {{/* @gohex:end:custom:register-user-validation */}}
    
    // Generated code - will be updated during regeneration
    user := &entity.User{
        Email: req.Email,
        Name:  req.Name,
    }
    
    return u.userRepo.Create(ctx, user)
}
```

#### hex.yaml Generation Metadata
Each generated component includes a `hex.yaml` file that tracks:

```yaml
# hex.yaml
generation:
  version: "1.0"
  timestamp: "2024-01-15T10:30:00Z"
  config_hash: "sha256:abc123..."
  template_version: "v1.2.3"

preservation:
  custom_regions:
    - id: "register-user-validation"
      start_line: 15
      end_line: 19
      last_modified: "2024-01-10T14:20:00Z"
    
    - id: "custom-business-logic"
      start_line: 45
      end_line: 67
      last_modified: "2024-01-12T09:15:00Z"

templates:
  used:
    - "usecase/usecase.go.tmpl"
    - "usecase/usecases.go.tmpl"
  
configuration:
  domain: "user"
  entity_fields: ["ID", "Email", "Name"]
  custom_methods: ["RegisterUser", "AuthenticateUser"]
```

### Safe Regeneration Process

#### 1. Pre-Generation Analysis
```go
func (g *Generator) analyzeExistingCode(targetPath string) (*PreservationMap, error) {
    // Read existing file
    content, err := os.ReadFile(targetPath)
    
    // Parse custom code regions
    regions := g.parseCustomRegions(content)
    
    // Read generation metadata
    metadata := g.readHexYaml(targetPath)
    
    return &PreservationMap{
        CustomRegions: regions,
        Metadata:      metadata,
    }, nil
}
```

#### 2. Smart Merging
```go
func (g *Generator) mergeWithExisting(newContent []byte, preservation *PreservationMap) ([]byte, error) {
    // Parse new generated content
    newAST := g.parseGoCode(newContent)
    
    // Insert preserved custom regions
    for _, region := range preservation.CustomRegions {
        g.insertCustomRegion(newAST, region)
    }
    
    // Format the merged code
    return g.formatGoCode(newAST)
}
```

#### 3. Conflict Resolution
```go
func (g *Generator) resolveConflicts(conflicts []Conflict) error {
    for _, conflict := range conflicts {
        switch conflict.Type {
        case "signature_change":
            // Method signature changed - preserve body but update signature
            g.updateMethodSignature(conflict)
            
        case "new_field":
            // New field added - add to struct, update custom code if needed
            g.addFieldToStruct(conflict)
            
        case "removed_method":
            // Method removed from config - ask user what to do
            g.promptUserForResolution(conflict)
        }
    }
    
    return nil
}
```

### Preservation Best Practices

#### Custom Code Organization
```go
// Good: Focused custom regions
func (u *UserUseCaseImpl) RegisterUser(ctx context.Context, req *RegisterUserRequest) error {
    {{/* @gohex:begin:custom:input-validation */}}
    if err := u.customValidation(req); err != nil {
        return err
    }
    {{/* @gohex:end:custom:input-validation */}}
    
    // Generated code here
    
    {{/* @gohex:begin:custom:post-creation-hooks */}}
    if err := u.notifyExternalSystems(user); err != nil {
        log.Warn("Failed to notify external systems: %v", err)
    }
    {{/* @gohex:end:custom:post-creation-hooks */}}
    
    return nil
}
```

#### Configuration Evolution
```yaml
# Version 1.0 config
entity:
  fields:
    - name: "Email"
      type: "string"

# Version 1.1 config - adds field
entity:
  fields:
    - name: "Email"
      type: "string"
    - name: "Phone"    # New field
      type: "string"
      
# Custom code in methods is preserved
# New field is added to all layers automatically
```

## Future MCP Server Design

### MCP Server Architecture

The synthesis engine could expose **Model Context Protocol (MCP) server capabilities** to enable AI agent integration:

#### Server Interface
```go
type SynthesisServer struct {
    configProcessor *ConfigProcessor
    generator       *Generator
    templateManager *TemplateManager
}

func (s *SynthesisServer) HandleMCPRequest(req *mcp.Request) (*mcp.Response, error) {
    switch req.Method {
    case "synthesis/generate":
        return s.handleGenerate(req)
    case "synthesis/validate":
        return s.handleValidate(req)
    case "synthesis/preview":
        return s.handlePreview(req)
    case "synthesis/templates":
        return s.handleListTemplates(req)
    default:
        return nil, mcp.ErrMethodNotFound
    }
}
```

### MCP Tool Definitions

#### Core Synthesis Tools
```json
{
  "tools": [
    {
      "name": "synthesis_generate",
      "description": "Generate code from synthesis configuration",
      "inputSchema": {
        "type": "object",
        "properties": {
          "config": {
            "type": "string",
            "description": "YAML configuration for code generation"
          },
          "components": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific components to generate (optional)"
          },
          "dry_run": {
            "type": "boolean",
            "description": "Preview changes without writing files"
          }
        },
        "required": ["config"]
      }
    },
    
    {
      "name": "synthesis_validate",
      "description": "Validate synthesis configuration",
      "inputSchema": {
        "type": "object",
        "properties": {
          "config": {
            "type": "string",
            "description": "YAML configuration to validate"
          }
        },
        "required": ["config"]
      }
    },
    
    {
      "name": "synthesis_preview",
      "description": "Preview generated code without writing files",
      "inputSchema": {
        "type": "object", 
        "properties": {
          "config": {
            "type": "string",
            "description": "YAML configuration"
          },
          "component": {
            "type": "string",
            "description": "Specific component to preview"
          }
        },
        "required": ["config"]
      }
    },
    
    {
      "name": "synthesis_templates",
      "description": "List available templates and their capabilities",
      "inputSchema": {
        "type": "object",
        "properties": {
          "technology": {
            "type": "string", 
            "description": "Filter by technology stack"
          },
          "pattern": {
            "type": "string",
            "description": "Filter by architectural pattern"
          }
        }
      }
    }
  ]
}
```

### AI Agent Integration Patterns

#### Configuration Generation
```typescript
// AI agent generates configuration from natural language
const aiPrompt = "Create a user management system with email authentication, profile management, and admin capabilities";

const mcpRequest = {
  method: "synthesis_generate",
  params: {
    config: await aiAgent.generateConfig(aiPrompt),
    dry_run: true
  }
};

const preview = await mcpClient.request(mcpRequest);
// AI agent reviews the preview and can iterate on the configuration
```

#### Intelligent Modification
```typescript
// AI agent modifies existing systems
const modification = {
  method: "synthesis_generate", 
  params: {
    config: await aiAgent.modifyConfig(existingConfig, "Add password reset functionality"),
    components: ["usecase", "handler"] // Only regenerate specific components
  }
};
```

#### Template Discovery
```typescript
// AI agent discovers appropriate templates
const templates = await mcpClient.request({
  method: "synthesis_templates",
  params: {
    technology: "go",
    pattern: "hexagonal"
  }
});

// AI agent selects the best template for the use case
const selectedTemplate = aiAgent.selectTemplate(templates, userRequirements);
```

### Integration with Intelligence Interface

#### Workflow Integration
```go
// Intelligence Interface integrates synthesis through MCP
type SynthesisIntegration struct {
    mcpClient *mcp.Client
}

func (si *SynthesisIntegration) HandleUserRequest(req string) error {
    // User: "Create a product catalog microservice"
    
    // 1. AI agent analyzes requirements
    requirements := si.analyzeRequirements(req)
    
    // 2. Generate appropriate configuration
    config := si.generateConfig(requirements)
    
    // 3. Call synthesis engine via MCP
    result, err := si.mcpClient.Request(&mcp.Request{
        Method: "synthesis_generate",
        Params: map[string]any{
            "config": config,
            "dry_run": false,
        },
    })
    
    // 4. Present results to user
    return si.presentResults(result)
}
```

#### Collaborative Development
```go
// Multiple AI agents collaborate on synthesis
func (si *SynthesisIntegration) CollaborativeGeneration(userStory string) error {
    // Architect agent designs system architecture
    architecture := si.architectAgent.DesignSystem(userStory)
    
    // Configuration agent creates synthesis config
    config := si.configAgent.CreateConfig(architecture)
    
    // Validation agent reviews configuration
    validation := si.validationAgent.ValidateConfig(config)
    
    // Generation agent executes synthesis
    if validation.IsValid {
        return si.synthesisAgent.Generate(config)
    }
    
    return validation.Errors
}
```

### Advanced MCP Capabilities

#### Stream-Based Generation
```go
// Support streaming responses for large codebases
func (s *SynthesisServer) handleGenerateStream(req *mcp.Request) <-chan *mcp.StreamResponse {
    responses := make(chan *mcp.StreamResponse)
    
    go func() {
        defer close(responses)
        
        // Stream generation progress
        responses <- &mcp.StreamResponse{
            Type: "progress",
            Data: map[string]any{"component": "entity", "progress": 0.2},
        }
        
        // Stream generated files
        responses <- &mcp.StreamResponse{
            Type: "file_generated",
            Data: map[string]any{
                "path": "internal/entity/user.go",
                "content": generatedContent,
            },
        }
    }()
    
    return responses
}
```

#### Template Management
```go
// Dynamic template management via MCP
func (s *SynthesisServer) handleTemplateOperations(req *mcp.Request) (*mcp.Response, error) {
    switch req.Params["operation"] {
    case "install":
        return s.installTemplate(req.Params["template_url"].(string))
    case "update":
        return s.updateTemplate(req.Params["template_name"].(string))
    case "create":
        return s.createTemplate(req.Params["template_def"])
    default:
        return nil, mcp.ErrInvalidParams
    }
}
```

This MCP server design would enable Intelligence Interface and other AI systems to seamlessly integrate with synthesis engines, providing a powerful abstraction layer for AI-driven code generation and system architecture.