# Memory Intelligence & Dart Project Coordination Framework

## Dart-First Coordination Philosophy

### Streamlined Agent Coordination with Dart Task Management
All agents follow the optimized **Dart Task → Context Chain → Plan → Implement** workflow:

**Primary Workflow**:
1. **Dart Task Context**: Extract context from Dart task hierarchy (task → parent → root)
2. **Selective Memory Loading**: Load minimal required memory files based on task type
3. **Comprehensive Planning**: Generate complete plans with all required components
4. **User Approval**: Mandatory approval before implementation begins
5. **Dart-Integrated Implementation**: Real-time progress tracking with learning capture

**Memory Context Optimization**:
- **Essential Context**: Always load projectbrief.md + systemPatterns.md
- **Task-Specific Context**: Load additional memory files only when needed
- **Progressive Loading**: Add context only when complexity requires it
- **No Redundant Reading**: Skip context already in Dart task descriptions

### Optimized Agent Specialization

#### Memory Intelligence & Dart Project Coordinator
**Streamlined Role**: Strategic intelligence synthesis and Dart project generation
**Primary Commands**:
- `GenerateDartProject` - Create Dart projects from memory intelligence
- `SynthesizeIntelligence` - High-level memory analysis and pattern enhancement
- `CoordinateSprint` - Strategic sprint planning and coordination
- `IntegrateLearning` - Memory enhancement through implementation feedback

**When to Use**:
- Strategic project planning and Dart project creation
- High-level architecture decisions and intelligence synthesis
- Sprint-level coordination and agent workflow optimization
- Memory system enhancement through learning integration

#### Dart Task Implementation Agent  
**Streamlined Role**: Direct task execution from Dart task IDs with comprehensive planning
**Primary Command**: `ImplementTask [DART_TASK_ID]`

**Optimized Workflow**:
1. **Dart Context Chain Reading**: Automatic task hierarchy analysis
2. **Selective Memory Loading**: Task-type specific context loading
3. **Comprehensive Planning**: Six-component plan generation
4. **User Approval**: Mandatory approval before implementation
5. **Dart-Integrated Implementation**: Real-time progress and completion tracking

**When to Use**:
- Any Dart task requiring implementation with comprehensive planning
- Complex features needing BDD scenarios and testing
- Architecture-compliant implementation with learning integration
- Multi-phase development work with quality validation

#### Rapid Task Resolution Agent
**Ultra-Light Role**: Immediate issue resolution with minimal context
**Primary Commands**:
- `QuickFix [DESCRIPTION]` - Immediate issue resolution from description
- `QuickTask [DART_TASK_ID]` - Simple task execution with minimal context

**Ultra-Fast Workflow**:
1. **Minimal Context**: Only systemPatterns.md + task description/Dart task
2. **Rapid Planning**: 3-5 task breakdown with quick approval
3. **Immediate Implementation**: Fast execution with validation
4. **Quick Documentation**: Brief completion logging

**When to Use**:
- Simple configuration changes and bug fixes
- Minor template corrections and documentation updates
- Quick improvements and organizational tasks
- Any change requiring minimal context and rapid execution

## Optimized Task Classification Framework

### Strategic Tasks (Memory Coordinator)
**Characteristics**:
- Project-level planning and coordination
- Multi-sprint scope and strategic decisions
- Dart project generation and architecture
- Memory intelligence synthesis

**Examples**:
- Generate complete Dart project from memory intelligence
- Strategic sprint planning and coordination
- Architecture pattern learning and memory enhancement
- Agent workflow optimization and coordination

### Implementation Tasks (Implementation Agent via `ImplementTask [DART_TASK_ID]`)
**Characteristics**:
- Dart task-driven implementation
- Comprehensive planning with BDD scenarios
- Single-task scope with quality validation
- Real-time Dart progress integration

**Examples**:
- Any Dart task requiring detailed implementation
- Template creation and code generation features
- Complex integrations with testing requirements
- Multi-phase development with architecture compliance

**Command**: `ImplementTask EqnpESMuShrt` (Go Reference Analysis Flow)

### Quick Tasks (Rapid Resolution Agent)
**Characteristics**:
- Immediate resolution scope
- Minimal context requirements
- Simple changes with fast execution
- Brief documentation and validation

**Examples**:
- Configuration file corrections
- Template placeholder fixes
- Documentation updates and improvements
- Simple bug fixes and organizational changes

**Commands**: 
- `QuickFix Fix typo in user_domain.yaml`
- `QuickTask Y35o7i1XOXM6` (for simple Dart tasks)

## Implementation Coordination Patterns

### Phase-Based Coordination

#### Phase Transition Protocol
1. **Phase Completion Validation**
   - All phase tasks completed and tested
   - Memory system updated with outcomes
   - Technical debt assessed and documented
   - Quality gates passed

2. **Next Phase Preparation**
   - Memory system reviewed for currency
   - Dependencies validated and confirmed
   - Resource allocation and timeline verification
   - Risk assessment and mitigation planning

3. **Agent Handoff**
   - Complete context transfer via memory system
   - Specific task requirements documented
   - Quality standards and acceptance criteria defined
   - Success metrics and validation approaches specified

### Quality Gate Enforcement

#### Pre-Implementation Gates
- [ ] **Memory Context Read**: All relevant memory files reviewed
- [ ] **Task Understanding**: Clear comprehension of requirements
- [ ] **Architecture Alignment**: Implementation approach matches patterns
- [ ] **Dependency Validation**: All prerequisites satisfied

#### Implementation Gates
- [ ] **Code Quality**: Follows established patterns and standards
- [ ] **Testing Coverage**: Appropriate tests implemented and passing
- [ ] **Documentation**: Implementation documented appropriately
- [ ] **Integration**: Works with existing components

#### Post-Implementation Gates
- [ ] **Validation Testing**: All acceptance criteria met
- [ ] **Memory Updates**: Relevant memory files updated
- [ ] **Technical Debt**: Any shortcuts or compromises documented
- [ ] **Learning Capture**: Insights and patterns documented

## Agent Prompt Templates

### Memory Management Agent Template
```markdown
# Memory Management Task: [TASK_NAME]

## Context Reading Requirements
**MANDATORY - Read ALL files before proceeding**:
- .claude/projectbrief.md - Project mission and objectives
- .claude/productContext.md - Problem context and solution approach
- .claude/systemPatterns.md - Architecture patterns and implementation strategies
- .claude/techContext.md - Technology stack and development environment
- .claude/activeContext.md - Current project state and decisions
- .claude/progress.md - Implementation status and roadmap
- .claude/TechDebt.md - Technical debt registry and status

## Task Objectives
[Specific objectives and deliverables]

## Success Criteria
[Measurable outcomes and validation approaches]

## Memory Update Requirements
[Which memory files need updates and what information to capture]
```

### BDD Implementation Agent Template
```markdown
# BDD Implementation Task: [TASK_NAME]

## Memory Context Requirements
**Read these files for implementation context**:
- .claude/systemPatterns.md - Architecture patterns for implementation
- .claude/techContext.md - Technology stack and configuration
- .claude/activeContext.md - Current implementation state
- .claude/testingContext.md - Testing approaches and BDD patterns

## Feature Requirements
[Detailed feature specifications with acceptance criteria]

## BDD Scenarios
```gherkin
Feature: [Feature Name]
  As a [user type]
  I want [functionality]
  So that [business value]

Scenario: [Specific behavior]
  Given [initial state]
  When [action performed]
  Then [expected outcome]
```

## Implementation Standards
[Specific coding standards, patterns, and quality requirements]

## Testing Requirements
[Test coverage expectations and validation approaches]
```

### Quickfire Agent Template
```markdown
# Quickfire Task: [TASK_NAME]

## Quick Context Check
**Essential reading**:
- .claude/activeContext.md - Current project state
- .claude/systemPatterns.md - Architecture patterns (relevant sections)

## Task Description
[Specific, focused task with clear scope]

## Implementation Approach
[Brief approach and expected changes]

## Validation Steps
[How to verify the change works correctly]
```

## Coordination Workflows

### Architecture Decision Workflow
1. **Problem Identification** (Any Agent)
   - Document architectural challenge or decision need
   - Log in TechDebt.md if blocking current work

2. **Decision Coordination** (Memory Management Agent)
   - Analyze impact across system components
   - Research solution options and trade-offs
   - Document decision rationale and implications
   - Update systemPatterns.md with new patterns

3. **Implementation Coordination** (BDD Implementation Agent)
   - Implement architectural changes with full testing
   - Update all affected components consistently
   - Validate integration and system behavior

4. **Validation & Documentation** (Memory Management Agent)
   - Verify implementation meets architectural goals
   - Update memory system with outcomes
   - Document lessons learned and pattern refinements

### Feature Implementation Workflow
1. **Feature Analysis** (Memory Management Agent)
   - Break down feature into implementable tasks
   - Define BDD scenarios and acceptance criteria
   - Identify dependencies and integration points
   - Create detailed implementation prompts

2. **Implementation** (BDD Implementation Agent)
   - Implement feature following BDD methodology
   - Create comprehensive test coverage
   - Document implementation patterns and decisions
   - Update relevant memory files with insights

3. **Integration & Validation** (Memory Management Agent)
   - Verify feature integration with system
   - Validate against acceptance criteria
   - Update progress tracking and milestone status
   - Plan next feature implementation

### Issue Resolution Workflow
1. **Issue Classification** (Any Agent)
   - Determine if issue is Quickfire, Story, or Epic level
   - Route to appropriate agent based on classification
   - Ensure sufficient context available

2. **Resolution** (Appropriate Agent)
   - Implement fix following agent-specific patterns
   - Test resolution thoroughly
   - Document changes and rationale

3. **Validation** (Memory Management Agent for Story/Epic level)
   - Verify fix doesn't introduce regressions
   - Update memory system if patterns affected
   - Close issue and update tracking

## Quality Assurance Coordination

### Code Quality Standards
- **Template Files**: Must follow established placeholder patterns
- **Generated Code**: Must produce working, well-structured applications
- **Documentation**: Must be comprehensive and up-to-date
- **Testing**: Must have appropriate coverage for complexity level

### Technical Debt Management
- **Immediate Logging**: All shortcuts and compromises documented immediately
- **Regular Assessment**: Weekly review of technical debt status
- **Prioritization**: Based on impact and effort for resolution
- **Resolution Tracking**: Progress updates and completion verification

### Knowledge Management
- **Pattern Documentation**: All successful patterns documented in systemPatterns.md
- **Decision Rationale**: Architecture decisions documented with context
- **Lesson Capture**: Implementation insights captured for future reference
- **Best Practice Evolution**: Continuous improvement of coordination processes

## Communication Protocols

### Status Reporting Format
```markdown
## [Agent Type] Status Report: [Date]

### Tasks Completed
- [List of completed tasks with brief outcomes]

### Current Work
- [Current task and progress status]

### Blockers/Issues
- [Any impediments or issues requiring coordination]

### Next Steps
- [Planned work for next session/period]

### Memory Updates Required
- [Any memory files needing updates]
```

### Escalation Triggers
- **Technical Blockers**: Cannot proceed due to technical constraints
- **Architecture Ambiguity**: Unclear how to implement within established patterns
- **Quality Concerns**: Implementation may not meet quality standards
- **Scope Questions**: Unclear if work is within defined scope
- **Resource Constraints**: Insufficient information or capabilities for task

### Decision Making Authority
- **Memory Management Agent**: Architecture, scope, coordination decisions
- **BDD Implementation Agent**: Implementation approach, testing strategy
- **Quickfire Agent**: Minor fixes and improvements within established patterns
- **User/Project Owner**: Scope changes, priority adjustments, major direction changes