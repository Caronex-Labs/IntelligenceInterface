package support

import (
	"os"
	"testing"

	"github.com/caronex/intelligence-interface/internal/core/config"
)

// SetupTestConfig initializes a minimal configuration for testing
func SetupTestConfig(t *testing.T) {
	t.Helper()
	
	// Get current working directory for test
	workingDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get working directory: %v", err)
	}
	
	// Initialize config with test defaults
	_, err = config.Load(workingDir, false)
	if err != nil {
		// If config initialization fails, try to set up minimal test environment
		t.Logf("Config initialization failed, continuing with mock: %v", err)
		// For tests that need config, we can provide mock values
		SetupMockEnvironment(t)
	}
}

// SetupMockProvider creates a mock configuration with a test provider for prompt tests
func SetupMockProvider(t *testing.T) {
	t.Helper()
	
	// Set environment variables for test providers
	os.Setenv("OPENAI_API_KEY", "test-key-for-tests")
	
	// Initialize config for tests
	SetupTestConfig(t)
}

// SetupMockEnvironment sets up minimal environment for tests that don't need real config
func SetupMockEnvironment(t *testing.T) {
	t.Helper()
	
	// Set minimal environment variables for testing
	os.Setenv("OPENAI_API_KEY", "test-key-for-tests")
	os.Setenv("ANTHROPIC_API_KEY", "test-key-for-tests")
}

// CleanupTestConfig cleans up test configuration
func CleanupTestConfig(t *testing.T) {
	t.Helper()
	// Clean up test environment variables
	os.Unsetenv("OPENAI_API_KEY")
	os.Unsetenv("ANTHROPIC_API_KEY")
}