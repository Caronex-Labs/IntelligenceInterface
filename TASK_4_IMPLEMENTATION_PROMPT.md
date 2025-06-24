# Task 4: TUI Caronex Integration - Implementation Prompt

## Memory Context Requirements (MANDATORY - READ ALL BEFORE IMPLEMENTATION)

### Foundation Files (Read First):
- `.claude/projectbrief.md` - Core project mission and Intelligence Interface meta-system goals
- `.claude/productContext.md` - Problem context and solution architecture 
- `.claude/systemPatterns.md` - Architecture patterns and design decisions
- `.claude/techContext.md` - Technology stack and setup requirements

### Coordination Files (Read Second):
- `.claude/activeContext.md` - Current focus and recent Sprint 1 developments
- `.claude/progress.md` - Implementation status and Sprint 1 roadmap
- `.claude/coordinationContext.md` - Task coordination framework
- `.claude/testingContext.md` - BDD testing integration

### Implementation Files (Read Third):
- `CLAUDE.md` - Critical implementation patterns and BDD rules (project root)
- `.claude/bddWorkflows.md` - BDD workflow patterns and templates
- `.claude/implementationLogs.md` - Previous task insights and discoveries
- `.claude/qualityFeedback.md` - Quality patterns from completed tasks
- `sprints/Sprint1.md` - Complete Sprint 1 context and task details

### Testing Standards (Read Fourth):
- `templates/testing/README.md` - Comprehensive testing framework and patterns
- `templates/testing/TESTING_REFERENCE.md` - Quick reference for testing standards
- `.claude/TechDebt.md` - Technical debt management requirements

## Task Definition

### Goal
Integrate Caronex manager into existing TUI with clear mode switching capabilities, enabling users to switch between coordination and implementation agent modes.

### Scope
Add Caronex manager mode to existing TUI without breaking current chat interface functionality. Extend existing agent switching system with visual distinction and hotkey support.

## BDD Scenarios (IMPLEMENT ALL SCENARIOS)

```gherkin
Feature: TUI Caronex Integration
  As a user of Intelligence Interface TUI
  I want to switch between Caronex manager and implementation agents
  So that I can access coordination capabilities when needed

  Scenario: Manager mode activation
    Given I am in the main TUI interface
    When I press the Caronex hotkey (Ctrl+M)
    Then I should enter manager mode
    And visual indicators should show I'm talking to Caronex
    And conversation context should switch to manager agent

  Scenario: Visual mode distinction  
    Given I am switching between agent modes
    When I interact with different agent types
    Then the interface should clearly indicate current agent
    And Caronex mode should have distinct visual styling
    And agent capabilities should be clearly communicated

  Scenario: Context preservation across modes
    Given I have conversation history with different agents
    When I switch between manager and implementation modes
    Then each agent mode should maintain its own conversation context
    And switching should preserve message history per agent
    And I should see relevant context when switching back

  Scenario: Functionality preservation
    Given the existing TUI functionality (chat, editing, navigation)
    When I add Caronex manager mode integration
    Then all existing functionality should continue working
    And existing keybindings should remain functional
    And performance should not be degraded

  Scenario: Agent delegation workflow
    Given I am in Caronex manager mode
    When I request implementation work
    Then Caronex should provide coordination guidance
    And should suggest appropriate implementation approaches
    And should not attempt direct implementation
```

## Technical Analysis

### Current Architecture Assessment

**Existing TUI Structure**:
- `internal/tui/page/chat.go` - Main chat interface with agent switching foundation
- `internal/tui/components/chat/` - Chat components (list, message, editor, sidebar) 
- `internal/tui/layout/` - Layout management (container, overlay, split)
- `internal/tui/styles/` - Styling and visual elements
- `internal/tui/theme/` - Theme management with intelligence-interface theme

**Agent System Status**:
- ✅ Caronex Manager Agent: Complete in `internal/agents/caronex/`
- ✅ Base Agent Framework: `internal/agents/base/`
- ✅ Existing agent switching system in chat.go (lines 38, 41-43)

**Key Integration Points**:
- Agent switching already implemented in chatPage struct
- Per-agent session management exists (agentSessions, conversationContexts)
- AgentSwitchedMsg events for mode changes

## Requirements

### Functional Requirements
1. **Caronex Mode Toggle**: Add Caronex manager to existing agent switching system
2. **Visual Indicators**: Clear distinction between manager vs implementation modes
3. **Hotkey Integration**: Ctrl+M hotkey for quick manager mode activation
4. **Context Management**: Separate conversation contexts per agent type
5. **Functionality Preservation**: All existing TUI features must continue working

### Technical Requirements
1. **Extend Agent Switching**: Add Caronex to existing agent mode system
2. **Theme Integration**: Manager mode styling using intelligence-interface theme
3. **Keybinding Extension**: Add Ctrl+M to existing key mappings
4. **Session Isolation**: Proper session management per agent mode
5. **Error Handling**: Graceful handling of mode switching edge cases

### Quality Requirements
1. **BDD Compliance**: All 5 scenarios must be implemented and passing
2. **Test Coverage**: Unit and integration tests for new functionality
3. **Code Quality**: Follow CLAUDE.md patterns and established conventions
4. **Documentation**: Update relevant documentation with new capabilities
5. **Performance**: No degradation of existing TUI responsiveness

## Implementation Strategy

### Phase 1: Agent Mode Extension (30 minutes)
1. **Analyze Current Agent System**: Examine existing agent switching in chat.go
2. **Add Caronex Mode**: Extend agent mode enumeration to include Caronex
3. **Update Agent Factory**: Ensure Caronex agent can be instantiated
4. **Test Basic Integration**: Verify Caronex mode can be selected

### Phase 2: Hotkey Integration (20 minutes)
1. **Extend Key Mappings**: Add Ctrl+M to ChatKeyMap struct
2. **Implement Key Handling**: Add hotkey processing in Update() method
3. **Mode Switching Logic**: Implement direct switch-to-manager functionality
4. **Test Hotkey Response**: Verify Ctrl+M activates manager mode

### Phase 3: Visual Distinction (25 minutes)
1. **Manager Mode Styling**: Create distinct visual indicators for Caronex mode
2. **Status Display**: Show current agent mode in UI header/status area
3. **Theme Integration**: Use intelligence-interface theme for manager styling
4. **Agent Capability Display**: Show mode-specific help text or indicators

### Phase 4: Context Management (20 minutes)
1. **Session Isolation**: Ensure per-agent conversation contexts work with Caronex
2. **Context Switching**: Proper preservation when switching between modes
3. **Message History**: Verify conversation history is maintained per agent
4. **State Synchronization**: Ensure UI state reflects current agent context

### Phase 5: Testing & Validation (25 minutes)
1. **BDD Test Implementation**: Create executable tests for all 5 scenarios
2. **Integration Testing**: Verify all existing functionality still works
3. **Performance Testing**: Ensure no degradation of TUI responsiveness
4. **User Experience Testing**: Manual validation of mode switching workflow

## Testing Requirements

### BDD Test Implementation
- **Framework**: Use existing Godog BDD infrastructure in `test/bdd/`
- **Test File**: Create `test/bdd/features/tui_caronex_integration.feature`
- **Step Definitions**: Implement in `test/bdd/steps/tui_steps.go`
- **Configuration**: Follow test configuration patterns from `templates/testing/`

### Unit Test Coverage
- **TUI Components**: Test mode switching logic in chat page
- **Agent Integration**: Test Caronex agent instantiation and context management
- **Key Handling**: Test hotkey processing and mode activation
- **State Management**: Test conversation context preservation

### Integration Test Scenarios
- **Full Workflow**: Test complete user workflow from TUI startup to mode switching
- **Existing Functionality**: Validate all current features still work
- **Performance**: Ensure TUI remains responsive with new functionality
- **Error Scenarios**: Test edge cases and error handling

## Code Quality Standards

### Architecture Patterns (from CLAUDE.md)
- **Agent-Everything System**: Caronex integration must support agent-everything philosophy
- **Caronex-Orchestrated Architecture**: Design for future Caronex orchestration capabilities
- **Configuration Cascade**: Use existing config system for manager mode settings
- **Session Management**: Integrate with hierarchical session system

### Implementation Standards
- **Bubble Tea Patterns**: Follow existing TUI component patterns
- **Event-Driven Design**: Use existing message passing and event system
- **Clean Architecture**: Maintain separation of concerns
- **Error Handling**: Consistent error handling and user feedback

### Code Style Requirements
- **No Comments**: Follow CLAUDE.md directive (DO NOT ADD ANY COMMENTS unless asked)
- **Consistent Naming**: Follow existing TUI and agent naming conventions  
- **Import Organization**: Maintain consistent import grouping and naming
- **Test Patterns**: Use established testing patterns from `templates/testing/`

## Technical Debt Management

### Pre-Implementation
- [ ] Read `.claude/TechDebt.md` to understand current technical debt status
- [ ] Verify no outstanding technical debt that would impact TUI integration
- [ ] Plan implementation to avoid creating new technical debt

### During Implementation
- [ ] Log any shortcuts or temporary solutions immediately in `.claude/TechDebt.md`
- [ ] Note any architectural compromises or design decisions requiring future attention
- [ ] Document any test scenarios that are temporarily skipped or incomplete

### Post-Implementation
- [ ] Update `.claude/TechDebt.md` with any new technical debt created
- [ ] Mark resolved any existing technical debt addressed during implementation
- [ ] Document patterns and insights for future TUI enhancement tasks

## Success Criteria

### Functional Success
- [ ] Ctrl+M hotkey successfully activates Caronex manager mode
- [ ] Visual indicators clearly distinguish manager vs implementation modes  
- [ ] Conversation contexts are properly isolated and preserved per agent
- [ ] All existing TUI functionality continues working without regression
- [ ] Agent delegation workflow provides appropriate coordination guidance

### Quality Success
- [ ] All 5 BDD scenarios implemented and passing
- [ ] Build succeeds without errors or warnings
- [ ] All existing tests continue passing
- [ ] Integration tests validate complete functionality
- [ ] Code follows CLAUDE.md patterns and established conventions

### User Experience Success
- [ ] Mode switching is intuitive and responsive
- [ ] Visual feedback clearly communicates current agent mode
- [ ] Performance is not degraded by new functionality
- [ ] Error scenarios are handled gracefully with clear user feedback
- [ ] Documentation is updated to reflect new capabilities

## Documentation Requirements

### Code Documentation
- **Function Documentation**: Document new public functions following Go conventions
- **Architecture Decision**: Document mode switching design in implementation logs
- **Integration Points**: Document how Caronex integrates with existing agent system

### User Documentation
- **Feature Documentation**: Update relevant user documentation with Ctrl+M hotkey
- **Mode Switching Guide**: Document how to use manager vs implementation modes
- **Troubleshooting**: Add common issues and solutions for mode switching

### Development Documentation
- **Implementation Patterns**: Document reusable patterns for future agent integration
- **Testing Patterns**: Document BDD patterns specific to TUI testing
- **Architecture Evolution**: Document how this implementation supports future meta-system evolution

## Memory Integration Protocol

### Implementation Feedback (MANDATORY)
Document the following in `.claude/implementationLogs.md`:

1. **Implementation Approach**: How you approached the TUI integration challenge
2. **Architecture Discoveries**: Any insights about existing TUI structure or patterns
3. **BDD Implementation**: How the BDD scenarios guided implementation decisions  
4. **Technical Challenges**: Any implementation challenges and how they were resolved
5. **Pattern Insights**: New patterns discovered that could benefit future implementations
6. **Integration Learnings**: Lessons learned about agent integration with TUI systems

### Quality Assessment (MANDATORY)
Document the following in `.claude/qualityFeedback.md`:

1. **Code Quality**: Assessment of implementation quality against established standards
2. **Test Coverage**: Evaluation of BDD and unit test coverage completeness
3. **User Experience**: Assessment of mode switching intuitiveness and visual clarity
4. **Performance Impact**: Analysis of any performance implications from new functionality
5. **Architecture Alignment**: How well the implementation aligns with meta-system goals
6. **Future Recommendations**: Suggestions for future TUI enhancements or improvements

### Memory Updates (MANDATORY)
1. **Update `.claude/activeContext.md`**: Mark Task 4 as completed and update current focus
2. **Update `.claude/progress.md`**: Document Task 4 completion and move to Phase 3 planning
3. **Update `CLAUDE.md`**: Document any new TUI or agent integration patterns discovered
4. **Update Sprint 1 Status**: Mark Phase 2 as complete in sprint tracking

## Implementation Validation

### Build Validation
```bash
# Verify build success
go build -o ii

# Run application to test basic functionality
go run main.go --help

# Test TUI mode activation
go run main.go
```

### Test Validation
```bash
# Run all existing tests to ensure no regressions
go test ./...

# Run BDD tests specifically
go test ./test/bdd/...

# Run with verbose output to see test details
go test -v ./internal/tui/...
```

### Functional Validation
1. **Start TUI**: `go run main.go` should launch TUI successfully
2. **Test Hotkey**: Ctrl+M should activate manager mode with visual indication
3. **Test Mode Switching**: Should be able to switch between agent modes smoothly
4. **Test Context Preservation**: Conversation history should be maintained per agent
5. **Test Existing Features**: All current TUI features should continue working

## Post-Implementation Tasks

### Immediate Tasks
1. **Commit Changes**: Create descriptive git commit for Task 4 completion
2. **Update Documentation**: Ensure all documentation reflects new capabilities
3. **Memory Synchronization**: Update all memory files with implementation insights
4. **Quality Assessment**: Complete structured feedback in quality files

### Coordination Tasks
1. **Task 5 Preparation**: Prepare for Basic Management Tools implementation
2. **Integration Planning**: Plan for comprehensive Sprint 1 integration testing
3. **Architecture Documentation**: Update architecture documentation with TUI patterns
4. **Pattern Library**: Add TUI integration patterns to reusable pattern library

---

## Task Coordination Note

This task is part of Sprint 1 Phase 2 and is critical for completing the meta-system foundation. The implementation must maintain the high quality standards established in Phase 1 (100% BDD compliance, outstanding quality ratings, 100% technical debt resolution).

The completed Caronex Manager Agent from Task 3 provides the foundation for this integration. Focus on extending existing TUI architecture rather than replacing it, ensuring zero regression while adding powerful coordination capabilities.

**Next Task Dependencies**: Task 5 (Basic Management Tools) depends on Task 4 completion, followed by Task 6 (Integration Testing & Documentation) to complete Sprint 1.