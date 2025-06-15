# Intelligence Interface Meta-System Directory Structure

## Overview

This directory structure supports the Intelligence Interface meta-system architecture where:
- **Caronex** serves as the central manager and coordinator
- **Agents** handle every capability with intelligence (agent-everything philosophy)
- **Spaces** provide persistent desktop environments that evolve over time
- **Bootstrap Compiler** enables system self-improvement
- **Golden Repository** connects to collective intelligence

## Directory Structure

```shell
root/
├── (Go files, .env, README.md, scripts, templates, docs, git files)
├── cmd/
│   ├── tui/
│   │   └── main.go          # TUI entry point
│   └── cli/
│       └── main.go          # CLI entry point
├── external/
│   ├── database/
│   │   ├── connection.go
│   │   └── db.go
│   └── providers/           # LLM provider implementations
│       ├── openai.go
│       ├── anthropic.go
│       ├── google.go
│       ├── openrouter.go
│       ├── ollama.go
│       └── custom.go
├── sprints/                 # Sprint planning and execution
│   ├── README.md
│   ├── Sprint1.md
│   └── templates/
└── internal/
    ├── core/                # Foundation layer
    │   ├── config/
    │   │   ├── config.go
    │   │   ├── space.go     # Space configuration types
    │   │   └── agent.go     # Agent configuration types
    │   ├── models/          # Core domain models
    │   │   ├── system.go
    │   │   ├── space.go
    │   │   └── agent.go
    │   └── logging/
    │       └── logger.go
    ├── caronex/             # Central manager system
    │   ├── manager.go       # Core Caronex manager logic
    │   ├── coordinator.go   # Agent and space coordination
    │   ├── prompts.go       # Caronex-specific prompts
    │   └── tools/           # Management-specific tools
    │       ├── system.go
    │       ├── spaces.go
    │       └── config.go
    ├── agents/              # Agent-everything system
    │   ├── base/            # Base agent framework
    │   │   ├── agent.go
    │   │   ├── lifecycle.go
    │   │   └── communication.go
    │   ├── builtin/         # Built-in system agents
    │   │   ├── coder.go
    │   │   ├── summarizer.go
    │   │   ├── task.go
    │   │   └── title.go
    │   └── specialist/      # User-defined specialist agents
    │       └── specialist.go
    ├── spaces/              # Space management system
    │   ├── manager.go       # Space lifecycle management
    │   ├── config.go        # Space configuration system
    │   ├── persistence.go   # Space state persistence
    │   └── ui/              # Space UI configuration
    │       ├── layout.go
    │       ├── cards.go
    │       └── components.go
    ├── tools/               # Extensible tool system
    │   ├── registry.go      # Tool discovery and registration
    │   ├── execution.go     # Tool execution framework
    │   ├── builtin/         # Built-in tools
    │   │   ├── file.go
    │   │   ├── shell.go
    │   │   ├── search.go
    │   │   └── diagnostic.go
    │   └── mcp/             # MCP tool integration
    │       ├── client.go
    │       ├── server.go
    │       └── protocol.go
    ├── bootstrap/           # Self-evolution system
    │   ├── compiler.go      # Bootstrap compiler core
    │   ├── templates.go     # Code generation templates
    │   ├── evolution.go     # System evolution logic
    │   └── golden/          # Golden repository integration
    │       ├── sync.go
    │       └── patterns.go
    ├── interfaces/          # User interface layer
    │   ├── tui/             # Terminal interface
    │   │   ├── app.go
    │   │   ├── caronex/     # Caronex manager UI
    │   │   ├── spaces/      # Space-specific UI
    │   │   └── components/  # Reusable UI components
    │   └── cli/             # Command line interface
    │       ├── commands.go
    │       └── caronex.go
    ├── services/            # Business logic layer
    │   ├── system.go        # System-wide services
    │   ├── coordination.go  # Agent coordination services
    │   ├── persistence.go   # Data persistence services
    │   └── events.go        # Event management
    └── infrastructure/      # Infrastructure layer
        ├── database/        # Database abstraction
        ├── pubsub/         # Event system
        ├── providers/       # Provider abstraction
        └── permissions/     # Security and permissions
```

## Directory Responsibilities

### **Root Level Components**

**Go Files**: Main application bootstrap files, build configuration, and top-level package management.

**Environment Configuration**:
- `.env` - Local environment variables for development
- `env.example` - Template showing required environment variables

**Documentation & Scripts**:
- `README.md` - Project overview and getting started guide
- `scripts/` - Build, deployment, and maintenance automation scripts

**Templates**: Golden repository templates for code generation and project scaffolding.

**Sprints**: Sprint planning and execution documentation following BDD methodology.

### **cmd/ - Application Entry Points**

**Responsibilities**: Define application entry points with minimal business logic, focusing on initialization and dependency injection.

**cmd/tui/**: Terminal User Interface entry point
- Initializes Bubble Tea framework
- Sets up TUI-specific configuration and middleware
- Handles signal processing and graceful shutdown

**cmd/cli/**: Command Line Interface entry point
- Processes command-line arguments and flags
- Executes single commands in non-interactive mode
- Provides scripting and automation capabilities

### **external/ - External Dependencies**

**Responsibilities**: Isolate third-party integrations and external service connections from core business logic.

**external/database/**: Database connection management
- Connection pooling and lifecycle management
- Database-specific configuration and health checks
- Migration execution and schema management

**external/providers/**: LLM provider implementations
- Direct API integrations for each AI provider
- Provider-specific authentication and rate limiting
- Response format normalization and error handling

### **internal/ - Core Business Logic**

**Responsibilities**: Contains all internal application logic that should not be imported by external packages.

### **internal/core/ - Foundation Layer**

**Responsibilities**: Provides fundamental services used across all application layers.

**config/**: Multi-source configuration management
- Cascading configuration from global, project, and environment sources
- Provider-specific settings and API key management
- Runtime configuration validation and defaults
- Space and agent configuration types

**models/**: Core domain models and shared types
- Business entities and value objects
- Cross-cutting concerns and shared interfaces
- Domain-specific error types and constants

**logging/**: Structured logging infrastructure
- Log level management and output formatting
- Context-aware logging with request tracing
- Performance monitoring and debug capabilities

### **internal/caronex/ - Central Manager System**

**Responsibilities**: Implements Caronex as the central orchestrator and manager for the entire Intelligence Interface system.

**manager.go**: Core Caronex manager logic
- Central coordination and decision making
- System state management and oversight
- Agent lifecycle coordination

**coordinator.go**: Agent and space coordination
- Inter-agent communication protocols
- Space-to-agent assignment management
- Task delegation and result aggregation

**prompts.go**: Caronex-specific prompts and personality
- Manager-focused prompt templates
- Coordination-specific conversation patterns
- Planning and delegation communication styles

**tools/**: Management-specific tools
- System introspection and status reporting
- Configuration management and validation
- Space management and coordination tools

### **internal/agents/ - Agent-Everything System**

**Responsibilities**: Implements the agent-everything philosophy where every capability is an intelligent agent.

**base/**: Base agent framework
- Common agent interfaces and lifecycle management
- Agent communication protocols
- Resource allocation and monitoring

**builtin/**: Built-in system agents
- Core system agents (coder, summarizer, task, title)
- Specialized implementation agents
- System maintenance and utility agents

**specialist/**: User-defined specialist agents
- Domain-specific agent configurations
- Custom agent creation and management
- Role-based capability assignment

### **internal/spaces/ - Space Management System**

**Responsibilities**: Manages persistent desktop environments that users build and evolve over time.

**manager.go**: Space lifecycle management
- Space creation, modification, and evolution
- Space state persistence and recovery
- Space-to-space communication and coordination

**config.go**: Space configuration system
- Space layout and UI configuration
- Agent assignment and tool availability
- Space-specific settings and preferences

**persistence.go**: Space state persistence
- Space configuration storage and retrieval
- Evolution history and rollback capabilities
- Cross-session state maintenance

**ui/**: Space UI configuration
- Layout definition and component management
- Card-based sidebar configuration
- Space-specific interface customization

### **internal/tools/ - Extensible Tool System**

**Responsibilities**: Provides extensible tool framework for agent capabilities.

**registry.go**: Tool discovery and registration
- Dynamic tool loading and registration
- Tool capability advertisement
- Tool dependency management

**execution.go**: Tool execution framework
- Sandboxed tool execution environment
- Permission and security enforcement
- Result aggregation and error handling

**builtin/**: Built-in tools
- File operations, shell execution, search capabilities
- System diagnostic and monitoring tools
- Development and debugging utilities

**mcp/**: MCP tool integration
- Model Context Protocol implementation
- External tool server integration
- Protocol message routing and validation

### **internal/bootstrap/ - Self-Evolution System**

**Responsibilities**: Enables the system to improve and evolve itself through code generation and learning.

**compiler.go**: Bootstrap compiler core
- System self-improvement capabilities
- Code generation and modification
- Safe evolution with rollback capabilities

**templates.go**: Code generation templates
- Pattern-based code generation
- Template versioning and management
- Custom template creation and sharing

**evolution.go**: System evolution logic
- Learning from usage patterns
- Capability expansion and improvement
- Performance optimization and adaptation

**golden/**: Golden repository integration
- Pattern sharing with collective intelligence
- Best practice synchronization
- Community-driven improvement integration

### **internal/interfaces/ - User Interface Layer**

**Responsibilities**: Handles user interaction and presentation logic while remaining decoupled from business logic.

**tui/**: Terminal User Interface implementation
- Bubble Tea components and page management
- Real-time UI updates and event handling
- Session management and conversation display
- Caronex manager interface and space switching

**cli/**: Command Line Interface implementation
- Command parsing and validation
- Output formatting for different use cases
- Progress reporting and error display

### **internal/services/ - Business Services**

**Responsibilities**: Implements business logic and coordinates between different layers while maintaining clear boundaries.

**system.go**: System-wide services
- Global system state management
- Service coordination and lifecycle
- Health monitoring and diagnostics

**coordination.go**: Agent coordination services
- Agent communication facilitation
- Task distribution and load balancing
- Result aggregation and conflict resolution

**persistence.go**: Data persistence services
- Data storage abstraction and management
- Transaction coordination and consistency
- Backup and recovery operations

**events.go**: Event management
- System-wide event publication and subscription
- Event routing and filtering
- Event persistence and replay capabilities

### **internal/infrastructure/ - Infrastructure Layer**

**Responsibilities**: Provides infrastructure abstraction and system-level services.

**database/**: Database abstraction
- Repository pattern implementation
- Query optimization and caching
- Migration and schema management

**pubsub/**: Event system
- Publish-subscribe message routing
- Event persistence and reliability
- Cross-component communication

**providers/**: Provider abstraction
- LLM provider interface and management
- Provider health monitoring and failover
- Rate limiting and cost management

**permissions/**: Security and permissions
- Access control and authorization
- Security policy enforcement
- Audit logging and compliance

## Architectural Principles

### **1. Meta-System Design**
- System can modify and improve its own architecture
- Self-evolving capabilities through bootstrap compiler
- Collective intelligence integration through golden repository

### **2. Agent-Everything Philosophy**
- Every capability is implemented as an intelligent agent
- Agents can learn, evolve, and coordinate with each other
- Clear separation between manager (Caronex) and implementation agents

### **3. Space-Based Computing**
- Persistent desktop environments that evolve over time
- User-defined workspaces with AI integration
- Configuration-driven UI and functionality

### **4. Clean Architecture**
- Clear separation of concerns between layers
- Dependency inversion and interface segregation
- Testable and maintainable code organization

### **5. Extensibility**
- Plugin architecture for tools and agents
- MCP integration for external capabilities
- Template-based code generation and customization

## Migration from OpenCode

This structure represents an evolution from the original OpenCode architecture:

### **Preserved Components**
- TUI framework and user interface patterns
- Provider abstraction and multi-LLM support
- Configuration system and session management
- Tool framework and MCP integration

### **New Meta-System Components**
- Caronex central manager system
- Space management and persistent environments
- Bootstrap compiler for self-evolution
- Agent-everything architecture with specialization

### **Enhanced Architecture**
- Clear separation between base system and user spaces
- Manager vs implementer agent distinction
- Foundation for AI-powered desktop environments
- Self-improving system capabilities

This directory structure supports the transformation from a traditional AI coding assistant into a true AI-powered operating system replacement.