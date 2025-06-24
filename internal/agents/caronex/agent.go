package caronex

import (
	"fmt"
	"strings"
	"time"

	"github.com/caronex/intelligence-interface/internal/agents/base"
	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/core/logging"
	"github.com/caronex/intelligence-interface/internal/llm/tools"
	"github.com/caronex/intelligence-interface/internal/tools/coordination"
	"github.com/caronex/intelligence-interface/internal/session"
	"github.com/caronex/intelligence-interface/internal/message"
)

// CaronexAgent represents the central manager agent for Intelligence Interface coordination
type CaronexAgent struct {
	Service       base.Service // Embedded base agent service
	config        *config.Config
	
	// Manager-specific capabilities
	coordinationTools   *coordination.Manager
	systemState        *SystemState
	agentRegistry      map[config.AgentName]*AgentInfo
	
	// Manager personality and behavior
	managerPersonality *ManagerPersonality
	coordinationMode   string
}

// AgentInfo contains information about available agents
type AgentInfo struct {
	Name           config.AgentName
	Capabilities   []string
	Specialization *config.AgentSpecialization
	Status         AgentStatus
	LastSeen       time.Time
}

// AgentStatus represents the current status of an agent
type AgentStatus string

const (
	AgentStatusAvailable AgentStatus = "available"
	AgentStatusBusy      AgentStatus = "busy"
	AgentStatusOffline   AgentStatus = "offline"
)

// SystemState represents the current state of the Intelligence Interface system
type SystemState struct {
	AvailableAgents    []string
	ConfigurationHash  string
	SystemCapabilities []string
	LastUpdated        time.Time
	EvolutionEnabled   bool
	SpacesSupported    bool
}

// ManagerPersonality defines the behavior patterns for Caronex manager
type ManagerPersonality struct {
	PlanningFocused      bool
	CoordinationOriented bool
	ImplementationBoundary bool
	HelpfulButDelegating bool
	SystemAware          bool
}

// NewCaronexAgent creates a new Caronex manager agent with coordination capabilities
func NewCaronexAgent(cfg *config.Config, sessionService session.Service, messageService message.Service) (*CaronexAgent, error) {
	// Create base service with manager-specific configuration  
	baseService, err := base.NewAgent(
		config.AgentCaronex,
		sessionService,
		messageService,
		[]tools.BaseTool{}, // No special tools for manager agent
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create base service for CaronexAgent: %w", err)
	}

	// Initialize coordination tools
	coordinationTools, err := coordination.NewManager(cfg)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize coordination tools: %w", err)
	}

	// Initialize system state
	systemState := &SystemState{
		AvailableAgents:    []string{},
		ConfigurationHash:  "",
		SystemCapabilities: []string{},
		LastUpdated:        time.Now(),
		EvolutionEnabled:   cfg.Caronex.Evolution.Enabled,
		SpacesSupported:    true, // Intelligence Interface supports spaces
	}

	// Initialize manager personality
	managerPersonality := &ManagerPersonality{
		PlanningFocused:        true,
		CoordinationOriented:   true,
		ImplementationBoundary: true, // Clear boundary - no direct implementation
		HelpfulButDelegating:   true,
		SystemAware:           true,
	}

	// Get coordination mode from agent specialization
	coordinationMode := "cooperative"
	if agentConfig, exists := cfg.Agents[config.AgentCaronex]; exists && agentConfig.Specialization != nil {
		if agentConfig.Specialization.CoordinationMode != "" {
			coordinationMode = agentConfig.Specialization.CoordinationMode
		}
	}

	caronexAgent := &CaronexAgent{
		Service:            baseService,
		config:             cfg,
		coordinationTools:  coordinationTools,
		systemState:       systemState,
		agentRegistry:     make(map[config.AgentName]*AgentInfo),
		managerPersonality: managerPersonality,
		coordinationMode:   coordinationMode,
	}

	// Initialize agent registry with available agents
	err = caronexAgent.initializeAgentRegistry()
	if err != nil {
		return nil, fmt.Errorf("failed to initialize agent registry: %w", err)
	}

	// Update system state with current configuration
	err = caronexAgent.updateSystemState()
	if err != nil {
		logging.Error("Failed to update initial system state", "error", err)
	}

	logging.Info("CaronexAgent initialized successfully", 
		"coordination_mode", coordinationMode,
		"available_agents", len(caronexAgent.agentRegistry))

	return caronexAgent, nil
}

// initializeAgentRegistry sets up the registry of available agents
func (c *CaronexAgent) initializeAgentRegistry() error {
	logging.Debug("Initializing agent registry")
	
	// Register all configured agents
	for agentName, agentConfig := range c.config.Agents {
		// Skip self-registration
		if agentName == config.AgentCaronex {
			continue
		}

		agentInfo := &AgentInfo{
			Name:           agentName,
			Capabilities:   c.getAgentCapabilities(agentName),
			Specialization: agentConfig.Specialization,
			Status:         AgentStatusAvailable,
			LastSeen:       time.Now(),
		}

		c.agentRegistry[agentName] = agentInfo
		logging.Debug("Registered agent", "name", agentName, "capabilities", agentInfo.Capabilities)
	}

	logging.Info("Agent registry initialized", "total_agents", len(c.agentRegistry))
	return nil
}

// getAgentCapabilities returns the capabilities of a specific agent
func (c *CaronexAgent) getAgentCapabilities(agentName config.AgentName) []string {
	switch agentName {
	case config.AgentCaronex:
		return []string{"system_coordination", "task_planning", "agent_delegation", "strategic_planning"}
	default:
		return []string{"general_assistance", "code_generation", "analysis", "implementation"}
	}
}

// updateSystemState refreshes the current system state information
func (c *CaronexAgent) updateSystemState() error {
	logging.Debug("Updating system state")

	// Update available agents list
	availableAgents := make([]string, 0, len(c.agentRegistry))
	for agentName, agentInfo := range c.agentRegistry {
		if agentInfo.Status == AgentStatusAvailable {
			availableAgents = append(availableAgents, string(agentName))
		}
	}
	c.systemState.AvailableAgents = availableAgents

	// Update system capabilities based on available agents
	capabilities := []string{"system_coordination", "agent_management", "planning_assistance"}
	for _, agentInfo := range c.agentRegistry {
		if agentInfo.Status == AgentStatusAvailable {
			capabilities = append(capabilities, agentInfo.Capabilities...)
		}
	}
	c.systemState.SystemCapabilities = capabilities

	// Update configuration hash for change detection
	c.systemState.ConfigurationHash = c.generateConfigurationHash()
	c.systemState.LastUpdated = time.Now()

	logging.Debug("System state updated", 
		"available_agents", len(availableAgents),
		"total_capabilities", len(capabilities))
	
	return nil
}

// generateConfigurationHash creates a hash of the current configuration for change detection
func (c *CaronexAgent) generateConfigurationHash() string {
	// Simple hash based on configured agents and their models
	var configElements []string
	for agentName, agentConfig := range c.config.Agents {
		configElements = append(configElements, fmt.Sprintf("%s:%s", agentName, agentConfig.Model))
	}
	return fmt.Sprintf("config_%d", len(strings.Join(configElements, "|")))
}

// GetSystemState returns the current system state for introspection
func (c *CaronexAgent) GetSystemState() *SystemState {
	c.updateSystemState() // Ensure current state
	return c.systemState
}

// GetAgentRegistry returns information about all registered agents
func (c *CaronexAgent) GetAgentRegistry() map[config.AgentName]*AgentInfo {
	return c.agentRegistry
}

// GetCoordinationCapabilities returns the coordination capabilities of Caronex
func (c *CaronexAgent) GetCoordinationCapabilities() []string {
	return []string{
		"system_introspection",
		"agent_coordination",
		"task_planning",
		"implementation_delegation",
		"progress_monitoring",
		"system_evolution_planning",
	}
}

// IsManagerAgent always returns true for CaronexAgent (manager vs implementer distinction)
func (c *CaronexAgent) IsManagerAgent() bool {
	return true
}

// ShouldImplementDirectly always returns false for CaronexAgent (coordination only)
func (c *CaronexAgent) ShouldImplementDirectly() bool {
	return false
}

// GetManagerPersonality returns the manager personality configuration
func (c *CaronexAgent) GetManagerPersonality() *ManagerPersonality {
	return c.managerPersonality
}

// String returns a string representation of the CaronexAgent
func (c *CaronexAgent) String() string {
	return fmt.Sprintf("CaronexAgent(coordination_mode=%s, agents=%d, capabilities=%d)",
		c.coordinationMode,
		len(c.agentRegistry),
		len(c.systemState.SystemCapabilities))
}