package internal

import (
	"fmt"
)

// CommandHandler handles CLI command execution
type CommandHandler struct {
	configProcessor   *ConfigProcessor
	templateGenerator *TemplateGenerator
}

// NewCommandHandler creates a new command handler
func NewCommandHandler() *CommandHandler {
	return &CommandHandler{
		configProcessor:   NewConfigProcessor(),
		templateGenerator: NewTemplateGenerator(),
	}
}

// GenerateFromConfig generates files from YAML configuration
func (ch *CommandHandler) GenerateFromConfig(configPath string) error {
	// Load configuration
	config, err := ch.configProcessor.LoadConfig(configPath)
	if err != nil {
		return err
	}

	// Create template data
	data := ch.configProcessor.CreateTemplateData(*config)

	// Generate files
	fmt.Printf("Generating files for domain '%s' from config...\n", config.Domain)
	
	if err := ch.templateGenerator.GenerateAllFiles(data, true); err != nil {
		return fmt.Errorf("failed to generate files: %w", err)
	}

	return nil
}

// GenerateLegacy generates files using legacy command-line interface
func (ch *CommandHandler) GenerateLegacy(domain, entity, command string) error {
	// Create template data (legacy mode)
	data := ch.configProcessor.CreateLegacyTemplateData(domain, entity)

	// Generate based on command
	switch command {
	case "entity":
		return ch.templateGenerator.GenerateEntityFiles(data, false)
	case "model":
		return ch.templateGenerator.GenerateModelFiles(data)
	case "repository":
		return ch.templateGenerator.GenerateRepositoryFiles(data, false)
	case "usecase":
		return ch.templateGenerator.GenerateUseCaseFiles(data, false)
	case "handler":
		return ch.templateGenerator.GenerateHandlerFiles(data)
	case "di":
		return ch.templateGenerator.GenerateDIFiles(data)
	case "all":
		return ch.templateGenerator.GenerateAllFiles(data, false)
	default:
		return fmt.Errorf("unknown command: %s", command)
	}
}

// GetAvailableCommands returns list of available commands
func (ch *CommandHandler) GetAvailableCommands() []Command {
	return []Command{
		{
			Name:        "entity",
			Description: "Generate entity files",
		},
		{
			Name:        "model",
			Description: "Generate model files",
		},
		{
			Name:        "repository",
			Description: "Generate repository files",
		},
		{
			Name:        "usecase",
			Description: "Generate usecase files",
		},
		{
			Name:        "handler",
			Description: "Generate handler files",
		},
		{
			Name:        "di",
			Description: "Generate dependency injection files",
		},
		{
			Name:        "all",
			Description: "Generate all files",
		},
	}
}
