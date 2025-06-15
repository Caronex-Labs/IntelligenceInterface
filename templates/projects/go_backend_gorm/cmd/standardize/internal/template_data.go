package internal

// TemplateData holds the data to be passed to templates
type TemplateData struct {
	// Original fields for backward compatibility
	Domain       string // PascalCase (e.g., "User")
	DomainSnake  string // snake_case (e.g., "user")
	Entity       string // PascalCase (e.g., "User") 
	EntitySnake  string // snake_case (e.g., "user")
	Entities     string // PascalCase plural (e.g., "Users")
	EntitiesSnake string // snake_case plural (e.g., "users")
	Module       string // Go module name

	// Configuration-driven fields
	EntityConfig   EntityConfig     `json:"entity"`
	ModelConfig    ModelConfig      `json:"model,omitempty"`
	Models         []ModelConfig    `json:"models,omitempty"`
	API            APIConfig        `json:"api,omitempty"`
	Repository     RepositoryConfig `json:"repository,omitempty"`
	UseCase        UseCaseConfig    `json:"use_case,omitempty"`
	Handlers       HandlersConfig   `json:"handlers,omitempty"`
	Endpoints      []EndpointConfig `json:"endpoints,omitempty"`
	Generation     GenerationConfig `json:"generation,omitempty"`
	Features       FeaturesConfig   `json:"features,omitempty"`
}

// Command represents a CLI command
type Command struct {
	Name        string
	Description string
	Execute     func(args []string) error
}
