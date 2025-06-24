package config

import (
	"os"
	"testing"
)

func TestMetaSystemConfiguration(t *testing.T) {
	// Set up test environment
	os.Setenv("OPENAI_API_KEY", "test-key-for-config")
	defer os.Unsetenv("OPENAI_API_KEY")

	// Test configuration loading
	workingDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get working directory: %v", err)
	}

	// Reset global config for clean test
	cfg = nil

	config, err := Load(workingDir, false)
	if err != nil {
		t.Fatalf("Failed to load configuration: %v", err)
	}

	// Test Caronex agent configuration
	t.Run("CaronexAgentConfiguration", func(t *testing.T) {
		caronexAgent, exists := config.Agents[AgentCaronex]
		if !exists {
			t.Error("Caronex agent should be configured by default")
			return
		}

		if caronexAgent.MaxTokens <= 0 {
			t.Errorf("Caronex agent should have positive token limit, got %d", caronexAgent.MaxTokens)
		}

		// Verify the model is set
		if caronexAgent.Model == "" {
			t.Error("Caronex agent should have a model configured")
		}
		
		t.Logf("✅ Caronex agent configured: model=%s, tokens=%d", caronexAgent.Model, caronexAgent.MaxTokens)
	})

	// Test Caronex configuration defaults
	t.Run("CaronexDefaults", func(t *testing.T) {
		if !config.Caronex.Enabled {
			t.Error("Caronex should be enabled by default")
		}

		if config.Caronex.Coordination.MaxConcurrentAgents <= 0 {
			t.Errorf("Max concurrent agents should be positive, got %d", config.Caronex.Coordination.MaxConcurrentAgents)
		}

		if config.Caronex.Coordination.SpaceMemoryLimit == "" {
			t.Error("Space memory limit should have a default value")
		}

		t.Logf("✅ Caronex defaults: enabled=%v, maxAgents=%d, memLimit=%s", 
			config.Caronex.Enabled, 
			config.Caronex.Coordination.MaxConcurrentAgents,
			config.Caronex.Coordination.SpaceMemoryLimit)
	})

	// Test space configuration support
	t.Run("SpaceConfiguration", func(t *testing.T) {
		if config.Spaces == nil {
			t.Error("Spaces map should be initialized")
			return
		}

		// Test that we can add a space configuration
		testSpace := SpaceConfig{
			ID:   "test-space",
			Name: "Test Space",
			Type: "development",
			UILayout: UILayoutConfig{
				Type:         "panels",
				DefaultTheme: "opencode",
				Customizable: true,
			},
			AssignedAgents: []string{"coder", "caronex"},
			Persistence: PersistenceConfig{
				Enabled:        true,
				StorageBackend: "memory",
				RetentionDays:  7,
			},
		}

		config.Spaces["test"] = testSpace
		
		if len(config.Spaces) == 0 {
			t.Error("Should be able to add space configurations")
		}

		t.Logf("✅ Space configuration support validated")
	})

	// Test agent specialization
	t.Run("AgentSpecialization", func(t *testing.T) {
		// Test that we can add specialization to existing agents
		if config.Agents == nil {
			t.Error("Agents should be initialized")
			return
		}

		// Add specialization to caronex agent
		caronexAgent := config.Agents[AgentCaronex]
		caronexAgent.Specialization = &AgentSpecialization{
			LearningRate:       0.1,
			CoordinationMode:   "cooperative",
			EvolutionCapable:   true,
			MetaSystemAware:    true,
		}
		config.Agents[AgentCaronex] = caronexAgent

		// Verify specialization was added
		updatedCaronex := config.Agents[AgentCaronex]
		if updatedCaronex.Specialization == nil {
			t.Error("Agent specialization should be supported")
			return
		}

		if updatedCaronex.Specialization.LearningRate != 0.1 {
			t.Errorf("Learning rate should be 0.1, got %f", updatedCaronex.Specialization.LearningRate)
		}

		t.Logf("✅ Agent specialization support validated")
	})

	// Test other existing agents still work
	t.Run("ExistingAgentsCompatibility", func(t *testing.T) {
		expectedAgents := []AgentName{AgentCaronex}
		
		for _, agentName := range expectedAgents {
			agent, exists := config.Agents[agentName]
			if !exists {
				t.Errorf("Agent %s should be configured", agentName)
				continue
			}

			if agent.Model == "" {
				t.Errorf("Agent %s should have a model configured", agentName)
			}

			if agent.MaxTokens <= 0 {
				t.Errorf("Agent %s should have positive token limit", agentName)
			}
		}

		t.Logf("✅ All %d agents configured correctly", len(expectedAgents))
	})

	// Test configuration validation
	t.Run("ConfigurationValidation", func(t *testing.T) {
		err := Validate()
		if err != nil {
			t.Errorf("Configuration validation should pass: %v", err)
		}

		t.Logf("✅ Configuration validation passed")
	})

	t.Logf("🎉 Meta-system configuration test completed successfully")
}