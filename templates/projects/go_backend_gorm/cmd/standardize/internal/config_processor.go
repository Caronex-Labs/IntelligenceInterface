package internal

import (
	"fmt"
	"os"
	"strings"

	"gopkg.in/yaml.v3"
)

// ConfigProcessor handles configuration file processing
type ConfigProcessor struct{}

// NewConfigProcessor creates a new configuration processor
func NewConfigProcessor() *ConfigProcessor {
	return &ConfigProcessor{}
}

// LoadConfig loads and parses a YAML configuration file
func (cp *ConfigProcessor) LoadConfig(configPath string) (*DomainConfig, error) {
	// Read configuration file
	configData, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	// Parse YAML configuration
	var domainConfig DomainConfig
	if err := yaml.Unmarshal(configData, &domainConfig); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	// Set defaults
	cp.setDefaults(&domainConfig)

	// Validate configuration
	if err := cp.validateConfig(&domainConfig); err != nil {
		return nil, fmt.Errorf("configuration validation failed: %w", err)
	}

	return &domainConfig, nil
}

// CreateTemplateData creates template data from configuration
func (cp *ConfigProcessor) CreateTemplateData(config DomainConfig) TemplateData {
	// Convert domain to snake_case and PascalCase
	domainSnake := ToSnakeCase(config.Domain)
	domainPascal := ToPascalCase(config.Domain)

	// Entity name (use from config or default to domain)
	entityName := config.Entity.Name
	if entityName == "" {
		entityName = domainPascal
	}

	// Convert entity to snake_case and PascalCase
	entitySnake := ToSnakeCase(entityName)
	entityPascal := ToPascalCase(entityName)

	// Create plurals
	entitiesSnake := Pluralize(entitySnake)
	entitiesPascal := ToPascalCase(entitiesSnake)

	// Process entity configuration
	entityConfig := config.Entity
	entityConfig.Name = entityPascal
	
	// Add standard fields if not present
	entityConfig = cp.addStandardFields(entityConfig, config.Generation.UUIDPrimaryKey)
	
	// Generate conversion methods if not specified
	if len(entityConfig.ConversionMethods) == 0 {
		entityConfig.ConversionMethods = cp.generateConversionMethods(entityPascal)
	}

	// Process computed fields
	for i, field := range entityConfig.ComputedFields {
		if field.NameSnake == "" {
			entityConfig.ComputedFields[i].NameSnake = ToSnakeCase(field.Name)
		}
	}

	// Process custom methods
	for i, method := range entityConfig.CustomMethods {
		if method.NameSnake == "" {
			entityConfig.CustomMethods[i].NameSnake = ToSnakeCase(method.Name)
		}
	}

	// Process model configuration
	modelConfig := cp.processModelConfig(config.Model, entityPascal, entitiesSnake, config.Generation)

	// Process repository configuration
	repoConfig := cp.processRepositoryConfig(config.Repository, entityPascal, config.Generation)

	// Process use case configuration
	useCaseConfig := cp.processUseCaseConfig(config.UseCase, entityPascal, config.Generation)

	return TemplateData{
		Domain:        domainPascal,
		DomainSnake:   domainSnake,
		Entity:        entityPascal, // For backward compatibility
		EntitySnake:   entitySnake,  // For backward compatibility
		Entities:      entitiesPascal,
		EntitiesSnake: entitiesSnake,
		Module:        config.Module,
		EntityConfig:  entityConfig,
		ModelConfig:   modelConfig,
		Models:        config.Models,
		API:           config.API,
		Repository:    repoConfig,
		UseCase:       useCaseConfig,
		Handlers:      config.Handlers,
		Endpoints:     config.Endpoints,
		Generation:    config.Generation,
		Features:      config.Features,
	}
}

// CreateLegacyTemplateData creates template data from domain and entity names (legacy)
func (cp *ConfigProcessor) CreateLegacyTemplateData(domain, entity string) TemplateData {
	// If entity is not provided, use domain as entity
	if entity == "" {
		entity = domain
	}

	// Convert domain to snake_case and PascalCase
	domainSnake := ToSnakeCase(domain)
	domainPascal := ToPascalCase(domain)

	// Convert entity to snake_case and PascalCase
	entitySnake := ToSnakeCase(entity)
	entityPascal := ToPascalCase(entity)

	// Create plurals
	entitiesSnake := Pluralize(entitySnake)
	entitiesPascal := ToPascalCase(entitiesSnake)

	return TemplateData{
		Domain:        domainPascal,
		DomainSnake:   domainSnake,
		Entity:        entityPascal,
		EntitySnake:   entitySnake,
		Entities:      entitiesPascal,
		EntitiesSnake: entitiesSnake,
		Module:        "go_backend_gorm",
	}
}

// setDefaults sets default values for configuration
func (cp *ConfigProcessor) setDefaults(config *DomainConfig) {
	// Set default module if not provided
	if config.Module == "" {
		config.Module = "go_backend_gorm"
	}

	// Set default generation options
	if config.Generation.UUIDPrimaryKey == false && config.Generation.PreserveCustomCode == false {
		// Set defaults only if no generation config is provided
		config.Generation.PreserveCustomCode = true
		config.Generation.UUIDPrimaryKey = true
		config.Generation.GenerateTests = true
	}
}

// validateConfig validates the configuration
func (cp *ConfigProcessor) validateConfig(config *DomainConfig) error {
	if config.Domain == "" {
		return fmt.Errorf("domain is required")
	}

	if config.Entity.Name == "" {
		config.Entity.Name = ToPascalCase(config.Domain)
	}

	return nil
}

// addStandardFields adds standard fields (ID, CreatedAt, UpdatedAt) if not present
func (cp *ConfigProcessor) addStandardFields(config EntityConfig, useUUID bool) EntityConfig {
	standardFields := []FieldConfig{
		{
			Name:        "ID",
			Type:        func() string { if useUUID { return "uuid.UUID" } else { return "uint" } }(),
			Tags:        `json:"id"`,
			Description: "Unique identifier",
			Standard:    true,
		},
		{
			Name:        "CreatedAt",
			Type:        "time.Time",
			Tags:        `json:"created_at"`,
			Description: "Creation timestamp",
			Standard:    true,
		},
		{
			Name:        "UpdatedAt",
			Type:        "time.Time",
			Tags:        `json:"updated_at"`,
			Description: "Last update timestamp",
			Standard:    true,
		},
	}

	// Check if standard fields already exist
	existingFields := make(map[string]bool)
	for _, field := range config.Fields {
		existingFields[field.Name] = true
	}

	// Add missing standard fields at the beginning
	var finalFields []FieldConfig
	for _, stdField := range standardFields {
		if !existingFields[stdField.Name] {
			finalFields = append(finalFields, stdField)
		}
	}
	
	// Add existing fields
	finalFields = append(finalFields, config.Fields...)
	config.Fields = finalFields

	// Set RequiresUUID flag
	config.RequiresUUID = useUUID

	return config
}

// generateConversionMethods generates default conversion methods
func (cp *ConfigProcessor) generateConversionMethods(entityName string) []ConversionMethodConfig {
	return []ConversionMethodConfig{
		{
			Name:        fmt.Sprintf("From%sModel", entityName),
			Description: "Converts a model to an entity",
			SourceType:  fmt.Sprintf("*modelsPkg.%s", entityName),
			TargetType:  fmt.Sprintf("*%s", entityName),
		},
		{
			Name:        fmt.Sprintf("To%sModel", entityName),
			Description: "Converts an entity to a model",
			SourceType:  fmt.Sprintf("*%s", entityName),
			TargetType:  fmt.Sprintf("*modelsPkg.%s", entityName),
		},
		{
			Name:        fmt.Sprintf("From%sRequest", entityName),
			Description: "Converts a request to an entity",
			SourceType:  "interface{}",
			TargetType:  fmt.Sprintf("*%s", entityName),
			Placeholder: true,
		},
		{
			Name:        fmt.Sprintf("To%sResponse", entityName),
			Description: "Converts an entity to a response",
			SourceType:  fmt.Sprintf("*%s", entityName),
			TargetType:  "interface{}",
			Placeholder: true,
		},
	}
}

// processModelConfig processes model configuration and sets defaults
func (cp *ConfigProcessor) processModelConfig(modelConfig ModelConfig, entityName, tableName string, generation GenerationConfig) ModelConfig {
	// Set defaults if not provided
	if modelConfig.Name == "" {
		modelConfig.Name = entityName
	}
	
	if modelConfig.TableName == "" {
		modelConfig.TableName = tableName
	}
	
	if modelConfig.Description == "" {
		modelConfig.Description = fmt.Sprintf("%s represents a %s in the database", entityName, ToSnakeCase(entityName))
	}
	
	// Set requirements based on configuration
	modelConfig.RequiresUUID = generation.UUIDPrimaryKey || cp.hasUUIDFields(modelConfig.Fields)
	modelConfig.RequiresTime = cp.hasTimeFields(modelConfig.Fields) || generation.UUIDPrimaryKey // UUID models typically have timestamps
	
	// Add standard fields if not present
	modelConfig.Fields = cp.addStandardModelFields(modelConfig.Fields, generation.UUIDPrimaryKey)
	
	// Process field GORM and JSON tags
	for i, field := range modelConfig.Fields {
		modelConfig.Fields[i] = cp.processModelField(field)
	}
	
	// Process method snake case names
	for i, method := range modelConfig.ComputedMethods {
		if method.NameSnake == "" {
			modelConfig.ComputedMethods[i].NameSnake = ToSnakeCase(method.Name)
		}
	}
	
	for i, method := range modelConfig.ValidationMethods {
		if method.NameSnake == "" {
			modelConfig.ValidationMethods[i].NameSnake = ToSnakeCase(method.Name)
		}
	}
	
	for i, method := range modelConfig.CustomMethods {
		if method.NameSnake == "" {
			modelConfig.CustomMethods[i].NameSnake = ToSnakeCase(method.Name)
		}
	}
	
	// Set default hooks
	if modelConfig.RequiresUUID && !modelConfig.Hooks.BeforeCreate {
		modelConfig.Hooks.BeforeCreate = true
	}
	
	return modelConfig
}

// hasUUIDFields checks if any field uses UUID type
func (cp *ConfigProcessor) hasUUIDFields(fields []ModelFieldConfig) bool {
	for _, field := range fields {
		if field.Type == "uuid.UUID" {
			return true
		}
	}
	return false
}

// hasTimeFields checks if any field uses time types
func (cp *ConfigProcessor) hasTimeFields(fields []ModelFieldConfig) bool {
	for _, field := range fields {
		if field.Type == "time.Time" || field.Type == "*time.Time" {
			return true
		}
	}
	return false
}

// addStandardModelFields adds standard model fields (ID, CreatedAt, UpdatedAt) if not present
func (cp *ConfigProcessor) addStandardModelFields(fields []ModelFieldConfig, useUUID bool) []ModelFieldConfig {
	standardFields := []ModelFieldConfig{
		{
			Name:        "ID",
			Type:        func() string { if useUUID { return "uuid.UUID" } else { return "uint" } }(),
			GormTags:    func() string { if useUUID { return "`gorm:\"type:uuid;primaryKey\"`" } else { return "`gorm:\"primaryKey\"`" } }(),
			JSONTags:    "`json:\"id\"`",
			Description: "Primary key identifier",
			Standard:    true,
		},
		{
			Name:        "CreatedAt",
			Type:        "time.Time",
			GormTags:    "`gorm:\"type:timestamp;default:now()\"`",
			JSONTags:    "`json:\"created_at\"`",
			Description: "Record creation timestamp",
			Standard:    true,
		},
		{
			Name:        "UpdatedAt",
			Type:        "time.Time",
			GormTags:    "`gorm:\"type:timestamp;default:now()\"`",
			JSONTags:    "`json:\"updated_at\"`",
			Description: "Record update timestamp",
			Standard:    true,
		},
	}
	
	// Check if standard fields already exist
	existingFields := make(map[string]bool)
	for _, field := range fields {
		existingFields[field.Name] = true
	}
	
	// Add missing standard fields at the beginning
	var finalFields []ModelFieldConfig
	for _, stdField := range standardFields {
		if !existingFields[stdField.Name] {
			finalFields = append(finalFields, stdField)
		}
	}
	
	// Add existing fields
	finalFields = append(finalFields, fields...)
	
	return finalFields
}

// processModelField processes individual model field configuration
func (cp *ConfigProcessor) processModelField(field ModelFieldConfig) ModelFieldConfig {
	// Generate GORM tags if not provided
	if field.GormTags == "" && !field.Standard {
		field.GormTags = cp.generateGormTags(field)
	}
	
	// Generate JSON tags if not provided
	if field.JSONTags == "" && !field.Standard {
		field.JSONTags = cp.generateJSONTags(field)
	}
	
	return field
}

// generateGormTags generates GORM tags based on field configuration
func (cp *ConfigProcessor) generateGormTags(field ModelFieldConfig) string {
	var tags []string
	
	// Type specification
	switch field.Type {
	case "string":
		if field.MaxLength > 0 {
			tags = append(tags, fmt.Sprintf("type:varchar(%d)", field.MaxLength))
		} else {
			tags = append(tags, "type:varchar(255)")
		}
	case "bool":
		tags = append(tags, "type:boolean")
	case "int", "int32":
		tags = append(tags, "type:integer")
	case "int64":
		tags = append(tags, "type:bigint")
	case "*time.Time":
		tags = append(tags, "type:timestamp")
	case "time.Time":
		tags = append(tags, "type:timestamp")
	}
	
	// Default value
	if field.DefaultValue != nil {
		tags = append(tags, fmt.Sprintf("default:%v", field.DefaultValue))
	}
	
	// Unique constraint
	if field.Unique {
		tags = append(tags, "uniqueIndex")
	}
	
	// Not null constraint
	if !field.Nullable {
		tags = append(tags, "not null")
	}
	
	return fmt.Sprintf("`gorm:\"%s\"`", strings.Join(tags, ";"))
}

// generateJSONTags generates JSON tags based on field configuration
func (cp *ConfigProcessor) generateJSONTags(field ModelFieldConfig) string {
	if field.ExcludeFromJSON {
		return "`json:\"-\"`"
	}
	
	fieldName := ToSnakeCase(field.Name)
	if field.Nullable {
		return fmt.Sprintf("`json:\"%s,omitempty\"`", fieldName)
	}
	
	return fmt.Sprintf("`json:\"%s\"`", fieldName)
}

// processRepositoryConfig processes repository configuration and sets defaults
func (cp *ConfigProcessor) processRepositoryConfig(repoConfig RepositoryConfig, entityName string, generation GenerationConfig) RepositoryConfig {
	// Set defaults if not provided
	if repoConfig.Interface.Name == "" {
		repoConfig.Interface.Name = fmt.Sprintf("I%sRepository", entityName)
	}
	
	if repoConfig.Implementation.Name == "" {
		repoConfig.Implementation.Name = fmt.Sprintf("%sRepository", entityName)
	}
	
	if repoConfig.Description == "" {
		repoConfig.Description = fmt.Sprintf("Repository for %s domain operations", ToSnakeCase(entityName))
	}
	
	// Set default standard methods if not specified
	if (repoConfig.Interface.StandardMethods == RepositoryMethodsConfig{}) {
		repoConfig.Interface.StandardMethods = RepositoryMethodsConfig{
			Create:    true,
			GetByID:   true,
			List:      true,
			Update:    true,
			Delete:    true,
			Count:     false,
			Exists:    false,
			GetByField: false,
		}
	}
	
	// Set default dependencies
	if len(repoConfig.Implementation.Dependencies) == 0 {
		repoConfig.Implementation.Dependencies = []string{"*postgres.DB", "*utils.Logger"}
	}
	
	// Set default pagination settings
	if !repoConfig.Pagination.Enabled {
		repoConfig.Pagination = PaginationConfig{
			Enabled:      true,
			DefaultLimit: 20,
			MaxLimit:     100,
			Type:         "offset",
		}
	}
	
	// Set default filtering settings
	if !repoConfig.Filtering.Enabled {
		repoConfig.Filtering = FilteringConfig{
			Enabled:   true,
			Operators: []string{"=", "!=", ">", ">=", "<", "<=", "LIKE", "IN"},
		}
	}
	
	// Set default logging settings
	if !repoConfig.Logging.Enabled {
		repoConfig.Logging = LoggingConfig{
			Enabled: true,
			Level:   "debug",
			Methods: []string{"Create", "Update", "Delete"},
		}
	}
	
	// Set default transaction settings
	if !repoConfig.Transactions.Enabled {
		repoConfig.Transactions = TransactionConfig{
			Enabled: true,
			Methods: []string{"Create", "Update", "Delete"},
		}
	}
	
	// Process custom methods
	for i, method := range repoConfig.Interface.CustomMethods {
		// Set snake case name if not provided
		if method.Name != "" {
			repoConfig.Interface.CustomMethods[i].Name = method.Name
		}
	}
	
	return repoConfig
}

// processUseCaseConfig processes use case configuration and sets defaults
func (cp *ConfigProcessor) processUseCaseConfig(useCaseConfig UseCaseConfig, entityName string, generation GenerationConfig) UseCaseConfig {
	// Set defaults if not provided
	if useCaseConfig.Interface.Name == "" {
		useCaseConfig.Interface.Name = fmt.Sprintf("I%sUseCase", entityName)
	}
	
	if useCaseConfig.Implementation.Name == "" {
		useCaseConfig.Implementation.Name = fmt.Sprintf("%sUseCase", entityName)
	}
	
	if useCaseConfig.Description == "" {
		useCaseConfig.Description = fmt.Sprintf("Use case for %s business operations", ToSnakeCase(entityName))
	}
	
	// Set default standard methods if not specified
	if (useCaseConfig.Interface.StandardMethods == UseCaseStandardMethods{}) {
		useCaseConfig.Interface.StandardMethods = UseCaseStandardMethods{
			Create:   true,
			GetByID:  true,
			List:     true,
			Update:   true,
			Delete:   true,
			Validate: false,
			Count:    false,
		}
	}
	
	// Set default dependencies if not provided
	if len(useCaseConfig.Implementation.Dependencies) == 0 {
		useCaseConfig.Implementation.Dependencies = []string{
			fmt.Sprintf("I%sRepository", entityName),
			"*utils.Logger",
		}
	}
	
	// Set default logging settings
	if !useCaseConfig.Logging.Enabled {
		useCaseConfig.Logging = LoggingConfig{
			Enabled: true,
			Level:   "debug",
			Methods: []string{"Create", "Update", "Delete"},
		}
	}
	
	// Set default transaction settings
	if !useCaseConfig.Transactions.Enabled {
		useCaseConfig.Transactions = TransactionConfig{
			Enabled: true,
			Methods: []string{"Create", "Update", "Delete"},
		}
	}
	
	// Set default validation settings
	if !useCaseConfig.Validation.Enabled {
		useCaseConfig.Validation = ValidationConfig{
			Enabled: true,
			Rules:   []string{"required", "format", "business_rules"},
		}
	}
	
	// Process business methods and enable auto-conversion detection
	for i, method := range useCaseConfig.BusinessMethods {
		// Enable auto-detect conversions by default
		if !method.Conversions.AutoDetect {
			useCaseConfig.BusinessMethods[i].Conversions.AutoDetect = true
		}
		
		// Set default validation if method has validation rules
		if len(method.Validation) > 0 && !useCaseConfig.Validation.Enabled {
			useCaseConfig.Validation.Enabled = true
		}
	}
	
	// Process interface business methods
	for i, method := range useCaseConfig.Interface.BusinessMethods {
		// Enable auto-detect conversions by default
		if !method.Conversions.AutoDetect {
			useCaseConfig.Interface.BusinessMethods[i].Conversions.AutoDetect = true
		}
	}
	
	return useCaseConfig
}
