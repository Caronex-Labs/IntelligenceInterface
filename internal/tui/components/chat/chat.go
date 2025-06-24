package chat

import (
	"fmt"
	"sort"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/x/ansi"
	"github.com/caronex/intelligence-interface/internal/core/config"
	"github.com/caronex/intelligence-interface/internal/message"
	"github.com/caronex/intelligence-interface/internal/session"
	"github.com/caronex/intelligence-interface/internal/tui/styles"
	"github.com/caronex/intelligence-interface/internal/tui/theme"
	"github.com/caronex/intelligence-interface/internal/version"
)

type SendMsg struct {
	Text        string
	Attachments []message.Attachment
}

type SessionSelectedMsg = session.Session

type SessionClearedMsg struct{}

type EditorFocusMsg bool

// AgentModeInfo contains information about the current agent mode
type AgentModeInfo struct {
	Mode          string
	IsManagerMode bool
}

func header(width int) string {
	return headerWithMode(width, AgentModeInfo{Mode: "Coder", IsManagerMode: false})
}

// headerWithMode creates a header with agent mode awareness
func headerWithMode(width int, modeInfo AgentModeInfo) string {
	t := theme.CurrentTheme()
	baseStyle := styles.BaseStyle()
	
	// Create mode indicator
	var modeIndicator string
	if modeInfo.IsManagerMode {
		modeStyle := baseStyle.
			Background(t.CaronexPrimary()).
			Foreground(t.Background()).
			Bold(true).
			Padding(0, 2)
		modeIndicator = modeStyle.Render("⚡ CARONEX COORDINATION MODE")
	}
	
	components := []string{
		logo(width),
		repo(width),
	}
	
	if modeIndicator != "" {
		components = append(components, "", modeIndicator)
	}
	
	components = append(components, "", cwd(width))
	
	return lipgloss.JoinVertical(
		lipgloss.Top,
		components...,
	)
}

func lspsConfigured(width int) string {
	cfg := config.Get()
	title := "LSP Configuration"
	title = ansi.Truncate(title, width, "…")

	t := theme.CurrentTheme()
	baseStyle := styles.BaseStyle()

	lsps := baseStyle.
		Width(width).
		Foreground(t.Primary()).
		Bold(true).
		Render(title)

	// Get LSP names and sort them for consistent ordering
	var lspNames []string
	for name := range cfg.LSP {
		lspNames = append(lspNames, name)
	}
	sort.Strings(lspNames)

	var lspViews []string
	for _, name := range lspNames {
		lsp := cfg.LSP[name]
		lspName := baseStyle.
			Foreground(t.Text()).
			Render(fmt.Sprintf("• %s", name))

		cmd := lsp.Command
		cmd = ansi.Truncate(cmd, width-lipgloss.Width(lspName)-3, "…")

		lspPath := baseStyle.
			Foreground(t.TextMuted()).
			Render(fmt.Sprintf(" (%s)", cmd))

		lspViews = append(lspViews,
			baseStyle.
				Width(width).
				Render(
					lipgloss.JoinHorizontal(
						lipgloss.Left,
						lspName,
						lspPath,
					),
				),
		)
	}

	return baseStyle.
		Width(width).
		Render(
			lipgloss.JoinVertical(
				lipgloss.Left,
				lsps,
				lipgloss.JoinVertical(
					lipgloss.Left,
					lspViews...,
				),
			),
		)
}

func logo(width int) string {
	logo := fmt.Sprintf("%s %s", styles.IntelligenceInterfaceIcon, "Intelligence Interface")
	t := theme.CurrentTheme()
	baseStyle := styles.BaseStyle()

	versionText := baseStyle.
		Foreground(t.TextMuted()).
		Render(version.Version)

	return baseStyle.
		Bold(true).
		Width(width).
		Render(
			lipgloss.JoinHorizontal(
				lipgloss.Left,
				logo,
				" ",
				versionText,
			),
		)
}

func repo(width int) string {
	repo := "https://github.com/caronex/intelligence-interface"
	t := theme.CurrentTheme()

	return styles.BaseStyle().
		Foreground(t.TextMuted()).
		Width(width).
		Render(repo)
}

func cwd(width int) string {
	cwd := fmt.Sprintf("cwd: %s", config.WorkingDirectory())
	t := theme.CurrentTheme()

	return styles.BaseStyle().
		Foreground(t.TextMuted()).
		Width(width).
		Render(cwd)
}

