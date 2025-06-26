package performance

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/tools/coordination"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// BenchmarkConfigurationLoad tests configuration loading performance
func BenchmarkConfigurationLoad(b *testing.B) {
	tempDir := b.TempDir()
	os.Setenv("OPENAI_API_KEY", "test-key-performance")
	defer os.Unsetenv("OPENAI_API_KEY")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		cfg, err := config.Load(tempDir, false)
		require.NoError(b, err)
		require.NotNil(b, cfg)
	}
}

// BenchmarkCoordinationManagerCreation tests coordination manager creation performance
func BenchmarkCoordinationManagerCreation(b *testing.B) {
	tempDir := b.TempDir()
	os.Setenv("OPENAI_API_KEY", "test-key-performance")
	defer os.Unsetenv("OPENAI_API_KEY")
	
	cfg, err := config.Load(tempDir, false)
	require.NoError(b, err)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		manager, err := coordination.NewManager(cfg)
		require.NoError(b, err)
		require.NotNil(b, manager)
	}
}

// BenchmarkSystemIntrospection tests system introspection performance
func BenchmarkSystemIntrospection(b *testing.B) {
	tempDir := b.TempDir()
	os.Setenv("OPENAI_API_KEY", "test-key-performance")
	defer os.Unsetenv("OPENAI_API_KEY")
	
	cfg, err := config.Load(tempDir, false)
	require.NoError(b, err)
	
	manager, err := coordination.NewManager(cfg)
	require.NoError(b, err)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		introspection, err := manager.GetSystemIntrospection()
		require.NoError(b, err)
		require.NotNil(b, introspection)
	}
}

// TestPerformanceBaselines validates that key operations meet performance expectations
func TestPerformanceBaselines(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance baseline tests in short mode")
	}

	tempDir := t.TempDir()
	os.Setenv("OPENAI_API_KEY", "test-key-performance")
	defer os.Unsetenv("OPENAI_API_KEY")

	t.Run("configuration load time", func(t *testing.T) {
		start := time.Now()
		cfg, err := config.Load(tempDir, false)
		duration := time.Since(start)

		require.NoError(t, err)
		require.NotNil(t, cfg)
		assert.Less(t, duration, 50*time.Millisecond, "Configuration loading should be fast")
	})

	t.Run("coordination manager creation time", func(t *testing.T) {
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)

		start := time.Now()
		manager, err := coordination.NewManager(cfg)
		duration := time.Since(start)

		require.NoError(t, err)
		require.NotNil(t, manager)
		assert.Less(t, duration, 10*time.Millisecond, "Coordination manager creation should be fast")
	})

	t.Run("system introspection time", func(t *testing.T) {
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)
		
		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)

		start := time.Now()
		introspection, err := manager.GetSystemIntrospection()
		duration := time.Since(start)

		require.NoError(t, err)
		require.NotNil(t, introspection)
		assert.Less(t, duration, 5*time.Millisecond, "System introspection should be fast")
	})

	t.Run("concurrent access performance", func(t *testing.T) {
		cfg, err := config.Load(tempDir, false)
		require.NoError(t, err)
		
		manager, err := coordination.NewManager(cfg)
		require.NoError(t, err)

		concurrency := 10
		done := make(chan time.Duration, concurrency)

		for i := 0; i < concurrency; i++ {
			go func() {
				start := time.Now()
				introspection, err := manager.GetSystemIntrospection()
				duration := time.Since(start)
				
				if err == nil && introspection != nil {
					done <- duration
				} else {
					done <- time.Duration(-1) // Error indicator
				}
			}()
		}

		var totalDuration time.Duration
		successCount := 0
		
		for i := 0; i < concurrency; i++ {
			duration := <-done
			if duration > 0 {
				totalDuration += duration
				successCount++
			}
		}

		assert.Equal(t, concurrency, successCount, "All concurrent operations should succeed")
		avgDuration := totalDuration / time.Duration(successCount)
		assert.Less(t, avgDuration, 10*time.Millisecond, "Average concurrent access time should be reasonable")
	})
}

// TestStabilityUnderLoad tests system stability under various load conditions
func TestStabilityUnderLoad(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping stability tests in short mode")
	}

	tempDir := t.TempDir()
	os.Setenv("OPENAI_API_KEY", "test-key-stability")
	defer os.Unsetenv("OPENAI_API_KEY")

	cfg, err := config.Load(tempDir, false)
	require.NoError(t, err)
	
	manager, err := coordination.NewManager(cfg)
	require.NoError(t, err)

	t.Run("sustained load test", func(t *testing.T) {
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		operations := 0
		errors := 0

		for {
			select {
			case <-ctx.Done():
				t.Logf("Sustained load test completed: %d operations, %d errors", operations, errors)
				assert.Less(t, float64(errors)/float64(operations), 0.01, "Error rate should be less than 1%")
				return
			default:
				_, err := manager.GetSystemIntrospection()
				operations++
				if err != nil {
					errors++
				}
				time.Sleep(1 * time.Millisecond) // Small delay to prevent overwhelming
			}
		}
	})

	t.Run("burst load test", func(t *testing.T) {
		bursts := 5
		operationsPerBurst := 100
		totalErrors := 0

		for burst := 0; burst < bursts; burst++ {
			done := make(chan error, operationsPerBurst)
			
			// Create burst
			for i := 0; i < operationsPerBurst; i++ {
				go func() {
					_, err := manager.GetSystemIntrospection()
					done <- err
				}()
			}

			// Collect results
			burstErrors := 0
			for i := 0; i < operationsPerBurst; i++ {
				if err := <-done; err != nil {
					burstErrors++
				}
			}

			t.Logf("Burst %d: %d operations, %d errors", burst+1, operationsPerBurst, burstErrors)
			totalErrors += burstErrors

			// Cool down between bursts
			time.Sleep(100 * time.Millisecond)
		}

		totalOperations := bursts * operationsPerBurst
		errorRate := float64(totalErrors) / float64(totalOperations)
		assert.Less(t, errorRate, 0.05, "Error rate under burst load should be less than 5%")
	})

	t.Run("memory stability test", func(t *testing.T) {
		// Run multiple operations to check for memory leaks
		iterations := 1000
		
		for i := 0; i < iterations; i++ {
			introspection, err := manager.GetSystemIntrospection()
			require.NoError(t, err)
			require.NotNil(t, introspection)
			
			// Verify expected data structure
			assert.NotEmpty(t, introspection.SystemStatus)
			assert.NotNil(t, introspection.AvailableAgents)
			assert.NotNil(t, introspection.SystemCapabilities)
		}
		
		// If we reach here without panics or excessive memory usage, test passes
		t.Log("Memory stability test completed successfully")
	})
}

// TestErrorRecovery tests system recovery from various error conditions
func TestErrorRecovery(t *testing.T) {
	tempDir := t.TempDir()
	os.Setenv("OPENAI_API_KEY", "test-key-recovery")
	defer os.Unsetenv("OPENAI_API_KEY")

	cfg, err := config.Load(tempDir, false)
	require.NoError(t, err)
	
	manager, err := coordination.NewManager(cfg)
	require.NoError(t, err)

	t.Run("invalid task delegation recovery", func(t *testing.T) {
		// Test invalid task delegation
		_, err := manager.DelegateTask("invalid_task_id", "invalid_task", "nonexistent_agent")
		assert.Error(t, err, "Invalid task delegation should return error")

		// System should remain functional
		introspection, err := manager.GetSystemIntrospection()
		assert.NoError(t, err, "System should remain functional after error")
		assert.NotNil(t, introspection)
	})

	t.Run("rapid error recovery", func(t *testing.T) {
		errorCount := 0
		successCount := 0
		
		// Generate multiple errors rapidly
		for i := 0; i < 50; i++ {
			_, err := manager.DelegateTask("invalid_task_"+string(rune(i)), "invalid", "none")
			if err != nil {
				errorCount++
			}
			
			// Verify system still works
			_, err = manager.GetSystemIntrospection()
			if err == nil {
				successCount++
			}
		}

		assert.Equal(t, 50, errorCount, "All invalid delegations should error")
		assert.Equal(t, 50, successCount, "System should remain functional during error recovery")
	})
}