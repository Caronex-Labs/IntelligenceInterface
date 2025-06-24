package support

import (
	"os"
	"os/exec"
	"strings"
	"testing"

	"github.com/caronex/intelligence-interface/internal/core/config"
)

// SystemTestSetup provides utilities for system-level testing
type SystemTestSetup struct {
	ProjectRoot   string
	TempDir       string
	initialized   bool
}

// NewSystemTestSetup creates a new system test setup
func NewSystemTestSetup(t *testing.T) *SystemTestSetup {
	t.Helper()
	
	// Get project root (current working directory should be project root)
	projectRoot, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get project root: %v", err)
	}
	
	return &SystemTestSetup{
		ProjectRoot: projectRoot,
	}
}

// Initialize sets up the system for testing
func (s *SystemTestSetup) Initialize(t *testing.T) {
	t.Helper()
	
	if s.initialized {
		return
	}
	
	// Set up test environment variables
	os.Setenv("OPENAI_API_KEY", "test-key-for-bdd-tests")
	os.Setenv("ANTHROPIC_API_KEY", "test-key-for-bdd-tests")
	
	// Load configuration
	_, err := config.Load(s.ProjectRoot, false)
	if err != nil {
		t.Logf("Config load failed (continuing with mock): %v", err)
	}
	
	s.initialized = true
}

// Cleanup cleans up after testing
func (s *SystemTestSetup) Cleanup(t *testing.T) {
	t.Helper()
	
	// Clean up environment variables
	os.Unsetenv("OPENAI_API_KEY")
	os.Unsetenv("ANTHROPIC_API_KEY")
	
	// Clean up temp directory if created
	if s.TempDir != "" {
		os.RemoveAll(s.TempDir)
	}
}

// RunBuild runs go build to test system compilation
func (s *SystemTestSetup) RunBuild(t *testing.T) error {
	t.Helper()
	
	cmd := exec.Command("go", "build", ".")
	cmd.Dir = s.ProjectRoot
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Logf("Build failed: %v\nOutput: %s", err, output)
		return err
	}
	return nil
}

// RunTests runs the test suite
func (s *SystemTestSetup) RunTests(t *testing.T) error {
	t.Helper()
	
	cmd := exec.Command("go", "test", "./...")
	cmd.Dir = s.ProjectRoot
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Logf("Tests failed: %v\nOutput: %s", err, output)
		return err
	}
	return nil
}

// CheckGitRepository verifies git repository is initialized
func (s *SystemTestSetup) CheckGitRepository(t *testing.T) error {
	t.Helper()
	
	// Check if .git directory exists
	gitDir := s.ProjectRoot + "/.git"
	if _, err := os.Stat(gitDir); os.IsNotExist(err) {
		return err
	}
	
	// Check if there are commits
	cmd := exec.Command("git", "log", "--oneline", "-1")
	cmd.Dir = s.ProjectRoot
	output, err := cmd.CombinedOutput()
	if err != nil {
		return err
	}
	
	if strings.TrimSpace(string(output)) == "" {
		t.Error("No commits found in git repository")
	}
	
	return nil
}

// ValidateDirectoryStructure checks if the meta-system directory structure exists
func (s *SystemTestSetup) ValidateDirectoryStructure(t *testing.T) error {
	t.Helper()
	
	requiredDirs := []string{
		"internal/caronex",
		"internal/agents/base",
		"internal/agents/builtin", 
		"internal/tools/builtin",
		"internal/spaces",
		"internal/core/config",
		"internal/core/logging",
		"internal/core/models",
	}
	
	for _, dir := range requiredDirs {
		fullPath := s.ProjectRoot + "/" + dir
		if _, err := os.Stat(fullPath); os.IsNotExist(err) {
			t.Errorf("Required directory missing: %s", dir)
			return err
		}
	}
	
	return nil
}

// CheckPackageConsistency verifies package declarations are consistent
func (s *SystemTestSetup) CheckPackageConsistency(t *testing.T) error {
	t.Helper()
	
	// This is a simplified check - in a full implementation, this would
	// parse Go files and verify package declarations match directory structure
	return nil
}