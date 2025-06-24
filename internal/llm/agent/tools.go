package agent

import (
	"context"

	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/history"
	"github.com/caronex/intelligence-interface/internal/llm/tools"
	"github.com/caronex/intelligence-interface/internal/lsp"
	"github.com/caronex/intelligence-interface/internal/message"
	"github.com/caronex/intelligence-interface/internal/permission"
	"github.com/caronex/intelligence-interface/internal/session"
	"github.com/caronex/intelligence-interface/internal/tools/builtin"
	"github.com/caronex/intelligence-interface/internal/tools/coordination"
)

// CaronexAgentTools returns full tools for Caronex agent
func CaronexAgentTools(
	permissions permission.Service,
	sessions session.Service,
	messages message.Service,
	history history.Service,
	lspClients map[string]*lsp.Client,
) []tools.BaseTool {
	ctx := context.Background()
	otherTools := GetMcpTools(ctx, permissions)
	if len(lspClients) > 0 {
		otherTools = append(otherTools, tools.NewDiagnosticsTool(lspClients))
	}
	return append(
		[]tools.BaseTool{
			tools.NewBashTool(permissions),
			tools.NewEditTool(lspClients, permissions, history),
			tools.NewFetchTool(permissions),
			tools.NewGlobTool(),
			tools.NewGrepTool(),
			tools.NewLsTool(),
			tools.NewSourcegraphTool(),
			tools.NewViewTool(lspClients),
			tools.NewPatchTool(lspClients, permissions, history),
			tools.NewWriteTool(lspClients, permissions, history),
			NewAgentTool(sessions, messages, lspClients),
		}, otherTools...,
	)
}

// ManagerAgentTools returns specialized tools for Caronex manager agent
// Manager agent focuses on coordination and delegation, not direct implementation
func ManagerAgentTools() []tools.BaseTool {
	cfg := config.Get()
	if cfg == nil {
		cfg = &config.Config{} // Fallback configuration
	}
	
	// Initialize coordination manager for management tools
	coordinationManager, _ := coordination.NewManager(cfg)
	
	// Create management tools specific to Caronex
	managementTools := []tools.BaseTool{
		builtin.NewSystemIntrospectionTool(cfg, coordinationManager),
		builtin.NewAgentCoordinationTool(cfg, coordinationManager),
		builtin.NewConfigurationInspectionTool(cfg, coordinationManager),
		builtin.NewAgentLifecycleTool(cfg, coordinationManager),
		builtin.NewSpaceFoundationTool(cfg, coordinationManager),
	}

	// Add basic tools for system introspection
	basicTools := []tools.BaseTool{
		tools.NewGlobTool(),    // For system introspection
		tools.NewGrepTool(),    // For system analysis
		tools.NewLsTool(),      // For system state viewing
		tools.NewViewTool(nil), // For reading system files (no LSP needed)
	}

	return append(managementTools, basicTools...)
}
