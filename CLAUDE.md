# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Intelligence Interface codebase, originally forked from OpenCode. It's evolving from a Go-based TUI application into a **self-evolving meta-system** where:
- **Caronex** serves as the central orchestrator managing the base system
- **User Spaces** are persistent desktop environments that evolve through conversation with Caronex
- **Agents** handle every capability with intelligence
- **Bootstrap Compiler** enables system self-improvement
- **Golden Repository** connects to collective intelligence

**Critical Distinction**: The TUI, agents, and tools are the BASE SYSTEM. Spaces are persistent DESKTOP ENVIRONMENTS that users build up and evolve over time, like macOS workspaces but with AI integration.

See `.claude/` directory for comprehensive meta-system documentation.

## Development Commands

### Building and Running
```bash
# Build the application
go build -o opencode

# Run with debug logging
go run main.go -d

# Run with specific working directory
go run main.go -c /path/to/project

# Run non-interactive mode
go run main.go -p "your prompt here"
```

### Testing
```bash
# Run all tests
go test ./...

# Run tests with verbose output
go test -v ./...

# Run specific test
go test -v ./internal/llm/prompt

# Test a single function
go test -run TestGetContextFromPaths ./internal/llm/prompt
```

### Database Operations
```bash
# Generate database code from SQL (requires sqlc)
sqlc generate

# Database migrations are automatically applied on startup
# Migration files are in: internal/db/migrations/
```

### Code Generation
```bash
# Go template generation (future feature)
go run templates/projects/go_backend_gorm/cmd/standardize/main.go --config user_domain.yaml
```

## Architecture Overview

### Space-Based Meta-System Architecture
- **Caronex Core**: Central orchestrator coordinating all system components
- **User Interface Space**: TUI/CLI/API agents providing adaptive user interaction
- **Agent Management Space**: Dynamic agent spawning, coordination, and evolution
- **Data Management Space**: Session, memory, and cache agents with persistence
- **Evolution Space**: Bootstrap compiler and golden repository integration

**Note**: This represents the target architecture. Current implementation follows traditional layers but is designed for space-based transformation.

### Key Architectural Patterns

**Agent-Everything System**: The `internal/llm/agent/` package is evolving toward an agent-everything architecture where every capability is an intelligent agent that can learn, evolve, and coordinate. Current agents (coder, summarizer, title, task) represent the foundation for expansion to agents handling UI, data, coordination, and evolution itself.

**Tool System**: `internal/llm/tools/` provides extensible tool integration. Tools implement `BaseTool` interface and are automatically available to AI agents. Built-in tools include file operations (view, edit, write), shell execution (bash), code search (grep, glob), and LSP diagnostics.

**Caronex-Orchestrated Architecture**: The `internal/pubsub/` broker provides the foundation for Caronex orchestration, where the central intelligence coordinates agents across spaces. Events flow through Caronex for intelligent routing, coordination decisions, and system evolution triggers.

**Configuration Cascade**: Uses Viper with multiple config sources: global (`~/.opencode.json`), project-local (`./.opencode.json`), and environment variables. The config system automatically selects default models based on available API keys.

**Session Management**: Implements hierarchical sessions with parent-child relationships, automatic summarization when approaching context limits, and persistent storage of conversation history with cost tracking.

### Meta-System Integration Points

The codebase is structured to support transformation into a self-evolving meta-system:

- **Caronex Integration**: Current services in `internal/app/` provide foundation for Caronex orchestrator
- **Space Framework**: Existing architecture can be refactored into space-based execution environments
- **Agent Evolution**: Current agent system in `internal/llm/agent/` expands to agent-everything architecture
- **Bootstrap Compiler**: Template system in `templates/` becomes foundation for system self-improvement
- **Golden Repository**: Configuration system supports collective intelligence integration

### Database Schema

SQLite with automatic migrations. Key tables:
- `sessions`: Conversation sessions with token/cost tracking
- `messages`: Individual messages with content, tool calls, and attachments  
- `files`: File change tracking for session context

Generated code in `internal/db/` uses SQLC for type-safe database operations.

## Important Files

- `documentation/ContextPrime.md`: Vision document for Intelligence Interface evolution
- `internal/app/app.go`: Main application bootstrap and service coordination
- `internal/tui/tui.go`: TUI state management and event routing
- `internal/llm/agent/agent.go`: Core agent orchestration and streaming
- `internal/config/config.go`: Multi-source configuration management
- `templates/projects/go_backend_gorm/`: Reference template system for hexagonal Go backends

## Configuration

The application uses cascading configuration:
1. Global: `~/.opencode.json` 
2. Project: `./.opencode.json`
3. Environment variables (API keys, endpoints)

API keys are automatically detected from environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.). The system selects appropriate default models based on available providers.

LSP integration requires language servers to be installed separately (e.g., `gopls` for Go).

## Development Workflow Guidance

### Meta-System Development Principles
1. **Caronex-First Design**: All components should be designed for Caronex orchestration
2. **Space-Based Thinking**: Consider how functionality fits into configurable spaces
3. **Agent-Everything**: Transform capabilities into intelligent, evolving agents
4. **Self-Evolution Ready**: Design for system self-improvement capabilities
5. **Collective Intelligence**: Plan for golden repository integration

### Current Phase Priorities
1. **Documentation**: Maintain comprehensive meta-system documentation in `.claude/`
2. **Foundation**: Preserve current functionality while preparing for transformation
3. **Architecture**: Design space-based architecture to replace traditional layers
4. **Agent Evolution**: Expand agent system toward agent-everything
5. **Bootstrap Preparation**: Prepare template system for self-improvement capabilities

### Critical Implementation Notes
- **Preserve Compatibility**: Maintain current OpenCode functionality during transformation
- **Incremental Evolution**: Transform gradually while maintaining system stability
- **Memory Integration**: Use `.claude/` documentation to guide architectural decisions
- **Test Evolution**: Implement meta-system testing approaches from `.claude/testingContext.md`
- **BDD Integration**: Apply evolutionary BDD patterns from `.claude/bddWorkflows.md`
- **Tech Debt Tracking**: Log all technical debt in `.claude/TechDebt.md` during development

### Sprint 1 Implementation Patterns

#### Migration Quality Patterns (Discovered 2025-06-15)
1. **Gradual Migration with Validation**: Migrate components incrementally, validating at each step
   - Apply systematic validation after each migration phase
   - Preserve functionality throughout transformation process
   - Use build success as immediate validation checkpoint

2. **Functionality Preservation First**: Ensure existing functionality works before optimizing new structure
   - Complete directory migration while maintaining import compatibility
   - Validate core functionality before implementing enhancements
   - Use BDD scenarios to guide preservation priorities

3. **BDD Scenario Compliance**: Use specific scenarios to guide implementation decisions
   - Write detailed Gherkin scenarios before implementation
   - Use scenarios as acceptance criteria throughout development
   - Validate scenario completion as quality gate

4. **Memory Context Integration**: Comprehensive memory file reading prevents misalignment
   - Require reading all memory files before complex implementation tasks
   - Use memory context to guide architectural decisions
   - Apply memory insights to maintain project coherence

#### Agent Coordination Quality Patterns (Discovered 2025-06-15)
1. **Comprehensive Prompt Design**: Include complete memory context and specific quality gates
   - Provide full memory file reading requirements in agent prompts
   - Include specific BDD scenarios and acceptance criteria
   - Define clear quality gates for task completion

2. **Real-time Feedback Loops**: Document discoveries and challenges during implementation
   - Log implementation insights immediately during development
   - Capture architectural discoveries for future replication
   - Document coordination challenges for prompt improvement

3. **Tech Debt Integration**: Log and track technical debt throughout development process
   - Read `.claude/TechDebt.md` before starting any development work
   - Log all shortcuts and temporary solutions immediately
   - Update tech debt status throughout implementation lifecycle

4. **Quality Gate Enforcement**: Mandatory quality checks prevent technical debt accumulation
   - Require all tests to pass before claiming task completion
   - Validate build integrity after each major change
   - Use BDD compliance as non-negotiable quality standard

### Technical Debt Management

All developers and agents working on this project must:

1. **Read TechDebt.md**: Check `.claude/TechDebt.md` before starting any work
2. **Log New Debt**: Document any quick fixes, workarounds, or shortcuts taken
3. **Update Status**: Mark tech debt as resolved when fixing issues
4. **Prioritize Quality**: Balance delivery speed with long-term code quality
5. **Regular Review**: Include tech debt assessment in code reviews and sprint planning

#### When to Log Tech Debt
- Quick fixes or temporary workarounds implemented
- Tests skipped due to time constraints
- Missing documentation for new features
- Performance issues identified but not addressed
- Architecture improvements needed but deferred