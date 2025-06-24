# Testing Reference Guide

## Quick Reference

### Available Templates
- `unit_test_template.go` - Standard unit testing
- `integration_test_template.go` - Multi-component testing  
- `tool_test_template.go` - Tool interface testing
- `config_test_template.go` - Configuration testing
- `meta_system_test_template.go` - Advanced system testing
- `bdd_feature_template.feature` - BDD scenario templates

### Standard Test Setup Pattern
```go
func TestYourComponent(t *testing.T) {
    os.Setenv("OPENAI_API_KEY", "test-key-component")
    defer os.Unsetenv("OPENAI_API_KEY")
    
    tempDir := t.TempDir()
    cfg, err := config.Load(tempDir, false)
    require.NoError(t, err)
    
    // Your test logic here
}
```

## Test Pattern Categories

### 1. Configuration Setup Patterns
- **Basic Setup**: `os.Setenv()` + `config.Load()` + `t.TempDir()`
- **Provider Keys**: Use `test-key-[component]` naming convention
- **Cleanup**: Always use `defer` for environment cleanup

### 2. Assertion Patterns
- **Critical Setup**: Use `require.NoError()` - test stops on failure
- **Validations**: Use `assert.*()` - test continues on failure
- **Error Messages**: Include descriptive context in assertions

### 3. Subtest Organization
- **Logical Grouping**: Use `t.Run("scenario name", func(t *testing.T) {...})`
- **Isolation**: Each subtest gets clean environment
- **Error Handling**: Test both success and error scenarios

### 4. Table-Driven Testing
```go
scenarios := []struct {
    name        string
    input       InputType
    expectError bool
    validation  func(t *testing.T, result ResultType)
}{
    // Test scenarios here
}

for _, scenario := range scenarios {
    t.Run(scenario.name, func(t *testing.T) {
        // Test execution
    })
}
```

### 5. Helper Function Patterns
- Mark with `t.Helper()` for better error reporting
- Place at end of test file
- Use for common setup/validation logic

## Meta-System Testing Patterns

### Agent Testing
```go
// Test agent learning behavior
func TestAgent_Learning(t *testing.T) {
    agent := createTestAgent(t, AgentTypeCoder)
    
    baseline := measureAgentPerformance(t, agent, testScenarios)
    
    // Provide learning experiences
    for _, scenario := range learningScenarios {
        result := agent.Process(scenario)
        agent.RecordOutcome(result, scenario.ExpectedOutcome)
    }
    
    improved := measureAgentPerformance(t, agent, testScenarios)
    assert.True(t, improved.IsBetterThan(baseline))
}
```

### Space Isolation Testing
```go
// Test space isolation
func TestSpace_Isolation(t *testing.T) {
    space1 := createTestSpace(t, "space1", config1)
    space2 := createTestSpace(t, "space2", config2)
    
    space1.Set("data", "value1")
    space2.Set("data", "value2")
    
    assert.Equal(t, "value1", space1.Get("data"))
    assert.Equal(t, "value2", space2.Get("data"))
    assert.NotEqual(t, space1.Get("data"), space2.Get("data"))
}
```

### System Evolution Testing
```go
// Test system self-modification
func TestSystem_Evolution(t *testing.T) {
    system := createTestSystem(t)
    initialCapabilities := system.GetCapabilities()
    
    evolution := system.TriggerEvolution(improvementScenario)
    assert.True(t, evolution.IsSuccessful())
    assert.True(t, evolution.IsReversible())
    
    newCapabilities := system.GetCapabilities()
    assert.True(t, newCapabilities.IsSuperset(initialCapabilities))
}
```

## Performance Testing Patterns

### Response Time Testing
```go
func TestPerformance(t *testing.T) {
    if testing.Short() {
        t.Skip("Skipping performance test in short mode")
    }
    
    start := time.Now()
    result := performOperation()
    duration := time.Since(start)
    
    assert.NoError(t, result.Error)
    assert.Less(t, duration, 5*time.Second)
}
```

### Memory Usage Testing
```go
func TestMemoryUsage(t *testing.T) {
    var memBefore runtime.MemStats
    runtime.ReadMemStats(&memBefore)
    
    performOperation()
    
    var memAfter runtime.MemStats
    runtime.ReadMemStats(&memAfter)
    
    memoryUsed := memAfter.TotalAlloc - memBefore.TotalAlloc
    assert.Less(t, memoryUsed, uint64(10*1024*1024)) // 10MB limit
}
```

## BDD Integration Patterns

### Feature File Structure
```gherkin
Feature: Component Behavior
  As a developer
  I want component functionality
  So that system works correctly

  Scenario: Happy Path
    Given initial condition
    When action occurs  
    Then expected outcome
    
  Scenario: Error Handling
    Given error condition
    When invalid action
    Then error handled gracefully
```

### Scenario Implementation
```go
func (s *FeatureSuite) iHaveAComponent() error {
    s.component = NewComponent(s.config)
    return nil
}

func (s *FeatureSuite) iCallMethodWith(method, param string) error {
    result, err := s.component.CallMethod(method, param)
    s.lastResult = result
    return err
}

func (s *FeatureSuite) theResultShouldBe(expected string) error {
    if s.lastResult != expected {
        return fmt.Errorf("expected %s, got %s", expected, s.lastResult)
    }
    return nil
}
```

## Quality Gates

### Before Committing
1. All tests pass: `go test ./...`
2. No race conditions: `go test -race ./...`
3. Coverage acceptable: `go test -cover ./...`
4. Performance within limits
5. BDD scenarios satisfied

### During Development
1. Follow TDD when possible
2. Use appropriate template as starting point
3. Include error handling tests
4. Add performance tests for critical paths
5. Validate meta-system behavior where applicable

## Common Pitfalls

### Configuration Issues
- ❌ Forgetting to set API keys in tests
- ❌ Not using `t.TempDir()` for isolation
- ❌ Missing cleanup with `defer`
- ✅ Use standard configuration setup pattern

### Test Organization
- ❌ Giant test functions testing everything
- ❌ Tests depending on execution order
- ❌ Missing error scenario testing
- ✅ Use subtests and table-driven approaches

### Meta-System Testing
- ❌ Testing only current functionality
- ❌ Ignoring agent coordination patterns
- ❌ Not testing evolution capabilities
- ✅ Include future-ready testing patterns

### Performance Testing
- ❌ Running performance tests in CI by default
- ❌ Not using `testing.Short()` flag
- ❌ Missing timeout and resource limits
- ✅ Conditional performance testing with appropriate limits

## Integration with Development Workflow

### Template Selection Guide
1. **Unit Tests**: Single component, isolated behavior → `unit_test_template.go`
2. **Integration**: Multiple components, workflows → `integration_test_template.go`
3. **Tools**: Tool interface testing → `tool_test_template.go`
4. **Configuration**: Config behavior/evolution → `config_test_template.go`
5. **Meta-System**: Agent/space/evolution → `meta_system_test_template.go`
6. **BDD**: User scenarios → `bdd_feature_template.feature`

### Memory Context Alignment
All testing should support the Intelligence Interface's evolution from Intelligence Interface to meta-system:
- Preserve existing Intelligence Interface functionality
- Enable agent-everything architecture testing
- Support space-based computing validation
- Test system self-improvement capabilities
- Validate collective intelligence patterns

This reference guide ensures consistent, high-quality testing across the Intelligence Interface codebase while supporting both current functionality and future meta-system evolution.