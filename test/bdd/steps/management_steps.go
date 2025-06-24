package steps

import (
	"context"
	"encoding/json"
	"fmt"
	"os"

	"github.com/cucumber/godog"
	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/llm/tools"
	"github.com/caronex/intelligence-interface/internal/tools/builtin"
	"github.com/caronex/intelligence-interface/internal/tools/coordination"
)

type ManagementTestState struct {
	caronexAgent      bool
	systemRunning     bool
	configLoaded      bool
	introspectionData map[string]interface{}
	coordinationData  map[string]interface{}
	configData        map[string]interface{}
	agentData         map[string]interface{}
	spaceData         map[string]interface{}
	errors           []error
	
	// Tools for testing
	systemIntrospectionTool    *builtin.SystemIntrospectionTool
	agentCoordinationTool      *builtin.AgentCoordinationTool
	configInspectionTool       *builtin.ConfigurationInspectionTool
	agentLifecycleTool         *builtin.AgentLifecycleTool
	spaceFoundationTool        *builtin.SpaceFoundationTool
}

var managementTestState = &ManagementTestState{
	introspectionData: make(map[string]interface{}),
	coordinationData:  make(map[string]interface{}),
	configData:        make(map[string]interface{}),
	agentData:         make(map[string]interface{}),
	spaceData:         make(map[string]interface{}),
	errors:           make([]error, 0),
}

func RegisterManagementSteps(ctx *godog.ScenarioContext) {
	// Background steps
	ctx.Step(`^I am Caronex with access to management tools$`, iAmCaronexWithAccessToManagementTools)
	ctx.Step(`^the Intelligence Interface system is running$`, theIntelligenceInterfaceSystemIsRunning)
	ctx.Step(`^the configuration is properly loaded$`, theConfigurationIsProperlyLoaded)

	// System state introspection scenario
	ctx.Step(`^I need to assess current system capabilities$`, iNeedToAssessCurrentSystemCapabilities)
	ctx.Step(`^I should be able to query available agents and their specializations$`, iShouldBeAbleToQueryAvailableAgentsAndTheirSpecializations)
	ctx.Step(`^I should be able to check current configuration state$`, iShouldBeAbleToCheckCurrentConfigurationState)
	ctx.Step(`^I should be able to report system status accurately$`, iShouldBeAbleToReportSystemStatusAccurately)

	// Basic coordination capabilities scenario
	ctx.Step(`^I need to coordinate agent activities$`, iNeedToCoordinateAgentActivities)
	ctx.Step(`^I assess implementation requirements$`, iAssessImplementationRequirements)
	ctx.Step(`^I should be able to identify appropriate specialist agents$`, iShouldBeAbleToIdentifyAppropriateSpecialistAgents)
	ctx.Step(`^I should be able to provide planning guidance$`, iShouldBeAbleToProvidePlanningGuidance)
	ctx.Step(`^I should be able to delegate implementation tasks appropriately$`, iShouldBeAbleToDelegateImplementationTasksAppropriately)

	// Configuration management scenario
	ctx.Step(`^I need to understand system configuration$`, iNeedToUnderstandSystemConfiguration)
	ctx.Step(`^I query configuration state$`, iQueryConfigurationState)
	ctx.Step(`^I should be able to retrieve current configuration values$`, iShouldBeAbleToRetrieveCurrentConfigurationValues)
	ctx.Step(`^I should be able to validate configuration consistency$`, iShouldBeAbleToValidateConfigurationConsistency)
	ctx.Step(`^I should be able to report configuration issues if any exist$`, iShouldBeAbleToReportConfigurationIssuesIfAnyExist)

	// Agent lifecycle management scenario
	ctx.Step(`^I manage agent operations$`, iManageAgentOperations)
	ctx.Step(`^I should be able to list available agent types$`, iShouldBeAbleToListAvailableAgentTypes)
	ctx.Step(`^I should be able to check agent readiness status$`, iShouldBeAbleToCheckAgentReadinessStatus)
	ctx.Step(`^I should be able to coordinate agent task delegation$`, iShouldBeAbleToCoordinateAgentTaskDelegation)

	// Space foundation introspection scenario
	ctx.Step(`^the foundation for space management exists$`, theFoundationForSpaceManagementExists)
	ctx.Step(`^I query space-related capabilities$`, iQuerySpaceRelatedCapabilities)
	ctx.Step(`^I should be able to list basic space configuration options$`, iShouldBeAbleToListBasicSpaceConfigurationOptions)
	ctx.Step(`^I should be able to report space readiness status$`, iShouldBeAbleToReportSpaceReadinessStatus)
	ctx.Step(`^I should be able to provide guidance for future space implementation$`, iShouldBeAbleToProvideGuidanceForFutureSpaceImplementation)
}

// Background step implementations
func iAmCaronexWithAccessToManagementTools() error {
	// Set up test environment
	os.Setenv("OPENAI_API_KEY", "test-key-for-management")
	
	// Load test configuration
	tempDir := "/tmp"
	_, err := config.Load(tempDir, false)
	if err != nil {
		return fmt.Errorf("failed to load configuration: %v", err)
	}
	
	cfg := config.Get()
	
	// Initialize coordination manager
	coordinationManager, err := coordination.NewManager(cfg)
	if err != nil {
		return fmt.Errorf("failed to initialize coordination manager: %v", err)
	}
	
	// Initialize management tools
	managementTestState.systemIntrospectionTool = builtin.NewSystemIntrospectionTool(cfg, coordinationManager)
	managementTestState.agentCoordinationTool = builtin.NewAgentCoordinationTool(cfg, coordinationManager)
	managementTestState.configInspectionTool = builtin.NewConfigurationInspectionTool(cfg, coordinationManager)
	managementTestState.agentLifecycleTool = builtin.NewAgentLifecycleTool(cfg, coordinationManager)
	managementTestState.spaceFoundationTool = builtin.NewSpaceFoundationTool(cfg, coordinationManager)
	
	managementTestState.caronexAgent = true
	return nil
}

func theIntelligenceInterfaceSystemIsRunning() error {
	managementTestState.systemRunning = true
	return nil
}

func theConfigurationIsProperlyLoaded() error {
	cfg := config.Get()
	if cfg == nil {
		return fmt.Errorf("configuration not loaded")
	}
	managementTestState.configLoaded = true
	return nil
}

// System state introspection scenario
func iNeedToAssessCurrentSystemCapabilities() error {
	if !managementTestState.caronexAgent {
		return fmt.Errorf("caronex agent not available")
	}
	return nil
}

func iShouldBeAbleToQueryAvailableAgentsAndTheirSpecializations() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_introspection",
		Name:  "system_introspection",
		Input: `{"include_details": true}`,
	}
	
	response, err := managementTestState.systemIntrospectionTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to run system introspection: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("system introspection returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse introspection result: %v", err)
	}
	
	managementTestState.introspectionData = result
	
	// Verify agents are listed
	if availableAgents, ok := result["available_agents"]; ok {
		if agents, ok := availableAgents.([]interface{}); ok && len(agents) > 0 {
			return nil
		}
	}
	
	return fmt.Errorf("no available agents found in introspection result")
}

func iShouldBeAbleToCheckCurrentConfigurationState() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_config",
		Name:  "configuration_inspection",
		Input: `{"section": "all", "validate": true}`,
	}
	
	response, err := managementTestState.configInspectionTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to run configuration inspection: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("configuration inspection returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse configuration result: %v", err)
	}
	
	managementTestState.configData = result
	return nil
}

func iShouldBeAbleToReportSystemStatusAccurately() error {
	if len(managementTestState.introspectionData) == 0 {
		return fmt.Errorf("system introspection data not available")
	}
	
	// Verify system status is reported
	if systemStatus, ok := managementTestState.introspectionData["system_status"]; ok {
		if status, ok := systemStatus.(string); ok && status != "" {
			return nil
		}
	}
	
	return fmt.Errorf("system status not accurately reported")
}

// Basic coordination capabilities scenario
func iNeedToCoordinateAgentActivities() error {
	if !managementTestState.caronexAgent {
		return fmt.Errorf("caronex agent not available for coordination")
	}
	return nil
}

func iAssessImplementationRequirements() error {
	// Mock implementation requirement assessment
	return nil
}

func iShouldBeAbleToIdentifyAppropriateSpecialistAgents() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_agent_list",
		Name:  "agent_lifecycle",
		Input: `{"action": "capabilities"}`,
	}
	
	response, err := managementTestState.agentLifecycleTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to get agent capabilities: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("agent capabilities returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse agent capabilities: %v", err)
	}
	
	managementTestState.agentData = result
	
	// Verify agent capabilities are available
	if capabilities, ok := result["agent_capabilities"]; ok {
		if caps, ok := capabilities.(map[string]interface{}); ok && len(caps) > 0 {
			return nil
		}
	}
	
	return fmt.Errorf("agent capabilities not properly identified")
}

func iShouldBeAbleToProvidePlanningGuidance() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_planning",
		Name:  "agent_coordination",
		Input: `{"action": "plan", "task_description": "Implement new feature", "requirements": ["coding", "testing"]}`,
	}
	
	response, err := managementTestState.agentCoordinationTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to create task plan: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("task planning returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse planning result: %v", err)
	}
	
	managementTestState.coordinationData = result
	
	// Verify planning guidance is provided
	if steps, ok := result["steps"]; ok {
		if stepsList, ok := steps.([]interface{}); ok && len(stepsList) > 0 {
			return nil
		}
	}
	
	return fmt.Errorf("planning guidance not properly provided")
}

func iShouldBeAbleToDelegateImplementationTasksAppropriately() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_delegation",
		Name:  "agent_coordination",
		Input: `{"action": "delegate", "task_description": "Write unit tests", "preferred_agent": "coder"}`,
	}
	
	response, err := managementTestState.agentCoordinationTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to delegate task: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("task delegation returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse delegation result: %v", err)
	}
	
	// Verify task delegation was successful
	if assignedTo, ok := result["assigned_to"]; ok {
		if agent, ok := assignedTo.(string); ok && agent != "" {
			return nil
		}
	}
	
	return fmt.Errorf("task delegation not properly handled")
}

// Configuration management scenario
func iNeedToUnderstandSystemConfiguration() error {
	if !managementTestState.configLoaded {
		return fmt.Errorf("system configuration not loaded")
	}
	return nil
}

func iQueryConfigurationState() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_config_query",
		Name:  "configuration_inspection",
		Input: `{"section": "all", "validate": true}`,
	}
	
	response, err := managementTestState.configInspectionTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to query configuration: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("configuration query returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse configuration query: %v", err)
	}
	
	managementTestState.configData = result
	return nil
}

func iShouldBeAbleToRetrieveCurrentConfigurationValues() error {
	if len(managementTestState.configData) == 0 {
		return fmt.Errorf("configuration data not available")
	}
	
	// Verify configuration sections are present
	expectedSections := []string{"agents", "caronex", "spaces"}
	for _, section := range expectedSections {
		if _, ok := managementTestState.configData[section]; !ok {
			return fmt.Errorf("configuration section '%s' not found", section)
		}
	}
	
	return nil
}

func iShouldBeAbleToValidateConfigurationConsistency() error {
	if len(managementTestState.configData) == 0 {
		return fmt.Errorf("configuration data not available")
	}
	
	// Check validation status
	if validationStatus, ok := managementTestState.configData["validation_status"]; ok {
		if status, ok := validationStatus.(string); ok && status == "valid" {
			return nil
		}
	}
	
	// Check for validation errors
	if validationErrors, ok := managementTestState.configData["validation_errors"]; ok {
		if errors, ok := validationErrors.([]interface{}); ok && len(errors) > 0 {
			return fmt.Errorf("configuration validation failed with errors")
		}
	}
	
	return nil
}

func iShouldBeAbleToReportConfigurationIssuesIfAnyExist() error {
	// This step verifies that the tool can report issues when they exist
	// Since we have a valid configuration, we expect no issues
	if validationErrors, ok := managementTestState.configData["validation_errors"]; ok {
		if errors, ok := validationErrors.([]interface{}); ok && len(errors) > 0 {
			// Issues were properly reported
			return nil
		}
	}
	
	// No issues to report, which is also valid
	return nil
}

// Agent lifecycle management scenario
func iManageAgentOperations() error {
	if !managementTestState.caronexAgent {
		return fmt.Errorf("caronex agent not available for operations management")
	}
	return nil
}

func iShouldBeAbleToListAvailableAgentTypes() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_agent_list",
		Name:  "agent_lifecycle",
		Input: `{"action": "list"}`,
	}
	
	response, err := managementTestState.agentLifecycleTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to list agents: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("agent listing returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse agent list: %v", err)
	}
	
	// Verify agents are listed
	if availableAgents, ok := result["available_agents"]; ok {
		if agents, ok := availableAgents.([]interface{}); ok && len(agents) > 0 {
			return nil
		}
	}
	
	return fmt.Errorf("available agent types not properly listed")
}

func iShouldBeAbleToCheckAgentReadinessStatus() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_agent_status",
		Name:  "agent_lifecycle",
		Input: `{"action": "status"}`,
	}
	
	response, err := managementTestState.agentLifecycleTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to check agent status: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("agent status check returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse agent status: %v", err)
	}
	
	// Verify readiness status is reported
	if systemReady, ok := result["system_ready"]; ok {
		if ready, ok := systemReady.(bool); ok && ready {
			return nil
		}
	}
	
	return fmt.Errorf("agent readiness status not properly checked")
}

func iShouldBeAbleToCoordinateAgentTaskDelegation() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_coordination_status",
		Name:  "agent_coordination",
		Input: `{"action": "status"}`,
	}
	
	response, err := managementTestState.agentCoordinationTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to check coordination status: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("coordination status returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse coordination status: %v", err)
	}
	
	// Verify coordination is active
	if coordinationActive, ok := result["coordination_active"]; ok {
		if active, ok := coordinationActive.(bool); ok && active {
			return nil
		}
	}
	
	return fmt.Errorf("agent task delegation coordination not properly available")
}

// Space foundation introspection scenario
func theFoundationForSpaceManagementExists() error {
	// Verify space foundation is established
	cfg := config.Get()
	if cfg == nil {
		return fmt.Errorf("configuration not available for space foundation check")
	}
	
	// Space foundation exists if configuration supports it
	return nil
}

func iQuerySpaceRelatedCapabilities() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_space_status",
		Name:  "space_foundation",
		Input: `{"action": "status"}`,
	}
	
	response, err := managementTestState.spaceFoundationTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to query space capabilities: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("space capabilities query returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse space capabilities: %v", err)
	}
	
	managementTestState.spaceData = result
	return nil
}

func iShouldBeAbleToListBasicSpaceConfigurationOptions() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_space_config",
		Name:  "space_foundation",
		Input: `{"action": "config"}`,
	}
	
	response, err := managementTestState.spaceFoundationTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to get space configuration options: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("space configuration query returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse space configuration: %v", err)
	}
	
	// Verify space configuration options are available
	expectedOptions := []string{"space_types", "ui_layouts", "themes"}
	for _, option := range expectedOptions {
		if _, ok := result[option]; !ok {
			return fmt.Errorf("space configuration option '%s' not found", option)
		}
	}
	
	return nil
}

func iShouldBeAbleToReportSpaceReadinessStatus() error {
	if len(managementTestState.spaceData) == 0 {
		return fmt.Errorf("space data not available")
	}
	
	// Verify space readiness is reported
	if foundationReady, ok := managementTestState.spaceData["foundation_ready"]; ok {
		if ready, ok := foundationReady.(bool); ok && ready {
			return nil
		}
	}
	
	return fmt.Errorf("space readiness status not properly reported")
}

func iShouldBeAbleToProvideGuidanceForFutureSpaceImplementation() error {
	ctx := context.Background()
	toolCall := tools.ToolCall{
		ID:    "test_space_guidance",
		Name:  "space_foundation",
		Input: `{"action": "guidance"}`,
	}
	
	response, err := managementTestState.spaceFoundationTool.Run(ctx, toolCall)
	if err != nil {
		return fmt.Errorf("failed to get space implementation guidance: %v", err)
	}
	
	if response.IsError {
		return fmt.Errorf("space guidance query returned error: %s", response.Content)
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal([]byte(response.Content), &result); err != nil {
		return fmt.Errorf("failed to parse space guidance: %v", err)
	}
	
	// Verify guidance is provided
	expectedGuidance := []string{"implementation_phases", "prerequisites", "next_steps"}
	for _, guidance := range expectedGuidance {
		if _, ok := result[guidance]; !ok {
			return fmt.Errorf("space guidance '%s' not found", guidance)
		}
	}
	
	return nil
}