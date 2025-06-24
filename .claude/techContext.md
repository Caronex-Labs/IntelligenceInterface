# Technology Context

## Core Technology Stack

### Programming Language
- **Go 1.24.0**: Modern, efficient language for building scalable applications
- **Why Go**: 
  - Excellent concurrency support for handling multiple AI providers
  - Fast compilation and small binary sizes
  - Strong standard library for building CLI/TUI applications
  - Great cross-platform support

### UI Framework
- **Bubble Tea**: Modern TUI framework for terminal applications
  - **Bubbles**: Pre-built components (text input, viewport, spinner)
  - **Lipgloss**: Terminal styling and layout
  - **Glamour**: Markdown rendering in terminal
- **Why Bubble Tea**: 
  - Elm-inspired architecture perfect for reactive UIs
  - Excellent developer experience
  - Active community and ecosystem

### Database
- **SQLite (via ncruces/go-sqlite3)**: Embedded database for local storage
  - Pure Go implementation (no CGO required)
  - WASM-based for better portability
  - Automatic migrations via Goose
- **Why SQLite**:
  - Zero configuration required
  - Excellent for local-first applications
  - Reliable and battle-tested
  - Single file storage

### Configuration Management
- **Viper**: Flexible configuration with multiple sources
- **Cobra**: CLI command and flag parsing
- **FSNotify**: File system watching for config changes

### Development Tools
- **SQLC**: Type-safe SQL code generation
- **Goose**: Database migration management
- **Testing**: Standard Go testing with testify assertions

## AI/LLM Integration

### Supported Providers
1. **OpenAI** (openai-go SDK)
   - GPT-4, GPT-4 Turbo, O1 series
   - Function calling support
   - Streaming responses

2. **Anthropic** (anthropic-sdk-go)
   - Claude 3.5 Sonnet, Claude 3 Opus
   - Advanced reasoning capabilities
   - Tool use support

3. **Google AI** (genai SDK)
   - Gemini 1.5 Pro, Flash, Thinking
   - Vertex AI integration
   - Multi-modal support

4. **AWS Bedrock**
   - Multiple model support
   - Enterprise security features
   - Regional deployment options

5. **Azure OpenAI**
   - Enterprise Azure integration
   - Custom deployments
   - Azure AD authentication

6. **Groq**
   - Ultra-fast inference
   - Open source model support
   - Cost-effective option

7. **OpenRouter**
   - Model routing and fallback
   - Unified billing
   - Access to multiple providers

8. **XAI**
   - Grok models
   - Advanced reasoning

9. **Local/Ollama**
   - Privacy-first option
   - No internet required
   - Custom model support

### Protocol Support

#### Model Context Protocol (MCP)
- **mcp-go v0.17.0**: Official Go implementation
- Server discovery and lifecycle management
- Tool and resource exposure
- Bidirectional communication

#### Language Server Protocol (LSP)
- Integration with language servers (gopls, pyright, etc.)
- Code intelligence features
- Diagnostic information
- Symbol navigation

## External Dependencies

### Markdown & HTML Processing
- **html-to-markdown**: Convert HTML content to markdown
- **PuerkitoBio/goquery**: jQuery-like HTML manipulation
- **goldmark**: Extensible markdown parser
- **chroma**: Syntax highlighting

### UI Enhancement
- **Catppuccin**: Modern color schemes
- **termenv**: Terminal capability detection
- **ansi**: ANSI escape sequence handling
- **lipgloss**: Terminal styling

### Utilities
- **UUID**: Unique identifier generation
- **go-diff**: Diff generation and display
- **doublestar**: Advanced glob matching
- **lithammer/fuzzysearch**: Fuzzy string matching

## Infrastructure Components

### File System Operations
- **fsnotify**: File system event monitoring
- **afero**: File system abstraction layer
- **doublestar**: Glob pattern matching

### Networking & HTTP
- **otelhttp**: OpenTelemetry HTTP instrumentation
- **websocket**: WebSocket support for real-time features

### Security & Authentication
- **Azure Identity**: Azure AD authentication
- **JWT**: Token validation and generation
- **crypto**: Cryptographic operations

## Testing Infrastructure

### Testing Libraries
- **testify**: Assertions and test suites
- **go-cmp**: Deep equality comparisons
- **httpsnoop**: HTTP middleware testing

### Code Quality
- **Standard Go testing**: Built-in testing framework
- **Coverage tracking**: Integrated coverage reports
- **Benchmarking**: Performance testing support

## Build & Deployment

### Build System
- **Go modules**: Dependency management
- **CGO-free**: Pure Go for easy cross-compilation
- **Embedded assets**: Templates and static files

### Supported Platforms
- **macOS**: Intel and Apple Silicon
- **Linux**: All major distributions
- **Windows**: Windows 10/11
- **FreeBSD**: Community supported

### Distribution
- **Single binary**: All assets embedded
- **No runtime dependencies**: SQLite embedded
- **Cross-compilation**: Easy multi-platform builds

## Template System (Future)

### Template Technologies
- **Go templates**: Built-in template engine
- **YAML**: Configuration format
- **Custom DSL**: Domain-specific language for templates

### Code Generation
- **AST manipulation**: Code-aware generation
- **Type safety**: Compile-time validation
- **Hot reload**: Live template updates

## Performance Optimizations

### Concurrency
- **Goroutines**: Lightweight concurrency
- **Channels**: Safe communication
- **Context**: Cancellation and timeouts
- **Worker pools**: Controlled parallelism

### Memory Management
- **Stream processing**: Handle large responses
- **Lazy loading**: Load data on demand
- **Connection pooling**: Reuse HTTP connections
- **Garbage collection tuning**: Optimized for TUI

## Monitoring & Observability

### Logging
- **Structured logging**: JSON format support
- **Log levels**: Debug, Info, Warn, Error
- **Context propagation**: Request tracing

### Metrics
- **Token tracking**: Usage per provider
- **Cost monitoring**: Real-time cost calculation
- **Performance metrics**: Response times

### Tracing
- **OpenTelemetry**: Distributed tracing support
- **Context propagation**: Cross-service tracing
- **Performance profiling**: Bottleneck identification

## Development Environment

### Required Tools
```bash
# Go 1.24+
go version

# SQLC for database code generation
go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest

# Goose for migrations
go install github.com/pressly/goose/v3/cmd/goose@latest

# Optional: Language servers for LSP
go install golang.org/x/tools/gopls@latest
```

### Environment Variables
```bash
# AI Provider Keys
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...

# Optional Configuration
OPENCODE_CONFIG_PATH=/custom/path
OPENCODE_LOG_LEVEL=debug
OPENCODE_DISABLE_TELEMETRY=true
```

### Development Commands
```bash
# Run with debugging
go run main.go -d

# Run tests
go test ./...

# Generate database code
sqlc generate

# Run migrations
goose -dir internal/db/migrations sqlite3 ./ii.db up

# Build for production
go build -ldflags="-s -w" -o ii
```

## Security Considerations

### API Key Management
- Environment variable storage
- No keys in code or config files
- Secure key rotation support

### Tool Execution
- Permission-based execution
- Sandboxed environments
- Audit logging

### Data Privacy
- Local-first architecture
- No telemetry by default
- Encrypted storage options

## Future Technology Considerations

### Planned Additions
- **WebAssembly**: Browser-based version
- **gRPC**: High-performance RPC
- **Redis**: Distributed caching
- **Kubernetes**: Container orchestration

### Research Areas
- **Vector databases**: Semantic search
- **Model fine-tuning**: Custom models
- **Edge deployment**: Local AI inference
- **Multi-modal**: Image/audio support