# Quickfire Mode - Memory-Integrated Fast Issue Resolution

Efficiently solve multiple issues with targeted fixes while maintaining memory system integration for quality and coordination.

## Memory-Light Integration Pattern

### Essential Memory Files (Quick Read)

- `CLAUDE.md` - Critical architecture patterns only (in project root)
- `.claude/activeContext.md` - Current focus areas
- Skip full memory context for speed, but ensure consistency

## Workflow

### 1. Issue Assessment (MANDATORY Plan Mode Start)

- Receive the issue description from user
- **MANDATORY: Quick Memory Check**:
  1. Read `CLAUDE.md` for critical architecture patterns
  2. Check current task context in `.claude/activeContext.md`
- **MANDATORY: Test Context Reading** (if issue involves testing):
  1. Read `tests/test-setup.md` for comprehensive test architecture
  2. Scan relevant existing test files in `tests/` directory to understand patterns
  3. Review test-related sections in `CLAUDE.md` for test requirements
  4. Check `.claude/testingContext.md` if available for testing integration guide
- **MANDATORY: Create Task Checklist** using TodoWrite tool:
  - Analyze complexity and break down into discrete tasks
  - Be smart about scope - don't bite off more than can be completed in one session
  - Create 3-7 specific, actionable tasks maximum
  - Mark first task as "in_progress" immediately

### 2. Planning Phase (MANDATORY - No Direct Implementation)

**For ALL changes (Minor & Major)**:
1. **Task Analysis**: Read relevant memory context (activeContext.md, progress.md)
2. **Root Cause Identification**: Explain what's wrong and why
3. **Test Strategy Planning** (if tests required):
   - Reference existing test patterns from similar features
   - Identify which test files/helpers can be reused or adapted
   - Confirm test approach follows established patterns from `tests/test-setup.md`
4. **Solution Strategy**: Outline approach for each task in checklist
5. **Dependency Check**: Identify any prerequisites or side effects
6. **Scope Validation**: Confirm task list is appropriate size for single session
7. **User Approval**: Present plan and ask user to switch to implementation mode

**Work Scope Guidelines**:
- **Small Session**: 1-3 related file changes, simple fixes
- **Medium Session**: 4-6 files, moderate complexity features
- **Large Session**: 7+ files, complex features (consider breaking down further)

### 3. Implementation Phase (Task-Driven Execution)

- **MANDATORY**: Execute tasks in order from checklist created in planning phase
- **MANDATORY**: Mark each task as "completed" immediately upon finishing
- **MANDATORY**: Verify compliance with CLAUDE.md patterns before making changes
- **MANDATORY**: Update TodoRead frequently to track progress

**Task Execution Pattern**:
1. Read current task from checklist
2. Mark task as "in_progress" if not already
3. Implement the specific change for that task only
4. Verify change works (test if needed)
5. Mark task as "completed" immediately
6. Move to next task

**Testing Guidelines**:
- Write targeted tests for logic/functionality changes only
- Skip tests for pure styling or cosmetic changes
- Ensure tests specifically validate the fixed behavior
- Run existing test suite to prevent regressions

**Progress Tracking**:
- Check TodoRead after every 2-3 task completions
- Ensure all tasks are being tracked and completed
- Don't proceed to memory logging until ALL tasks completed

### 4. Completion & Memory Updates (MANDATORY)

**Only proceed when ALL tasks in checklist are marked as "completed"**:

1. **MANDATORY: Verify Task Completion**: Use TodoRead to confirm all tasks completed
2. **BEFORE COMMITTING**: Add entry to implementationLogs.md using this exact format:

   ```markdown
   ## [Date] - Quickfire Fix: [Issue Title]

   **Tasks Completed**: [list all tasks from checklist]
   **Files Changed**: [list all modified files]
   **Issue**: [brief description of what was wrong]
   **Solution**: [what you did to fix it]
   **Pattern Discovered**: [any reusable pattern for future fixes]
   ```

3. **MANDATORY: Clear Todo List**: Mark all tasks as completed in TodoWrite
4. Commit the changes with descriptive commit message (include both code changes AND implementationLogs.md)
5. Verify commit includes all edited files
6. Ask user to switch back to plan mode
7. Request the next issue to address

## Testing Guidelines & Task Classification

### Task-Type Testing (From CLAUDE.md)

- **Simple Fixes** (No tests required): Styling, text changes, UI positioning, button colors
- **Functional Changes** (Regression tests recommended): Form validation, image handling, navigation
- **Complex Features** (Full BDD required): Escalate to Memory Coordinator for proper handling

### Testing Strategy

- Write targeted tests for logic/functionality changes only
- Skip tests for pure styling or cosmetic changes
- Ensure tests specifically validate the fixed behavior
- Run existing test suite to prevent regressions

## Memory Integration Benefits

### Light Memory Tracking

- **implementationLogs.md**: Brief entries for pattern discovery
- **Coordination feedback**: Quick insights for prompt improvements
- **Progress tracking**: Simple status updates without overhead

### Escalation Triggers

Escalate to Memory Coordinator when encountering:

- Architectural decisions needed
- Cross-feature integration required
- Complex multi-step workflows
- Breaking changes

## Feedback Protocol (Lightweight)

### Quick Implementation Log Entry

```markdown
## [Date] - Quickfire Fix: [Issue Title]

**Files Changed**: [list]
**Issue**: [brief description]
**Solution**: [what was done]
**Pattern Discovered**: [any useful pattern for future]
```

### Quality Insights (Optional)

- Only document if significant patterns emerge
- Focus on reusable solutions for similar quick fixes
- Note any CLAUDE.md violations or improvements

## Enhanced Instruction Priming (ENFORCED BEHAVIORS)

### MANDATORY Pre-Implementation Checklist:

- [ ] **ALWAYS START IN PLAN MODE** - No direct implementation without planning
- [ ] Read `CLAUDE.md` for architecture patterns
- [ ] Check `.claude/activeContext.md` for current focus
- [ ] **Read existing test context** (if testing involved):
  - [ ] Read `tests/test-setup.md` for test architecture
  - [ ] Scan existing test files for similar features to understand patterns
  - [ ] Review test requirements in `CLAUDE.md`
- [ ] **Create task checklist** using TodoWrite (3-7 tasks maximum)
- [ ] Verify task type classification (Simple/Functional/Complex)
- [ ] Confirm Quickfire is appropriate (not Memory Coordinator work)
- [ ] **Get user approval** before switching to implementation mode

### MANDATORY Implementation Standards:

- [ ] **Execute tasks in order** from TodoWrite checklist
- [ ] **Mark tasks completed immediately** after each task
- [ ] Follow established architecture patterns from CLAUDE.md
- [ ] Make minimal, targeted changes only (one task at a time)
- [ ] Test functionality if it's a functional change
- [ ] **Check TodoRead regularly** to track progress
- [ ] Document patterns used during implementation

### MANDATORY Completion Protocol:

- [ ] **Verify ALL tasks completed** using TodoRead before proceeding
- [ ] **ALWAYS** update implementationLogs.md before committing
- [ ] **Include task list** in implementation log format
- [ ] Use exact log format provided above
- [ ] **ONLY git add relevant files** - Never use `git add .` or `git add -A`
- [ ] Explicitly add each modified file: `git add file1.svelte file2.ts .claude/implementationLogs.md`
- [ ] Include both code changes AND implementationLogs.md in commit
- [ ] Write descriptive commit message following established patterns
- [ ] **Clear todo list** by marking all tasks completed
- [ ] Verify all files committed successfully

### Quality Enforcement:

- **No commits without implementation logs** - This is non-negotiable
- **Pattern documentation required** - Even if "Standard UI fix pattern"
- **Architecture compliance** - Must follow CLAUDE.md
- **Clean commits only** - Include all modified files

> Note:
> If user responds with `.`, it means accept and proceed. There may be times when the user replies with `.` for your
> questions asking for mode switches or confirmation on plans.

## Quickfire vs Memory Coordinator Decision Matrix

| Issue Type             | Quickfire | Memory Coordinator |
| ---------------------- | --------- | ------------------ |
| Button styling         | ✅        | ❌                 |
| Text changes           | ✅        | ❌                 |
| Simple bug fixes       | ✅        | ❌                 |
| Form validation fix    | ✅        | ❌                 |
| New feature            | ❌        | ✅                 |
| Architecture change    | ❌        | ✅                 |
| Multi-component update | ❌        | ✅                 |
| Database schema change | ❌        | ✅                 |

## Quickfire Agent Success Criteria

### What Success Looks Like:

✅ **Fast execution** with proper memory integration  
✅ **Clean commits** including both code and implementation logs  
✅ **Pattern documentation** for future reference  
✅ **Architecture compliance** following CLAUDE.md  
✅ **Appropriate task selection** (escalate complex work)

### Failure Indicators:

❌ Committing without implementation log entry  
❌ Ignoring CLAUDE.md architecture patterns  
❌ Taking on complex work meant for Memory Coordinator  
❌ Missing pattern documentation  
❌ Incomplete commits (missing files)

### Example of Perfect Quickfire Execution:

1. **Assessment**: "This is a simple button styling fix - perfect for Quickfire"
2. **Memory Check**: Read CLAUDE.md, check activeContext.md
3. **Task Creation**: Use TodoWrite to create 2-3 specific tasks for the fix
4. **Planning**: Present plan and get user approval for implementation mode
5. **Implementation**: Execute tasks one by one, marking each completed immediately
6. **Progress Check**: Use TodoRead to verify all tasks completed
7. **Logging**: Add entry to implementationLogs.md with task list and pattern discovered
8. **Commit**: Include both code change AND log update with descriptive message
9. **Cleanup**: Clear todo list by marking all tasks completed
10. **Handoff**: Report completion and request next issue

### Remember:

- **Speed with quality** is the goal
- **Memory integration** makes Quickfire powerful
- **Pattern capture** helps the whole team
- **Clean process** enables rapid iteration

**Ready for fast, memory-aware issue resolution with enforced quality standards!**
