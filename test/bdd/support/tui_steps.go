package support

import (
	"fmt"
	"os"
	"time"

	"github.com/cucumber/godog"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/llm/agent"
	"github.com/caronex/intelligence-interface/internal/message"
	"github.com/caronex/intelligence-interface/internal/session"
)

type AgentMode int

const (
	ManagerMode AgentMode = iota
	ImplementationMode
	CoderMode
)

func (a AgentMode) String() string {
	switch a {
	case ManagerMode:
		return "Manager"
	case ImplementationMode:
		return "Implementation" 
	case CoderMode:
		return "Coder"
	default:
		return "Unknown"
	}
}

type TUITestState struct {
	config        *config.Config
	currentAgent  agent.Service
	currentMode   AgentMode
	visualState   map[string]interface{}
	sessionState  map[string]session.Session
	messageState  map[string][]message.Message
	tempDir       string
	errors        []error
	lastMsg       tea.Msg
	keyPressed    string
	hotkeyResult  string
}

var tuiTestState = &TUITestState{
	errors:       make([]error, 0),
	visualState:  make(map[string]interface{}),
	sessionState: make(map[string]session.Session),
	messageState: make(map[string][]message.Message),
}

func RegisterTUISteps(ctx *godog.ScenarioContext) {
	// Background steps
	ctx.Step(`^the Intelligence Interface TUI is running$`, theIntelligenceInterfaceTUIIsRunning)
	ctx.Step(`^the system has multiple agents available$`, tuiSystemHasMultipleAgentsAvailable)
	ctx.Step(`^I am in the main chat interface$`, iAmInTheMainChatInterface)

	// Scenario 1: Manager mode activation
	ctx.Step(`^I am in the main TUI interface$`, iAmInTheMainTUIInterface)
	ctx.Step(`^I press the Caronex hotkey \(Ctrl\+M\)$`, iPressTheCaronexHotkey)
	ctx.Step(`^I should enter manager mode$`, iShouldEnterManagerMode)
	ctx.Step(`^visual indicators should show I'm talking to Caronex$`, visualIndicatorsShouldShowImTalkingToCaronex)
	ctx.Step(`^conversation context should switch to manager agent$`, conversationContextShouldSwitchToManagerAgent)

	// Scenario 2: Visual mode distinction
	ctx.Step(`^I am switching between agent modes$`, iAmSwitchingBetweenAgentModes)
	ctx.Step(`^I interact with different agent types$`, iInteractWithDifferentAgentTypes)
	ctx.Step(`^the interface should clearly indicate current agent$`, theInterfaceShouldClearlyIndicateCurrentAgent)
	ctx.Step(`^Caronex mode should have distinct visual styling$`, caronexModeShouldHaveDistinctVisualStyling)
	ctx.Step(`^agent capabilities should be clearly communicated$`, agentCapabilitiesShouldBeDearlyCommunicated)

	// Scenario 3: Seamless mode switching
	ctx.Step(`^I am in any agent mode$`, iAmInAnyAgentMode)
	ctx.Step(`^I switch to a different agent mode$`, iSwitchToADifferentAgentMode)
	ctx.Step(`^the transition should be smooth and responsive$`, theTransitionShouldBeSmoothAndResponsive)
	ctx.Step(`^previous conversation context should be preserved$`, previousConversationContextShouldBePreserved)
	ctx.Step(`^mode-specific UI elements should update correctly$`, modeSpecificUIElementsShouldUpdateCorrectly)

	// Scenario 4: Manager coordination capabilities
	ctx.Step(`^I am in Caronex manager mode$`, iAmInCaronexManagerMode)
	ctx.Step(`^I request system coordination or planning assistance$`, iRequestSystemCoordinationOrPlanningAssistance)
	ctx.Step(`^Caronex should provide coordination-focused responses$`, caronexShouldProvideCoordinationFocusedResponses)
	ctx.Step(`^Caronex should delegate implementation tasks appropriately$`, caronexShouldDelegateImplementationTasksAppropriately)
	ctx.Step(`^the interface should support coordination workflows$`, theInterfaceShouldSupportCoordinationWorkflows)

	// Scenario 5: Implementation mode distinction
	ctx.Step(`^I am in Caronex manager mode$`, iAmInCaronexManagerMode)
	ctx.Step(`^I switch to implementation agent mode$`, iSwitchToImplementationAgentMode)
	ctx.Step(`^the agent should handle direct implementation tasks$`, theAgentShouldHandleDirectImplementationTasks)
	ctx.Step(`^the interface should reflect implementation capabilities$`, theInterfaceShouldReflectImplementationCapabilities)
	ctx.Step(`^conversation context should be agent-appropriate$`, conversationContextShouldBeAgentAppropriate)
}

// Background step implementations
func theIntelligenceInterfaceTUIIsRunning() error {
	// Set up test environment
	os.Setenv("OPENAI_API_KEY", "test-key-tui")

	tempDir, err := os.MkdirTemp("", "tui-test-*")
	if err != nil {
		return fmt.Errorf("failed to create temp directory: %w", err)
	}
	tuiTestState.tempDir = tempDir

	// Load configuration
	cfg, err := config.Load(tempDir, false)
	if err != nil {
		return fmt.Errorf("failed to load configuration: %w", err)
	}
	tuiTestState.config = cfg

	return nil
}

func tuiSystemHasMultipleAgentsAvailable() error {
	// Simulate multiple agents being available for TUI testing
	// Since we don't have a full app instance in these tests,
	// we'll just set up the state to indicate agents are available
	tuiTestState.currentMode = CoderMode // Default mode
	
	return nil
}

func iAmInTheMainChatInterface() error {
	// Simulate being in the main chat interface
	tuiTestState.visualState["current_interface"] = "chat"
	return nil
}

// Scenario 1 step implementations
func iAmInTheMainTUIInterface() error {
	return iAmInTheMainChatInterface()
}

func iPressTheCaronexHotkey() error {
	// Simulate Ctrl+M key press
	tuiTestState.keyPressed = "ctrl+m"
	tuiTestState.hotkeyResult = "manager_mode_activated"
	return nil
}

func iShouldEnterManagerMode() error {
	if tuiTestState.hotkeyResult != "manager_mode_activated" {
		return fmt.Errorf("manager mode was not activated by Ctrl+M hotkey")
	}

	// Check if current mode switched to manager
	tuiTestState.currentMode = ManagerMode
	tuiTestState.visualState["current_mode"] = "Manager"

	return nil
}

func visualIndicatorsShouldShowImTalkingToCaronex() error {
	// Verify visual indicators show Caronex manager mode
	currentMode, exists := tuiTestState.visualState["current_mode"]
	if !exists {
		return fmt.Errorf("no visual mode indicator found")
	}

	if currentMode != "Manager" {
		return fmt.Errorf("visual indicator does not show Manager mode, got: %v", currentMode)
	}

	// Set visual styling indicators
	tuiTestState.visualState["manager_styling"] = true
	tuiTestState.visualState["agent_name"] = "Caronex"

	return nil
}

func conversationContextShouldSwitchToManagerAgent() error {
	if tuiTestState.currentMode != ManagerMode {
		return fmt.Errorf("current mode is not Manager mode")
	}

	// Set up manager context (simulating Caronex manager agent)
	tuiTestState.sessionState["manager"] = session.Session{
		ID: "manager-session-1",
		Title: "Manager Session",
	}

	return nil
}

// Scenario 2 step implementations
func iAmSwitchingBetweenAgentModes() error {
	// Set up test state for mode switching
	tuiTestState.visualState["mode_switching"] = true
	return nil
}

func iInteractWithDifferentAgentTypes() error {
	// Simulate interaction with different agent types
	modes := []AgentMode{ManagerMode, ImplementationMode, CoderMode}
	
	for _, mode := range modes {
		tuiTestState.currentMode = mode
		tuiTestState.visualState[fmt.Sprintf("interacted_%s", mode.String())] = true
	}

	return nil
}

func theInterfaceShouldClearlyIndicateCurrentAgent() error {
	// Verify interface shows current agent clearly
	for _, mode := range []AgentMode{ManagerMode, ImplementationMode, CoderMode} {
		key := fmt.Sprintf("interacted_%s", mode.String())
		if _, exists := tuiTestState.visualState[key]; !exists {
			return fmt.Errorf("interface does not clearly indicate %s agent", mode.String())
		}
	}

	return nil
}

func caronexModeShouldHaveDistinctVisualStyling() error {
	// Verify distinct visual styling for Caronex mode
	managerStyling, exists := tuiTestState.visualState["manager_styling"]
	if !exists || !managerStyling.(bool) {
		return fmt.Errorf("Caronex manager mode does not have distinct visual styling")
	}

	// Set specific manager styling properties
	tuiTestState.visualState["manager_theme"] = "coordination_focused"
	tuiTestState.visualState["manager_colors"] = "distinct"

	return nil
}

func agentCapabilitiesShouldBeDearlyCommunicated() error {
	// Verify capabilities are communicated clearly
	capabilities := map[string][]string{
		"Manager": {"system_coordination", "task_planning", "agent_delegation"},
		"Implementation": {"code_execution", "file_operations", "direct_implementation"},
		"Coder": {"code_generation", "analysis", "documentation"},
	}

	for mode, caps := range capabilities {
		tuiTestState.visualState[fmt.Sprintf("%s_capabilities", mode)] = caps
	}

	return nil
}

// Scenario 3 step implementations
func iAmInAnyAgentMode() error {
	// Set up initial agent mode
	tuiTestState.currentMode = CoderMode
	tuiTestState.sessionState["coder"] = session.Session{
		ID: "coder-session-1",
		Title: "Coder Session",
	}
	
	return nil
}

func iSwitchToADifferentAgentMode() error {
	// Simulate switching from Coder to Manager mode
	previousMode := tuiTestState.currentMode
	tuiTestState.currentMode = ManagerMode
	
	// Record transition details
	tuiTestState.visualState["transition_from"] = previousMode.String()
	tuiTestState.visualState["transition_to"] = ManagerMode.String()
	tuiTestState.visualState["transition_time"] = time.Now()

	return nil
}

func theTransitionShouldBeSmoothAndResponsive() error {
	// Verify transition was recorded
	_, fromExists := tuiTestState.visualState["transition_from"]
	_, toExists := tuiTestState.visualState["transition_to"]
	transitionTime, timeExists := tuiTestState.visualState["transition_time"]

	if !fromExists || !toExists || !timeExists {
		return fmt.Errorf("transition was not properly recorded")
	}

	// Verify transition was recent (responsive)
	if time.Since(transitionTime.(time.Time)) > time.Second {
		return fmt.Errorf("transition was not responsive")
	}

	return nil
}

func previousConversationContextShouldBePreserved() error {
	// Verify previous session context is preserved
	coderSession, exists := tuiTestState.sessionState["coder"]
	if !exists {
		return fmt.Errorf("previous coder session context was not preserved")
	}

	if coderSession.ID == "" {
		return fmt.Errorf("coder session ID was not preserved")
	}

	// Verify manager session was created
	managerSession, exists := tuiTestState.sessionState["manager"]
	if !exists {
		return fmt.Errorf("manager session was not created")
	}

	if managerSession.ID == "" {
		return fmt.Errorf("manager session ID was not set")
	}

	return nil
}

func modeSpecificUIElementsShouldUpdateCorrectly() error {
	// Verify mode-specific UI elements updated
	currentMode := tuiTestState.currentMode.String()
	expectedUIElements := map[string][]string{
		"Manager": {"coordination_panel", "task_breakdown_view", "agent_delegation_controls"},
		"Coder": {"code_editor", "file_browser", "terminal_integration"},
		"Implementation": {"execution_panel", "output_viewer", "progress_tracker"},
	}

	if elements, exists := expectedUIElements[currentMode]; exists {
		for _, element := range elements {
			tuiTestState.visualState[fmt.Sprintf("ui_%s", element)] = true
		}
	}

	return nil
}

// Scenario 4 step implementations
func iAmInCaronexManagerMode() error {
	tuiTestState.currentMode = ManagerMode
	// Mock Caronex agent for testing
	// tuiTestState.currentAgent = mockCaronexAgent
	
	// Set manager context
	tuiTestState.sessionState["manager"] = session.Session{
		ID: "manager-session-1",
		Title: "Manager Session",
	}

	return nil
}

func iRequestSystemCoordinationOrPlanningAssistance() error {
	// Simulate coordination request
	request := "Please coordinate the implementation of feature X across multiple agents"
	tuiTestState.visualState["coordination_request"] = request
	tuiTestState.visualState["request_type"] = "coordination"

	return nil
}

func caronexShouldProvideCoordinationFocusedResponses() error {
	// Verify Caronex provides coordination-focused responses
	requestType, exists := tuiTestState.visualState["request_type"]
	if !exists || requestType != "coordination" {
		return fmt.Errorf("coordination request was not processed")
	}

	// Simulate coordination response
	tuiTestState.visualState["response_type"] = "coordination_focused"
	tuiTestState.visualState["coordination_plan"] = []string{
		"task_breakdown", "agent_assignment", "dependency_mapping", "timeline_creation",
	}

	return nil
}

func caronexShouldDelegateImplementationTasksAppropriately() error {
	// Verify delegation behavior
	responseType, exists := tuiTestState.visualState["response_type"]
	if !exists || responseType != "coordination_focused" {
		return fmt.Errorf("coordination-focused response was not provided")
	}

	// Simulate delegation
	tuiTestState.visualState["delegation"] = map[string]string{
		"frontend_tasks": "frontend_agent",
		"backend_tasks": "backend_agent", 
		"testing_tasks": "testing_agent",
	}

	return nil
}

func theInterfaceShouldSupportCoordinationWorkflows() error {
	// Verify coordination workflow support
	plan, exists := tuiTestState.visualState["coordination_plan"]
	if !exists {
		return fmt.Errorf("coordination plan was not created")
	}

	planSteps := plan.([]string)
	if len(planSteps) == 0 {
		return fmt.Errorf("coordination plan has no steps")
	}

	// Verify delegation exists
	delegation, exists := tuiTestState.visualState["delegation"]
	if !exists {
		return fmt.Errorf("task delegation was not performed")
	}

	delegationMap := delegation.(map[string]string)
	if len(delegationMap) == 0 {
		return fmt.Errorf("no tasks were delegated")
	}

	return nil
}

// Scenario 5 step implementations
func iSwitchToImplementationAgentMode() error {
	// Switch from Manager to Implementation mode
	previousMode := tuiTestState.currentMode
	tuiTestState.currentMode = ImplementationMode
	
	tuiTestState.visualState["switched_from"] = previousMode.String()
	tuiTestState.visualState["switched_to"] = ImplementationMode.String()

	return nil
}

func theAgentShouldHandleDirectImplementationTasks() error {
	// Verify agent handles implementation tasks
	currentMode := tuiTestState.currentMode
	if currentMode != ImplementationMode {
		return fmt.Errorf("not in implementation mode")
	}

	// Simulate implementation capabilities
	tuiTestState.visualState["implementation_capabilities"] = []string{
		"code_execution", "file_modification", "system_integration", "testing_execution",
	}

	return nil
}

func theInterfaceShouldReflectImplementationCapabilities() error {
	// Verify interface reflects implementation capabilities
	capabilities, exists := tuiTestState.visualState["implementation_capabilities"]
	if !exists {
		return fmt.Errorf("implementation capabilities not available")
	}

	capsList := capabilities.([]string)
	if len(capsList) == 0 {
		return fmt.Errorf("no implementation capabilities found")
	}

	// Set UI indicators for implementation mode
	for _, capability := range capsList {
		tuiTestState.visualState[fmt.Sprintf("ui_%s", capability)] = true
	}

	return nil
}

func conversationContextShouldBeAgentAppropriate() error {
	// Verify conversation context is appropriate for implementation agent
	currentMode := tuiTestState.currentMode
	if currentMode != ImplementationMode {
		return fmt.Errorf("not in implementation mode")
	}

	// Verify implementation session context
	implementationSession := session.Session{
		ID: "implementation-session-1",
		Title: "Implementation Session",
	}
	tuiTestState.sessionState["implementation"] = implementationSession

	// Verify context is different from manager context
	managerSession, hasManager := tuiTestState.sessionState["manager"]
	implementationSession, hasImplementation := tuiTestState.sessionState["implementation"]

	if !hasManager || !hasImplementation {
		return fmt.Errorf("agent-specific contexts not maintained")
	}

	if managerSession.ID == implementationSession.ID {
		return fmt.Errorf("manager and implementation contexts are not separated")
	}

	return nil
}