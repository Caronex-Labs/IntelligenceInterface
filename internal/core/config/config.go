// Package config manages application configuration from various sources.
package config

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"os"
	"path/filepath"
	"strings"

	"github.com/caronex/intelligence-interface/internal/llm/models"
	"github.com/caronex/intelligence-interface/internal/core/logging"
	"github.com/spf13/viper"
)

// MCPType defines the type of MCP (Model Control Protocol) server.
type MCPType string

// Supported MCP types
const (
	MCPStdio MCPType = "stdio"
	MCPSse   MCPType = "sse"
)

// MCPServer defines the configuration for a Model Control Protocol server.
type MCPServer struct {
	Command string            `json:"command"`
	Env     []string          `json:"env"`
	Args    []string          `json:"args"`
	Type    MCPType           `json:"type"`
	URL     string            `json:"url"`
	Headers map[string]string `json:"headers"`
}

type AgentName string

const (
	AgentCaronex AgentName = "caronex"
)

// Agent defines configuration for different LLM models and their token limits.
type Agent struct {
	Model           models.ModelID `json:"model"`
	MaxTokens       int64          `json:"maxTokens"`
	ReasoningEffort string         `json:"reasoningEffort"` // For openai models low,medium,heigh
	Specialization  *AgentSpecialization `json:"specialization,omitempty"`
}

// AgentSpecialization defines advanced configuration for agent specialization
type AgentSpecialization struct {
	LearningRate       float64 `json:"learning_rate,omitempty"`
	CoordinationMode   string  `json:"coordination_mode,omitempty"`
	EvolutionCapable   bool    `json:"evolution_capable,omitempty"`
	MetaSystemAware    bool    `json:"meta_system_aware,omitempty"`
}

// CoordinationConfig defines Caronex coordination settings
type CoordinationConfig struct {
	MaxConcurrentAgents   int                    `json:"max_concurrent_agents,omitempty"`
	SpaceMemoryLimit      string                 `json:"space_memory_limit,omitempty"`
	EvolutionCycle        string                 `json:"evolution_cycle,omitempty"`
	AgentSpawningEnabled  bool                   `json:"agent_spawning_enabled,omitempty"`
	CommunicationProtocol string                 `json:"communication_protocol,omitempty"`
	LoadBalancing         map[string]interface{} `json:"load_balancing,omitempty"`
}

// SpaceManagementConfig defines space management settings for Caronex
type SpaceManagementConfig struct {
	MaxSpaces              int    `json:"max_spaces,omitempty"`
	DefaultSpaceTemplate   string `json:"default_space_template,omitempty"`
	SpaceIsolationLevel    string `json:"space_isolation_level,omitempty"`
	AutoSpaceCleanup       bool   `json:"auto_space_cleanup,omitempty"`
	SpacePersistencePolicy string `json:"space_persistence_policy,omitempty"`
}

// EvolutionConfig defines system evolution settings
type EvolutionConfig struct {
	Enabled                bool   `json:"enabled,omitempty"`
	BootstrapCompilerPath  string `json:"bootstrap_compiler_path,omitempty"`
	GoldenRepositoryURL    string `json:"golden_repository_url,omitempty"`
	SafetyChecksEnabled    bool   `json:"safety_checks_enabled,omitempty"`
	RollbackCapability     bool   `json:"rollback_capability,omitempty"`
}

// LearningConfig defines agent learning settings
type LearningConfig struct {
	Enabled              bool    `json:"enabled,omitempty"`
	PatternRecognition   bool    `json:"pattern_recognition,omitempty"`
	KnowledgeRetention   string  `json:"knowledge_retention,omitempty"`
	AdaptationThreshold  float64 `json:"adaptation_threshold,omitempty"`
	LearningHistoryLimit int     `json:"learning_history_limit,omitempty"`
}

// UILayoutConfig defines UI layout configuration for spaces
type UILayoutConfig struct {
	Type          string                 `json:"type,omitempty"`
	Panels        []PanelConfig          `json:"panels,omitempty"`
	DefaultTheme  string                 `json:"default_theme,omitempty"`
	Customizable  bool                   `json:"customizable,omitempty"`
	Configuration map[string]interface{} `json:"configuration,omitempty"`
}

// PanelConfig defines individual panel configuration
type PanelConfig struct {
	ID       string                 `json:"id"`
	Type     string                 `json:"type"`
	Position string                 `json:"position"`
	Size     string                 `json:"size"`
	Config   map[string]interface{} `json:"config,omitempty"`
}

// PersistenceConfig defines space persistence settings
type PersistenceConfig struct {
	Enabled        bool   `json:"enabled,omitempty"`
	StorageBackend string `json:"storage_backend,omitempty"`
	RetentionDays  int    `json:"retention_days,omitempty"`
	BackupEnabled  bool   `json:"backup_enabled,omitempty"`
}

// ResourceLimitsConfig defines resource limits for spaces
type ResourceLimitsConfig struct {
	MaxMemoryMB   int64 `json:"max_memory_mb,omitempty"`
	MaxCPUPercent int   `json:"max_cpu_percent,omitempty"`
	MaxAgents     int   `json:"max_agents,omitempty"`
	MaxTools      int   `json:"max_tools,omitempty"`
}

// SpaceConfig defines configuration for persistent desktop environments
type SpaceConfig struct {
	ID                 string                 `json:"id"`
	Name               string                 `json:"name"`
	Type               string                 `json:"type"`
	UILayout           UILayoutConfig         `json:"ui_layout,omitempty"`
	AssignedAgents     []string               `json:"assigned_agents,omitempty"`
	Persistence        PersistenceConfig      `json:"persistence,omitempty"`
	ResourceLimits     ResourceLimitsConfig   `json:"resource_limits,omitempty"`
	EvolutionEnabled   bool                   `json:"evolution_enabled,omitempty"`
	Configuration      map[string]interface{} `json:"configuration,omitempty"`
}

// Provider defines configuration for an LLM provider.
type Provider struct {
	APIKey   string `json:"apiKey"`
	Disabled bool   `json:"disabled"`
}

// Data defines storage configuration.
type Data struct {
	Directory string `json:"directory,omitempty"`
}

// LSPConfig defines configuration for Language Server Protocol integration.
type LSPConfig struct {
	Disabled bool     `json:"enabled"`
	Command  string   `json:"command"`
	Args     []string `json:"args"`
	Options  any      `json:"options"`
}

// TUIConfig defines the configuration for the Terminal User Interface.
type TUIConfig struct {
	Theme string `json:"theme,omitempty"`
}

// ShellConfig defines the configuration for the shell used by the bash tool.
type ShellConfig struct {
	Path string   `json:"path,omitempty"`
	Args []string `json:"args,omitempty"`
}

// CaronexConfig defines the central orchestrator configuration
type CaronexConfig struct {
	Enabled           bool                    `json:"enabled,omitempty"`
	Coordination      CoordinationConfig      `json:"coordination,omitempty"`
	SpaceManagement   SpaceManagementConfig   `json:"space_management,omitempty"`
	Evolution         EvolutionConfig         `json:"evolution,omitempty"`
	Learning          LearningConfig          `json:"learning,omitempty"`
	ManagementMode    bool                    `json:"management_mode,omitempty"`
	Hotkey            string                  `json:"hotkey,omitempty"`
}

// Config is the main configuration structure for the application.
type Config struct {
	Data         Data                              `json:"data"`
	WorkingDir   string                            `json:"wd,omitempty"`
	MCPServers   map[string]MCPServer              `json:"mcpServers,omitempty"`
	Providers    map[models.ModelProvider]Provider `json:"providers,omitempty"`
	LSP          map[string]LSPConfig              `json:"lsp,omitempty"`
	Agents       map[AgentName]Agent               `json:"agents,omitempty"`
	Caronex      CaronexConfig                     `json:"caronex,omitempty"`
	Spaces       map[string]SpaceConfig            `json:"spaces,omitempty"`
	Debug        bool                              `json:"debug,omitempty"`
	DebugLSP     bool                              `json:"debugLSP,omitempty"`
	ContextPaths []string                          `json:"contextPaths,omitempty"`
	TUI          TUIConfig                         `json:"tui"`
	Shell        ShellConfig                       `json:"shell,omitempty"`
	AutoCompact  bool                              `json:"autoCompact,omitempty"`
}

// Application constants
const (
	defaultDataDirectory = ".intelligence-interface"
	defaultLogLevel      = "info"
	appName              = "intelligence-interface"

	MaxTokensFallbackDefault = 4096
)

var defaultContextPaths = []string{
	".github/copilot-instructions.md",
	".cursorrules",
	".cursor/rules/",
	"CLAUDE.md",
	"CLAUDE.local.md",
	"opencode.md",
	"opencode.local.md",
	"intelligence-interface.md",
	"intelligence-interface.local.md",
	"Intelligence Interface.md",
	"Intelligence Interface.local.md",
	"OPENCODE.md",
	"OPENCODE.local.md",
}

// Global configuration instance
var cfg *Config

// Load initializes the configuration from environment variables and config files.
// If debug is true, debug mode is enabled and log level is set to debug.
// It returns an error if configuration loading fails.
func Load(workingDir string, debug bool) (*Config, error) {
	if cfg != nil {
		return cfg, nil
	}

	cfg = &Config{
		WorkingDir: workingDir,
		MCPServers: make(map[string]MCPServer),
		Providers:  make(map[models.ModelProvider]Provider),
		LSP:        make(map[string]LSPConfig),
		Spaces:     make(map[string]SpaceConfig),
	}

	configureViper()
	setDefaults(debug)

	// Read global config
	if err := readConfig(viper.ReadInConfig()); err != nil {
		return cfg, err
	}

	// Load and merge local config
	mergeLocalConfig(workingDir)

	setProviderDefaults()

	// Apply configuration to the struct
	if err := viper.Unmarshal(cfg); err != nil {
		return cfg, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	applyDefaultValues()
	defaultLevel := slog.LevelInfo
	if cfg.Debug {
		defaultLevel = slog.LevelDebug
	}
	if os.Getenv("OPENCODE_DEV_DEBUG") == "true" {
		loggingFile := fmt.Sprintf("%s/%s", cfg.Data.Directory, "debug.log")

		// if file does not exist create it
		if _, err := os.Stat(loggingFile); os.IsNotExist(err) {
			if err := os.MkdirAll(cfg.Data.Directory, 0o755); err != nil {
				return cfg, fmt.Errorf("failed to create directory: %w", err)
			}
			if _, err := os.Create(loggingFile); err != nil {
				return cfg, fmt.Errorf("failed to create log file: %w", err)
			}
		}

		sloggingFileWriter, err := os.OpenFile(loggingFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o666)
		if err != nil {
			return cfg, fmt.Errorf("failed to open log file: %w", err)
		}
		// Configure logger
		logger := slog.New(slog.NewTextHandler(sloggingFileWriter, &slog.HandlerOptions{
			Level: defaultLevel,
		}))
		slog.SetDefault(logger)
	} else {
		// Configure logger
		logger := slog.New(slog.NewTextHandler(logging.NewWriter(), &slog.HandlerOptions{
			Level: defaultLevel,
		}))
		slog.SetDefault(logger)
	}

	// Validate configuration
	if err := Validate(); err != nil {
		return cfg, fmt.Errorf("config validation failed: %w", err)
	}

	if cfg.Agents == nil {
		cfg.Agents = make(map[AgentName]Agent)
	}

	return cfg, nil
}

// configureViper sets up viper's configuration paths and environment variables.
func configureViper() {
	viper.SetConfigName(fmt.Sprintf(".%s", appName))
	viper.SetConfigType("json")
	viper.AddConfigPath("$HOME")
	viper.AddConfigPath(fmt.Sprintf("$XDG_CONFIG_HOME/%s", appName))
	viper.AddConfigPath(fmt.Sprintf("$HOME/.config/%s", appName))
	viper.SetEnvPrefix(strings.ToUpper(appName))
	viper.AutomaticEnv()
}

// setDefaults configures default values for configuration options.
func setDefaults(debug bool) {
	viper.SetDefault("data.directory", defaultDataDirectory)
	viper.SetDefault("contextPaths", defaultContextPaths)
	viper.SetDefault("tui.theme", "intelligence-interface")
	viper.SetDefault("autoCompact", true)

	// Set default shell from environment or fallback to /bin/bash
	shellPath := os.Getenv("SHELL")
	if shellPath == "" {
		shellPath = "/bin/bash"
	}
	viper.SetDefault("shell.path", shellPath)
	viper.SetDefault("shell.args", []string{"-l"})

	// Meta-system defaults
	setMetaSystemDefaults()

	if debug {
		viper.SetDefault("debug", true)
		viper.Set("log.level", "debug")
	} else {
		viper.SetDefault("debug", false)
		viper.SetDefault("log.level", defaultLogLevel)
	}
}

// setMetaSystemDefaults configures default values for meta-system features
func setMetaSystemDefaults() {
	// Caronex defaults
	viper.SetDefault("caronex.enabled", true)
	viper.SetDefault("caronex.management_mode", false)
	viper.SetDefault("caronex.hotkey", "ctrl+m")
	
	// Coordination defaults
	viper.SetDefault("caronex.coordination.max_concurrent_agents", 10)
	viper.SetDefault("caronex.coordination.space_memory_limit", "1GB")
	viper.SetDefault("caronex.coordination.evolution_cycle", "24h")
	viper.SetDefault("caronex.coordination.agent_spawning_enabled", true)
	viper.SetDefault("caronex.coordination.communication_protocol", "pubsub")
	
	// Space management defaults
	viper.SetDefault("caronex.space_management.max_spaces", 20)
	viper.SetDefault("caronex.space_management.default_space_template", "development")
	viper.SetDefault("caronex.space_management.space_isolation_level", "standard")
	viper.SetDefault("caronex.space_management.auto_space_cleanup", true)
	viper.SetDefault("caronex.space_management.space_persistence_policy", "session")
	
	// Evolution defaults
	viper.SetDefault("caronex.evolution.enabled", false) // Disabled by default for safety
	viper.SetDefault("caronex.evolution.safety_checks_enabled", true)
	viper.SetDefault("caronex.evolution.rollback_capability", true)
	
	// Learning defaults
	viper.SetDefault("caronex.learning.enabled", true)
	viper.SetDefault("caronex.learning.pattern_recognition", true)
	viper.SetDefault("caronex.learning.knowledge_retention", "session")
	viper.SetDefault("caronex.learning.adaptation_threshold", 0.8)
	viper.SetDefault("caronex.learning.learning_history_limit", 1000)
}

// setProviderDefaults configures LLM provider defaults based on provider provided by
// environment variables and configuration file.
func setProviderDefaults() {
	// Set all API keys we can find in the environment
	if apiKey := os.Getenv("ANTHROPIC_API_KEY"); apiKey != "" {
		viper.SetDefault("providers.anthropic.apiKey", apiKey)
	}
	if apiKey := os.Getenv("OPENAI_API_KEY"); apiKey != "" {
		viper.SetDefault("providers.openai.apiKey", apiKey)
	}
	if apiKey := os.Getenv("GEMINI_API_KEY"); apiKey != "" {
		viper.SetDefault("providers.gemini.apiKey", apiKey)
	}
	if apiKey := os.Getenv("GROQ_API_KEY"); apiKey != "" {
		viper.SetDefault("providers.groq.apiKey", apiKey)
	}
	if apiKey := os.Getenv("OPENROUTER_API_KEY"); apiKey != "" {
		viper.SetDefault("providers.openrouter.apiKey", apiKey)
	}
	if apiKey := os.Getenv("XAI_API_KEY"); apiKey != "" {
		viper.SetDefault("providers.xai.apiKey", apiKey)
	}
	if apiKey := os.Getenv("AZURE_OPENAI_ENDPOINT"); apiKey != "" {
		// api-key may be empty when using Entra ID credentials – that's okay
		viper.SetDefault("providers.azure.apiKey", os.Getenv("AZURE_OPENAI_API_KEY"))
	}

	// Use this order to set the default models
	// 1. Anthropic
	// 2. OpenAI
	// 3. Google Gemini
	// 4. Groq
	// 5. OpenRouter
	// 6. AWS Bedrock
	// 7. Azure
	// 8. Google Cloud VertexAI

	// Anthropic configuration
	if key := viper.GetString("providers.anthropic.apiKey"); strings.TrimSpace(key) != "" {
		viper.SetDefault("agents.caronex.model", models.Claude4Sonnet)
		return
	}

	// OpenAI configuration
	if key := viper.GetString("providers.openai.apiKey"); strings.TrimSpace(key) != "" {
		viper.SetDefault("agents.caronex.model", models.GPT41)
		return
	}

	// Google Gemini configuration
	if key := viper.GetString("providers.gemini.apiKey"); strings.TrimSpace(key) != "" {
		viper.SetDefault("agents.caronex.model", models.Gemini25)
		return
	}

	// Groq configuration
	if key := viper.GetString("providers.groq.apiKey"); strings.TrimSpace(key) != "" {
		viper.SetDefault("agents.caronex.model", models.QWENQwq)
		return
	}

	// OpenRouter configuration
	if key := viper.GetString("providers.openrouter.apiKey"); strings.TrimSpace(key) != "" {
		viper.SetDefault("agents.caronex.model", models.OpenRouterClaude37Sonnet)
		return
	}

	// XAI configuration
	if key := viper.GetString("providers.xai.apiKey"); strings.TrimSpace(key) != "" {
		viper.SetDefault("agents.caronex.model", models.XAIGrok3Beta)
		return
	}

	// AWS Bedrock configuration
	if hasAWSCredentials() {
		viper.SetDefault("agents.caronex.model", models.BedrockClaude37Sonnet)
		return
	}

	// Azure OpenAI configuration
	if os.Getenv("AZURE_OPENAI_ENDPOINT") != "" {
		viper.SetDefault("agents.caronex.model", models.AzureGPT41)
		return
	}

	// Google Cloud VertexAI configuration
	if hasVertexAICredentials() {
		viper.SetDefault("agents.caronex.model", models.VertexAIGemini25)
		return
	}
}

// hasAWSCredentials checks if AWS credentials are available in the environment.
func hasAWSCredentials() bool {
	// Check for explicit AWS credentials
	if os.Getenv("AWS_ACCESS_KEY_ID") != "" && os.Getenv("AWS_SECRET_ACCESS_KEY") != "" {
		return true
	}

	// Check for AWS profile
	if os.Getenv("AWS_PROFILE") != "" || os.Getenv("AWS_DEFAULT_PROFILE") != "" {
		return true
	}

	// Check for AWS region
	if os.Getenv("AWS_REGION") != "" || os.Getenv("AWS_DEFAULT_REGION") != "" {
		return true
	}

	// Check if running on EC2 with instance profile
	if os.Getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI") != "" ||
		os.Getenv("AWS_CONTAINER_CREDENTIALS_FULL_URI") != "" {
		return true
	}

	return false
}

// hasVertexAICredentials checks if VertexAI credentials are available in the environment.
func hasVertexAICredentials() bool {
	// Check for explicit VertexAI parameters
	if os.Getenv("VERTEXAI_PROJECT") != "" && os.Getenv("VERTEXAI_LOCATION") != "" {
		return true
	}
	// Check for Google Cloud project and location
	if os.Getenv("GOOGLE_CLOUD_PROJECT") != "" && (os.Getenv("GOOGLE_CLOUD_REGION") != "" || os.Getenv("GOOGLE_CLOUD_LOCATION") != "") {
		return true
	}
	return false
}

// readConfig handles the result of reading a configuration file.
func readConfig(err error) error {
	if err == nil {
		return nil
	}

	// It's okay if the config file doesn't exist
	if _, ok := err.(viper.ConfigFileNotFoundError); ok {
		return nil
	}

	return fmt.Errorf("failed to read config: %w", err)
}

// mergeLocalConfig loads and merges configuration from the local directory.
func mergeLocalConfig(workingDir string) {
	local := viper.New()
	local.SetConfigName(fmt.Sprintf(".%s", appName))
	local.SetConfigType("json")
	local.AddConfigPath(workingDir)

	// Merge local config if it exists
	if err := local.ReadInConfig(); err == nil {
		viper.MergeConfigMap(local.AllSettings())
	}
}

// applyDefaultValues sets default values for configuration fields that need processing.
func applyDefaultValues() {
	// Set default MCP type if not specified
	for k, v := range cfg.MCPServers {
		if v.Type == "" {
			v.Type = MCPStdio
			cfg.MCPServers[k] = v
		}
	}
	
	// Apply Caronex defaults if not set
	if cfg.Caronex.Coordination.MaxConcurrentAgents == 0 {
		cfg.Caronex.Coordination.MaxConcurrentAgents = 10
	}
	if cfg.Caronex.Coordination.SpaceMemoryLimit == "" {
		cfg.Caronex.Coordination.SpaceMemoryLimit = "1GB"
	}
	if cfg.Caronex.Coordination.EvolutionCycle == "" {
		cfg.Caronex.Coordination.EvolutionCycle = "24h"
	}
	if cfg.Caronex.Coordination.CommunicationProtocol == "" {
		cfg.Caronex.Coordination.CommunicationProtocol = "pubsub"
	}
	
	// Apply space management defaults
	if cfg.Caronex.SpaceManagement.MaxSpaces == 0 {
		cfg.Caronex.SpaceManagement.MaxSpaces = 20
	}
	if cfg.Caronex.SpaceManagement.DefaultSpaceTemplate == "" {
		cfg.Caronex.SpaceManagement.DefaultSpaceTemplate = "development"
	}
	if cfg.Caronex.SpaceManagement.SpaceIsolationLevel == "" {
		cfg.Caronex.SpaceManagement.SpaceIsolationLevel = "standard"
	}
	if cfg.Caronex.SpaceManagement.SpacePersistencePolicy == "" {
		cfg.Caronex.SpaceManagement.SpacePersistencePolicy = "session"
	}
	
	// Apply learning defaults
	if cfg.Caronex.Learning.KnowledgeRetention == "" {
		cfg.Caronex.Learning.KnowledgeRetention = "session"
	}
	if cfg.Caronex.Learning.AdaptationThreshold == 0 {
		cfg.Caronex.Learning.AdaptationThreshold = 0.8
	}
	if cfg.Caronex.Learning.LearningHistoryLimit == 0 {
		cfg.Caronex.Learning.LearningHistoryLimit = 1000
	}
}

// It validates model IDs and providers, ensuring they are supported.
func validateAgent(cfg *Config, name AgentName, agent Agent) error {
	// Check if model exists
	model, modelExists := models.SupportedModels[agent.Model]
	if !modelExists {
		logging.Warn("unsupported model configured, reverting to default",
			"agent", name,
			"configured_model", agent.Model)

		// Set default model based on available providers
		if setDefaultModelForAgent(name) {
			logging.Info("set default model for agent", "agent", name, "model", cfg.Agents[name].Model)
		} else {
			return fmt.Errorf("no valid provider available for agent %s", name)
		}
		return nil
	}

	// Check if provider for the model is configured
	provider := model.Provider
	providerCfg, providerExists := cfg.Providers[provider]

	if !providerExists {
		// Provider not configured, check if we have environment variables
		apiKey := getProviderAPIKey(provider)
		if apiKey == "" {
			logging.Warn("provider not configured for model, reverting to default",
				"agent", name,
				"model", agent.Model,
				"provider", provider)

			// Set default model based on available providers
			if setDefaultModelForAgent(name) {
				logging.Info("set default model for agent", "agent", name, "model", cfg.Agents[name].Model)
			} else {
				return fmt.Errorf("no valid provider available for agent %s", name)
			}
		} else {
			// Add provider with API key from environment
			cfg.Providers[provider] = Provider{
				APIKey: apiKey,
			}
			logging.Info("added provider from environment", "provider", provider)
		}
	} else if providerCfg.Disabled || providerCfg.APIKey == "" {
		// Provider is disabled or has no API key
		logging.Warn("provider is disabled or has no API key, reverting to default",
			"agent", name,
			"model", agent.Model,
			"provider", provider)

		// Set default model based on available providers
		if setDefaultModelForAgent(name) {
			logging.Info("set default model for agent", "agent", name, "model", cfg.Agents[name].Model)
		} else {
			return fmt.Errorf("no valid provider available for agent %s", name)
		}
	}

	// Validate max tokens
	if agent.MaxTokens <= 0 {
		logging.Warn("invalid max tokens, setting to default",
			"agent", name,
			"model", agent.Model,
			"max_tokens", agent.MaxTokens)

		// Update the agent with default max tokens
		updatedAgent := cfg.Agents[name]
		if model.DefaultMaxTokens > 0 {
			updatedAgent.MaxTokens = model.DefaultMaxTokens
		} else {
			updatedAgent.MaxTokens = MaxTokensFallbackDefault
		}
		cfg.Agents[name] = updatedAgent
	} else if model.ContextWindow > 0 && agent.MaxTokens > model.ContextWindow/2 {
		// Ensure max tokens doesn't exceed half the context window (reasonable limit)
		logging.Warn("max tokens exceeds half the context window, adjusting",
			"agent", name,
			"model", agent.Model,
			"max_tokens", agent.MaxTokens,
			"context_window", model.ContextWindow)

		// Update the agent with adjusted max tokens
		updatedAgent := cfg.Agents[name]
		updatedAgent.MaxTokens = model.ContextWindow / 2
		cfg.Agents[name] = updatedAgent
	}

	// Validate reasoning effort for models that support reasoning
	if model.CanReason && provider == models.ProviderOpenAI || provider == models.ProviderLocal {
		if agent.ReasoningEffort == "" {
			// Set default reasoning effort for models that support it
			logging.Info("setting default reasoning effort for model that supports reasoning",
				"agent", name,
				"model", agent.Model)

			// Update the agent with default reasoning effort
			updatedAgent := cfg.Agents[name]
			updatedAgent.ReasoningEffort = "medium"
			cfg.Agents[name] = updatedAgent
		} else {
			// Check if reasoning effort is valid (low, medium, high)
			effort := strings.ToLower(agent.ReasoningEffort)
			if effort != "low" && effort != "medium" && effort != "high" {
				logging.Warn("invalid reasoning effort, setting to medium",
					"agent", name,
					"model", agent.Model,
					"reasoning_effort", agent.ReasoningEffort)

				// Update the agent with valid reasoning effort
				updatedAgent := cfg.Agents[name]
				updatedAgent.ReasoningEffort = "medium"
				cfg.Agents[name] = updatedAgent
			}
		}
	} else if !model.CanReason && agent.ReasoningEffort != "" {
		// Model doesn't support reasoning but reasoning effort is set
		logging.Warn("model doesn't support reasoning but reasoning effort is set, ignoring",
			"agent", name,
			"model", agent.Model,
			"reasoning_effort", agent.ReasoningEffort)

		// Update the agent to remove reasoning effort
		updatedAgent := cfg.Agents[name]
		updatedAgent.ReasoningEffort = ""
		cfg.Agents[name] = updatedAgent
	}

	return nil
}

// Validate checks if the configuration is valid and applies defaults where needed.
func Validate() error {
	if cfg == nil {
		return fmt.Errorf("config not loaded")
	}

	// Validate agent models
	for name, agent := range cfg.Agents {
		if err := validateAgent(cfg, name, agent); err != nil {
			return err
		}
	}

	// Validate providers
	for provider, providerCfg := range cfg.Providers {
		if providerCfg.APIKey == "" && !providerCfg.Disabled {
			logging.Warn("provider has no API key, marking as disabled", "provider", provider)
			providerCfg.Disabled = true
			cfg.Providers[provider] = providerCfg
		}
	}

	// Validate LSP configurations
	for language, lspConfig := range cfg.LSP {
		if lspConfig.Command == "" && !lspConfig.Disabled {
			logging.Warn("LSP configuration has no command, marking as disabled", "language", language)
			lspConfig.Disabled = true
			cfg.LSP[language] = lspConfig
		}
	}

	// Validate meta-system configurations
	if err := validateMetaSystemConfig(); err != nil {
		return fmt.Errorf("meta-system config validation failed: %w", err)
	}

	return nil
}

// validateMetaSystemConfig validates meta-system specific configurations
func validateMetaSystemConfig() error {
	// Validate Caronex configuration
	if err := validateCaronexConfig(); err != nil {
		return fmt.Errorf("Caronex config validation failed: %w", err)
	}

	// Validate space configurations
	if err := validateSpaceConfigs(); err != nil {
		return fmt.Errorf("space config validation failed: %w", err)
	}

	// Validate agent specializations
	if err := validateAgentSpecializations(); err != nil {
		return fmt.Errorf("agent specialization validation failed: %w", err)
	}

	return nil
}

// validateCaronexConfig validates Caronex configuration parameters
func validateCaronexConfig() error {
	caronex := &cfg.Caronex

	// Validate coordination settings
	if caronex.Coordination.MaxConcurrentAgents < 0 {
		logging.Warn("invalid max concurrent agents, setting to default", "value", caronex.Coordination.MaxConcurrentAgents)
		caronex.Coordination.MaxConcurrentAgents = 10
	}
	if caronex.Coordination.MaxConcurrentAgents > 100 {
		logging.Warn("max concurrent agents exceeds reasonable limit, adjusting", "value", caronex.Coordination.MaxConcurrentAgents)
		caronex.Coordination.MaxConcurrentAgents = 100
	}

	// Validate communication protocol
	validProtocols := []string{"pubsub", "direct", "queue", ""}
	if caronex.Coordination.CommunicationProtocol != "" {
		valid := false
		for _, protocol := range validProtocols {
			if caronex.Coordination.CommunicationProtocol == protocol {
				valid = true
				break
			}
		}
		if !valid {
			logging.Warn("invalid communication protocol, setting to default", "protocol", caronex.Coordination.CommunicationProtocol)
			caronex.Coordination.CommunicationProtocol = "pubsub"
		}
	}

	// Validate space management settings
	if caronex.SpaceManagement.MaxSpaces < 0 {
		logging.Warn("invalid max spaces, setting to default", "value", caronex.SpaceManagement.MaxSpaces)
		caronex.SpaceManagement.MaxSpaces = 20
	}
	if caronex.SpaceManagement.MaxSpaces > 1000 {
		logging.Warn("max spaces exceeds reasonable limit, adjusting", "value", caronex.SpaceManagement.MaxSpaces)
		caronex.SpaceManagement.MaxSpaces = 1000
	}

	// Validate space isolation level
	validIsolationLevels := []string{"none", "basic", "standard", "strict", ""}
	if caronex.SpaceManagement.SpaceIsolationLevel != "" {
		valid := false
		for _, level := range validIsolationLevels {
			if caronex.SpaceManagement.SpaceIsolationLevel == level {
				valid = true
				break
			}
		}
		if !valid {
			logging.Warn("invalid space isolation level, setting to default", "level", caronex.SpaceManagement.SpaceIsolationLevel)
			caronex.SpaceManagement.SpaceIsolationLevel = "standard"
		}
	}

	// Validate learning configuration
	if caronex.Learning.AdaptationThreshold < 0.0 || caronex.Learning.AdaptationThreshold > 1.0 {
		logging.Warn("adaptation threshold out of range, setting to default", "threshold", caronex.Learning.AdaptationThreshold)
		caronex.Learning.AdaptationThreshold = 0.8
	}

	if caronex.Learning.LearningHistoryLimit < 0 {
		logging.Warn("invalid learning history limit, setting to default", "limit", caronex.Learning.LearningHistoryLimit)
		caronex.Learning.LearningHistoryLimit = 1000
	}

	return nil
}

// validateSpaceConfigs validates space configuration parameters
func validateSpaceConfigs() error {
	for spaceID, spaceConfig := range cfg.Spaces {
		if spaceConfig.ID == "" {
			logging.Warn("space missing ID, setting from key", "space_key", spaceID)
			updatedConfig := spaceConfig
			updatedConfig.ID = spaceID
			cfg.Spaces[spaceID] = updatedConfig
		}

		if spaceConfig.Name == "" {
			logging.Warn("space missing name, setting default", "space_id", spaceID)
			updatedConfig := spaceConfig
			updatedConfig.Name = fmt.Sprintf("Space %s", spaceID)
			cfg.Spaces[spaceID] = updatedConfig
		}

		// Validate space type
		validTypes := []string{"development", "knowledge_base", "social", "custom", ""}
		if spaceConfig.Type != "" {
			valid := false
			for _, spaceType := range validTypes {
				if spaceConfig.Type == spaceType {
					valid = true
					break
				}
			}
			if !valid {
				logging.Warn("invalid space type, setting to default", "space_id", spaceID, "type", spaceConfig.Type)
				updatedConfig := spaceConfig
				updatedConfig.Type = "custom"
				cfg.Spaces[spaceID] = updatedConfig
			}
		}

		// Validate resource limits
		if spaceConfig.ResourceLimits.MaxMemoryMB < 0 {
			logging.Warn("invalid memory limit, disabling", "space_id", spaceID, "memory_mb", spaceConfig.ResourceLimits.MaxMemoryMB)
			updatedConfig := spaceConfig
			updatedConfig.ResourceLimits.MaxMemoryMB = 0
			cfg.Spaces[spaceID] = updatedConfig
		}

		if spaceConfig.ResourceLimits.MaxCPUPercent < 0 || spaceConfig.ResourceLimits.MaxCPUPercent > 100 {
			logging.Warn("invalid CPU limit, disabling", "space_id", spaceID, "cpu_percent", spaceConfig.ResourceLimits.MaxCPUPercent)
			updatedConfig := spaceConfig
			updatedConfig.ResourceLimits.MaxCPUPercent = 0
			cfg.Spaces[spaceID] = updatedConfig
		}

		// Validate persistence settings
		validStorageBackends := []string{"memory", "disk", "database", ""}
		if spaceConfig.Persistence.StorageBackend != "" {
			valid := false
			for _, backend := range validStorageBackends {
				if spaceConfig.Persistence.StorageBackend == backend {
					valid = true
					break
				}
			}
			if !valid {
				logging.Warn("invalid storage backend, setting to default", "space_id", spaceID, "backend", spaceConfig.Persistence.StorageBackend)
				updatedConfig := spaceConfig
				updatedConfig.Persistence.StorageBackend = "memory"
				cfg.Spaces[spaceID] = updatedConfig
			}
		}
	}

	return nil
}

// validateAgentSpecializations validates agent specialization configurations
func validateAgentSpecializations() error {
	for agentName, agent := range cfg.Agents {
		if agent.Specialization == nil {
			continue
		}

		spec := agent.Specialization

		// Validate learning rate
		if spec.LearningRate < 0.0 || spec.LearningRate > 1.0 {
			logging.Warn("learning rate out of range, setting to default", "agent", agentName, "rate", spec.LearningRate)
			spec.LearningRate = 0.1
		}

		// Validate coordination mode
		validModes := []string{"cooperative", "competitive", "independent", "hierarchical", ""}
		if spec.CoordinationMode != "" {
			valid := false
			for _, mode := range validModes {
				if spec.CoordinationMode == mode {
					valid = true
					break
				}
			}
			if !valid {
				logging.Warn("invalid coordination mode, setting to default", "agent", agentName, "mode", spec.CoordinationMode)
				spec.CoordinationMode = "cooperative"
			}
		}

		// Update the agent with validated specialization
		updatedAgent := agent
		updatedAgent.Specialization = spec
		cfg.Agents[agentName] = updatedAgent
	}

	return nil
}

// getProviderAPIKey gets the API key for a provider from environment variables
func getProviderAPIKey(provider models.ModelProvider) string {
	switch provider {
	case models.ProviderAnthropic:
		return os.Getenv("ANTHROPIC_API_KEY")
	case models.ProviderOpenAI:
		return os.Getenv("OPENAI_API_KEY")
	case models.ProviderGemini:
		return os.Getenv("GEMINI_API_KEY")
	case models.ProviderGROQ:
		return os.Getenv("GROQ_API_KEY")
	case models.ProviderAzure:
		return os.Getenv("AZURE_OPENAI_API_KEY")
	case models.ProviderOpenRouter:
		return os.Getenv("OPENROUTER_API_KEY")
	case models.ProviderBedrock:
		if hasAWSCredentials() {
			return "aws-credentials-available"
		}
	case models.ProviderVertexAI:
		if hasVertexAICredentials() {
			return "vertex-ai-credentials-available"
		}
	}
	return ""
}

// setDefaultModelForAgent sets a default model for an agent based on available providers
func setDefaultModelForAgent(agent AgentName) bool {
	// Check providers in order of preference
	if apiKey := os.Getenv("ANTHROPIC_API_KEY"); apiKey != "" {
		maxTokens := int64(8000) // Higher token limit for Caronex manager agent
		cfg.Agents[agent] = Agent{
			Model:     models.Claude37Sonnet,
			MaxTokens: maxTokens,
		}
		return true
	}

	if apiKey := os.Getenv("OPENAI_API_KEY"); apiKey != "" {
		model := models.GPT41
		maxTokens := int64(8000) // Higher token limit for Caronex manager agent
		reasoningEffort := ""

		// Check if model supports reasoning
		if modelInfo, ok := models.SupportedModels[model]; ok && modelInfo.CanReason {
			reasoningEffort = "medium"
		}

		cfg.Agents[agent] = Agent{
			Model:           model,
			MaxTokens:       maxTokens,
			ReasoningEffort: reasoningEffort,
		}
		return true
	}

	if apiKey := os.Getenv("OPENROUTER_API_KEY"); apiKey != "" {
		model := models.OpenRouterClaude37Sonnet
		maxTokens := int64(8000) // Higher token limit for Caronex manager agent
		reasoningEffort := ""

		// Check if model supports reasoning
		if modelInfo, ok := models.SupportedModels[model]; ok && modelInfo.CanReason {
			reasoningEffort = "medium"
		}

		cfg.Agents[agent] = Agent{
			Model:           model,
			MaxTokens:       maxTokens,
			ReasoningEffort: reasoningEffort,
		}
		return true
	}

	if apiKey := os.Getenv("GEMINI_API_KEY"); apiKey != "" {
		model := models.Gemini25
		maxTokens := int64(8000) // Higher token limit for Caronex manager agent

		cfg.Agents[agent] = Agent{
			Model:     model,
			MaxTokens: maxTokens,
		}
		return true
	}

	if apiKey := os.Getenv("GROQ_API_KEY"); apiKey != "" {
		maxTokens := int64(8000) // Higher token limit for Caronex manager agent

		cfg.Agents[agent] = Agent{
			Model:     models.QWENQwq,
			MaxTokens: maxTokens,
		}
		return true
	}

	if hasAWSCredentials() {
		maxTokens := int64(8000) // Higher token limit for Caronex manager agent

		cfg.Agents[agent] = Agent{
			Model:           models.BedrockClaude37Sonnet,
			MaxTokens:       maxTokens,
			ReasoningEffort: "medium", // Claude models support reasoning
		}
		return true
	}

	if hasVertexAICredentials() {
		model := models.VertexAIGemini25
		maxTokens := int64(8000) // Higher token limit for Caronex manager agent

		cfg.Agents[agent] = Agent{
			Model:     model,
			MaxTokens: maxTokens,
		}
		return true
	}

	return false
}

func updateCfgFile(updateCfg func(config *Config)) error {
	if cfg == nil {
		return fmt.Errorf("config not loaded")
	}

	// Get the config file path
	configFile := viper.ConfigFileUsed()
	var configData []byte
	if configFile == "" {
		homeDir, err := os.UserHomeDir()
		if err != nil {
			return fmt.Errorf("failed to get home directory: %w", err)
		}
		configFile = filepath.Join(homeDir, fmt.Sprintf(".%s.json", appName))
		logging.Info("config file not found, creating new one", "path", configFile)
		configData = []byte(`{}`)
	} else {
		// Read the existing config file
		data, err := os.ReadFile(configFile)
		if err != nil {
			return fmt.Errorf("failed to read config file: %w", err)
		}
		configData = data
	}

	// Parse the JSON
	var userCfg *Config
	if err := json.Unmarshal(configData, &userCfg); err != nil {
		return fmt.Errorf("failed to parse config file: %w", err)
	}

	updateCfg(userCfg)

	// Write the updated config back to file
	updatedData, err := json.MarshalIndent(userCfg, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(configFile, updatedData, 0o644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// Get returns the current configuration.
// It's safe to call this function multiple times.
func Get() *Config {
	return cfg
}

// WorkingDirectory returns the current working directory from the configuration.
func WorkingDirectory() string {
	if cfg == nil {
		panic("config not loaded")
	}
	return cfg.WorkingDir
}

func UpdateAgentModel(agentName AgentName, modelID models.ModelID) error {
	if cfg == nil {
		panic("config not loaded")
	}

	existingAgentCfg := cfg.Agents[agentName]

	model, ok := models.SupportedModels[modelID]
	if !ok {
		return fmt.Errorf("model %s not supported", modelID)
	}

	maxTokens := existingAgentCfg.MaxTokens
	if model.DefaultMaxTokens > 0 {
		maxTokens = model.DefaultMaxTokens
	}

	newAgentCfg := Agent{
		Model:           modelID,
		MaxTokens:       maxTokens,
		ReasoningEffort: existingAgentCfg.ReasoningEffort,
	}
	cfg.Agents[agentName] = newAgentCfg

	if err := validateAgent(cfg, agentName, newAgentCfg); err != nil {
		// revert config update on failure
		cfg.Agents[agentName] = existingAgentCfg
		return fmt.Errorf("failed to update agent model: %w", err)
	}

	return updateCfgFile(func(config *Config) {
		if config.Agents == nil {
			config.Agents = make(map[AgentName]Agent)
		}
		config.Agents[agentName] = newAgentCfg
	})
}

// UpdateTheme updates the theme in the configuration and writes it to the config file.
func UpdateTheme(themeName string) error {
	if cfg == nil {
		return fmt.Errorf("config not loaded")
	}

	// Update the in-memory config
	cfg.TUI.Theme = themeName

	// Update the file config
	return updateCfgFile(func(config *Config) {
		config.TUI.Theme = themeName
	})
}
