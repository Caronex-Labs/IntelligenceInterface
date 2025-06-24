# Intelligence Interface

A self-evolving meta-system that serves as an intelligent orchestrator of AI capabilities, where Caronex acts as the central nervous system coordinating agents, spaces, and evolutionary processes.

## Overview

Intelligence Interface is evolving from a Go-based TUI application (originally forked from Intelligence Interface) into a revolutionary meta-system featuring:

- **Caronex Orchestration**: Central intelligence managing all system components
- **User Spaces**: Persistent desktop environments that evolve through conversation
- **Agent-Everything**: Every capability implemented as an intelligent agent
- **Bootstrap Compiler**: System self-improvement capabilities
- **Golden Repository**: Collective intelligence integration

## Prerequisites

- Go 1.24+ installed
- API keys for AI providers (optional, but recommended)

## Quick Start

### 1. Clone and Navigate
```bash
git clone [repository-url]
cd IntelligenceInterface
```

### 2. Install Dependencies
```bash
go mod download
```

### 3. Build the Application
```bash
go build -o ii
```

### 4. Run the Application
```bash
# Basic run - launches TUI interface
./ii

# Or run directly with go
go run main.go
```

## Running Options

### Debug Mode
```bash
# Run with debug logging
go run main.go -d
```

### Specific Working Directory
```bash
# Run with specific working directory
go run main.go -c /path/to/your/project
```

### Non-Interactive Mode
```bash
# Run in non-interactive mode with a prompt
go run main.go -p "your prompt here"
```

## Configuration

### API Keys Setup

For AI features to work, set up API keys as environment variables:

```bash
# Add to your ~/.bashrc, ~/.zshrc, or set before running
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
export GROQ_API_KEY="your-groq-key"
```

The system automatically selects appropriate models based on available API keys.

### Configuration Files

The application uses cascading configuration:
1. Global: `~/.ii.json`
2. Project: `./.ii.json`
3. Environment variables (highest priority)

## Features

### Terminal User Interface (TUI)
- Interactive terminal interface using Bubble Tea framework
- Multiple themes available
- Intuitive navigation and command system

### Multi-Provider AI Support
- 9+ AI providers supported (OpenAI, Anthropic, Google, etc.)
- Automatic provider selection based on available API keys
- Streaming responses for better user experience

### Agent System
- **Coder Agent**: High-capability code generation
- **Summarizer Agent**: Efficient content summarization
- **Title Agent**: Creative title generation
- **Task Agent**: Planning and task breakdown
- **Caronex Manager**: System coordination and planning (coming soon)

### Session Management
- Hierarchical sessions with parent-child relationships
- Automatic summarization when approaching context limits
- Persistent conversation history
- Cost tracking across providers

### Tool System
- File operations (view, edit, write)
- Shell execution (bash)
- Code search (grep, glob)
- LSP integration for code intelligence
- Extensible tool framework

## Testing

### Run All Tests
```bash
go test ./...
```

### Run Tests with Verbose Output
```bash
go test -v ./...
```

### Run Specific Test
```bash
go test -v ./internal/llm/prompt
```

### Test a Single Function
```bash
go test -run TestGetContextFromPaths ./internal/llm/prompt
```

## Development

### Building for Production
```bash
go build -ldflags="-s -w" -o ii
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

## Architecture

### Space-Based Meta-System Architecture
- **Caronex Core**: Central orchestrator coordinating all system components
- **User Interface Space**: TUI/CLI/API agents providing adaptive user interaction
- **Agent Management Space**: Dynamic agent spawning, coordination, and evolution
- **Data Management Space**: Session, memory, and cache agents with persistence
- **Evolution Space**: Bootstrap compiler and golden repository integration

### Key Components
- **Bubble Tea TUI**: Responsive terminal interface
- **SQLite Database**: Lightweight, embedded storage with automatic migrations
- **Model Context Protocol (MCP)**: Extensible AI tool connectivity
- **Language Server Protocol (LSP)**: Code intelligence integration

## Troubleshooting

### Build Failures
- Ensure Go 1.24+ is installed: `go version`
- Run `go mod tidy` to clean up dependencies

### Missing Configuration
- The application creates configuration files automatically
- Check `~/.ii.json` for global settings

### API Errors
- Verify API keys are set correctly in environment
- Check provider-specific error messages in debug mode

### Database Issues
- SQLite database is created automatically at first run
- Database location: `./ii.db` (configurable)

### Performance Issues
- Use debug mode (`-d`) to identify bottlenecks
- Check token usage in session management
- Monitor provider response times

## Project Structure

```
IntelligenceInterface/
├── internal/           # Core application code
│   ├── agents/        # Agent implementations
│   ├── caronex/       # Caronex orchestrator
│   ├── core/          # Core infrastructure
│   ├── spaces/        # Space management
│   ├── tools/         # Tool implementations
│   └── tui/           # Terminal UI
├── templates/         # Code generation templates
├── test/             # Test infrastructure
│   └── bdd/          # BDD test scenarios
└── .claude/          # Project memory and documentation
```

## The Vision

Intelligence Interface isn't just another productivity tool - it's an AI-powered desktop environment that evolves with you. Think of Spaces like different desktops on your Mac - each one evolved over time for the work you regularly do:

- **Knowledge Base Space**: Like your personal library that has grown to understand exactly how you research and write
- **Development Space**: Like your workshop that has accumulated all the tools and configurations you've perfected over years of coding
- **Social Space**: Like your office setup that knows your team, your communication patterns, and your collaboration preferences

You switch between spaces with simple hotkeys, and each space remembers everything about how you like to work.

## Contributing

See `.claude/` directory for comprehensive development documentation including:
- Project architecture and patterns
- BDD workflows and testing
- Technical debt tracking
- Memory coordination system

## License

[License information to be added]

## Acknowledgments

Originally forked from Intelligence Interface - an open-source AI coding assistant.