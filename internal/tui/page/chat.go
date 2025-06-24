package page

import (
	"context"
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/key"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/caronex/intelligence-interface/internal/app"
	"github.com/caronex/intelligence-interface/internal/completions"
	"github.com/caronex/intelligence-interface/internal/llm/agent"
	"github.com/caronex/intelligence-interface/internal/message"
	"github.com/caronex/intelligence-interface/internal/session"
	"github.com/caronex/intelligence-interface/internal/tui/components/chat"
	"github.com/caronex/intelligence-interface/internal/tui/components/dialog"
	"github.com/caronex/intelligence-interface/internal/tui/layout"
	"github.com/caronex/intelligence-interface/internal/tui/util"
)

var ChatPage PageID = "chat"

// AgentMode represents different agent operational modes
type AgentMode interface {
	String() string
	IsManagerMode() bool
}

// ManagerMode represents coordination/management agent mode
type ManagerMode struct{}

func (m ManagerMode) String() string { return "Manager" }
func (m ManagerMode) IsManagerMode() bool { return true }

// ImplementationMode represents direct implementation agent mode  
type ImplementationMode struct{}

func (i ImplementationMode) String() string { return "Implementation" }
func (i ImplementationMode) IsManagerMode() bool { return false }

// CoderMode represents traditional coder agent mode
type CoderMode struct{}

func (c CoderMode) String() string { return "Coder" }
func (c CoderMode) IsManagerMode() bool { return false }

// AgentSwitchedMsg is sent when the current agent mode changes
type AgentSwitchedMsg struct {
	AgentMode AgentMode
	Agent     agent.Service
}

type chatPage struct {
	app                  *app.App
	editor               layout.Container
	messages             layout.Container
	layout               layout.SplitPaneLayout
	session              session.Session
	completionDialog     dialog.CompletionDialog
	showCompletionDialog bool
	currentAgent         agent.Service // Current agent service based on mode
	
	// Per-agent session and context management
	agentSessions        map[string]session.Session // AgentMode.String() -> Session
	conversationContexts map[string][]message.Message // AgentMode.String() -> Context messages
	currentAgentMode     AgentMode // Current agent mode for context management
}

type ChatKeyMap struct {
	ShowCompletionDialog key.Binding
	NewSession           key.Binding
	Cancel               key.Binding
	CaronexManager       key.Binding
}

var keyMap = ChatKeyMap{
	ShowCompletionDialog: key.NewBinding(
		key.WithKeys("@"),
		key.WithHelp("@", "Complete"),
	),
	NewSession: key.NewBinding(
		key.WithKeys("ctrl+n"),
		key.WithHelp("ctrl+n", "new session"),
	),
	Cancel: key.NewBinding(
		key.WithKeys("esc"),
		key.WithHelp("esc", "cancel"),
	),
	CaronexManager: key.NewBinding(
		key.WithKeys("ctrl+m"),
		key.WithHelp("ctrl+m", "manager mode"),
	),
}

func (p *chatPage) Init() tea.Cmd {
	cmds := []tea.Cmd{
		p.layout.Init(),
		p.completionDialog.Init(),
	}
	return tea.Batch(cmds...)
}

func (p *chatPage) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		cmd := p.layout.SetSize(msg.Width, msg.Height)
		cmds = append(cmds, cmd)
	case dialog.CompletionDialogCloseMsg:
		p.showCompletionDialog = false
	case chat.SendMsg:
		cmd := p.sendMessage(msg.Text, msg.Attachments)
		if cmd != nil {
			return p, cmd
		}
	case AgentSwitchedMsg:
		// Save current context before switching
		if p.session.ID != "" && p.currentAgentMode != nil {
			p.saveAgentContext(p.currentAgentMode.String(), p.session)
		}
		
		// Update current agent and mode
		p.currentAgent = msg.Agent
		p.currentAgentMode = msg.AgentMode
		
		// Switch to appropriate session for this agent
		cmd := p.switchToAgentSession(p.currentAgentMode.String())
		if cmd != nil {
			return p, cmd
		}
		
		// Update messages component with new agent mode
		modeInfo := chat.AgentModeInfo{
			Mode:          p.currentAgentMode.String(),
			IsManagerMode: p.currentAgentMode.IsManagerMode(),
		}
		
		// Show mode switch confirmation and update both messages and layout components
		modeMsg := fmt.Sprintf("Switched to %s mode", p.currentAgentMode.String())
		agentSwitchMsg := chat.AgentSwitchedMsg{AgentMode: modeInfo}
		
		// Forward agent mode change to layout components
		var layoutCmd tea.Cmd
		_, layoutCmd = p.layout.Update(agentSwitchMsg)
		return p, tea.Batch(
			util.ReportInfo(modeMsg),
			layoutCmd,
		)
		
	case dialog.CommandRunCustomMsg:
		// Check if the current agent is busy before executing custom commands
		if p.getCurrentAgent().IsBusy() {
			return p, util.ReportWarn("Agent is busy, please wait before executing a command...")
		}
		
		// Process the command content with arguments if any
		content := msg.Content
		if msg.Args != nil {
			// Replace all named arguments with their values
			for name, value := range msg.Args {
				placeholder := "$" + name
				content = strings.ReplaceAll(content, placeholder, value)
			}
		}
		
		// Handle custom command execution
		cmd := p.sendMessage(content, nil)
		if cmd != nil {
			return p, cmd
		}
	case chat.SessionSelectedMsg:
		if p.session.ID == "" {
			cmd := p.setSidebar()
			if cmd != nil {
				cmds = append(cmds, cmd)
			}
		}
		p.session = msg
	case tea.KeyMsg:
		switch {
		case key.Matches(msg, keyMap.ShowCompletionDialog):
			p.showCompletionDialog = true
			// Continue sending keys to layout->chat
		case key.Matches(msg, keyMap.NewSession):
			p.session = session.Session{}
			return p, tea.Batch(
				p.clearSidebar(),
				util.CmdHandler(chat.SessionClearedMsg{}),
			)
		case key.Matches(msg, keyMap.Cancel):
			if p.session.ID != "" {
				// Cancel the current session's generation process
				// This allows users to interrupt long-running operations
				p.getCurrentAgent().Cancel(p.session.ID)
				return p, nil
			}
		case key.Matches(msg, keyMap.CaronexManager):
			// Handle Ctrl+M within chat page
			agentSwitchMsg := AgentSwitchedMsg{
				AgentMode: ManagerMode{},
				Agent:     p.app.CaronexAgent,
			}
			return p.Update(agentSwitchMsg)
		}
	}
	if p.showCompletionDialog {
		context, contextCmd := p.completionDialog.Update(msg)
		p.completionDialog = context.(dialog.CompletionDialog)
		cmds = append(cmds, contextCmd)

		// Doesn't forward event if enter key is pressed
		if keyMsg, ok := msg.(tea.KeyMsg); ok {
			if keyMsg.String() == "enter" {
				return p, tea.Batch(cmds...)
			}
		}
	}

	u, cmd := p.layout.Update(msg)
	cmds = append(cmds, cmd)
	p.layout = u.(layout.SplitPaneLayout)

	return p, tea.Batch(cmds...)
}

func (p *chatPage) setSidebar() tea.Cmd {
	sidebarContainer := layout.NewContainer(
		chat.NewSidebarCmp(p.session, p.app.History),
		layout.WithPadding(1, 1, 1, 1),
	)
	return tea.Batch(p.layout.SetRightPanel(sidebarContainer), sidebarContainer.Init())
}

func (p *chatPage) clearSidebar() tea.Cmd {
	return p.layout.ClearRightPanel()
}

func (p *chatPage) sendMessage(text string, attachments []message.Attachment) tea.Cmd {
	var cmds []tea.Cmd
	if p.session.ID == "" {
		session, err := p.app.Sessions.Create(context.Background(), "New Session")
		if err != nil {
			return util.ReportError(err)
		}

		p.session = session
		cmd := p.setSidebar()
		if cmd != nil {
			cmds = append(cmds, cmd)
		}
		cmds = append(cmds, util.CmdHandler(chat.SessionSelectedMsg(session)))
	}

	_, err := p.getCurrentAgent().Run(context.Background(), p.session.ID, text, attachments...)
	if err != nil {
		return util.ReportError(err)
	}
	return tea.Batch(cmds...)
}

func (p *chatPage) SetSize(width, height int) tea.Cmd {
	return p.layout.SetSize(width, height)
}

func (p *chatPage) GetSize() (int, int) {
	return p.layout.GetSize()
}

func (p *chatPage) View() string {
	layoutView := p.layout.View()

	if p.showCompletionDialog {
		_, layoutHeight := p.layout.GetSize()
		editorWidth, editorHeight := p.editor.GetSize()

		p.completionDialog.SetWidth(editorWidth)
		overlay := p.completionDialog.View()

		layoutView = layout.PlaceOverlay(
			0,
			layoutHeight-editorHeight-lipgloss.Height(overlay),
			overlay,
			layoutView,
			false,
		)
	}

	return layoutView
}

func (p *chatPage) BindingKeys() []key.Binding {
	bindings := layout.KeyMapToSlice(keyMap)
	bindings = append(bindings, p.messages.BindingKeys()...)
	bindings = append(bindings, p.editor.BindingKeys()...)
	return bindings
}

// getCurrentAgent returns the current agent service or defaults to CaronexAgent
func (p *chatPage) getCurrentAgent() agent.Service {
	if p.currentAgent != nil {
		return p.currentAgent
	}
	// Default to CaronexAgent if no current agent is set
	return p.app.CaronexAgent
}

// max returns the maximum of two integers
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// saveAgentContext saves the current session and messages for an agent mode
func (p *chatPage) saveAgentContext(agentMode string, session session.Session) {
	if session.ID != "" {
		p.agentSessions[agentMode] = session
		
		// Get current messages and save last 10 for context
		messages, err := p.app.Messages.List(context.Background(), session.ID)
		if err == nil && len(messages) > 0 {
			// Keep last 10 messages for context
			startIdx := max(0, len(messages)-10)
			p.conversationContexts[agentMode] = messages[startIdx:]
		}
	}
}

// switchToAgentSession switches to the session for the given agent mode
func (p *chatPage) switchToAgentSession(agentMode string) tea.Cmd {
	var cmds []tea.Cmd
	
	// Check if we have an existing session for this agent
	if savedSession, exists := p.agentSessions[agentMode]; exists {
		// Restore the existing session
		p.session = savedSession
		cmds = append(cmds, util.CmdHandler(chat.SessionSelectedMsg(savedSession)))
		
		// Restore sidebar
		cmd := p.setSidebar()
		if cmd != nil {
			cmds = append(cmds, cmd)
		}
	} else {
		// Create a new session for this agent
		sessionTitle := fmt.Sprintf("%s Session", agentMode)
		newSession, err := p.app.Sessions.Create(context.Background(), sessionTitle)
		if err != nil {
			return util.ReportError(err)
		}
		
		p.session = newSession
		p.agentSessions[agentMode] = newSession
		cmds = append(cmds, util.CmdHandler(chat.SessionSelectedMsg(newSession)))
		
		// Set up sidebar for new session
		cmd := p.setSidebar()
		if cmd != nil {
			cmds = append(cmds, cmd)
		}
		
		// Show context resumed message if we have previous context
		if context, hasContext := p.conversationContexts[agentMode]; hasContext && len(context) > 0 {
			cmds = append(cmds, util.ReportInfo(fmt.Sprintf("Resumed %s conversation context (%d messages)", agentMode, len(context))))
		}
	}
	
	return tea.Batch(cmds...)
}

func NewChatPage(app *app.App) tea.Model {
	cg := completions.NewFileAndFolderContextGroup()
	completionDialog := dialog.NewCompletionDialogCmp(cg)

	messagesContainer := layout.NewContainer(
		chat.NewMessagesCmp(app),
		layout.WithPadding(1, 1, 0, 1),
	)
	editorContainer := layout.NewContainer(
		chat.NewEditorCmp(app),
		layout.WithBorder(true, false, false, false),
	)
	return &chatPage{
		app:                  app,
		editor:               editorContainer,
		messages:             messagesContainer,
		completionDialog:     completionDialog,
		currentAgent:         app.CaronexAgent, // Default to CaronexAgent
		agentSessions:        make(map[string]session.Session),
		conversationContexts: make(map[string][]message.Message),
		currentAgentMode:     CoderMode{}, // Default mode
		layout: layout.NewSplitPane(
			layout.WithLeftPanel(messagesContainer),
			layout.WithBottomPanel(editorContainer),
		),
	}
}
