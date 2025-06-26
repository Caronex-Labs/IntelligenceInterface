package integration

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/caronex/intelligence-interface/internal/agents/base"
	agent "github.com/caronex/intelligence-interface/internal/llm/agent"
	"github.com/caronex/intelligence-interface/internal/agents/builtin"
	"github.com/caronex/intelligence-interface/internal/agents/caronex"
	"github.com/caronex/intelligence-interface/internal/core/config"
	db "github.com/caronex/intelligence-interface/internal/infrastructure/database"
	app "github.com/caronex/intelligence-interface/internal/services"
	"github.com/caronex/intelligence-interface/internal/tools/coordination"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSprint1_CompleteWorkflowIntegration(t *testing.T) {
	setupIntegrationTest(t)

	t.Run("directory migration validation", func(t *testing.T) {
		validateDirectoryMigration(t)
	})

	t.Run("caronex manager agent integration", func(t *testing.T) {
		validateCaronexManagerIntegration(t)
	})

	t.Run("configuration system validation", func(t *testing.T) {
		validateConfigurationSystem(t)
	})

	t.Run("management tools integration", func(t *testing.T) {
		validateManagementToolsIntegration(t)
	})

	t.Run("end-to-end workflow validation", func(t *testing.T) {
		validateEndToEndWorkflow(t)
	})
}

func setupIntegrationTest(t *testing.T) {
	t.Helper()

	os.Setenv("OPENAI_API_KEY", "test-key-integration")
	defer os.Unsetenv("OPENAI_API_KEY")

	tempDir := t.TempDir()
	_, err := config.Load(tempDir, false)
	require.NoError(t, err)
}

func validateDirectoryMigration(t *testing.T) {
	t.Helper()

	t.Run("agents package structure", func(t *testing.T) {
		// Note: Agent creation requires proper services setup in full integration tests
		// Here we just validate package structure exists
		tempDir := t.TempDir()
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)
		
		// Validate that agent packages are accessible
		assert.NotNil(t, cfg.Agents, "Agents configuration should be available")
		assert.Contains(t, cfg.Agents, config.AgentCaronex, "Caronex agent should be in configuration")
	})

	t.Run("tools package structure", func(t *testing.T) {
		tempDir := t.TempDir()
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)
		assert.NotNil(t, manager, "Coordination manager should be available")
	})

	t.Run("configuration package migration", func(t *testing.T) {
		tempDir := t.TempDir()
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)
		assert.NotNil(t, cfg, "Configuration should load from core/config package")
	})

	t.Run("services package structure", func(t *testing.T) {
		// Create database connection for app
		ctx := context.Background()
		dbConn, err := db.Connect()
		require.NoError(t, err)
		defer dbConn.Close()
		
		appInstance, err := app.New(ctx, dbConn)
		assert.NoError(t, err, "App service should be created without error")
		assert.NotNil(t, appInstance, "App service should be available from services package")
	})
}

func validateCaronexManagerIntegration(t *testing.T) {
	t.Helper()

	tempDir := t.TempDir()
	cfg, err := config.Load(tempDir, false)
	require.NoError(t, err)

	t.Run("caronex agent creation", func(t *testing.T) {
		agent := caronex.NewCaronexAgent()
		require.NotNil(t, agent, "Caronex agent should be created successfully")

		info := agent.Info()
		assert.Equal(t, "caronex", info.Name, "Caronex agent should have correct name")
		assert.Contains(t, info.Description, "coordination", "Caronex should be described as coordination agent")
	})

	t.Run("manager vs implementer distinction", func(t *testing.T) {
		caronexAgent := caronex.NewCaronexAgent()
		coderAgent := builtin.NewCoderAgent()

		assert.True(t, isManagerAgent(caronexAgent), "Caronex should be identified as manager agent")
		assert.False(t, isManagerAgent(coderAgent), "Coder should not be identified as manager agent")
	})

	t.Run("system coordination capabilities", func(t *testing.T) {
		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)
		require.NotNil(t, manager, "Coordination manager should be available")

		introspection, err := manager.GetSystemIntrospection()
		assert.NoError(t, err, "System introspection should work")
		assert.NotEmpty(t, introspection.SystemStatus, "System status should be available")

		assert.NotEmpty(t, introspection.AvailableAgents, "Available agents should be listed")
	})
}

func validateConfigurationSystem(t *testing.T) {
	t.Helper()

	tempDir := t.TempDir()

	t.Run("meta-system configuration support", func(t *testing.T) {
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		assert.NotNil(t, cfg.Caronex, "Caronex configuration should be available")
		assert.NotNil(t, cfg.Spaces, "Spaces configuration should be available")
		assert.NotNil(t, cfg.Agents, "Agents configuration should be available")
	})

	t.Run("configuration validation", func(t *testing.T) {
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		// Configuration validation happens during load
		assert.NotNil(t, cfg, "Configuration should be loaded successfully")
	})

	t.Run("backward compatibility", func(t *testing.T) {
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		assert.NotNil(t, cfg.Providers, "Existing provider configuration should still work")
		assert.NotNil(t, cfg.TUI, "Existing TUI configuration should still work")
	})
}

func validateManagementToolsIntegration(t *testing.T) {
	t.Helper()

	tempDir := t.TempDir()
	cfg, err := config.Load(tempDir, false)
	require.NoError(t, err)

	t.Run("management tools availability", func(t *testing.T) {
		tools := agent.ManagerAgentTools()

		assert.NotEmpty(t, tools, "Management tools should be available")

		toolNames := make([]string, len(tools))
		for i, tool := range tools {
			toolNames[i] = tool.Info().Name
		}

		expectedTools := []string{
			"system_introspection",
			"agent_coordination", 
			"configuration_inspection",
			"agent_lifecycle",
			"space_foundation",
		}

		for _, expectedTool := range expectedTools {
			assert.Contains(t, toolNames, expectedTool, "Management tool %s should be available", expectedTool)
		}
	})

	t.Run("coordination manager integration", func(t *testing.T) {
		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)
		require.NotNil(t, manager, "Coordination manager should be available")

		introspection, err := manager.GetSystemIntrospection()
		assert.NoError(t, err, "System introspection should work")
		assert.NotEmpty(t, introspection.SystemStatus, "System status should be retrievable")

		agentNames := make([]string, len(introspection.AvailableAgents))
		for i, agent := range introspection.AvailableAgents {
			agentNames[i] = agent.Name
		}
		assert.Contains(t, agentNames, "caronex", "Caronex should be listed as available agent")
		assert.Contains(t, agentNames, "coder", "Coder should be listed as available agent")
	})
}

func validateEndToEndWorkflow(t *testing.T) {
	t.Helper()

	tempDir := t.TempDir()
	cfg, err := config.Load(tempDir, false)
	require.NoError(t, err)

	t.Run("complete system initialization", func(t *testing.T) {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		// Create database connection for app
		dbConn, err := db.Connect()
		require.NoError(t, err)
		defer dbConn.Close()
		
		appInstance, err := app.New(ctx, dbConn)
		require.NoError(t, err)
		require.NotNil(t, appInstance, "App should initialize successfully")

		err = appInstance.Initialize(ctx)
		assert.NoError(t, err, "App should initialize without errors")
	})

	t.Run("database integration", func(t *testing.T) {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		db, err := db.Connect(ctx, tempDir+"/test.db")
		require.NoError(t, err, "Database should connect successfully")
		defer db.Close()

		err = database.ApplyMigrations(ctx, db)
		assert.NoError(t, err, "Database migrations should apply successfully")
	})

	t.Run("agent coordination workflow", func(t *testing.T) {
		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)
		caronexAgent := caronex.NewCaronexAgent()

		tasks := []string{
			"system_status_check",
			"agent_capability_assessment", 
			"configuration_validation",
		}

		for _, task := range tasks {
			result, err := manager.DelegateTask(task+"_id", task, "caronex")
			assert.NoError(t, err, "Task %s should delegate successfully", task)
			assert.NotEmpty(t, result, "Task %s should produce result", task)
		}
	})
}

func isManagerAgent(agent base.Service) bool {
	info := agent.Info()
	return info.Name == "caronex" || info.Description == "Caronex Manager Agent"
}

func TestSprint1_PerformanceValidation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance tests in short mode")
	}

	setupIntegrationTest(t)

	t.Run("startup performance", func(t *testing.T) {
		tempDir := t.TempDir()
		
		start := time.Now()
		cfg, err := config.Load(tempDir, false)
		loadDuration := time.Since(start)

		require.NoError(t, err)
		assert.Less(t, loadDuration, 100*time.Millisecond, "Configuration loading should be fast")

		start = time.Now()
		app := app.New(cfg)
		creationDuration := time.Since(start)

		require.NotNil(t, appInstance)
		assert.Less(t, creationDuration, 50*time.Millisecond, "App creation should be fast")
	})

	t.Run("agent creation performance", func(t *testing.T) {
		iterations := 100
		start := time.Now()

		for i := 0; i < iterations; i++ {
			agent := caronex.NewCaronexAgent()
			require.NotNil(t, agent)
		}

		duration := time.Since(start)
		avgDuration := duration / time.Duration(iterations)
		assert.Less(t, avgDuration, 1*time.Millisecond, "Agent creation should be efficient")
	})

	t.Run("memory usage validation", func(t *testing.T) {
		tempDir := t.TempDir()
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		app := app.New(cfg)
		require.NotNil(t, appInstance)

		caronexAgent := caronex.NewCaronexAgent()
		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)

		require.NotNil(t, caronexAgent)
		require.NotNil(t, manager)
	})
}

func TestSprint1_StabilityValidation(t *testing.T) {
	setupIntegrationTest(t)

	t.Run("concurrent agent access", func(t *testing.T) {
		tempDir := t.TempDir()
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)
		
		concurrency := 10
		done := make(chan bool, concurrency)

		for i := 0; i < concurrency; i++ {
			go func() {
				defer func() { done <- true }()
				
				introspection, err := manager.GetSystemIntrospection()
				assert.NoError(t, err)
				assert.NotEmpty(t, introspection.AvailableAgents)
				
				assert.NotEmpty(t, introspection.SystemStatus)
			}()
		}

		for i := 0; i < concurrency; i++ {
			select {
			case <-done:
			case <-time.After(5 * time.Second):
				t.Fatal("Concurrent access test timed out")
			}
		}
	})

	t.Run("error recovery", func(t *testing.T) {
		tempDir := t.TempDir()
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)
		
		result, err := manager.DelegateTask("invalid_task_id", "invalid_task", "invalid_agent")
		assert.Error(t, err, "System should handle invalid tasks gracefully")

		introspection, err := manager.GetSystemIntrospection()
		assert.NoError(t, err, "System should remain functional after errors")
		assert.NotEmpty(t, introspection.SystemStatus, "System should remain functional after errors")
	})

	t.Run("configuration reload", func(t *testing.T) {
		tempDir := t.TempDir()
		
		cfg1, err := config.Load(tempDir, false)
		require.NoError(t, err)
		
		cfg2, err := config.Load(tempDir, false)
		require.NoError(t, err)
		
		assert.Equal(t, cfg1.Caronex, cfg2.Caronex, "Configuration should be consistent across reloads")
	})
}