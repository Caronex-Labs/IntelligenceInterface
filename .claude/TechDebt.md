# Technical Debt Registry

## Overview

This file tracks technical debt across the Intelligence Interface project. All developers and agents must log technical
debt items here when they are identified during development, code review, or maintenance activities.

**Last Updated**: 2025-06-15  
**Total Items**: 4 (2 resolved)  
**High Priority**: 1 | **Medium Priority**: 2 | **Low Priority**: 0

## Memory Assimilation Status (2025-06-15)
**Memory Assimilation for Sprint 1 Phase 1 Task 1 completed**: All tech debt items reviewed and validated against implementation reality. Status confirmed accurate with priority adjustments based on current system state.

## How to Use This File

### **When to Log Tech Debt**

- When implementing a quick fix that needs a proper solution later
- When skipping tests due to time constraints
- When identifying missing documentation
- When noticing performance issues
- When finding architectural improvements needed
- When discovering code that violates established patterns

### **Entry Format**

```markdown
### [Category] - [Brief Description]

- **ID**: TD-YYYY-MM-DD-### (e.g., TD-2025-01-15-001)
- **Priority**: High/Medium/Low
- **Type**: [Category from sections below]
- **Component**: [Affected system/file]
- **Description**: [Detailed description of the debt]
- **Impact**: [How this affects the system]
- **Proposed Solution**: [Suggested approach to resolve]
- **Effort Estimate**: [Time required to fix]
- **Logged By**: [Developer/Agent name]
- **Date Logged**: [Date]
- **Target Resolution**: [Sprint/Date when this should be addressed]
- **Status**: Open/In Progress/Resolved
```

## Technical Debt Categories

### **1. Dirty Fixes**

> Quick hacks and workarounds that need proper solutions

*No items currently logged*

#### **Template Entry**

```markdown
### Dirty Fix - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Dirty Fix
- **Component**: [File/System affected]
- **Description**: [What hack was implemented and why]
- **Impact**: [Maintenance issues, code clarity problems, etc.]
- **Proposed Solution**: [Proper implementation approach]
- **Effort Estimate**: [Hours/Days]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [When this should be fixed]
- **Status**: Open
```

### **2. Missing Tests**

> Code lacking proper test coverage or test quality issues

### Missing Tests - Permission Service Test Missing Import

- **ID**: TD-2025-06-15-001
- **Priority**: High
- **Type**: Missing Tests
- **Component**: internal/permission/permission_test.go
- **Description**: Permission test file is missing import statement for pubsub package, causing test compilation failures
- **Impact**: Tests cannot run, no test coverage for permission system functionality
- **Proposed Solution**: Add missing import "github.com/opencode-ai/opencode/internal/pubsub" to permission_test.go
- **Effort Estimate**: 5 minutes
- **Logged By**: BDD Implementation Agent
- **Date Logged**: 2025-06-15
- **Target Resolution**: Immediate (during directory migration)
- **Status**: Resolved
- **Resolved By**: BDD Implementation Agent
- **Date Resolved**: 2025-06-15
- **Resolution**: Added missing pubsub import statement during directory migration

### Missing Tests - LLM Prompt Test Configuration Issues

- **ID**: TD-2025-06-15-002
- **Priority**: High  
- **Type**: Missing Tests
- **Component**: internal/llm/prompt/prompt_test.go
- **Description**: Prompt test fails with "no valid provider available for agent coder" - missing test configuration setup
- **Impact**: LLM prompt functionality cannot be properly tested, reduces confidence in AI agent behavior
- **Proposed Solution**: Add proper test configuration setup or mock provider for testing environment
- **Effort Estimate**: 30 minutes
- **Logged By**: BDD Implementation Agent
- **Date Logged**: 2025-06-15
- **Target Resolution**: During directory migration (Task 4 - Agent System Transformation)
- **Status**: Open

### Missing Tests - Tools Test Configuration Dependency

- **ID**: TD-2025-06-15-003
- **Priority**: Medium
- **Type**: Missing Tests
- **Component**: internal/llm/tools/ls_test.go
- **Description**: Tool tests fail with "config not loaded" panic - missing test setup for configuration dependency
- **Impact**: Tool functionality cannot be properly tested, affects reliability of file system operations
- **Proposed Solution**: Add proper test configuration initialization or dependency injection for tools testing
- **Effort Estimate**: 20 minutes
- **Logged By**: BDD Implementation Agent
- **Date Logged**: 2025-06-15
- **Target Resolution**: During directory migration (Task 5 - Tool System Consolidation)
- **Status**: Open

### Missing Tests - Git Repository Not Initialized

- **ID**: TD-2025-06-15-004
- **Priority**: Medium
- **Type**: Migration Debt
- **Component**: Project Root
- **Description**: Project is not a git repository, preventing version control tracking of directory migration changes
- **Impact**: Cannot track migration changes, no commit history, no rollback capability
- **Proposed Solution**: Initialize git repository with `git init`, add initial commit for baseline
- **Effort Estimate**: 10 minutes
- **Logged By**: BDD Implementation Agent
- **Date Logged**: 2025-06-15
- **Target Resolution**: Immediate (next sprint task)
- **Status**: Resolved
- **Resolved By**: BDD Implementation Agent
- **Date Resolved**: 2025-06-15
- **Resolution**: Git repository successfully initialized with comprehensive .gitignore and initial commit (0b7ede5) capturing complete project state after directory migration completion. Git workflow validated with test commit and rollback functionality confirmed.

### Migration Debt - Old Directory Structure Cleanup

- **ID**: TD-2025-06-15-005
- **Priority**: Medium
- **Type**: Migration Debt
- **Component**: internal/ directory structure
- **Description**: Old directory structure still exists alongside new structure, creating duplication and potential confusion
- **Impact**: Code duplication, import confusion, increased codebase size, maintenance overhead
- **Proposed Solution**: Systematically remove old directories: internal/config/, internal/logging/, internal/message/, internal/llm/prompt/, internal/llm/agent/, internal/llm/tools/, internal/app/
- **Effort Estimate**: 30 minutes
- **Logged By**: BDD Implementation Agent
- **Date Logged**: 2025-06-15
- **Target Resolution**: Phase 10 - Documentation & Cleanup (per MigrationMapping.md)
- **Status**: Open

#### **Template Entry**

```markdown
### Missing Tests - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Missing Tests
- **Component**: [File/Function needing tests]
- **Description**: [What needs testing and current coverage gap]
- **Impact**: [Risk of regressions, deployment confidence issues]
- **Proposed Solution**: [Test strategy and coverage plan]
- **Effort Estimate**: [Hours/Days]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [Sprint/Timeline]
- **Status**: Open
```

### **3. Additional Features**

> Planned enhancements and feature improvements

#### **Template Entry**

```markdown
### Feature Enhancement - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Additional Feature
- **Component**: [System/Area for enhancement]
- **Description**: [Feature requirements and benefits]
- **Impact**: [User experience improvements, functionality gaps]
- **Proposed Solution**: [Implementation approach]
- **Effort Estimate**: [Story points/Days]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [Future sprint/milestone]
- **Status**: Open
```

### **4. Performance Issues**

> Known performance bottlenecks and optimization opportunities

*No items currently logged*

#### **Template Entry**

```markdown
### Performance Issue - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Performance Issue
- **Component**: [Affected system/function]
- **Description**: [Performance problem and symptoms]
- **Impact**: [User experience, resource usage, scalability]
- **Proposed Solution**: [Optimization strategy]
- **Effort Estimate**: [Hours/Days]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [Timeline]
- **Status**: Open
```

### **5. Documentation Gaps**

> Missing or outdated documentation

*No items currently logged*

#### **Template Entry**

```markdown
### Documentation Gap - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Documentation Gap
- **Component**: [System/Feature needing docs]
- **Description**: [What documentation is missing or outdated]
- **Impact**: [Developer onboarding, maintenance issues]
- **Proposed Solution**: [Documentation plan and scope]
- **Effort Estimate**: [Hours]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [Sprint/Timeline]
- **Status**: Open
```

### **6. Migration Debt**

> Issues specific to OpenCode → Intelligence Interface migration

*No items currently logged*

#### **Template Entry**

```markdown
### Migration Debt - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Migration Debt
- **Component**: [System affected by migration]
- **Description**: [Migration-related technical debt]
- **Impact**: [Architecture coherence, maintainability]
- **Proposed Solution**: [Clean-up or refactoring needed]
- **Effort Estimate**: [Hours/Days]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [Migration phase/sprint]
- **Status**: Open
```

### **7. Architecture Improvements**

> Structural improvements and design pattern updates needed

*No items currently logged*

#### **Template Entry**

```markdown
### Architecture Improvement - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Architecture Improvement
- **Component**: [System/Layer needing improvement]
- **Description**: [Architectural debt and issues]
- **Impact**: [Code maintainability, scalability, clarity]
- **Proposed Solution**: [Refactoring or redesign approach]
- **Effort Estimate**: [Days/Weeks]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [Major refactoring sprint]
- **Status**: Open
```

### **8. Security Concerns**

> Security-related improvements and vulnerability fixes

*No items currently logged*

#### **Template Entry**

```markdown
### Security Concern - [Brief Description]

- **ID**: TD-YYYY-MM-DD-###
- **Priority**: [High/Medium/Low]
- **Type**: Security Concern
- **Component**: [Affected system/code]
- **Description**: [Security issue or improvement needed]
- **Impact**: [Security risk level and scope]
- **Proposed Solution**: [Security improvement plan]
- **Effort Estimate**: [Hours/Days]
- **Logged By**: [Name]
- **Date Logged**: [Date]
- **Target Resolution**: [Immediate/Next sprint]
- **Status**: Open
```

## Tech Debt Management Process

### **Priority Guidelines**

#### **High Priority**

- Security vulnerabilities
- Performance issues affecting user experience
- Dirty fixes in critical paths
- Missing tests for core functionality
- Architecture debt blocking new features

#### **Medium Priority**

- Missing tests for non-critical features
- Documentation gaps for important features
- Performance optimizations for better experience
- Minor architecture improvements
- Feature enhancements with clear user value

#### **Low Priority**

- Code cleanup and refactoring for maintainability
- Nice-to-have documentation improvements
- Feature enhancements with limited impact
- Minor performance optimizations

### **Resolution Process**

1. **Identification**: Log tech debt immediately when discovered
2. **Prioritization**: Assign priority based on impact and urgency
3. **Sprint Planning**: Include high-priority items in sprint planning
4. **Implementation**: Address tech debt during regular development cycles
5. **Validation**: Verify resolution and update status
6. **Removal**: Remove resolved items or move to historical log

### **Regular Reviews**

- **Sprint Planning**: Review high-priority tech debt for inclusion
- **Sprint Retrospectives**: Identify new tech debt and evaluate process
- **Monthly Reviews**: Assess overall tech debt trends and priorities
- **Major Releases**: Comprehensive tech debt cleanup sprints

## Agent Integration

### **For Implementation Agents**

When working on tasks, agents must:

- Check this file for relevant tech debt before starting work
- Log any new tech debt discovered during implementation
- Update tech debt status when resolving issues
- Include tech debt considerations in implementation feedback

### **For Caronex Manager**

- Monitor tech debt trends and prioritize high-impact items
- Coordinate tech debt resolution across implementation agents
- Include tech debt metrics in system health assessments
- Plan tech debt reduction sprints when accumulated debt is high

### **Reporting Templates**

#### **New Tech Debt Discovery**

```markdown
**Tech Debt Identified During [Task/Sprint]:**

- Component: [Affected area]
- Type: [Category]
- Description: [Brief description]
- Recommended Priority: [High/Medium/Low]
- Suggested Timeline: [When to address]
```

#### **Tech Debt Resolution**

```markdown
**Tech Debt Resolved:**

- ID: [Tech debt ID]
- Resolution: [How it was fixed]
- Effort: [Actual time spent]
- Impact: [Improvement achieved]
- Additional Notes: [Lessons learned]
```

## Historical Log

### **Resolved Items**

*Items will be moved here when resolved to maintain history*

### **Rejected Items**

*Items deemed not worth addressing will be moved here with rationale*

---

## Maintenance Notes

- Update summary statistics when adding/resolving items
- Review and update priority guidelines quarterly
- Archive resolved items annually to keep file manageable
- Ensure all team members and agents understand the process

**Remember**: Technical debt is not inherently bad - it's a tool for managing trade-offs. The key is to make conscious
decisions about when to incur debt and have a plan for paying it down.