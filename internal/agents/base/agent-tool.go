package base

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/caronex/intelligence-interface/internal/llm/tools"
	"github.com/caronex/intelligence-interface/internal/lsp"
	"github.com/caronex/intelligence-interface/internal/message"
	"github.com/caronex/intelligence-interface/internal/session"
)

type agentTool struct {
	sessions   session.Service
	messages   message.Service
	lspClients map[string]*lsp.Client
}

const (
	AgentToolName = "agent"
)

type AgentParams struct {
	Prompt string `json:"prompt"`
}

func (b *agentTool) Info() tools.ToolInfo {
	return tools.ToolInfo{
		Name:        AgentToolName,
		Description: "Launch a new Caronex sub-agent for specialized tasks. This tool is temporarily disabled pending Caronex coordination implementation.",
		Parameters: map[string]any{
			"prompt": map[string]any{
				"type":        "string",
				"description": "The task for the agent to perform",
			},
		},
		Required: []string{"prompt"},
	}
}

func (b *agentTool) Run(ctx context.Context, call tools.ToolCall) (tools.ToolResponse, error) {
	var params AgentParams
	if err := json.Unmarshal([]byte(call.Input), &params); err != nil {
		return tools.NewTextErrorResponse(fmt.Sprintf("error parsing parameters: %s", err)), nil
	}
	if params.Prompt == "" {
		return tools.NewTextErrorResponse("prompt is required"), nil
	}

	sessionID, messageID := tools.GetContextValues(ctx)
	if sessionID == "" || messageID == "" {
		return tools.ToolResponse{}, fmt.Errorf("session_id and message_id are required")
	}

	// TODO: For now, sub-agents are disabled until Caronex agent coordination is implemented
	return tools.ToolResponse{}, fmt.Errorf("sub-agent spawning is temporarily disabled pending Caronex coordination implementation")

	/* Disabled pending Caronex coordination implementation
	session, err := b.sessions.CreateTaskSession(ctx, call.ID, sessionID, "New Agent Session")
	if err != nil {
		return tools.ToolResponse{}, fmt.Errorf("error creating session: %s", err)
	}

	done, err := agent.Run(ctx, session.ID, params.Prompt)
	if err != nil {
		return tools.ToolResponse{}, fmt.Errorf("error generating agent: %s", err)
	}
	result := <-done
	if result.Error != nil {
		return tools.ToolResponse{}, fmt.Errorf("error generating agent: %s", result.Error)
	}

	response := result.Message
	if response.Role != message.Assistant {
		return tools.NewTextErrorResponse("no response"), nil
	}

	updatedSession, err := b.sessions.Get(ctx, session.ID)
	if err != nil {
		return tools.ToolResponse{}, fmt.Errorf("error getting session: %s", err)
	}
	parentSession, err := b.sessions.Get(ctx, sessionID)
	if err != nil {
		return tools.ToolResponse{}, fmt.Errorf("error getting parent session: %s", err)
	}

	parentSession.Cost += updatedSession.Cost

	_, err = b.sessions.Save(ctx, parentSession)
	if err != nil {
		return tools.ToolResponse{}, fmt.Errorf("error saving parent session: %s", err)
	}
	return tools.NewTextResponse(response.Content().String()), nil
	*/
}

func NewAgentTool(
	Sessions session.Service,
	Messages message.Service,
	LspClients map[string]*lsp.Client,
) tools.BaseTool {
	return &agentTool{
		sessions:   Sessions,
		messages:   Messages,
		lspClients: LspClients,
	}
}
