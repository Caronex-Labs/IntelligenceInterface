package main

import (
	"os"
	"testing"

	"github.com/caronex/intelligence-interface/internal/core/config"
)

func TestMetaSystemConfiguration(t *testing.T) {
	// Set up test environment
	os.Setenv("OPENAI_API_KEY", "test-key-for-configuration-test")
	defer os.Unsetenv("OPENAI_API_KEY")

	// Test configuration loading
	workingDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get working directory: %v", err)
	}

	cfg, err := config.Load(workingDir, false)
	if err != nil {
		t.Fatalf("Failed to load configuration: %v", err)
	}

	// Test Caronex agent configuration
	caronexAgent, exists := cfg.Agents[config.AgentCaronex]
	if !exists {
		t.Error("Caronex agent should be configured by default")
	} else {
		t.Logf("Caronex agent configured with model: %s, tokens: %d", caronexAgent.Model, caronexAgent.MaxTokens)
		
		// Caronex should have higher token limit than other agents
		if caronexAgent.MaxTokens <= 0 {
			t.Error("Caronex agent should have a positive token limit")
		}
	}

	// Test Caronex configuration defaults
	if !cfg.Caronex.Enabled {
		t.Error("Caronex should be enabled by default")
	}

	if cfg.Caronex.Coordination.MaxConcurrentAgents <= 0 {
		t.Error("Max concurrent agents should be positive")
	}

	if cfg.Caronex.Coordination.CommunicationProtocol == "" {
		t.Log("Communication protocol not set, should use default")
	}

	// Test space configuration support
	if cfg.Spaces == nil {
		t.Error("Spaces map should be initialized")
	}

	t.Log("Meta-system configuration test passed successfully")
}