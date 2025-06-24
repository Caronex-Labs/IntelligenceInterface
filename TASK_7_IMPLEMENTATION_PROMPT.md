# Task 7: Production Codebase Cleanup - Implementation Prompt

## Memory Context Requirements (MANDATORY - READ ALL BEFORE IMPLEMENTATION)

### Foundation Files (Read First):
- `.claude/projectbrief.md` - Core project mission and Intelligence Interface meta-system goals
- `.claude/productContext.md` - Problem context and solution architecture
- `.claude/systemPatterns.md` - Architecture patterns and design decisions
- `.claude/techContext.md` - Technology stack and setup requirements

### Coordination Files (Read Second):
- `.claude/activeContext.md` - Current focus and Sprint 1 completion status
- `.claude/progress.md` - Implementation status and final sprint state
- `.claude/coordinationContext.md` - Task coordination framework
- `.claude/testingContext.md` - BDD testing integration

### Implementation Files (Read Third):
- `CLAUDE.md` - Critical implementation patterns and BDD rules (project root)
- `.claude/bddWorkflows.md` - BDD workflow patterns and templates
- `.claude/implementationLogs.md` - All task insights and implementation learnings
- `.claude/qualityFeedback.md` - Quality patterns from all completed tasks
- `sprints/Sprint1.md` - Complete Sprint 1 context and task details

### Testing Standards (Read Fourth):
- `templates/testing/README.md` - Comprehensive testing framework and patterns
- `templates/testing/TESTING_REFERENCE.md` - Quick reference for testing standards
- `.claude/TechDebt.md` - Technical debt management requirements

## Task Definition

### Goal
Perform comprehensive production-ready cleanup of the Intelligence Interface codebase, removing all unused files, duplicate structures, dead code, and ensuring the codebase is optimized for production deployment.

### Scope
Complete cleanup and optimization including: old directory structure removal, dead code elimination, unused import cleanup, documentation consistency, configuration optimization, and production readiness validation.

## BDD Scenarios (IMPLEMENT ALL SCENARIOS)

```gherkin
Feature: Production Codebase Cleanup
  As a development team
  I want a clean, production-ready codebase
  So that the Intelligence Interface system is optimized, maintainable, and deployment-ready

  Scenario: Old directory structure cleanup
    Given the codebase has both old and new directory structures from migration
    When I remove all deprecated directory structures
    Then only the new meta-system directory structure should remain
    And no duplicate code should exist
    And all imports should reference new structure only

  Scenario: Dead code elimination
    Given the codebase may contain unused functions, variables, and imports
    When I analyze and remove all dead code
    Then only actively used code should remain
    And all imports should be necessary and used
    And no unreachable code should exist

  Scenario: Configuration optimization
    Given the configuration system may have unused or duplicate settings
    When I optimize configuration files and structures
    Then only necessary configuration options should remain
    And configuration should be properly documented
    And default values should be appropriate for production

  Scenario: Documentation consistency
    Given documentation may be outdated or inconsistent after migration
    When I review and update all documentation
    Then all documentation should reflect current architecture
    And code comments should be accurate and necessary
    And API documentation should be complete

  Scenario: Production readiness validation
    Given the cleaned codebase should be production-ready
    When I validate the system for production deployment
    Then all builds should succeed without warnings
    And all tests should pass consistently
    And performance should be optimized
    And security best practices should be followed
```

## Technical Analysis

### Current Architecture Assessment

**Cleanup Target Areas**:
- **Old Directory Structure**: `internal/config/`, `internal/logging/`, `internal/message/`, `internal/llm/`, `internal/app/`
- **Duplicate Code**: Functions and structures that exist in both old and new locations
- **Unused Imports**: Import statements that are no longer necessary
- **Dead Code**: Unreachable functions, unused variables, commented-out code
- **Configuration Cleanup**: Unused config options, deprecated settings

**Production Readiness Requirements**:
- Zero build warnings or errors
- All tests passing consistently
- Optimized binary size
- Clean import trees
- Proper error handling
- Security validation
- Performance optimization

## Requirements

### Functional Requirements
1. **Directory Structure Cleanup**: Remove all old directories and duplicate structures
2. **Dead Code Elimination**: Remove unused functions, variables, and imports
3. **Configuration Optimization**: Clean and optimize configuration system
4. **Documentation Consistency**: Update all documentation to reflect current state
5. **Production Validation**: Ensure system is production-ready

### Technical Requirements
1. **Build Optimization**: Zero warnings, minimal binary size
2. **Import Cleanup**: Remove all unused imports, organize remaining imports
3. **Code Quality**: Ensure all code follows established patterns
4. **Test Validation**: All tests must pass after cleanup
5. **Performance Check**: Validate no performance regressions

### Quality Requirements
1. **BDD Compliance**: All 5 scenarios must be implemented and passing
2. **Zero Regressions**: All functionality must be preserved
3. **Code Quality**: Follow CLAUDE.md patterns and established conventions
4. **Documentation Quality**: All documentation accurate and up-to-date
5. **Production Standards**: Meet production deployment requirements

## Implementation Strategy

### Phase 1: Analysis & Planning (30 minutes)
1. **Comprehensive Code Analysis**: Scan entire codebase for cleanup opportunities
2. **Dependency Mapping**: Map all imports and dependencies
3. **Dead Code Identification**: Identify unused functions, variables, and imports
4. **Cleanup Plan Creation**: Create systematic cleanup plan with validation steps

### Phase 2: Directory Structure Cleanup (45 minutes)
1. **Old Directory Removal**: Systematically remove old directory structures
2. **Import Path Updates**: Update any remaining references to old paths
3. **Duplicate Code Elimination**: Remove duplicate functions and structures
4. **Build Validation**: Ensure builds succeed after each cleanup step

### Phase 3: Dead Code Elimination (40 minutes)
1. **Unused Import Removal**: Remove all unused import statements
2. **Dead Function Removal**: Remove unreachable and unused functions
3. **Variable Cleanup**: Remove unused variables and constants
4. **Comment Cleanup**: Remove outdated comments and commented-out code

### Phase 4: Configuration & Documentation (35 minutes)
1. **Configuration Optimization**: Clean and optimize configuration structures
2. **Documentation Updates**: Update all documentation for consistency
3. **API Documentation**: Ensure all APIs are properly documented
4. **README Updates**: Update project documentation

### Phase 5: Production Readiness Validation (30 minutes)
1. **Build Optimization**: Minimize binary size and build warnings
2. **Test Validation**: Ensure all tests pass consistently
3. **Performance Validation**: Check for performance regressions
4. **Security Review**: Validate security best practices

## Cleanup Specifications

### Directory Structure Cleanup

#### Directories to Remove
- `internal/config/` → use `internal/core/config/`
- `internal/logging/` → use `internal/core/logging/`
- `internal/message/` → use `internal/core/models/`
- `internal/llm/agent/` → use `internal/agents/base/`
- `internal/llm/prompt/` → use `internal/agents/builtin/`
- `internal/llm/tools/` → use `internal/tools/builtin/`
- `internal/app/` → use `internal/services/`
- `internal/permission/` → use `internal/infrastructure/permissions/`
- `internal/pubsub/` → use `internal/infrastructure/pubsub/`
- `internal/db/` → use `internal/infrastructure/database/`

#### Validation Steps
- Verify no imports reference old directories
- Ensure all functionality is available in new locations
- Validate all tests pass after removal
- Confirm build succeeds without warnings

### Dead Code Analysis

#### Code Analysis Tools
- Use `go mod tidy` to clean dependencies
- Use `goimports` to clean import statements
- Use `go vet` to identify potential issues
- Manual review for unreachable code

#### Cleanup Targets
- Unused import statements
- Unreachable functions
- Unused variables and constants
- Commented-out code blocks
- Obsolete helper functions

### Configuration Optimization

#### Configuration Cleanup
- Remove unused configuration options
- Optimize default values for production
- Ensure all configuration is documented
- Validate configuration loading performance

#### Documentation Updates
- Update all code comments for accuracy
- Ensure API documentation is complete
- Update README.md with current information
- Validate all examples work correctly

## Testing Requirements

### BDD Test Implementation
- **Framework**: Use existing Godog BDD infrastructure in `test/bdd/`
- **Test File**: Create `test/bdd/features/production_cleanup.feature`
- **Step Definitions**: Implement in `test/bdd/steps/cleanup_steps.go`
- **Configuration**: Follow test configuration patterns from `templates/testing/`

### Cleanup Validation Tests
- **Build Tests**: Verify builds succeed without warnings
- **Import Tests**: Validate all imports are necessary and used
- **Functionality Tests**: Ensure all features work after cleanup
- **Performance Tests**: Validate no performance regressions

### Production Readiness Tests
- **Binary Size**: Verify optimized binary size
- **Startup Performance**: Test application startup time
- **Memory Usage**: Validate memory usage patterns
- **Security Validation**: Check for security best practices

## Code Quality Standards

### Architecture Patterns (from CLAUDE.md)
- **Meta-System Architecture**: Ensure cleanup supports meta-system evolution
- **Agent-Everything System**: Validate agent system integrity
- **Caronex-Orchestrated Architecture**: Ensure Caronex coordination works
- **Configuration Cascade**: Maintain configuration system performance

### Implementation Standards
- **Zero Build Warnings**: All builds must succeed without warnings
- **Clean Import Trees**: All imports must be necessary and organized
- **Performance Optimization**: No performance regressions allowed
- **Security Compliance**: Follow security best practices

### Code Style Requirements
- **No Comments**: Follow CLAUDE.md directive (only necessary comments)
- **Consistent Naming**: Maintain naming consistency across codebase
- **Import Organization**: Clean and organized import statements
- **Production Quality**: Code ready for production deployment

## Technical Debt Management

### Pre-Implementation
- [ ] Read `.claude/TechDebt.md` to understand all current technical debt
- [ ] Update TD-2025-06-15-005 status to reflect actual current state
- [ ] Plan cleanup to address all remaining technical debt

### During Implementation
- [ ] Log any issues discovered during cleanup in `.claude/TechDebt.md`
- [ ] Document any cleanup decisions that might impact future development
- [ ] Note any performance optimizations or improvements made

### Post-Implementation
- [ ] Update `.claude/TechDebt.md` with final technical debt status
- [ ] Mark all cleanup-related technical debt as resolved
- [ ] Document production readiness status and any remaining considerations

## Success Criteria

### Functional Success
- [ ] All old directory structures completely removed
- [ ] No duplicate code exists in the codebase
- [ ] All dead code and unused imports eliminated
- [ ] Configuration system optimized for production
- [ ] All documentation updated and consistent

### Quality Success
- [ ] All 5 BDD scenarios implemented and passing
- [ ] Build succeeds without any warnings or errors
- [ ] All existing tests continue passing
- [ ] Performance meets or exceeds baseline
- [ ] Code follows all established patterns and conventions

### Production Readiness Success
- [ ] Binary size optimized for deployment
- [ ] Startup performance meets production requirements
- [ ] Memory usage optimized
- [ ] Security best practices validated
- [ ] System ready for production deployment

## Documentation Requirements

### Code Documentation
- **Cleanup Documentation**: Document all cleanup decisions and rationale
- **Architecture Updates**: Update architecture documentation
- **API Documentation**: Ensure all APIs are properly documented

### Production Documentation
- **Deployment Guide**: Update deployment documentation
- **Production Configuration**: Document production configuration options
- **Performance Guide**: Document performance characteristics

### Development Documentation
- **Cleanup Patterns**: Document reusable cleanup patterns
- **Production Standards**: Document production readiness standards
- **Maintenance Guide**: Document ongoing maintenance requirements

## Memory Integration Protocol

### Implementation Feedback (MANDATORY)
Document the following in `.claude/implementationLogs.md`:

1. **Cleanup Approach**: How you approached comprehensive codebase cleanup
2. **Architecture Discoveries**: Insights about system architecture and organization
3. **Dead Code Analysis**: Findings about unused code and optimization opportunities
4. **Technical Challenges**: Cleanup challenges and solutions implemented
5. **Production Insights**: Discoveries about production readiness requirements
6. **Performance Impact**: Analysis of cleanup impact on system performance

### Quality Assessment (MANDATORY)
Document the following in `.claude/qualityFeedback.md`:

1. **Cleanup Quality**: Assessment of cleanup thoroughness and effectiveness
2. **Code Quality Impact**: How cleanup improved overall code quality
3. **Production Readiness**: Assessment of system production readiness
4. **Performance Impact**: Analysis of performance improvements from cleanup
5. **Maintainability**: How cleanup improved system maintainability
6. **Future Recommendations**: Suggestions for ongoing code quality maintenance

### Memory Updates (MANDATORY)
1. **Update `.claude/activeContext.md`**: Mark Task 7 as completed and update project status
2. **Update `.claude/progress.md`**: Document Task 7 completion and production readiness
3. **Update `CLAUDE.md`**: Document production cleanup patterns and standards
4. **Update Sprint 1 Status**: Mark Sprint 1 as 100% complete with production readiness
5. **Update `.claude/TechDebt.md`**: Final technical debt status with all items resolved

## Implementation Validation

### Build Validation
```bash
# Verify clean build with no warnings
go build -o ii

# Check for any build warnings
go build -v -o ii 2>&1 | grep -i warning

# Validate binary size optimization
ls -lh ii

# Test application functionality
go run main.go --help
go run main.go --version
```

### Code Quality Validation
```bash
# Clean up dependencies
go mod tidy

# Format code
go fmt ./...

# Organize imports
goimports -w .

# Validate code quality
go vet ./...

# Run all tests
go test ./...

# Run with race detection
go test -race ./...
```

### Production Readiness Validation
```bash
# Build for production
go build -ldflags="-s -w" -o ii

# Test memory usage
go test -memprofile=mem.prof ./...

# Test CPU usage
go test -cpuprofile=cpu.prof ./...

# Security check (if available)
gosec ./...
```

## Post-Implementation Tasks

### Immediate Tasks
1. **Final Commit**: Create comprehensive git commit documenting production cleanup
2. **Documentation Updates**: Ensure all documentation reflects cleaned state
3. **Memory Synchronization**: Update all memory files with production readiness status
4. **Quality Assessment**: Complete comprehensive quality assessment

### Production Preparation Tasks
1. **Deployment Documentation**: Update deployment guides and procedures
2. **Performance Baselines**: Document performance characteristics
3. **Monitoring Setup**: Prepare monitoring and observability configurations
4. **Release Preparation**: Prepare for production release

---

## Task Coordination Note

This task completes Sprint 1 by achieving 100% completion with production-ready codebase. The implementation should focus on comprehensive cleanup while maintaining all functionality and ensuring the system is optimized for production deployment.

**Dependencies**: All previous Sprint 1 tasks (1-6) should be completed before starting this task.
**Sprint Impact**: Completes Sprint 1 at 100% with production readiness achieved.
**Next Phase**: System ready for production deployment and future sprint development.

The cleanup should maintain the high quality standards established throughout Sprint 1 while preparing the Intelligence Interface meta-system for production use and future evolution.