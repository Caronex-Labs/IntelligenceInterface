# Task 5: Basic Management Tools - Implementation Prompt

## Memory Context Requirements (MANDATORY - READ ALL BEFORE IMPLEMENTATION)

### Foundation Files (Read First):
- `.claude/projectbrief.md` - Core project mission and Intelligence Interface meta-system goals
- `.claude/productContext.md` - Problem context and solution architecture
- `.claude/systemPatterns.md` - Architecture patterns and design decisions
- `.claude/techContext.md` - Technology stack and setup requirements

### Coordination Files (Read Second):
- `.claude/activeContext.md` - Current focus and Task 4 completion status (Phase 2 complete)
- `.claude/progress.md` - Implementation status and Sprint 1 roadmap (89% complete, 8/9 tasks)
- `.claude/coordinationContext.md` - Task coordination framework
- `.claude/testingContext.md` - BDD testing integration

### Implementation Files (Read Third):
- `CLAUDE.md` - Critical implementation patterns and BDD rules (project root)
- `.claude/bddWorkflows.md` - BDD workflow patterns and templates
- `.claude/implementationLogs.md` - Task 4 insights and TUI integration learnings (outstanding quality patterns)
- `.claude/qualityFeedback.md` - Quality patterns from completed tasks
- `sprints/Sprint1.md` - Complete Sprint 1 context and task details

### Testing Standards (Read Fourth):
- `templates/testing/README.md` - Comprehensive testing framework and patterns
- `templates/testing/TESTING_REFERENCE.md` - Quick reference for testing standards
- `.claude/TechDebt.md` - Technical debt management requirements

## Task Definition

### Goal
Create essential tools for Caronex manager to inspect and coordinate system state, providing basic system introspection and coordination capabilities without complex implementations.

### Scope
Implement basic management tools that enable Caronex to understand current system capabilities, configuration state, and provide coordination guidance. Focus on introspection and planning capabilities, not complex implementation features.

## BDD Scenarios (IMPLEMENT ALL SCENARIOS)

```gherkin
Feature: Caronex Management Tools
  As Caronex manager agent
  I want basic tools to understand and coordinate system state
  So that I can provide accurate information and effective coordination

  Scenario: System state introspection
    Given I am Caronex with access to management tools
    When I need to assess current system capabilities
    Then I should be able to query available agents and their specializations
    And I should be able to check current configuration state
    And I should be able to report system status accurately

  Scenario: Basic coordination capabilities
    Given I need to coordinate agent activities
    When I assess implementation requirements
    Then I should be able to identify appropriate specialist agents
    And I should be able to provide planning guidance
    And I should be able to delegate implementation tasks appropriately

  Scenario: Configuration management
    Given I need to understand system configuration
    When I query configuration state
    Then I should be able to retrieve current configuration values
    And I should be able to validate configuration consistency
    And I should be able to report configuration issues if any exist

  Scenario: Agent lifecycle management
    Given I need to coordinate agent activities
    When I manage agent operations
    Then I should be able to list available agent types
    And I should be able to check agent readiness status
    And I should be able to coordinate agent task delegation

  Scenario: Space foundation introspection
    Given the foundation for space management exists
    When I query space-related capabilities
    Then I should be able to list basic space configuration options
    And I should be able to report space readiness status
    And I should be able to provide guidance for future space implementation
```

## Technical Analysis

### Current Architecture Assessment

**Management Tool Integration Points**:
- `internal/agents/caronex/` - Caronex manager agent ready for tool integration (Task 3 completed)
- `internal/tools/` - Existing tool framework for extending capabilities
- `internal/agents/base/` - Base agent system with tool integration support
- `internal/core/config/` - Meta-system configuration system for introspection (Task 2 completed)
- TUI integration available via completed Task 4 (purple/violet theme, Ctrl+M switching)

**Existing Tool Patterns**:
- `internal/tools/builtin/` - Existing tool implementations (bash, edit, view, etc.)
- Tool interface patterns in `internal/agents/base/tools.go`
- Tool integration with agent system via `internal/agents/base/agent-tool.go`

**Key Requirements**:
- Management tools should be Caronex-specific (not general-purpose)
- Focus on coordination and introspection, not implementation
- Integrate with existing tool framework without disrupting current tools
- Support manager agent personality and coordination focus

## Requirements

### Functional Requirements
1. **System Introspection Tools**: Query agents, configuration, and system state
2. **Agent Coordination Tools**: List agents, check readiness, support delegation
3. **Configuration Management**: Read, validate, and report on configuration state
4. **Space Foundation Tools**: Basic space configuration introspection
5. **Planning Support Tools**: Assist with implementation planning and guidance

### Technical Requirements
1. **Tool Framework Integration**: Extend existing tool system in `internal/tools/`
2. **Caronex Integration**: Make tools available specifically to Caronex manager
3. **Agent System Integration**: Leverage existing agent framework capabilities
4. **Configuration Integration**: Use existing config system for introspection
5. **Error Handling**: Robust error handling and user-friendly feedback

### Quality Requirements
1. **BDD Compliance**: All 5 scenarios must be implemented and passing
2. **Test Coverage**: Unit and integration tests for all management tools
3. **Code Quality**: Follow CLAUDE.md patterns and established conventions
4. **Documentation**: Clear documentation of tool purposes and usage
5. **Performance**: Efficient tool execution without system impact

## Implementation Strategy

### Phase 1: Management Tool Framework (40 minutes)
1. **Analyze Tool Architecture**: Understand existing tool integration patterns
2. **Create Management Tool Package**: New package for Caronex-specific tools
3. **Tool Interface Implementation**: Implement management tool interfaces
4. **Basic Integration**: Connect management tools to Caronex agent

### Phase 2: System Introspection Tools (30 minutes)
1. **Agent Query Tool**: List available agents and their specializations
2. **Configuration Inspection Tool**: Read and validate current configuration
3. **System Status Tool**: Report overall system health and readiness
4. **Testing**: Validate introspection accuracy and reliability

### Phase 3: Coordination Tools (25 minutes)
1. **Agent Coordination Tool**: Support agent delegation and task planning
2. **Planning Assistant Tool**: Provide implementation planning guidance
3. **Readiness Check Tool**: Validate system readiness for various operations
4. **Integration Testing**: Verify coordination tool effectiveness

### Phase 4: Space Foundation Tools (20 minutes)
1. **Space Configuration Tool**: Basic space configuration introspection
2. **Space Readiness Tool**: Report on space management foundation status
3. **Future Planning Tool**: Guidance for space implementation planning
4. **Validation**: Ensure space tools support future development

### Phase 5: Testing & Documentation (25 minutes)
1. **BDD Test Implementation**: Create executable tests for all 5 scenarios
2. **Unit Testing**: Comprehensive test coverage for all management tools
3. **Integration Validation**: Verify tools work correctly with Caronex agent
4. **Documentation**: Complete tool documentation and usage guides

## Management Tool Specifications

### System Introspection Tools

#### Agent Query Tool
- **Purpose**: List available agents and their capabilities
- **Interface**: `ListAgents() ([]AgentInfo, error)`
- **Returns**: Agent types, specializations, readiness status
- **Integration**: Query agent registry and configuration

#### Configuration Inspection Tool
- **Purpose**: Read and validate current system configuration
- **Interface**: `InspectConfig() (ConfigStatus, error)`
- **Returns**: Configuration state, validation results, issues
- **Integration**: Use existing configuration system introspection

#### System Status Tool
- **Purpose**: Report overall system health and capabilities
- **Interface**: `SystemStatus() (SystemInfo, error)`
- **Returns**: System readiness, capabilities, resource status
- **Integration**: Aggregate information from various system components

### Coordination Tools

#### Agent Coordination Tool
- **Purpose**: Support agent delegation and coordination
- **Interface**: `CoordinateAgents(task TaskInfo) (CoordinationPlan, error)`
- **Returns**: Recommended agents, delegation strategy, task breakdown
- **Integration**: Analyze task requirements and agent capabilities

#### Planning Assistant Tool
- **Purpose**: Provide implementation planning guidance
- **Interface**: `PlanImplementation(requirements Requirements) (Plan, error)`
- **Returns**: Implementation phases, dependencies, recommendations
- **Integration**: Use system knowledge to generate planning guidance

#### Readiness Check Tool
- **Purpose**: Validate system readiness for operations
- **Interface**: `CheckReadiness(operation OperationType) (ReadinessStatus, error)`
- **Returns**: Readiness assessment, missing dependencies, recommendations
- **Integration**: Validate prerequisites and system state

### Space Foundation Tools

#### Space Configuration Tool
- **Purpose**: Basic space configuration introspection
- **Interface**: `InspectSpaceConfig() (SpaceConfigStatus, error)`
- **Returns**: Space configuration foundation, available options
- **Integration**: Query space-related configuration and capabilities

#### Space Readiness Tool
- **Purpose**: Report space management foundation status
- **Interface**: `SpaceReadiness() (SpaceStatus, error)`
- **Returns**: Space implementation readiness, foundation completeness
- **Integration**: Assess space management foundation and requirements

## Testing Requirements

### BDD Test Implementation
- **Framework**: Use existing Godog BDD infrastructure in `test/bdd/`
- **Test File**: Create `test/bdd/features/caronex_management_tools.feature`
- **Step Definitions**: Implement in `test/bdd/steps/management_steps.go`
- **Configuration**: Follow test configuration patterns from `templates/testing/`

### Unit Test Coverage
- **Tool Implementation**: Test each management tool individually
- **Agent Integration**: Test tool integration with Caronex agent
- **Error Handling**: Test error scenarios and edge cases
- **Performance**: Validate tool execution performance

### Integration Test Scenarios
- **End-to-End Workflow**: Test complete management tool usage workflow
- **Agent Coordination**: Validate tool-supported coordination capabilities
- **Configuration Integration**: Test configuration introspection accuracy
- **System Introspection**: Validate system state reporting accuracy

## Code Quality Standards

### Architecture Patterns (from CLAUDE.md)
- **Agent-Everything System**: Management tools support agent-everything philosophy
- **Caronex-Orchestrated Architecture**: Tools designed for Caronex orchestration
- **Tool System Integration**: Follow existing tool framework patterns
- **Configuration Integration**: Use established configuration patterns

### Implementation Standards
- **Tool Interface Consistency**: Follow existing tool interface patterns
- **Error Handling**: Consistent error handling and user feedback
- **Performance**: Efficient tool execution without system impact
- **Extensibility**: Design for future management tool expansion

### Code Style Requirements
- **No Comments**: Follow CLAUDE.md directive (DO NOT ADD ANY COMMENTS unless asked)
- **Consistent Naming**: Follow existing tool and agent naming conventions
- **Import Organization**: Maintain consistent import grouping and naming
- **Test Patterns**: Use established testing patterns from `templates/testing/`

## Technical Debt Management

### Pre-Implementation
- [ ] Read `.claude/TechDebt.md` to understand current technical debt status
- [ ] Review Task 4 implementation for any dependencies or integration points
- [ ] Plan implementation to avoid creating new technical debt

### During Implementation
- [ ] Log any shortcuts or temporary solutions immediately in `.claude/TechDebt.md`
- [ ] Note any architectural compromises or design decisions requiring future attention
- [ ] Document any test scenarios that are temporarily skipped or incomplete

### Post-Implementation
- [ ] Update `.claude/TechDebt.md` with any new technical debt created
- [ ] Mark resolved any existing technical debt addressed during implementation
- [ ] Document patterns and insights for future management tool development

## Success Criteria

### Functional Success
- [ ] All management tools provide accurate system introspection
- [ ] Agent coordination tools support effective task delegation
- [ ] Configuration management tools report system state correctly
- [ ] Space foundation tools provide useful planning guidance
- [ ] All tools integrate seamlessly with Caronex manager agent

### Quality Success
- [ ] All 5 BDD scenarios implemented and passing
- [ ] Build succeeds without errors or warnings
- [ ] All existing tests continue passing
- [ ] Unit tests provide comprehensive coverage of management tools
- [ ] Code follows CLAUDE.md patterns and established conventions

### User Experience Success
- [ ] Management tools provide clear, actionable information
- [ ] Tool responses are formatted appropriately for Caronex personality
- [ ] Error messages are helpful and guide appropriate actions
- [ ] Tool execution is fast and responsive
- [ ] Integration with Caronex agent feels natural and intuitive

## Documentation Requirements

### Code Documentation
- **Tool Documentation**: Document each management tool's purpose and usage
- **Architecture Integration**: Document how tools integrate with existing systems
- **API Documentation**: Clear interface documentation for all tool functions

### User Documentation
- **Management Tool Guide**: Document how to use management tools through Caronex
- **Coordination Workflows**: Document effective coordination patterns using tools
- **Troubleshooting**: Common issues and solutions for management tool usage

### Development Documentation
- **Implementation Patterns**: Document reusable patterns for future management tools
- **Testing Patterns**: Document BDD patterns specific to management tool testing
- **Extension Guide**: Document how to add new management tools in the future

## Memory Integration Protocol

### Implementation Feedback (MANDATORY)
Document the following in `.claude/implementationLogs.md`:

1. **Tool Design Approach**: How you approached management tool architecture and design
2. **Integration Discoveries**: Insights about tool framework integration and patterns
3. **BDD Implementation**: How BDD scenarios guided tool development decisions
4. **Technical Challenges**: Implementation challenges and solutions for management tools
5. **Pattern Insights**: New patterns discovered for management and coordination tools
6. **Caronex Integration**: Lessons learned about extending agent capabilities with specialized tools

### Quality Assessment (MANDATORY)
Document the following in `.claude/qualityFeedback.md`:

1. **Tool Quality**: Assessment of management tool implementation quality and reliability
2. **Integration Quality**: How well tools integrate with existing agent and tool systems
3. **User Experience**: Assessment of tool usability and information presentation
4. **Performance Impact**: Analysis of tool execution performance and system impact
5. **Architecture Alignment**: How well tools support meta-system coordination goals
6. **Future Recommendations**: Suggestions for additional management tools or improvements

### Memory Updates (MANDATORY)
1. **Update `.claude/activeContext.md`**: Mark Task 5 as completed and update focus to Task 6
2. **Update `.claude/progress.md`**: Document Task 5 completion and Phase 3 readiness
3. **Update `CLAUDE.md`**: Document management tool patterns and integration insights
4. **Update Sprint 1 Status**: Update Phase 3 completion status in sprint tracking

## Implementation Validation

### Build Validation
```bash
# Verify build success
go build -o ii

# Run application to test basic functionality
go run main.go --help

# Test management tool availability through Caronex
go run main.go
```

### Test Validation
```bash
# Run all existing tests to ensure no regressions
go test ./...

# Run BDD tests specifically
go test ./test/bdd/...

# Run management tool tests
go test -v ./internal/tools/coordination/...
```

### Functional Validation
1. **Tool Integration**: Verify management tools are available to Caronex agent
2. **System Introspection**: Test agent listing, configuration inspection, system status
3. **Coordination Support**: Validate coordination and planning tool functionality
4. **Space Foundation**: Test space-related introspection and planning tools
5. **Error Handling**: Verify graceful handling of error scenarios

## Post-Implementation Tasks

### Immediate Tasks
1. **Commit Changes**: Create descriptive git commit for Task 5 completion
2. **Update Documentation**: Ensure all documentation reflects new management capabilities
3. **Memory Synchronization**: Update all memory files with implementation insights
4. **Quality Assessment**: Complete structured feedback in quality files

### Coordination Tasks
1. **Task 6 Preparation**: Prepare for Integration Testing & Documentation
2. **Sprint 1 Completion**: Ready for final sprint validation and documentation
3. **Architecture Documentation**: Update architecture documentation with management patterns
4. **Pattern Library**: Add management tool patterns to reusable pattern library

---

## Task Coordination Note

This task completes Sprint 1 Phase 3 by providing Caronex manager with essential coordination capabilities. The implementation should focus on practical tools that enhance Caronex's ability to understand and coordinate system state rather than complex implementation features.

**Dependencies**: ✅ Task 4 (TUI Caronex Integration) completed with outstanding quality on 2025-06-16.
**Sprint Status**: 89% complete (8/9 tasks), Phase 2 complete, Phase 3 in progress.
**Next Task**: Task 6 (Integration Testing & Documentation) to complete Sprint 1 at 100%.

The management tools should embody the coordination-focused nature of Caronex, providing information and guidance rather than performing direct implementations. This maintains the clear distinction between manager and implementer agents established in the meta-system architecture.