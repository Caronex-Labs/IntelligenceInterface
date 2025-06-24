# Intelligence Interface Migration Mapping

## Overview

This document provides a comprehensive mapping from the current Intelligence Interface directory structure to the new Intelligence Interface meta-system architecture, ensuring that all existing functionality is preserved while enabling the transformation to an AI-powered desktop environment.

## Current Intelligence Interface Structure Analysis

### **Root Level Components**
```
Current Structure:
├── cmd/root.go + cmd/schema/           # CLI entry points
├── internal/                          # Core business logic
├── main.go                           # Application entry point
├── scripts/                          # Build and deployment scripts
├── templates/                        # Golden repository templates
├── go.mod/go.sum                     # Go module management
└── Configuration files               # Various config and documentation
```

### **Internal Structure Inventory**

#### **Core Infrastructure (`internal/`)**
```
internal/
├── app/                              # Application bootstrap
│   ├── app.go                        # Main app coordination
│   └── lsp.go                        # LSP integration
├── config/                           # Configuration management
│   ├── config.go                     # Multi-source config
│   └── init.go                       # Config initialization
├── db/                               # Database layer
│   ├── connect.go, db.go             # Connection management
│   ├── models.go, querier.go         # Generated models
│   ├── migrations/                   # Database migrations
│   └── sql/                          # SQL queries
├── logging/                          # Logging infrastructure
├── message/                          # Message handling
├── session/                          # Session management
├── permission/                       # Permission system
├── pubsub/                           # Event system
└── version/                          # Version management
```

#### **LLM System (`internal/llm/`)**
```
internal/llm/
├── agent/                            # Agent framework
│   ├── agent.go                      # Core agent logic
│   ├── agent-tool.go                 # Tool integration
│   ├── mcp-tools.go                  # MCP integration
│   └── tools.go                      # Tool management
├── models/                           # Provider models
│   ├── anthropic.go, openai.go, etc # Provider-specific models
│   └── models.go                     # Model abstractions
├── prompt/                           # Prompt management
│   ├── coder.go, task.go, etc        # Agent-specific prompts
│   ├── caronex.go                    # Caronex prompt (newly added)
│   └── prompt.go                     # Prompt routing
├── provider/                         # Provider implementations
│   ├── anthropic.go, openai.go, etc # Provider integrations
│   └── provider.go                   # Provider abstraction
└── tools/                            # Tool implementations
    ├── bash.go, file.go, etc         # Individual tools
    ├── shell/                        # Shell utilities
    └── tools.go                      # Tool registry
```

#### **User Interface (`internal/tui/`)**
```
internal/tui/
├── components/                       # UI components
│   ├── chat/                         # Chat interface
│   ├── dialog/                       # Modal dialogs
│   ├── logs/                         # Log viewer
│   └── util/                         # Utilities
├── image/                            # Image handling
├── layout/                           # Layout management
├── page/                             # Page management
├── styles/                           # Styling
├── theme/                            # Theme system
└── tui.go                            # Main TUI controller
```

#### **Supporting Systems**
```
internal/
├── completions/                      # Auto-completion
├── diff/                             # Diff utilities
├── fileutil/                         # File utilities
├── format/                           # Formatting utilities
├── history/                          # History management
└── lsp/                              # Language Server Protocol
```

## Migration Mapping Matrix

### **1. Root Level Migrations**

| Current Location | New Location | Type | Notes |
|------------------|--------------|------|-------|
| `cmd/` | `cmd/` | **PRESERVE** | Keep existing structure |
| `main.go` | `main.go` | **PRESERVE** | Keep application entry point |
| `scripts/` | `scripts/` | **PRESERVE** | Keep build scripts |
| `templates/` | `templates/` | **PRESERVE** | Golden repository templates |
| `go.mod/go.sum` | `go.mod/go.sum` | **PRESERVE** | Keep module management |

### **2. Core Infrastructure Migrations**

| Current Location | New Location | Type | Notes |
|------------------|--------------|------|-------|
| `internal/app/` | `internal/services/` | **MIGRATE** | Application services |
| `internal/config/` | `internal/core/config/` | **MIGRATE** | Foundation configuration |
| `internal/logging/` | `internal/core/logging/` | **MIGRATE** | Foundation logging |
| `internal/db/` | `internal/infrastructure/database/` | **MIGRATE** | Database abstraction |
| `internal/pubsub/` | `internal/infrastructure/pubsub/` | **MIGRATE** | Event system |
| `internal/permission/` | `internal/infrastructure/permissions/` | **MIGRATE** | Security system |
| `internal/message/` | `internal/core/models/` | **MIGRATE** | Core domain models |
| `internal/session/` | `internal/services/` | **MIGRATE** | Session services |
| `internal/version/` | `internal/core/` | **MIGRATE** | Core utilities |

### **3. LLM System Transformations**

#### **Agent System Evolution**
| Current Location | New Location | Type | Notes |
|------------------|--------------|------|-------|
| `internal/llm/agent/agent.go` | `internal/agents/base/agent.go` | **MIGRATE** | Base agent framework |
| `internal/llm/agent/tools.go` | `internal/agents/base/communication.go` | **MIGRATE** | Agent-tool communication |
| `internal/llm/agent/mcp-tools.go` | `internal/tools/mcp/` | **MIGRATE** | MCP tool integration |
| `internal/llm/prompt/coder.go` | `internal/agents/builtin/coder.go` | **MIGRATE** | Built-in coder agent |
| `internal/llm/prompt/task.go` | `internal/agents/builtin/task.go` | **MIGRATE** | Built-in task agent |
| `internal/llm/prompt/title.go` | `internal/agents/builtin/title.go` | **MIGRATE** | Built-in title agent |
| `internal/llm/prompt/summarizer.go` | `internal/agents/builtin/summarizer.go` | **MIGRATE** | Built-in summarizer agent |
| `internal/llm/prompt/caronex.go` | `internal/caronex/prompts.go` | **MIGRATE** | Caronex manager prompts |
| `internal/llm/prompt/prompt.go` | `internal/agents/base/` | **MIGRATE** | Agent prompt routing |

#### **Provider System Split**
| Current Location | New Location | Type | Notes |
|------------------|--------------|------|-------|
| `internal/llm/provider/*.go` | `external/providers/` | **MIGRATE** | Provider implementations |
| `internal/llm/provider/provider.go` | `internal/infrastructure/providers/` | **MIGRATE** | Provider abstraction |
| `internal/llm/models/` | `internal/core/models/` | **MIGRATE** | Model definitions |

#### **Tool System Consolidation**
| Current Location | New Location | Type | Notes |
|------------------|--------------|------|-------|
| `internal/llm/tools/tools.go` | `internal/tools/registry.go` | **MIGRATE** | Tool registry |
| `internal/llm/tools/bash.go` | `internal/tools/builtin/shell.go` | **MIGRATE** | Shell execution |
| `internal/llm/tools/file.go` | `internal/tools/builtin/file.go` | **MIGRATE** | File operations |
| `internal/llm/tools/view.go` | `internal/tools/builtin/file.go` | **MERGE** | File viewing (merge with file ops) |
| `internal/llm/tools/write.go` | `internal/tools/builtin/file.go` | **MERGE** | File writing (merge with file ops) |
| `internal/llm/tools/edit.go` | `internal/tools/builtin/file.go` | **MERGE** | File editing (merge with file ops) |
| `internal/llm/tools/glob.go` | `internal/tools/builtin/search.go` | **MIGRATE** | Search capabilities |
| `internal/llm/tools/grep.go` | `internal/tools/builtin/search.go` | **MERGE** | Search capabilities |
| `internal/llm/tools/ls.go` | `internal/tools/builtin/file.go` | **MERGE** | File listing (merge with file ops) |
| `internal/llm/tools/diagnostics.go` | `internal/tools/builtin/diagnostic.go` | **MIGRATE** | Diagnostic tools |
| `internal/llm/tools/fetch.go` | `internal/tools/builtin/` | **MIGRATE** | Network tools |
| `internal/llm/tools/patch.go` | `internal/tools/builtin/file.go` | **MERGE** | File patching (merge with file ops) |
| `internal/llm/tools/sourcegraph.go` | `internal/tools/builtin/search.go` | **MERGE** | External search (merge with search) |
| `internal/llm/tools/shell/` | `internal/tools/builtin/shell.go` | **MERGE** | Shell utilities (merge with shell) |

### **4. User Interface Evolution**

| Current Location | New Location | Type | Notes |
|------------------|--------------|------|-------|
| `internal/tui/tui.go` | `internal/interfaces/tui/app.go` | **MIGRATE** | Main TUI controller |
| `internal/tui/components/chat/` | `internal/interfaces/tui/components/` | **MIGRATE** | Reusable chat components |
| `internal/tui/components/dialog/` | `internal/interfaces/tui/components/` | **MIGRATE** | Dialog components |
| `internal/tui/components/logs/` | `internal/interfaces/tui/components/` | **MIGRATE** | Log components |
| `internal/tui/page/` | `internal/interfaces/tui/` | **MIGRATE** | Page management |
| `internal/tui/layout/` | `internal/interfaces/tui/components/` | **MIGRATE** | Layout components |
| `internal/tui/styles/` | `internal/interfaces/tui/components/` | **MIGRATE** | Styling system |
| `internal/tui/theme/` | `internal/interfaces/tui/components/` | **MIGRATE** | Theme system |
| `internal/tui/image/` | `internal/interfaces/tui/components/` | **MIGRATE** | Image handling |
| `internal/tui/util/` | `internal/interfaces/tui/components/` | **MIGRATE** | TUI utilities |

### **5. Supporting System Migrations**

| Current Location | New Location | Type | Notes |
|------------------|--------------|------|-------|
| `internal/completions/` | `internal/interfaces/tui/components/` | **MIGRATE** | TUI completion support |
| `internal/diff/` | `internal/tools/builtin/file.go` | **MERGE** | File diff utilities |
| `internal/fileutil/` | `internal/tools/builtin/file.go` | **MERGE** | File utilities |
| `internal/format/` | `internal/interfaces/tui/components/` | **MIGRATE** | TUI formatting |
| `internal/history/` | `internal/services/` | **MIGRATE** | History services |
| `internal/lsp/` | `internal/tools/builtin/diagnostic.go` | **MIGRATE** | LSP diagnostic integration |

### **6. Net-New Components (No Current Source)**

| New Location | Type | Notes |
|--------------|------|-------|
| `internal/caronex/manager.go` | **NEW** | Central manager logic |
| `internal/caronex/coordinator.go` | **NEW** | Agent coordination |
| `internal/caronex/tools/` | **NEW** | Management tools |
| `internal/spaces/` | **NEW** | Space management system |
| `internal/bootstrap/` | **NEW** | Self-evolution system |
| `internal/agents/specialist/` | **NEW** | User-defined agents |
| `internal/interfaces/tui/caronex/` | **NEW** | Caronex UI components |
| `internal/interfaces/tui/spaces/` | **NEW** | Space-specific UI |
| `internal/interfaces/cli/` | **NEW** | CLI interface |
| `internal/tools/execution.go` | **NEW** | Tool execution framework |

## Migration Strategy

### **Phase 1: Foundation Setup (Week 1)**

#### **Directory Creation**
1. Create new directory structure
2. Set up empty directories for new components
3. Prepare migration tracking

#### **Core Infrastructure Migration**
1. **MIGRATE** `internal/config/` → `internal/core/config/`
2. **MIGRATE** `internal/logging/` → `internal/core/logging/`
3. **CREATE** `internal/core/models/` (consolidate message types)
4. **UPDATE** import statements for moved components

#### **Validation**
- Ensure application still builds
- Verify configuration loading works
- Test logging functionality

### **Phase 2: Infrastructure Layer (Week 2)**

#### **Infrastructure Migration**
1. **MIGRATE** `internal/db/` → `internal/infrastructure/database/`
2. **MIGRATE** `internal/pubsub/` → `internal/infrastructure/pubsub/`
3. **MIGRATE** `internal/permission/` → `internal/infrastructure/permissions/`
4. **SPLIT** `internal/llm/provider/` → `external/providers/` + `internal/infrastructure/providers/`

#### **Service Layer Setup**
1. **MIGRATE** `internal/app/` → `internal/services/`
2. **MIGRATE** `internal/session/` → `internal/services/`
3. **MIGRATE** `internal/history/` → `internal/services/`

#### **Validation**
- Database operations functional
- Event system working
- Provider abstraction intact

### **Phase 3: Tool System Migration (Week 3)**

#### **Tool Consolidation**
1. **CREATE** `internal/tools/registry.go` from `internal/llm/tools/tools.go`
2. **CREATE** `internal/tools/execution.go` (new framework)
3. **CONSOLIDATE** file operations:
   - `file.go`, `view.go`, `write.go`, `edit.go`, `ls.go`, `patch.go` → `builtin/file.go`
4. **CONSOLIDATE** search operations:
   - `glob.go`, `grep.go`, `sourcegraph.go` → `builtin/search.go`
5. **MIGRATE** `bash.go` + `shell/` → `builtin/shell.go`
6. **MIGRATE** `diagnostics.go` → `builtin/diagnostic.go`
7. **MIGRATE** `fetch.go` → `builtin/network.go`

#### **MCP Integration**
1. **MIGRATE** `internal/llm/tools/mcp-tools.go` → `internal/tools/mcp/`
2. **ENHANCE** MCP tool registration and discovery

#### **Validation**
- All existing tools functional
- Tool registry working
- MCP integration intact

### **Phase 4: Agent System Evolution (Week 4)**

#### **Base Agent Framework**
1. **MIGRATE** `internal/llm/agent/agent.go` → `internal/agents/base/agent.go`
2. **CREATE** `internal/agents/base/lifecycle.go` (enhanced agent lifecycle)
3. **CREATE** `internal/agents/base/communication.go` (agent coordination)

#### **Built-in Agents**
1. **TRANSFORM** `internal/llm/prompt/coder.go` → `internal/agents/builtin/coder.go`
2. **TRANSFORM** `internal/llm/prompt/task.go` → `internal/agents/builtin/task.go`
3. **TRANSFORM** `internal/llm/prompt/title.go` → `internal/agents/builtin/title.go`
4. **TRANSFORM** `internal/llm/prompt/summarizer.go` → `internal/agents/builtin/summarizer.go`

#### **Specialist Framework**
1. **CREATE** `internal/agents/specialist/specialist.go` (user-defined agents)
2. **UPDATE** configuration system for specialist agents

#### **Validation**
- All existing agents functional
- Agent communication working
- Specialist framework ready

### **Phase 5: Caronex Manager Implementation (Week 5)**

#### **Caronex Core**
1. **CREATE** `internal/caronex/manager.go` (central manager logic)
2. **CREATE** `internal/caronex/coordinator.go` (agent coordination)
3. **MIGRATE** `internal/llm/prompt/caronex.go` → `internal/caronex/prompts.go`
4. **CREATE** `internal/caronex/tools/` (management tools)

#### **Agent Integration**
1. **UPDATE** agent system to support Caronex coordination
2. **IMPLEMENT** manager vs implementer distinction
3. **ADD** Caronex to agent configuration system

#### **Validation**
- Caronex manager functional
- Agent coordination working
- Manager/implementer separation clear

### **Phase 6: Interface Layer Migration (Week 6)**

#### **TUI Migration**
1. **MIGRATE** `internal/tui/` → `internal/interfaces/tui/`
2. **RESTRUCTURE** components for reusability
3. **CREATE** `internal/interfaces/tui/caronex/` (Caronex-specific UI)
4. **CREATE** `internal/interfaces/tui/spaces/` (space UI foundation)

#### **CLI Interface**
1. **CREATE** `internal/interfaces/cli/` (new CLI interface)
2. **MIGRATE** CLI logic from `cmd/` where appropriate
3. **ADD** Caronex CLI integration

#### **Validation**
- TUI functionality preserved
- Caronex UI integration working
- CLI interface functional

### **Phase 7: Space Management Foundation (Week 7)**

#### **Space System**
1. **CREATE** `internal/spaces/manager.go` (space lifecycle)
2. **CREATE** `internal/spaces/config.go` (space configuration)
3. **CREATE** `internal/spaces/persistence.go` (space state)
4. **CREATE** `internal/spaces/ui/` (UI configuration framework)

#### **Configuration Integration**
1. **EXTEND** configuration system for spaces
2. **ADD** space-to-agent mapping
3. **IMPLEMENT** space switching logic

#### **Validation**
- Space management framework functional
- Configuration system extended
- Foundation ready for space implementation

### **Phase 8: Bootstrap Compiler Foundation (Week 8)**

#### **Self-Evolution Framework**
1. **CREATE** `internal/bootstrap/compiler.go` (code generation core)
2. **CREATE** `internal/bootstrap/templates.go` (template system)
3. **CREATE** `internal/bootstrap/evolution.go` (system evolution)
4. **CREATE** `internal/bootstrap/golden/` (repository integration)

#### **Template Integration**
1. **ENHANCE** existing `templates/` directory integration
2. **ADD** bootstrap compiler template support
3. **IMPLEMENT** self-improvement foundation

#### **Validation**
- Bootstrap framework functional
- Template system integrated
- Self-evolution foundation ready

### **Phase 9: Integration & Testing (Week 9)**

#### **End-to-End Integration**
1. **INTEGRATE** all migrated components
2. **VALIDATE** complete system functionality
3. **TEST** Caronex coordination with all agents
4. **VERIFY** space management integration

#### **Performance & Optimization**
1. **OPTIMIZE** import statements and dependencies
2. **CLEANUP** temporary migration artifacts
3. **VALIDATE** performance metrics

#### **Validation**
- Complete system functional
- All migration goals achieved
- Performance acceptable

### **Phase 10: Documentation & Cleanup (Week 10)**

#### **Documentation Updates**
1. **UPDATE** all code documentation
2. **COMPLETE** migration documentation
3. **CREATE** developer onboarding guides
4. **UPDATE** user documentation

#### **Final Cleanup**
1. **REMOVE** old directory structure remnants
2. **CLEANUP** temporary migration code
3. **VALIDATE** clean repository state

#### **Validation**
- Documentation complete and accurate
- Repository clean and organized
- Migration fully complete

## Dependency Management

### **Critical Dependencies**

1. **Configuration System**: Must be migrated first (all components depend on it)
2. **Logging System**: Must be migrated early (debugging migration issues)
3. **Database Layer**: Required for session and message management
4. **Provider System**: Required for agent functionality
5. **Tool System**: Required before agent migration
6. **Agent System**: Required before Caronex implementation

### **Import Statement Updates**

Each migration phase will require systematic import statement updates:

```go
// Example transformation
// Before:
import "github.com/ii-ai/ii/internal/llm/agent"

// After:
import "github.com/ii-ai/ii/internal/agents/base"
```

### **Configuration Migration**

Configuration files will need updates to reflect new structure:

```json
// Before:
{
  "agents": {
    "coder": { "model": "claude-3.7-sonnet" }
  }
}

// After:
{
  "agents": {
    "builtin": {
      "coder": { "model": "claude-3.7-sonnet" }
    },
    "caronex": { "model": "claude-3.7-sonnet" },
    "specialist": {}
  },
  "spaces": {}
}
```

## Risk Mitigation

### **Rollback Strategy**

Each phase includes:
1. **Git branching**: Separate branch for each migration phase
2. **Validation checkpoints**: Functional testing at each step
3. **Rollback procedures**: Clear steps to revert if issues arise

### **Testing Strategy**

1. **Unit Tests**: Preserve and update existing unit tests
2. **Integration Tests**: Validate component interactions
3. **Functional Tests**: Ensure user-facing functionality preserved
4. **Performance Tests**: Verify no performance degradation

### **Communication Plan**

1. **Documentation Updates**: Keep documentation current throughout migration
2. **Developer Notifications**: Clear communication of changes and timelines
3. **User Impact**: Minimize user-facing changes during migration

## Success Metrics

### **Completion Criteria**

1. **Functionality Preservation**: 100% of existing Intelligence Interface functionality working
2. **New Capabilities**: Caronex manager operational
3. **Architecture Compliance**: All components in correct new locations
4. **Performance**: No significant performance degradation
5. **Documentation**: Complete and accurate documentation
6. **Testing**: All tests passing in new structure

### **Quality Gates**

- Each phase must pass all validation criteria before proceeding
- No functionality may be lost during migration
- All new components must have proper documentation
- Performance metrics must be maintained or improved

This migration mapping ensures a systematic, safe transformation from Intelligence Interface to Intelligence Interface while preserving all existing functionality and enabling the powerful meta-system capabilities of the new architecture.