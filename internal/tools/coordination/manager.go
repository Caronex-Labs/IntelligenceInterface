package coordination

import (
	"fmt"
	"strings"
	"time"

	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/core/logging"
)

// Manager provides coordination tools for the Caronex manager agent
type Manager struct {
	config *config.Config
	
	// Coordination capabilities
	introspectionTools *IntrospectionTools
	planningTools     *PlanningTools
	delegationTools   *DelegationTools
}

// IntrospectionTools provides system state inspection capabilities
type IntrospectionTools struct {
}

// PlanningTools provides task planning and breakdown capabilities
type PlanningTools struct {
}

// DelegationTools provides agent delegation and communication capabilities
type DelegationTools struct {
}

// SystemIntrospectionResult contains results of system introspection
type SystemIntrospectionResult struct {
	AvailableAgents    []AgentCapability `json:"available_agents"`
	SystemConfig       ConfigSummary     `json:"system_config"`
	SystemCapabilities []string          `json:"system_capabilities"`
	SystemStatus       string            `json:"system_status"`
	LastUpdated        time.Time         `json:"last_updated"`
}

// AgentCapability describes an agent and its capabilities
type AgentCapability struct {
	Name           string   `json:"name"`
	Model          string   `json:"model"`
	Capabilities   []string `json:"capabilities"`
	Status         string   `json:"status"`
	Specialization string   `json:"specialization,omitempty"`
}

// ConfigSummary provides a summary of system configuration
type ConfigSummary struct {
	AgentCount        int    `json:"agent_count"`
	ProvidersEnabled  []string `json:"providers_enabled"`
	EvolutionEnabled  bool   `json:"evolution_enabled"`
	SpacesSupported   bool   `json:"spaces_supported"`
	ConfigurationHash string `json:"configuration_hash"`
}

// TaskPlan represents a planned breakdown of a complex task
type TaskPlan struct {
	TaskID      string     `json:"task_id"`
	Description string     `json:"description"`
	Steps       []TaskStep `json:"steps"`
	Dependencies []string  `json:"dependencies"`
	EstimatedDuration string `json:"estimated_duration"`
	RequiredAgents []string `json:"required_agents"`
}

// TaskStep represents a single step in a task plan
type TaskStep struct {
	StepID        string   `json:"step_id"`
	Description   string   `json:"description"`
	AssignedAgent string   `json:"assigned_agent"`
	Dependencies  []string `json:"dependencies"`
	Status        string   `json:"status"`
	EstimatedTime string   `json:"estimated_time"`
}

// DelegationResult represents the result of task delegation
type DelegationResult struct {
	TaskID       string    `json:"task_id"`
	AssignedTo   string    `json:"assigned_to"`
	Status       string    `json:"status"`
	Message      string    `json:"message"`
	CreatedAt    time.Time `json:"created_at"`
	ExpectedCompletion time.Time `json:"expected_completion,omitempty"`
}

// NewManager creates a new coordination manager with all tools initialized
func NewManager(cfg *config.Config) (*Manager, error) {
	introspectionTools := &IntrospectionTools{}
	planningTools := &PlanningTools{}
	delegationTools := &DelegationTools{}

	manager := &Manager{
		config:             cfg,
		introspectionTools: introspectionTools,
		planningTools:     planningTools,
		delegationTools:   delegationTools,
	}

	logging.Info("Coordination manager initialized successfully")
	return manager, nil
}

// GetSystemIntrospection provides comprehensive system state information
func (m *Manager) GetSystemIntrospection() (*SystemIntrospectionResult, error) {
	logging.Debug("Performing system introspection")

	// Get available agents with their capabilities
	availableAgents := make([]AgentCapability, 0)
	for agentName, agentConfig := range m.config.Agents {
		capabilities := m.getAgentCapabilities(agentName)
		specialization := ""
		if agentConfig.Specialization != nil {
			specialization = agentConfig.Specialization.CoordinationMode
		}

		agentCapability := AgentCapability{
			Name:           string(agentName),
			Model:          string(agentConfig.Model),
			Capabilities:   capabilities,
			Status:         "available", // In real system, this would be dynamic
			Specialization: specialization,
		}
		availableAgents = append(availableAgents, agentCapability)
	}

	// Create configuration summary
	configSummary := ConfigSummary{
		AgentCount:        len(m.config.Agents),
		ProvidersEnabled:  m.getEnabledProviders(),
		EvolutionEnabled:  m.config.Caronex.Evolution.Enabled,
		SpacesSupported:   true, // Intelligence Interface supports spaces
		ConfigurationHash: m.generateConfigHash(),
	}

	// Get system capabilities
	systemCapabilities := m.getSystemCapabilities()

	result := &SystemIntrospectionResult{
		AvailableAgents:    availableAgents,
		SystemConfig:       configSummary,
		SystemCapabilities: systemCapabilities,
		SystemStatus:       "operational",
		LastUpdated:        time.Now(),
	}

	logging.Info("System introspection completed", 
		"agents", len(availableAgents),
		"capabilities", len(systemCapabilities))

	return result, nil
}

// CreateTaskPlan breaks down a complex task into manageable steps
func (m *Manager) CreateTaskPlan(taskDescription string, requirements []string) (*TaskPlan, error) {
	logging.Debug("Creating task plan", "description", taskDescription)

	// Generate unique task ID
	taskID := fmt.Sprintf("task_%d", time.Now().Unix())

	// Analyze requirements and create steps
	steps := m.planningTools.analyzeAndCreateSteps(taskDescription, requirements)

	// Determine required agents based on steps
	requiredAgents := m.planningTools.determineRequiredAgents(steps)

	// Calculate dependencies
	dependencies := m.planningTools.calculateDependencies(steps)

	// Estimate duration
	estimatedDuration := m.planningTools.estimateDuration(steps)

	taskPlan := &TaskPlan{
		TaskID:            taskID,
		Description:       taskDescription,
		Steps:             steps,
		Dependencies:      dependencies,
		EstimatedDuration: estimatedDuration,
		RequiredAgents:    requiredAgents,
	}

	logging.Info("Task plan created", 
		"task_id", taskID,
		"steps", len(steps),
		"required_agents", len(requiredAgents))

	return taskPlan, nil
}

// DelegateTask assigns a task to an appropriate agent
func (m *Manager) DelegateTask(taskID string, taskDescription string, preferredAgent string) (*DelegationResult, error) {
	logging.Debug("Delegating task", "task_id", taskID, "preferred_agent", preferredAgent)

	// Determine best agent for the task
	assignedAgent := m.delegationTools.selectBestAgent(taskDescription, preferredAgent, m.config.Agents)

	// Create delegation result
	result := &DelegationResult{
		TaskID:     taskID,
		AssignedTo: assignedAgent,
		Status:     "delegated",
		Message:    fmt.Sprintf("Task successfully delegated to %s", assignedAgent),
		CreatedAt:  time.Now(),
		ExpectedCompletion: time.Now().Add(2 * time.Hour), // Default 2-hour estimation
	}

	logging.Info("Task delegated successfully", 
		"task_id", taskID,
		"assigned_to", assignedAgent)

	return result, nil
}

// getAgentCapabilities returns capabilities for a specific agent
func (m *Manager) getAgentCapabilities(agentName config.AgentName) []string {
	switch agentName {
	case config.AgentCaronex:
		return []string{"system_coordination", "agent_management", "planning_assistance", "system_evolution",
			"code_generation", "code_analysis", "debugging", "refactoring", "architecture_review",
			"text_summarization", "context_compression", "content_analysis", "documentation",
			"task_planning", "requirement_analysis", "project_coordination", "timeline_management"}
	default:
		return []string{"general_assistance"}
	}
}

// getEnabledProviders returns list of enabled AI providers
func (m *Manager) getEnabledProviders() []string {
	// In a real implementation, this would check actual provider availability
	return []string{"openai", "anthropic", "google", "groq"}
}

// getSystemCapabilities returns overall system capabilities
func (m *Manager) getSystemCapabilities() []string {
	capabilities := []string{
		"multi_agent_coordination",
		"task_planning_and_delegation",
		"system_introspection",
		"configuration_management",
		"session_management",
		"tool_integration",
	}

	if m.config.Caronex.Evolution.Enabled {
		capabilities = append(capabilities, "system_evolution", "bootstrap_compilation")
	}

	return capabilities
}

// generateConfigHash creates a simple hash of current configuration
func (m *Manager) generateConfigHash() string {
	// Simple hash based on agent count and configuration
	return fmt.Sprintf("cfg_%d_%d", len(m.config.Agents), time.Now().Day())
}

// Helper methods for planning tools
func (p *PlanningTools) analyzeAndCreateSteps(taskDescription string, requirements []string) []TaskStep {
	// Simplified step creation based on common patterns
	steps := []TaskStep{
		{
			StepID:        "step_1",
			Description:   "Analyze requirements and plan approach",
			AssignedAgent: "task",
			Dependencies:  []string{},
			Status:        "pending",
			EstimatedTime: "30 minutes",
		},
	}

	// Add implementation step if needed
	if len(requirements) > 0 {
		steps = append(steps, TaskStep{
			StepID:        "step_2",
			Description:   "Implement solution based on requirements",
			AssignedAgent: "coder",
			Dependencies:  []string{"step_1"},
			Status:        "pending",
			EstimatedTime: "1-2 hours",
		})
	}

	return steps
}

func (p *PlanningTools) determineRequiredAgents(steps []TaskStep) []string {
	agentSet := make(map[string]bool)
	for _, step := range steps {
		if step.AssignedAgent != "" {
			agentSet[step.AssignedAgent] = true
		}
	}

	agents := make([]string, 0, len(agentSet))
	for agent := range agentSet {
		agents = append(agents, agent)
	}
	return agents
}

func (p *PlanningTools) calculateDependencies(steps []TaskStep) []string {
	dependencies := make([]string, 0)
	for _, step := range steps {
		if len(step.Dependencies) > 0 {
			dependencies = append(dependencies, step.Dependencies...)
		}
	}
	return dependencies
}

func (p *PlanningTools) estimateDuration(steps []TaskStep) string {
	if len(steps) <= 1 {
		return "1 hour"
	} else if len(steps) <= 3 {
		return "2-3 hours"
	}
	return "4+ hours"
}

// Helper methods for delegation tools
func (d *DelegationTools) selectBestAgent(taskDescription string, preferredAgent string, agents map[config.AgentName]config.Agent) string {
	// If preferred agent is specified and available, use it
	if preferredAgent != "" {
		for agentName := range agents {
			if string(agentName) == preferredAgent {
				return preferredAgent
			}
		}
	}

	// Simple agent selection based on task keywords
	taskLower := strings.ToLower(taskDescription)
	
	if strings.Contains(taskLower, "code") || strings.Contains(taskLower, "implement") {
		return "coder"
	} else if strings.Contains(taskLower, "plan") || strings.Contains(taskLower, "task") {
		return "task"
	} else if strings.Contains(taskLower, "summary") || strings.Contains(taskLower, "summarize") {
		return "summarizer"
	} else if strings.Contains(taskLower, "title") || strings.Contains(taskLower, "name") {
		return "title"
	}

	// Default to task agent for planning
	return "task"
}

// GetIntrospectionTools returns the introspection tools
func (m *Manager) GetIntrospectionTools() *IntrospectionTools {
	return m.introspectionTools
}

// GetPlanningTools returns the planning tools
func (m *Manager) GetPlanningTools() *PlanningTools {
	return m.planningTools
}

// GetDelegationTools returns the delegation tools
func (m *Manager) GetDelegationTools() *DelegationTools {
	return m.delegationTools
}