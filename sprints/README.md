# Neo Group Sprints

This directory contains sprint planning and execution documentation for the New Neo Group SvelteKit project.

## Sprint Organization

### Current Sprint Structure

```
sprints/
├── README.md                           # This file
├── sprint-01-core-cms-email.md         # Current active sprint
└── templates/                          # Sprint templates for future use
```

## Sprint Methodology

### BDD-Driven Sprint Planning

- **Gherkin Scenarios First**: Every task begins with clear behavioral scenarios
- **Test-Driven Development**: Red-Green-Refactor cycle enforced
- **Memory Coordination**: Implementation agents provide structured feedback
- **Quality Gates**: 100% test pass requirement before task completion

### Sprint Phases

1. **Planning**: Requirements analysis and BDD scenario creation
2. **Implementation**: Task execution with mandatory memory integration
3. **Verification**: Evidence-based completion validation
4. **Retrospective**: Feedback analysis and coordination improvement

### Task Numbering Convention

- **X**: Main implementation tasks (1, 2, 3, etc.)
- **X.5**: Quality/reliability completion tasks for substantial leftovers
- **Phases**: Logical groupings by priority and dependencies

## Memory Integration

### Implementation Agent Requirements

- **Memory Context**: All agents must read complete .claude/ memory bank
- **MCP Documentation**: Mandatory validation for non-trivial implementations
- **Feedback Loop**: Structured observations in implementationLogs.md and qualityFeedback.md
- **Quality Documentation**: Testing patterns and insights captured

### Coordination Evolution

- **Real-Time Learning**: Agent feedback improves prompt templates
- **Pattern Discovery**: Architecture insights drive memory bank updates
- **Quality Enhancement**: Testing patterns evolve based on implementation experience

## Sprint Success Metrics

### Completion Criteria

- ✅ All BDD scenarios implemented as passing Playwright tests
- ✅ All existing tests continue to pass
- ✅ Code follows established .clinerules patterns
- ✅ Git commits with proper documentation
- ✅ Implementation feedback provided in memory files
- ✅ MCP documentation validation completed

### Quality Indicators

- **Test Reliability**: Consistent execution without flaky tests
- **Feedback Quality**: Valuable insights for coordination improvement
- **Architecture Compliance**: Adherence to established patterns
- **Performance**: Efficient test execution and code quality

## Current Sprint Status

### Sprint 01: Core CMS + Email System

- **Status**: 60% Complete (Phase 1 finished, Phase 2 pending)
- **Quality**: Excellent - comprehensive feedback and testing established
- **Innovation**: Memory coordination system with real-time agent feedback
- **Next**: Email system implementation with SMTP infrastructure

## Future Sprint Planning

### Upcoming Features

- Advanced search capabilities
- SEO optimization implementation
- Performance monitoring setup
- Analytics integration
- User role management expansion

### Methodology Improvements

- Enhanced BDD workflow patterns based on Sprint 01 learnings
- Improved selector hierarchy for complex UI testing
- Optimized test execution performance
- Refined memory coordination protocols

---

**Sprint Planning Philosophy**: Every sprint should advance both feature development and development methodology quality through comprehensive BDD implementation and memory-coordinated agent feedback.
