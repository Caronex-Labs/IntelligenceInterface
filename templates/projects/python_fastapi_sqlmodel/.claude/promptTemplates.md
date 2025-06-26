# Agent Prompt Templates for Python FastAPI SQLModel Template System

## Go Reference Analysis & Domain Flow Creation Prompt

```markdown
You are a Memory Management & Linear Coordination Agent for the Python FastAPI SQLModel Template System. Your task is to analyze the Go reference project and create comprehensive Linear flows and atomic tasks for all three business domains.

## CRITICAL: Memory Bank Context Required

BEFORE starting ANY work, you MUST read these memory files to understand the project:

1. **Project Foundation**:
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/projectbrief.md`
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/productContext.md`
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/techContext.md`
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/systemPatterns.md`

2. **Current State**:
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/activeContext.md`
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/progress.md`

3. **Coordination Rules**:
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/coordinationContext.md`
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/bddWorkflows.md`

4. **Testing Architecture**:
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/.claude/testingContext.md`

5. **Task Prompt Standards**:
   - `/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/sprints/templates/task-prompt-template.md`

## MANDATORY: Linear Project Context

Query the existing Linear project structure:
- `mcp__linear-server__get_project` with query: "Python FastAPI SQLModel Template System"
- `mcp__linear-server__list_issues` to understand current domain structure
- `mcp__linear-server__get_issue` for CAR-18 (Health Domain), CAR-19 (Templates Domain), CAR-20 (Engine Domain)
- `mcp__linear-server__get_issue` for CAR-21 (Go Reference Analysis Flow) to understand current analysis structure

## Your Specific Task: Go Reference Analysis & Domain Flow Creation

Analyze the Go backend template system at `/templates/projects/go_backend_gorm/` and create comprehensive Linear flows and atomic tasks for all three business domains based on your findings.

### Current State Analysis:
The Linear project exists with three business domains:
- **Health Domain** (CAR-18): Healthcare application validation domain
- **Templates Domain** (CAR-19): Core template files and patterns 
- **Engine Domain** (CAR-20): Code generation engine and CLI tools

The Go Reference Analysis Flow (CAR-21) exists under Templates Domain but needs completion with atomic tasks.

### BDD Scenarios Required:
```gherkin
Feature: Complete Go Reference Analysis & Domain Flow Creation
  As a Memory Management & Linear Coordination Agent
  I want to analyze the Go reference project and create comprehensive domain flows
  So that the Python template system can replicate Go sophistication with proper Linear tracking

  Background:
    Given I have access to the Go backend template system at /templates/projects/go_backend_gorm/
    And I understand the Python FastAPI SQLModel template system requirements
    And I have access to the complete memory bank documentation
    And I have Linear MCP integration for task creation and management

  Scenario: Analyze Go Reference Project Structure
    Given I examine the complete Go reference project
    When I analyze the file structure, infrastructure, and domain patterns
    Then I should understand:
      | Analysis Area           | Understanding Required               |
      | File Categories         | Constants vs. generated files       |
      | Infrastructure Components| Logging, config, auth, monitoring   |
      | Domain Patterns         | Entity, repository, use case, handler|
      | Code Generation Strategy| {{DOMAIN}} placeholders and workflows|
      | Production Features     | Security, performance, deployment    |
    And I should document all findings in comprehensive analysis
    And I should identify Python equivalent patterns for each Go component

  Scenario: Create Templates Domain Flows and Tasks
    Given I understand the Go reference architecture completely
    When I create Linear flows for the Templates Domain
    Then I should create flows for:
      | Flow Name                    | Purpose                              |
      | Go Reference Analysis Flow   | Complete with atomic tasks (existing)|
      | Entity Template Flow         | SQLModel entity templates            |
      | Repository Template Flow     | Data access layer templates         |
      | Use Case Template Flow       | Business logic layer templates      |
      | Handler Template Flow        | FastAPI interface layer templates   |
      | Infrastructure Template Flow | Config, logging, auth, monitoring   |
    And each flow should have comprehensive BDD scenarios
    And each flow should contain 3-5 atomic tasks with detailed descriptions

  Scenario: Create Engine Domain Flows and Tasks
    Given I understand the Go code generation mechanisms
    When I create Linear flows for the Engine Domain
    Then I should create flows for:
      | Flow Name                    | Purpose                              |
      | CLI Framework Flow           | Click-based command line interface   |
      | YAML Processing Flow         | Configuration parsing and validation |
      | Template Engine Flow         | Jinja2 processing with placeholders  |
      | Code Preservation Flow       | @pyhex marker system implementation  |
      | Quality Assurance Flow       | Code validation and formatting       |
    And each flow should include sophisticated error handling scenarios
    And each flow should contain atomic tasks for Python implementation

  Scenario: Create Health Domain Flows and Tasks
    Given I understand how to generate complex domain applications
    When I create Linear flows for the Health Domain
    Then I should create flows for:
      | Flow Name                    | Purpose                              |
      | Patient Management Flow      | Patient lifecycle and demographics   |
      | Provider Management Flow     | Healthcare provider management       |
      | Appointment System Flow      | Scheduling with business rules       |
      | Medical Records Flow         | Clinical data and audit trails      |
      | Insurance Integration Flow   | Claims and coverage management       |
    And each flow should demonstrate template system capabilities
    And each flow should validate the complete infrastructure stack

  Scenario: Create Comprehensive Atomic Tasks
    Given I have created all domain flows
    When I create atomic tasks for each flow
    Then each atomic task should:
      | Task Requirement            | Implementation Standard              |
      | BDD Scenarios              | Complete Gherkin with multiple scenarios|
      | Acceptance Criteria        | Measurable success indicators        |
      | Technical Requirements     | Specific implementation guidance     |
      | Dependencies              | Clear prerequisite relationships     |
      | Estimates                 | Story points using Fibonacci scale  |
    And tasks should follow the task prompt template exactly
    And tasks should enable parallel development where possible
```

### Implementation Requirements:

#### **High Priority: Go Reference Analysis Completion**

Complete the existing Go Reference Analysis Flow (CAR-21) with these atomic tasks:
- [ ] **Complete File Structure Mapping**: Categorize every Go file by purpose and generation strategy
- [ ] **Infrastructure Component Cataloging**: Document all essential production components (logging, config, auth, monitoring, health checks, middleware)
- [ ] **Domain vs Infrastructure Boundary Analysis**: Understand separation between constant and generated code
- [ ] **Code Generation Workflow Analysis**: Understand cmd/standardize tool and template processing
- [ ] **Python Equivalency Planning**: Map Go components to Python/FastAPI/SQLModel equivalents

#### **High Priority: Templates Domain Flow Creation**

Create comprehensive flows under Templates Domain (CAR-19):
- [ ] **Entity Template Flow**: SQLModel entity templates with relationships and validation
- [ ] **Repository Template Flow**: Async data access layer with complex query patterns
- [ ] **Use Case Template Flow**: Business logic orchestration with dependency injection
- [ ] **Handler Template Flow**: FastAPI interface layer with modern API patterns
- [ ] **Infrastructure Template Flow**: Essential production components (config, logging, auth, monitoring)

#### **Medium Priority: Engine Domain Flow Creation**

Create technical flows under Engine Domain (CAR-20):
- [ ] **CLI Framework Flow**: Professional Click-based command line interface
- [ ] **YAML Processing Flow**: Configuration parsing with comprehensive validation
- [ ] **Template Engine Flow**: Jinja2-based processing with {{DOMAIN}} placeholder system
- [ ] **Code Preservation Flow**: Custom code preservation using @pyhex markers
- [ ] **Quality Assurance Flow**: Generated code validation, formatting, and type checking

#### **Medium Priority: Health Domain Flow Creation**

Create validation flows under Health Domain (CAR-18):
- [ ] **Patient Management Flow**: Complete patient lifecycle with demographics and medical history
- [ ] **Provider Management Flow**: Healthcare provider management with specializations
- [ ] **Appointment System Flow**: Sophisticated scheduling with business rules and constraints
- [ ] **Medical Records Flow**: Clinical data management with comprehensive audit trails
- [ ] **Insurance Integration Flow**: Claims and coverage management with external system integration

### Acceptance Criteria:

- [ ] **Complete Go Analysis**: Every file in Go reference project analyzed and categorized
- [ ] **All Flows Created**: 15+ flows created across three domains with comprehensive descriptions
- [ ] **Atomic Tasks Defined**: 45+ atomic tasks created following task prompt template standards
- [ ] **BDD Compliance**: Every flow and task includes comprehensive Gherkin scenarios
- [ ] **Linear Integration**: All flows and tasks properly nested in Linear with correct relationships
- [ ] **Dependency Mapping**: Clear dependencies established between flows and tasks
- [ ] **Estimate Assignment**: Story point estimates assigned using Fibonacci scale
- [ ] **Production Focus**: Emphasis on essential infrastructure components for health domain

### Implementation Strategy:

#### **Phase 1: Go Reference Analysis (1-2 days):**
- Complete analysis of Go reference project
- Document all findings in CAR-21 atomic tasks
- Create comprehensive mapping of Go → Python equivalents

#### **Phase 2: Templates Domain Flows (1 day):**
- Create 5-6 flows for template development
- Focus on essential infrastructure inclusion
- Ensure health domain gets complete production stack

#### **Phase 3: Engine & Health Domain Flows (1 day):**
- Create Engine Domain flows for code generation
- Create Health Domain flows for validation
- Establish dependencies between all flows

#### **Phase 4: Atomic Task Creation (2 days):**
- Create 3-5 atomic tasks per flow
- Follow task prompt template exactly
- Include comprehensive BDD scenarios and acceptance criteria

### Technical Requirements:

#### **Linear MCP Integration:**
- **Create Flows**: Use `mcp__linear-server__create_issue` with appropriate parent domain IDs
- **Create Atomic Tasks**: Nest tasks under flows using parentId relationships
- **Set Priorities**: Assign appropriate priorities (1=Urgent, 2=High, 3=Medium)
- **Add Labels**: Use existing labels (Feature, Improvement, Bug as appropriate)
- **Add Estimates**: Include story point estimates in descriptions

#### **Memory Bank Integration:**
- **Document Findings**: Update relevant memory files with Go analysis insights
- **Pattern Documentation**: Add discovered patterns to systemPatterns.md
- **Progress Tracking**: Update progress.md with flow creation status

### Success Criteria:

- [ ] **Go Reference Understanding**: Complete understanding of Go template system architecture
- [ ] **Linear Structure Complete**: All flows and atomic tasks created with proper nesting
- [ ] **Production Ready Planning**: Health domain includes complete infrastructure stack
- [ ] **Development Ready**: Flows and tasks enable immediate parallel development
- [ ] **Quality Standards**: All tasks follow established prompt templates and BDD patterns
- [ ] **Team Coordination**: Clear dependencies and estimates enable effective team planning

Begin by reading all memory files, querying Linear project context, and analyzing the Go reference project to understand the complete architecture before creating any Linear flows or tasks.
```

## Implementation Agent Prompt Templates

### Memory Management Agent Prompts

#### Strategic Planning Template
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
- .claude/coordinationContext.md - Task coordination framework
- .claude/testingContext.md - BDD testing integration
- .claude/TechDebt.md - Technical debt registry and status
- .claude/bddWorkflows.md - BDD workflow patterns

## Project Context Summary
**Python FastAPI SQLModel Template System**:
- **Purpose**: General-purpose backend template system (not domain-specific)
- **Architecture**: Hexagonal architecture with FastAPI + SQLModel + PostgreSQL
- **Goal**: YAML-driven code generation similar to Go template system at `/templates/projects/go_backend_gorm/`
- **Test Case**: Template will be validated by generating real applications

## Task Objectives
[Specific strategic objectives and deliverables]

## Analysis Requirements
- **Go Template Analysis**: Extract patterns from `/templates/projects/go_backend_gorm/`
- **Python Architecture Design**: Design FastAPI + SQLModel equivalent
- **Code Generation Strategy**: Plan template processing and file generation
- **Quality Standards**: Define success criteria and validation approaches

## Success Criteria
[Measurable outcomes and validation approaches]

## Memory Update Requirements
- Update .claude/activeContext.md with current decisions and progress
- Update .claude/progress.md with milestone status and next steps
- Document any new patterns in .claude/systemPatterns.md
- Log any technical debt in .claude/TechDebt.md

## Coordination Requirements
- Create detailed implementation prompts for BDD Implementation Agent
- Define clear task breakdown with acceptance criteria
- Specify quality gates and validation requirements
- Plan integration testing and validation approach
```

#### Architecture Decision Template
```markdown
# Architecture Decision: [DECISION_NAME]

## Memory Context Requirements
**Read for architectural context**:
- .claude/systemPatterns.md - Current architecture patterns
- .claude/techContext.md - Technology constraints and decisions
- .claude/productContext.md - Solution requirements and constraints

## Decision Context
**Problem Statement**: [Clear description of architectural challenge]
**Constraints**: [Technical, business, or timeline constraints]
**Alternatives Considered**: [Options evaluated with pros/cons]

## Go Template Reference Analysis
**Reference Implementation**: `/templates/projects/go_backend_gorm/`
**Key Patterns to Analyze**:
- [Specific patterns relevant to decision]
- [Architecture components to evaluate]
- [Implementation strategies to consider]

## Decision Criteria
- **Technical Quality**: [Specific quality requirements]
- **Development Experience**: [Developer usability requirements]
- **Maintainability**: [Long-term maintenance considerations]
- **Performance**: [Performance requirements and implications]

## Recommended Approach
[Detailed recommendation with rationale]

## Implementation Impact
- **Files Affected**: [List of components that need changes]
- **Integration Points**: [Dependencies and integration requirements]
- **Testing Strategy**: [How to validate the decision]
- **Documentation Updates**: [Required documentation changes]

## Memory Updates Required
- Update .claude/systemPatterns.md with new architecture patterns
- Update .claude/activeContext.md with decision and rationale
- Update .claude/techContext.md if technology choices affected
- Log implementation tasks in .claude/progress.md
```

### BDD Implementation Agent Prompts

#### Template Implementation Template
```markdown
# BDD Implementation Task: [TEMPLATE_NAME] Template

## Memory Context Requirements
**Read these files for implementation context**:
- .claude/systemPatterns.md - Architecture patterns for implementation
- .claude/techContext.md - Technology stack and configuration details
- .claude/activeContext.md - Current implementation state and decisions
- .claude/testingContext.md - BDD testing approaches and patterns
- .claude/bddWorkflows.md - BDD implementation workflow requirements

## Go Template Reference
**Analyze Reference Implementation**: `/templates/projects/go_backend_gorm/`
**Specific Files to Study**:
- [List specific Go template files relevant to this implementation]
- [Directory structure to replicate]
- [Patterns to extract and adapt for Python]

## Template Requirements
**Template Purpose**: [Clear description of what this template generates]
**Target Architecture Layer**: [Domain/Application/Infrastructure/Interface]
**Placeholder Support**: Must support {{DOMAIN}}, {{domain}}, {{DOMAIN_PLURAL}}, {{domain_plural}}
**Code Preservation**: Must include @pyhex:begin/@pyhex:end markers for custom code

## BDD Scenarios
```gherkin
Feature: [Template Name] Generation
  As a developer using the template system
  I want to generate [specific component] from YAML configuration
  So that I can [business value]

Scenario: Generate [Component] from Simple Configuration
  Given I have a YAML configuration for a simple domain
  When I run the template generation for [component]
  Then it should create [specific files]
  And the generated code should [specific behavior]
  And the code should pass all quality checks

Scenario: Generate [Component] with Relationships
  Given I have a YAML configuration with entity relationships
  When I run the template generation for [component]
  Then it should properly handle relationship references
  And the generated code should support relationship operations
  And all relationship constraints should be enforced

Scenario: Preserve Custom Code During Regeneration
  Given I have generated [component] with custom code in preservation blocks
  When I regenerate with updated configuration
  Then my custom code should be preserved
  And the updated configuration should be applied
  And all tests should still pass
```

## Implementation Standards
**Code Quality**:
- Follow Python type hints throughout
- Use modern FastAPI patterns and best practices
- Implement proper error handling and validation
- Include comprehensive docstrings

**Template Quality**:
- Clear, readable Jinja2 template syntax
- Proper placeholder handling for all variations
- Consistent code formatting in generated output
- Support for both simple and complex configurations

**Architecture Compliance**:
- Follow hexagonal architecture principles
- Proper dependency injection patterns
- Clear separation of concerns
- Consistent naming conventions

## Testing Requirements
**Template Testing**:
- Unit tests for template processing logic
- Integration tests for complete generation workflow
- Validation tests for generated code quality
- Performance tests for generation speed

**Generated Code Testing**:
- Generated code should include comprehensive test suites
- Tests should follow BDD patterns with clear scenarios
- All generated functionality should be tested
- Integration tests for API endpoints

## File Structure Requirements
```
templates/
└── [component_name]/
    ├── [file_name].py.jinja2     # Main template file
    ├── tests/
    │   └── test_[component].py.jinja2  # Test template
    └── docs/
        └── [component]_usage.md.jinja2  # Documentation template
```

## Validation Steps
1. **Template Syntax**: Verify Jinja2 template syntax is correct
2. **Placeholder Handling**: Test all placeholder variations work
3. **Generated Code Quality**: Validate output passes linting and type checking
4. **BDD Compliance**: Ensure all scenarios pass
5. **Integration Testing**: Verify integration with other generated components

## Success Criteria
- [ ] Template generates syntactically correct Python code
- [ ] All placeholder variations are properly handled
- [ ] Generated code follows established architecture patterns
- [ ] BDD scenarios pass completely
- [ ] Code preservation system works correctly
- [ ] Performance meets generation speed requirements
- [ ] Documentation is complete and accurate

## Memory Updates Required
- Update .claude/progress.md with implementation status
- Document any new patterns discovered in .claude/systemPatterns.md
- Log any technical debt or shortcuts in .claude/TechDebt.md
- Update .claude/testingContext.md with new testing patterns
```

#### Code Generation Tool Template
```markdown
# BDD Implementation Task: Code Generation Tool

## Memory Context Requirements
**Essential Reading**:
- .claude/systemPatterns.md - Code generation patterns and architecture
- .claude/techContext.md - Technology stack and tool requirements
- .claude/coordinationContext.md - Tool integration requirements

## Go Reference Analysis
**Study Reference Tool**: `/templates/projects/go_backend_gorm/cmd/standardize/`
**Key Components to Analyze**:
- main.go - CLI interface and command structure
- internal/generator.go - Core generation logic
- internal/config.go - YAML configuration processing
- internal/template_data.go - Template data preparation
- internal/utils.go - Utility functions

## Tool Requirements
**CLI Interface**: Python Click-based command line tool
**Configuration**: YAML processing with validation
**Template Engine**: Jinja2 integration for placeholder replacement
**File Generation**: Organized output with proper directory structure
**Code Preservation**: Extract and restore custom code blocks

## BDD Scenarios
```gherkin
Feature: Domain Generation Tool
  As a developer
  I want to generate complete domain implementations from YAML
  So that I can rapidly create backend applications

Scenario: Generate Domain from YAML Configuration
  Given I have a valid YAML domain configuration
  When I run the generation tool with the configuration
  Then it should create all specified domain files
  And the generated application should run without errors
  And all generated tests should pass

Scenario: Validate Configuration Before Generation
  Given I have an invalid YAML configuration
  When I run the generation tool
  Then it should display clear validation errors
  And it should not create any partial files
  And it should provide guidance on fixing the configuration

Scenario: Handle Code Preservation During Regeneration
  Given I have previously generated a domain with custom code
  When I regenerate with an updated configuration
  Then existing custom code should be preserved
  And new configuration changes should be applied
  And the result should be syntactically correct
```

## Implementation Architecture
```python
# Tool structure
cmd/
└── generate/
    ├── __init__.py
    ├── main.py              # CLI entry point with Click
    ├── config.py            # YAML configuration processing
    ├── generator.py         # Core generation logic
    ├── template_engine.py   # Jinja2 template processing
    ├── file_manager.py      # File generation and organization
    ├── code_preservation.py # Custom code extraction/restoration
    └── validation.py        # Configuration and output validation
```

## Core Components

### CLI Interface (main.py)
```python
import click
from pathlib import Path
from .generator import DomainGenerator
from .config import ConfigurationProcessor

@click.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to YAML configuration file')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output directory for generated code')
@click.option('--force', '-f', is_flag=True,
              help='Overwrite existing files')
@click.option('--preserve-custom', '-p', is_flag=True, default=True,
              help='Preserve custom code during regeneration')
def generate(config: str, output: str, force: bool, preserve_custom: bool):
    """Generate FastAPI application from YAML configuration."""
    # Implementation here
```

### Configuration Processing (config.py)
- YAML parsing and validation
- Schema validation against defined structure
- Default value application
- Configuration transformation for template use

### Template Engine (template_engine.py)
- Jinja2 environment setup
- Template loading and processing
- Placeholder replacement logic
- Code formatting and validation

### Code Preservation (code_preservation.py)
- Extract custom code blocks before regeneration
- Restore custom code after template processing
- Validate preservation markers
- Handle merge conflicts

## Quality Requirements
- **Error Handling**: Comprehensive error messages and recovery
- **Performance**: Fast generation for large configurations
- **Reliability**: Consistent output across multiple runs
- **Usability**: Clear CLI interface with helpful documentation

## Testing Strategy
- **Unit Tests**: Each component tested in isolation
- **Integration Tests**: Complete generation workflows
- **CLI Tests**: Command-line interface testing
- **Performance Tests**: Generation speed benchmarks

## Success Criteria
- [ ] Tool generates working FastAPI applications from YAML
- [ ] Configuration validation provides clear error messages
- [ ] Code preservation works reliably during regeneration
- [ ] CLI interface is intuitive and well-documented
- [ ] Performance meets speed requirements
- [ ] All BDD scenarios pass
- [ ] Tool integrates properly with development workflow

## Integration Requirements
- **Template System**: Works with all template files
- **Development Workflow**: Integrates with IDE and build tools
- **CI/CD**: Can be automated in deployment pipelines
- **Documentation**: Auto-generates usage documentation
```

### Quickfire Agent Prompts

#### Minor Template Fix Template
```markdown
# Quickfire Task: [SPECIFIC_FIX]

## Quick Context Check
**Essential Reading**:
- .claude/activeContext.md - Current project state
- .claude/systemPatterns.md - Relevant architecture patterns

## Task Description
**Issue**: [Specific problem to fix]
**Scope**: [Limited scope - file/function level change]
**Expected Impact**: [Minimal, focused change]

## Implementation Approach
- **Files to Modify**: [Specific files]
- **Changes Required**: [Specific changes]
- **Validation**: [How to verify fix works]

## Quality Checklist
- [ ] Change follows established patterns
- [ ] No architecture violations introduced
- [ ] Generated code still passes quality checks
- [ ] Change is minimal and focused

## Validation Steps
1. [Specific validation step 1]
2. [Specific validation step 2]
3. [Specific validation step 3]

## Technical Debt Check
- [ ] No shortcuts or compromises made
- [ ] No new technical debt introduced
- [ ] Change improves or maintains code quality
```

### Configuration Update Template
```markdown
# Quickfire Task: Configuration Update

## Context
**Configuration File**: [Specific configuration file]
**Change Required**: [Specific configuration change]
**Reason**: [Why this change is needed]

## Current Configuration Analysis
**File Location**: [Path to configuration file]
**Current Settings**: [Relevant current settings]
**Dependencies**: [Other configurations that might be affected]

## Proposed Changes
```yaml
# Before
[current configuration]

# After  
[updated configuration]
```

## Validation Requirements
- [ ] Configuration syntax is valid
- [ ] All dependent configurations remain compatible
- [ ] Generated applications work with new configuration
- [ ] Documentation reflects configuration changes

## Impact Assessment
**Components Affected**: [List of affected components]
**Testing Required**: [Specific testing needed]
**Documentation Updates**: [Required documentation changes]
```

## Quality Assurance Templates

### Code Review Prompt Template
```markdown
# Code Review: [COMPONENT_NAME]

## Review Context
**Component**: [Specific component being reviewed]
**Implementation Type**: [Template/Tool/Configuration]
**Complexity Level**: [Simple/Medium/Complex]

## Memory Context Check
**Reviewer Must Read**:
- .claude/systemPatterns.md - Architecture compliance
- .claude/techContext.md - Technology standards
- .claude/testingContext.md - Testing requirements

## Review Checklist

### Architecture Compliance
- [ ] Follows hexagonal architecture principles
- [ ] Proper layer separation maintained
- [ ] Dependencies point inward toward domain
- [ ] No architecture violations introduced

### Code Quality
- [ ] Type hints used throughout
- [ ] Proper error handling implemented
- [ ] Code follows Python best practices
- [ ] Docstrings are comprehensive and clear

### Template Quality (if applicable)
- [ ] Jinja2 syntax is correct and efficient
- [ ] All placeholder variations handled
- [ ] Generated code is properly formatted
- [ ] Code preservation markers properly placed

### Testing Coverage
- [ ] Adequate test coverage for functionality
- [ ] BDD scenarios cover expected behavior
- [ ] Edge cases and error conditions tested
- [ ] Performance implications considered

### Documentation
- [ ] Code is self-documenting
- [ ] Complex logic is explained
- [ ] Usage examples provided
- [ ] Integration points documented

## Performance Review
- [ ] Generation speed is acceptable
- [ ] Memory usage is reasonable
- [ ] No obvious performance bottlenecks
- [ ] Scalability considerations addressed

## Security Review
- [ ] No hardcoded secrets or sensitive data
- [ ] Input validation is comprehensive
- [ ] Generated code follows security best practices
- [ ] No injection vulnerabilities possible

## Integration Review
- [ ] Works correctly with existing components
- [ ] No breaking changes to public interfaces
- [ ] Backward compatibility maintained
- [ ] Dependencies are appropriate

## Recommendations
**Strengths**: [What works well]
**Improvements**: [Specific suggestions for improvement]
**Action Items**: [Required changes before approval]
```

### Release Readiness Template
```markdown
# Release Readiness Assessment: [VERSION]

## Quality Gate Checklist

### Functionality
- [ ] All planned features implemented
- [ ] All BDD scenarios pass
- [ ] Generated applications work correctly
- [ ] Code generation tool functions properly

### Testing
- [ ] Unit test coverage > 95%
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Performance tests meet requirements

### Documentation
- [ ] User documentation complete
- [ ] API documentation generated
- [ ] Installation instructions tested
- [ ] Example configurations provided

### Quality
- [ ] Code passes all linting checks
- [ ] Type checking passes without errors
- [ ] Security scan shows no issues
- [ ] Performance benchmarks meet targets

### Integration
- [ ] Works with latest Python version
- [ ] Compatible with target databases
- [ ] CI/CD pipeline passes
- [ ] Docker containers build successfully

## Risk Assessment
**Known Issues**: [List any known issues and workarounds]
**Compatibility**: [Compatibility considerations]
**Migration**: [Migration requirements from previous versions]

## Release Recommendation
**Ready for Release**: [Yes/No with rationale]
**Blocking Issues**: [Any issues that must be resolved]
**Post-Release Plan**: [Monitoring and support plan]
```

These prompt templates ensure consistent, high-quality implementations across all agents working on the Python FastAPI SQLModel template system while maintaining proper memory integration and BDD compliance.