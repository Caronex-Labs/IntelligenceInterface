# Testing Templates

This directory contains standardized test templates for the Intelligence Interface project. These templates implement the test patterns and configuration standards established in Task 2.6.

## Template Overview

| Template | Purpose | When to Use |
|----------|---------|-------------|
| `unit_test_template.go` | Standard unit tests | Testing individual functions/methods |
| `integration_test_template.go` | Integration tests | Testing component interactions |
| `tool_test_template.go` | Tool interface tests | Testing tool implementations |
| `bdd_feature_template.feature` | BDD scenarios | Behavior-driven development |
| `meta_system_test_template.go` | Meta-system tests | Testing agent/space functionality |
| `config_test_template.go` | Configuration tests | Testing configuration behavior |

## Quick Start

1. **Copy** the appropriate template to your package directory
2. **Rename** the file to match your component (e.g., `my_component_test.go`)
3. **Replace** placeholder text with your actual implementation
4. **Customize** test cases for your specific requirements

## Template Usage Guidelines

### Standard Configuration Pattern

All templates use the standardized configuration pattern:
```go
// Set up test environment
os.Setenv("OPENAI_API_KEY", "test-key-[component]")
defer os.Unsetenv("OPENAI_API_KEY")

// Create isolated test directory
tempDir := t.TempDir()

// Load configuration for test directory
_, err := config.Load(tempDir, false)
require.NoError(t, err)
```

### Test Organization
- Use **subtests** (`t.Run()`) for multiple scenarios
- Use **table-driven tests** for comprehensive coverage
- Include both **positive** and **negative** test cases
- Test **error conditions** explicitly

### Helper Functions
- Always include `t.Helper()` in helper functions
- Extract common setup into reusable helpers
- Use descriptive helper function names
- Handle all errors with appropriate assertions

### Error Handling
- Use `require` for setup that must succeed
- Use `assert` for validations that allow test continuation
- Test error conditions explicitly
- Validate error messages when appropriate

## Meta-System Testing

Templates support future meta-system capabilities:
- **Agent testing patterns** for behavior and coordination
- **Space testing patterns** for isolation and communication
- **Configuration evolution** testing approaches
- **BDD integration** for evolutionary scenarios

## Quality Standards

All templates enforce:
- ✅ **Reliability**: Deterministic and repeatable tests
- ✅ **Isolation**: Tests don't affect each other
- ✅ **Clarity**: Descriptive names and clear assertions
- ✅ **Maintainability**: Standard patterns and helper functions
- ✅ **Performance**: Quick execution (< 1 second for unit tests)

## Examples

See existing test files for real-world usage:
- `internal/tools/builtin/ls_test.go` - Comprehensive tool testing
- `internal/core/config/config_test.go` - Configuration testing
- `test/bdd/main_test.go` - BDD framework integration

## Support

For questions about test patterns or template usage:
1. Review the comprehensive analysis in `.claude/testPatterns.md`
2. Check configuration standards in `.claude/testingContext.md`
3. Follow established patterns from existing tests