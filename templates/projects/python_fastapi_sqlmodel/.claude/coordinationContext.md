# Memory Intelligence & Dart Project Coordination Framework

## Production CLI Tool Coordination Philosophy

### Agent-Driven Project Generation with Production CLI Tool

All agents coordinate around the production-ready `fastapi-sqlmodel-generator` CLI tool:

**Primary Workflow**:

1. **CLI Tool Access**: Use `fastapi-sqlmodel-generator docs` for complete documentation
2. **Project Generation**: Execute multi-phase project generation using CLI tool
3. **Configuration Management**: Co-located configuration approach with domain.yaml + entities.yaml
4. **Quality Validation**: Automatic testing and dependency installation during generation
5. **Template Customization**: Copy templates to target projects for project-specific modifications

**Production CLI Integration**:

- **Global Tool Access**: CLI tool installed globally via `uv tool install -e .`
- **Embedded Documentation**: Complete usage guide accessible via `docs` command
- **Agent Coordination**: Multi-phase prompts for Health and User domain generation
- **Technical Debt Resolution**: All 6 critical technical debt items resolved

### Optimized Agent Specialization

#### CLI Tool Coordination Agent

**Production Role**: Agent workflow coordination using production CLI tool
**Primary Commands**:

- `CoordinateProjectGeneration` - Multi-phase project generation coordination
- `ValidateCliToolAccess` - Ensure agents have CLI tool documentation access
- `ManageProjectTemplates` - Template customization and configuration management
- `MonitorGenerationQuality` - Validate automatic testing and dependency installation

**When to Use**:

- Multi-phase project generation coordination (Health + User domains)
- Agent prompt creation and workflow coordination
- CLI tool integration and documentation access validation
- Template system optimization and quality monitoring

#### Project Generation Agent

**Production Role**: Direct project generation using fastapi-sqlmodel-generator CLI tool
**Primary Command**: `GenerateProject [TARGET_DIRECTORY] [PHASE_NUMBER]`

**Multi-Phase Workflow**:

1. **Documentation Access**: Execute `fastapi-sqlmodel-generator docs` for complete context
2. **Configuration Preparation**: Prepare domain.yaml and entities.yaml configurations
3. **Project Generation**: Execute CLI tool with appropriate parameters
4. **Quality Validation**: Verify automatic testing and dependency installation
5. **Template Customization**: Modify templates in target project for specific requirements

**When to Use**:

- Actual project generation using production CLI tool
- Multi-phase domain implementation (Health domain, User domain)
- Configuration-driven project customization
- Production-ready project initialization with automatic validation

#### Template Enhancement Agent

**Specialized Role**: Template system improvement and customization
**Primary Commands**:

- `EnhanceTemplate [TEMPLATE_NAME]` - Improve existing template functionality
- `CreateCustomTemplate [DOMAIN_NAME]` - Create domain-specific templates
- `ValidateGeneration [PROJECT_PATH]` - Verify generated project quality

**Template-Focused Workflow**:

1. **Template Analysis**: Analyze existing template patterns and structure
2. **Enhancement Planning**: Plan improvements based on requirements
3. **Implementation**: Implement template enhancements with preservation markers
4. **Validation**: Test generation quality and functionality
5. **Documentation**: Update template documentation and usage guides

**When to Use**:

- Template system improvements and enhancements
- Custom template creation for specific domains
- Template validation and quality assurance
- Documentation updates and template usage optimization

## Optimized Task Classification Framework

### Strategic Tasks (CLI Tool Coordination Agent)

**Characteristics**:

- Multi-phase project generation coordination
- Production CLI tool workflow management
- Agent prompt creation and optimization
- Template system quality monitoring

**Examples**:

- Coordinate Health + User domain generation workflow
- Create agent prompts for multi-phase project generation
- Validate CLI tool documentation access across agents
- Monitor automatic testing and dependency installation quality

### Project Generation Tasks (Project Generation Agent)

**Characteristics**:

- Direct CLI tool execution for project generation
- Configuration-driven project customization
- Multi-phase domain implementation
- Production-ready project initialization

**Examples**:

- Generate Health domain using fastapi-sqlmodel-generator
- Generate User domain with co-located configuration
- Execute multi-phase Riskbook backend generation
- Validate generated project quality and functionality

**Command**: `GenerateProject ./riskbook-backend 1` (Phase 1: Health Domain)

### Template Enhancement Tasks (Template Enhancement Agent)

**Characteristics**:

- Template system improvement and optimization
- Custom template creation for specific domains
- Template validation and quality assurance
- Documentation updates and usage optimization

**Examples**:

- Enhance entity template with advanced SQLModel features
- Create custom templates for financial domain models
- Validate template generation quality and performance
- Update template documentation and usage guides

**Commands**:

- `EnhanceTemplate entities.py.j2`
- `CreateCustomTemplate financial_domain`
- `ValidateGeneration ./generated-project`

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