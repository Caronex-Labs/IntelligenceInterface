# Task Prompt Examples

This file contains real examples of task prompts from Sprint 01 to demonstrate the expected level of detail and structure for different types of tasks.

## Example 1: Enhancement Task (Task 1 - Publications Tag Enhancement)

### Task Type: Frontend Enhancement (Simplified Scope)

### Complexity: Medium

### Context: Existing feature improvement

````
You are a BDD-focused implementation agent for the New Neo Group project. This is a SvelteKit-based corporate website with integrated CMS for Neo Wealth & Asset Management.

## CRITICAL: Memory Bank Context Required
[Standard memory file list]

## MANDATORY: MCP Documentation Validation
BEFORE implementing, query these MCP documentation servers:
- `mcp__sveltekit-docs__search_kit_documentation` for "component validation form patterns"
- `mcp__playwright-docs__search_playwright_documentation` for "form input testing patterns"

## Your Specific Task: Publications Tag Enhancement (Simplified)

Enhance the existing single tag field system with improved UI/UX - NO database changes needed.

### Current State Analysis:
- ✅ Single `tag` field already exists as string in model
- ✅ Simple text input already implemented in form
- ✅ No filtering/searching functionality required

### BDD Scenarios Required:
```gherkin
Feature: Publications Tag Display Enhancement
  As an admin user
  I want improved tag input experience
  So that tagging publications is more user-friendly

  Scenario: Enhanced tag input validation
    Given I am creating a publication
    When I enter a tag value
    Then input should provide immediate validation feedback
    And tag should be properly formatted

  Scenario: Tag display consistency
    Given publications have various tags
    When I view publications in admin
    Then tags should display consistently
    And formatting should be uniform
````

### Acceptance Criteria:

- [ ] Improve tag input UX (validation, formatting)
- [ ] Ensure consistent tag display in admin lists
- [ ] Add client-side validation for tag format
- [ ] Maintain existing string field structure
- [ ] Comprehensive BDD tests for tag input/display

### Technical Requirements:

- **NO Schema Changes**: Keep existing single string field
- **Frontend Only**: UI/UX improvements to existing form
- **Validation**: Client-side tag format validation
- **Display**: Consistent tag display in admin interface
- **Testing**: BDD tests for enhanced tag functionality

This is a pure frontend enhancement - no database migration needed.

```

**Key Features of Enhancement Tasks:**
- Clear scope limitations (NO database changes)
- Current state analysis showing what already exists
- Focused BDD scenarios on specific improvements
- Technical requirements emphasizing constraints

## Example 2: Complex Fix Task (Task 3 - News Media Images)

### Task Type: Bug Fix with System Integration
### Complexity: High
### Context: Multi-component state management issue

```

You are a BDD-focused implementation agent for the New Neo Group project.

[Standard header sections]

## Your Specific Task: Fix News Media Picture Handling

Resolve picture handling issues in the person form news media section to ensure reliable image persistence across form operations.

### Current Issue Analysis Required:

**CRITICAL**: Study the existing news media testing architecture which shows known issues:

1. **Examine Test Files**:

   - `/Users/caronex/Work/AdroitAlliance/New-Neo-Group/tests/cms/people-management/news-media/`
   - Focus on `IDENTIFIED-ISSUES.md` and existing E2E tests
   - Review `image-persistence.spec.ts` and related test failures

2. **Analyze Components**:
   - `/Users/caronex/Work/AdroitAlliance/New-Neo-Group/src/lib/components/admin/MultipleImageUpload.svelte`
   - `/Users/caronex/Work/AdroitAlliance/New-Neo-Group/src/lib/components/admin/NewsMediaSection.svelte`

### BDD Scenarios Required:

```gherkin
Feature: News Media Image Management Reliability
  As an admin user
  I want reliable image upload in news media sections
  So that person profiles have consistent media attachments

  Background:
    Given I am logged in as an admin user
    And I am on the person creation/edit page
    And I have news media entries to manage

  Scenario: Upload single image to news media entry
    Given I have created a news media entry
    When I upload an image to that entry
    Then the image should be attached successfully
    And I should see image preview immediately
    And image data should persist in form state
    And form submission should include the image

  Scenario: Image persistence across form operations
    Given I have uploaded images to news media entries
    When I add new entries or modify existing ones
    Then existing images should remain intact
    And image state should be maintained correctly
```

### Technical Investigation Required:

**Analyze Current Issues**:

1. **State Management**: How news media image state is managed in PersonForm
2. **Form Data Handling**: How images are included in form submission
3. **API Integration**: Picture upload and association with publishers
4. **Component Communication**: Data flow between NewsMediaSection and image upload components

### Acceptance Criteria:

- [ ] Images persist correctly across all form operations
- [ ] Multiple images can be uploaded without conflicts or state loss
- [ ] Form submission includes all image data correctly
- [ ] Error handling provides clear feedback without breaking form state
- [ ] BDD tests covering all identified scenarios pass consistently

### Implementation Strategy:

1. **Diagnostic Phase**:

   - Run existing tests to reproduce issues
   - Identify specific failure points in image persistence
   - Document root causes of state management problems

2. **Fix Implementation**:

   - Address state management issues in reactive components
   - Improve FormData handling for multiple images
   - Enhance error handling and recovery mechanisms

3. **Testing Phase**:
   - Implement comprehensive BDD tests for all scenarios
   - Ensure tests are reliable and non-flaky
   - Validate fixes against all identified issue patterns

```

**Key Features of Complex Fix Tasks:**
- Detailed investigation requirements with specific file references
- Multi-phase implementation strategy
- Root cause analysis requirements
- Comprehensive testing validation

## Example 3: Refinement Task (Task 3.5 - News Media Testing Reliability)

### Task Type: Quality/Reliability Completion
### Complexity: Medium
### Context: Following up on previous agent's work

```

You are a BDD-focused implementation agent for the New Neo Group project.

[Standard header sections]

6. **CRITICAL - Previous Agent Feedback**:
   - `/Users/caronex/Work/AdroitAlliance/New-Neo-Group/.claude/implementationLogs.md` (READ THE TASK 3 ENTRY!)
   - `/Users/caronex/Work/AdroitAlliance/New-Neo-Group/.claude/qualityFeedback.md`

## Your Specific Task: News Media Testing Reliability & Quality Completion (Task 3.5)

Complete the remaining work from Task 3 focusing on test reliability, documentation, and coordination improvements based on the previous agent's detailed feedback.

### Previous Agent's Key Findings (FROM IMPLEMENTATION LOGS):

**✅ CORE FUNCTIONALITY WORKING:**

- News media component state management resolved
- Image persistence working correctly
- Component follows proper reactive patterns
- Zero console errors in normal operation

**❌ REMAINING ISSUES TO RESOLVE:**

- **Test Selector Specificity**: Multiple "Edit" buttons causing Playwright strict mode violations
- **Test Flow Misunderstandings**: Placeholder text and button text mismatches
- **Complex Multi-Entry Workflows**: Need refined selectors for multiple entries
- **Missing Quality Feedback**: qualityFeedback.md not updated as required

### BDD Scenarios Required:

```gherkin
Feature: News Media Testing Reliability Completion
  As a QA engineer
  I want reliable news media tests with proper selectors
  So that the test suite executes without failures or timeouts

  Background:
    Given Task 3 core functionality is working
    And implementation logs show specific selector issues
    And 3/6 tests are currently failing due to selector problems

  Scenario: Fix selector specificity violations
    Given multiple "Edit" buttons exist on the person form
    When I use context-specific selectors for news media edit buttons
    Then Playwright strict mode violations should be resolved
    And tests should target the correct components
```

### Specific Implementation Requirements Based on Previous Agent Feedback:

#### **1. Selector Specificity Fixes (HIGH PRIORITY):**

- **Issue**: `page.getByRole('button', { name: 'Edit' })` matches multiple buttons
- **Solution**: Use context-specific selectors as suggested:
  ```typescript
  // ✅ GOOD - Previous agent's recommendation
  await page
  	.locator('[data-testid="news-media-entry-0"]')
  	.getByRole('button', { name: 'Edit' })
  	.click();
  ```

#### **2. UI Text Alignment (MEDIUM PRIORITY):**

- **Fix placeholder mismatches**: "Publisher Name" vs "Enter publisher name"
- **Fix button text mismatches**: "Add News/Media Appearance" vs "Add Media Appearance"
- **Understand auto-edit mode**: New entries automatically open in edit mode

### Implementation Strategy:

#### **Phase 1: Analyze Previous Work (15 minutes):**

- Read the detailed implementation logs from Task 3 agent
- Understand the specific selector issues and solutions identified
- Review the current test files and identify the 3 failing tests

#### **Phase 2: Implement Selector Fixes (45 minutes):**

- Apply context-specific selectors as recommended by previous agent
- Fix UI text mismatches in test assertions
- Implement proper file upload patterns with Buffer handling

### Success Criteria:

- 100% news media test pass rate (6/6 tests passing)
- Zero timeout failures in test execution
- Quality feedback properly documented
- Previous agent's recommendations successfully implemented

Begin by reading ALL memory files, especially the implementationLogs.md Task 3 entry, to understand the specific issues and solutions identified by the previous agent.

```

**Key Features of Refinement Tasks:**
- Heavy emphasis on previous agent feedback integration
- Specific issue identification from implementation logs
- Detailed solution references from previous work
- Quality completion focus rather than new feature development

## Example 4: Infrastructure Task (Task 4 - SMTP Module)

### Task Type: New Infrastructure Implementation
### Complexity: High
### Context: Foundation for email system

```

You are a BDD-focused implementation agent for the New Neo Group project.

[Standard header sections]

## MANDATORY: MCP Documentation Validation

BEFORE implementing, query these MCP documentation servers:

- `mcp__sveltekit-docs__search_kit_documentation` for "email form actions SMTP"
- `mcp__sveltekit-docs__search_kit_documentation` for "server actions email handling"

## Your Specific Task: SMTP Trigger Module

Implement core SMTP infrastructure for triggering emails from SvelteKit form actions.

### BDD Scenarios Required:

```gherkin
Feature: SMTP Email Infrastructure
  As a system administrator
  I want reliable email sending capability
  So that forms can trigger email notifications

  Scenario: Send email via SMTP
    Given SMTP configuration is valid
    When a form action triggers an email
    Then email should be sent successfully
    And confirmation should be logged
    And errors should be handled gracefully

  Scenario: Email template rendering
    Given I have email template data
    When I render an email template
    Then HTML and text versions should be generated
    And template variables should be substituted correctly
```

### Technical Requirements:

- **SMTP Library**: Research Node.js email libraries (nodemailer recommended)
- **Configuration**: Environment variables for SMTP settings
- **Service Layer**: Email service following ObjectId conversion patterns
- **Error Handling**: Robust error handling and logging
- **Templates**: HTML/text email template system
- **Testing**: Mock SMTP for testing (no real emails in tests)

### Implementation Structure:

```
src/lib/server/services/
├── email.ts              # Core email service
├── smtp.ts               # SMTP configuration
└── templates/
    ├── contact-form.ts    # Contact form templates
    └── subscription.ts    # Subscription templates
```

Query MCP documentation for SvelteKit email patterns before starting implementation.

```

**Key Features of Infrastructure Tasks:**
- Heavy MCP documentation requirements
- Clear architecture and file structure specifications
- Foundation focus for future features
- Mock testing requirements for external services

## Template Usage Patterns

### **Task Type Classification:**

#### **Enhancement Tasks** (1, 1.5, 2, 2.5)
- **Focus**: Improve existing functionality
- **Scope**: Usually constrained to prevent scope creep
- **Context**: Current state analysis of existing implementation
- **Testing**: Enhanced test coverage for improved functionality

#### **Fix Tasks** (3, 3.5)
- **Focus**: Resolve specific issues or bugs
- **Scope**: Problem investigation and resolution
- **Context**: Issue analysis and root cause identification
- **Testing**: Regression prevention and reliability improvement

#### **Infrastructure Tasks** (4, 5, 6, 7)
- **Focus**: New foundational capabilities
- **Scope**: System architecture and integration
- **Context**: Foundation for future features
- **Testing**: Comprehensive coverage for new capabilities

### **Refinement Tasks** (.5 tasks)
- **Focus**: Quality, reliability, and documentation completion
- **Scope**: Address leftovers from main task implementation
- **Context**: Previous agent feedback integration
- **Testing**: Test reliability and documentation completion

## Quality Indicators for Task Prompts

### **Excellent Task Prompts Include:**
- ✅ **Comprehensive Memory Context**: All required files listed
- ✅ **Specific MCP Queries**: Targeted documentation validation
- ✅ **Detailed BDD Scenarios**: Multiple scenarios with clear business value
- ✅ **Implementation Guidance**: Clear technical direction and constraints
- ✅ **Success Metrics**: Measurable completion criteria
- ✅ **Feedback Requirements**: Structured feedback collection
- ✅ **Context Integration**: Previous work analysis when applicable

### **Task Prompt Anti-Patterns to Avoid:**
- ❌ **Vague Requirements**: Unclear or unmeasurable acceptance criteria
- ❌ **Missing Context**: Insufficient background or current state analysis
- ❌ **Poor BDD Scenarios**: Single scenario or business value unclear
- ❌ **Technical Gaps**: Missing implementation guidance or constraints
- ❌ **No Feedback Structure**: Missing feedback requirements
- ❌ **Scope Creep**: Unclear boundaries or too many objectives
```
