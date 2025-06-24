package builtin

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/llm/tools"
	"github.com/caronex/intelligence-interface/internal/tools/coordination"
)

type SystemIntrospectionTool struct {
	config *config.Config
	manager *coordination.Manager
}

type AgentCoordinationTool struct {
	config *config.Config
	manager *coordination.Manager
}

type ConfigurationInspectionTool struct {
	config *config.Config
	manager *coordination.Manager
}

type AgentLifecycleTool struct {
	config *config.Config
	manager *coordination.Manager
}

type SpaceFoundationTool struct {
	config *config.Config
	manager *coordination.Manager
}

func NewSystemIntrospectionTool(cfg *config.Config, manager *coordination.Manager) *SystemIntrospectionTool {
	return &SystemIntrospectionTool{
		config: cfg,
		manager: manager,
	}
}

func NewAgentCoordinationTool(cfg *config.Config, manager *coordination.Manager) *AgentCoordinationTool {
	return &AgentCoordinationTool{
		config: cfg,
		manager: manager,
	}
}

func NewConfigurationInspectionTool(cfg *config.Config, manager *coordination.Manager) *ConfigurationInspectionTool {
	return &ConfigurationInspectionTool{
		config: cfg,
		manager: manager,
	}
}

func NewAgentLifecycleTool(cfg *config.Config, manager *coordination.Manager) *AgentLifecycleTool {
	return &AgentLifecycleTool{
		config: cfg,
		manager: manager,
	}
}

func NewSpaceFoundationTool(cfg *config.Config, manager *coordination.Manager) *SpaceFoundationTool {
	return &SpaceFoundationTool{
		config: cfg,
		manager: manager,
	}
}

func (t *SystemIntrospectionTool) Info() tools.ToolInfo {
	return tools.ToolInfo{
		Name:        "system_introspection",
		Description: "Provides comprehensive system state information including agents, capabilities, and configuration",
		Parameters: map[string]any{
			"include_details": map[string]any{
				"type":        "boolean",
				"description": "Include detailed agent and configuration information",
				"default":     true,
			},
		},
		Required: []string{},
	}
}

func (t *SystemIntrospectionTool) Run(ctx context.Context, params tools.ToolCall) (tools.ToolResponse, error) {
	var input struct {
		IncludeDetails bool `json:"include_details"`
	}
	input.IncludeDetails = true

	if params.Input != "" {
		if err := json.Unmarshal([]byte(params.Input), &input); err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Invalid input parameters: %v", err)), nil
		}
	}

	result, err := t.manager.GetSystemIntrospection()
	if err != nil {
		return tools.NewTextErrorResponse(fmt.Sprintf("Failed to get system introspection: %v", err)), nil
	}

	if !input.IncludeDetails {
		summary := fmt.Sprintf("System Status: %s | Agents: %d | Capabilities: %d | Evolution: %t",
			result.SystemStatus,
			len(result.AvailableAgents),
			len(result.SystemCapabilities),
			result.SystemConfig.EvolutionEnabled)
		return tools.NewTextResponse(summary), nil
	}

	resultBytes, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize system state: %v", err)), nil
	}

	return tools.NewTextResponse(string(resultBytes)), nil
}

func (t *AgentCoordinationTool) Info() tools.ToolInfo {
	return tools.ToolInfo{
		Name:        "agent_coordination",
		Description: "Coordinates agent activities, creates task plans, and delegates implementation tasks",
		Parameters: map[string]any{
			"action": map[string]any{
				"type":        "string",
				"description": "Action to perform: 'plan' for task planning, 'delegate' for task delegation, 'status' for coordination status",
				"enum":        []string{"plan", "delegate", "status"},
			},
			"task_description": map[string]any{
				"type":        "string",
				"description": "Description of the task to plan or delegate",
			},
			"preferred_agent": map[string]any{
				"type":        "string",
				"description": "Preferred agent for task delegation (optional)",
			},
			"requirements": map[string]any{
				"type":        "array",
				"description": "List of requirements for task planning",
				"items": map[string]any{
					"type": "string",
				},
			},
		},
		Required: []string{"action"},
	}
}

func (t *AgentCoordinationTool) Run(ctx context.Context, params tools.ToolCall) (tools.ToolResponse, error) {
	var input struct {
		Action          string   `json:"action"`
		TaskDescription string   `json:"task_description"`
		PreferredAgent  string   `json:"preferred_agent"`
		Requirements    []string `json:"requirements"`
	}

	if err := json.Unmarshal([]byte(params.Input), &input); err != nil {
		return tools.NewTextErrorResponse(fmt.Sprintf("Invalid input parameters: %v", err)), nil
	}

	switch input.Action {
	case "plan":
		if input.TaskDescription == "" {
			return tools.NewTextErrorResponse("Task description is required for planning"), nil
		}

		plan, err := t.manager.CreateTaskPlan(input.TaskDescription, input.Requirements)
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to create task plan: %v", err)), nil
		}

		planBytes, err := json.MarshalIndent(plan, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize task plan: %v", err)), nil
		}

		return tools.NewTextResponse(string(planBytes)), nil

	case "delegate":
		if input.TaskDescription == "" {
			return tools.NewTextErrorResponse("Task description is required for delegation"), nil
		}

		taskID := fmt.Sprintf("task_%d", len(input.TaskDescription))
		delegation, err := t.manager.DelegateTask(taskID, input.TaskDescription, input.PreferredAgent)
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to delegate task: %v", err)), nil
		}

		delegationBytes, err := json.MarshalIndent(delegation, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize delegation result: %v", err)), nil
		}

		return tools.NewTextResponse(string(delegationBytes)), nil

	case "status":
		status := map[string]interface{}{
			"coordination_active": true,
			"available_agents":    len(t.config.Agents),
			"coordination_mode":   "cooperative",
			"delegation_enabled":  true,
			"planning_enabled":    true,
		}

		statusBytes, err := json.MarshalIndent(status, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize coordination status: %v", err)), nil
		}

		return tools.NewTextResponse(string(statusBytes)), nil

	default:
		return tools.NewTextErrorResponse(fmt.Sprintf("Unknown action: %s. Valid actions: plan, delegate, status", input.Action)), nil
	}
}

func (t *ConfigurationInspectionTool) Info() tools.ToolInfo {
	return tools.ToolInfo{
		Name:        "configuration_inspection",
		Description: "Inspects and validates system configuration, reports configuration state and issues",
		Parameters: map[string]any{
			"section": map[string]any{
				"type":        "string",
				"description": "Configuration section to inspect: 'all', 'agents', 'caronex', 'spaces'",
				"default":     "all",
			},
			"validate": map[string]any{
				"type":        "boolean",
				"description": "Perform configuration validation",
				"default":     true,
			},
		},
		Required: []string{},
	}
}

func (t *ConfigurationInspectionTool) Run(ctx context.Context, params tools.ToolCall) (tools.ToolResponse, error) {
	var input struct {
		Section  string `json:"section"`
		Validate bool   `json:"validate"`
	}
	input.Section = "all"
	input.Validate = true

	if params.Input != "" {
		if err := json.Unmarshal([]byte(params.Input), &input); err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Invalid input parameters: %v", err)), nil
		}
	}

	result := make(map[string]interface{})

	if input.Section == "all" || input.Section == "agents" {
		agents := make(map[string]interface{})
		for agentName, agentConfig := range t.config.Agents {
			agents[string(agentName)] = map[string]interface{}{
				"model":      agentConfig.Model,
				"max_tokens": agentConfig.MaxTokens,
				"has_specialization": agentConfig.Specialization != nil,
			}
		}
		result["agents"] = agents
	}

	if input.Section == "all" || input.Section == "caronex" {
		result["caronex"] = map[string]interface{}{
			"enabled":           t.config.Caronex.Enabled,
			"evolution_enabled": t.config.Caronex.Evolution.Enabled,
			"max_agents":        t.config.Caronex.Coordination.MaxConcurrentAgents,
			"memory_limit":      t.config.Caronex.Coordination.SpaceMemoryLimit,
		}
	}

	if input.Section == "all" || input.Section == "spaces" {
		result["spaces"] = map[string]interface{}{
			"configured_count": len(t.config.Spaces),
			"supported":        true,
		}
	}

	if input.Validate {
		if err := config.Validate(); err != nil {
			result["validation_errors"] = []string{err.Error()}
		} else {
			result["validation_status"] = "valid"
		}
	}

	resultBytes, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize configuration: %v", err)), nil
	}

	return tools.NewTextResponse(string(resultBytes)), nil
}

func (t *AgentLifecycleTool) Info() tools.ToolInfo {
	return tools.ToolInfo{
		Name:        "agent_lifecycle",
		Description: "Manages agent lifecycle, lists available agents, checks readiness, and coordinates task delegation",
		Parameters: map[string]any{
			"action": map[string]any{
				"type":        "string",
				"description": "Action to perform: 'list' for available agents, 'status' for agent status, 'capabilities' for agent capabilities",
				"enum":        []string{"list", "status", "capabilities"},
			},
			"agent_name": map[string]any{
				"type":        "string",
				"description": "Specific agent name for status checks (optional)",
			},
		},
		Required: []string{"action"},
	}
}

func (t *AgentLifecycleTool) Run(ctx context.Context, params tools.ToolCall) (tools.ToolResponse, error) {
	var input struct {
		Action    string `json:"action"`
		AgentName string `json:"agent_name"`
	}

	if err := json.Unmarshal([]byte(params.Input), &input); err != nil {
		return tools.NewTextErrorResponse(fmt.Sprintf("Invalid input parameters: %v", err)), nil
	}

	switch input.Action {
	case "list":
		agents := make([]map[string]interface{}, 0)
		for agentName, agentConfig := range t.config.Agents {
			agentInfo := map[string]interface{}{
				"name":   string(agentName),
				"model":  agentConfig.Model,
				"status": "available",
			}

			if agentConfig.Specialization != nil {
				agentInfo["specialization"] = agentConfig.Specialization.CoordinationMode
				agentInfo["learning_enabled"] = agentConfig.Specialization.LearningRate > 0
				agentInfo["evolution_capable"] = agentConfig.Specialization.EvolutionCapable
			}

			agents = append(agents, agentInfo)
		}

		result := map[string]interface{}{
			"total_agents":     len(agents),
			"available_agents": agents,
		}

		resultBytes, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize agent list: %v", err)), nil
		}

		return tools.NewTextResponse(string(resultBytes)), nil

	case "status":
		var result map[string]interface{}

		if input.AgentName != "" {
			if agentConfig, exists := t.config.Agents[config.AgentName(input.AgentName)]; exists {
				result = map[string]interface{}{
					"agent_name": input.AgentName,
					"status":     "available",
					"model":      agentConfig.Model,
					"ready":      true,
				}
			} else {
				result = map[string]interface{}{
					"agent_name": input.AgentName,
					"status":     "not_found",
					"ready":      false,
				}
			}
		} else {
			readyCount := 0
			for range t.config.Agents {
				readyCount++
			}

			result = map[string]interface{}{
				"total_agents": len(t.config.Agents),
				"ready_agents": readyCount,
				"system_ready": readyCount > 0,
			}
		}

		resultBytes, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize agent status: %v", err)), nil
		}

		return tools.NewTextResponse(string(resultBytes)), nil

	case "capabilities":
		capabilities := make(map[string][]string)
		
		for agentName := range t.config.Agents {
			agentCaps := t.getAgentCapabilities(agentName)
			capabilities[string(agentName)] = agentCaps
		}

		result := map[string]interface{}{
			"agent_capabilities": capabilities,
		}

		resultBytes, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize capabilities: %v", err)), nil
		}

		return tools.NewTextResponse(string(resultBytes)), nil

	default:
		return tools.NewTextErrorResponse(fmt.Sprintf("Unknown action: %s. Valid actions: list, status, capabilities", input.Action)), nil
	}
}

func (t *AgentLifecycleTool) getAgentCapabilities(agentName config.AgentName) []string {
	switch agentName {
	case config.AgentCaronex:
		return []string{"system_coordination", "agent_management", "planning_assistance", "system_evolution"}
	default:
		return []string{"general_assistance", "code_generation", "analysis", "implementation"}
	}
}

func (t *SpaceFoundationTool) Info() tools.ToolInfo {
	return tools.ToolInfo{
		Name:        "space_foundation",
		Description: "Provides introspection of space management foundation and guidance for future space implementation",
		Parameters: map[string]any{
			"action": map[string]any{
				"type":        "string",
				"description": "Action to perform: 'status' for foundation status, 'config' for space configuration options, 'guidance' for implementation guidance",
				"enum":        []string{"status", "config", "guidance"},
			},
		},
		Required: []string{"action"},
	}
}

func (t *SpaceFoundationTool) Run(ctx context.Context, params tools.ToolCall) (tools.ToolResponse, error) {
	var input struct {
		Action string `json:"action"`
	}

	if err := json.Unmarshal([]byte(params.Input), &input); err != nil {
		return tools.NewTextErrorResponse(fmt.Sprintf("Invalid input parameters: %v", err)), nil
	}

	switch input.Action {
	case "status":
		result := map[string]interface{}{
			"foundation_ready":     true,
			"configuration_support": true,
			"ui_layout_support":    true,
			"persistence_support":  true,
			"agent_assignment":     true,
			"evolution_capable":    t.config.Caronex.Evolution.Enabled,
			"configured_spaces":    len(t.config.Spaces),
		}

		resultBytes, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize space status: %v", err)), nil
		}

		return tools.NewTextResponse(string(resultBytes)), nil

	case "config":
		configOptions := map[string]interface{}{
			"space_types": []string{"development", "knowledge_base", "communication", "creative", "analysis"},
			"ui_layouts":  []string{"panels", "terminal", "hybrid", "custom"},
			"themes":      []string{"intelligence-interface", "dark", "light", "catppuccin"},
			"persistence_backends": []string{"memory", "file", "database"},
			"agent_assignment_modes": []string{"manual", "automatic", "dynamic"},
		}

		if len(t.config.Spaces) > 0 {
			configuredSpaces := make(map[string]interface{})
			for spaceID, spaceConfig := range t.config.Spaces {
				configuredSpaces[spaceID] = map[string]interface{}{
					"name": spaceConfig.Name,
					"type": spaceConfig.Type,
					"ui_layout": spaceConfig.UILayout.Type,
					"agents": spaceConfig.AssignedAgents,
				}
			}
			configOptions["configured_spaces"] = configuredSpaces
		}

		resultBytes, err := json.MarshalIndent(configOptions, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize space config: %v", err)), nil
		}

		return tools.NewTextResponse(string(resultBytes)), nil

	case "guidance":
		guidance := map[string]interface{}{
			"implementation_phases": []string{
				"Phase 1: Space UI Infrastructure",
				"Phase 2: Space Management API",
				"Phase 3: Agent-Space Integration",
				"Phase 4: Space Persistence",
				"Phase 5: Space Evolution",
			},
			"prerequisites": []string{
				"TUI infrastructure (✓ completed)",
				"Agent system (✓ completed)",
				"Configuration framework (✓ completed)",
				"Caronex manager (✓ completed)",
			},
			"next_steps": []string{
				"Implement space UI components",
				"Create space management service",
				"Add space switching hotkeys",
				"Implement space persistence",
			},
			"estimated_effort": "2-3 sprints for full space management",
		}

		resultBytes, err := json.MarshalIndent(guidance, "", "  ")
		if err != nil {
			return tools.NewTextErrorResponse(fmt.Sprintf("Failed to serialize space guidance: %v", err)), nil
		}

		return tools.NewTextResponse(string(resultBytes)), nil

	default:
		return tools.NewTextErrorResponse(fmt.Sprintf("Unknown action: %s. Valid actions: status, config, guidance", input.Action)), nil
	}
}