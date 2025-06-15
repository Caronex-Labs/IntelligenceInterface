package internal

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"text/template"
)

// TemplateGenerator handles code generation from templates
type TemplateGenerator struct{}

// NewTemplateGenerator creates a new template generator
func NewTemplateGenerator() *TemplateGenerator {
	return &TemplateGenerator{}
}

// GenerateEntityFiles generates entity files using configuration
func (tg *TemplateGenerator) GenerateEntityFiles(data TemplateData, useConfig bool) error {
	var templatePath string
	if useConfig {
		templatePath = filepath.Join("internal", "core", "entity", "{{DOMAIN}}", "entity_config.go.tmpl")
	} else {
		templatePath = filepath.Join("internal", "core", "entity", "{{DOMAIN}}", "entity.go.tmpl")
	}
	
	outputPath := filepath.Join("internal", "core", "entity", data.DomainSnake, fmt.Sprintf("%s.go", data.EntitySnake))
	return tg.generateFile(templatePath, outputPath, data)
}

// GenerateModelFiles generates model files
func (tg *TemplateGenerator) GenerateModelFiles(data TemplateData) error {
	templatePath := filepath.Join("internal", "core", "models", "{{DOMAIN}}", "model.go.tmpl")
	outputPath := filepath.Join("internal", "core", "models", data.DomainSnake, fmt.Sprintf("%s.go", data.EntitySnake))
	return tg.generateFile(templatePath, outputPath, data)
}

// GenerateRepositoryFiles generates repository files
func (tg *TemplateGenerator) GenerateRepositoryFiles(data TemplateData, useConfig bool) error {
	// Generate repository implementation
	var templatePath string
	if useConfig {
		templatePath = filepath.Join("internal", "repository", "{{DOMAIN}}", "repository_config.go.tmpl")
	} else {
		templatePath = filepath.Join("internal", "repository", "{{DOMAIN}}", "repository.go.tmpl")
	}
	
	outputPath := filepath.Join("internal", "repository", data.DomainSnake, fmt.Sprintf("%s_repository.go", data.EntitySnake))
	if err := tg.generateFile(templatePath, outputPath, data); err != nil {
		return err
	}

	// Generate repository registration
	templatePath = filepath.Join("internal", "repository", "{{DOMAIN}}", "repositories.go.tmpl")
	outputPath = filepath.Join("internal", "repository", data.DomainSnake, "repositories.go")
	return tg.generateFile(templatePath, outputPath, data)
}

// GenerateUseCaseFiles generates use case files
func (tg *TemplateGenerator) GenerateUseCaseFiles(data TemplateData, useConfig bool) error {
	// Generate usecase implementation
	var templatePath string
	if useConfig {
		templatePath = filepath.Join("internal", "usecase", "{{DOMAIN}}", "usecase_config.go.tmpl")
	} else {
		templatePath = filepath.Join("internal", "usecase", "{{DOMAIN}}", "usecase.go.tmpl")
	}
	
	outputPath := filepath.Join("internal", "usecase", data.DomainSnake, fmt.Sprintf("%s_usecase.go", data.EntitySnake))
	if err := tg.generateFile(templatePath, outputPath, data); err != nil {
		return err
	}

	// Generate usecase registration
	templatePath = filepath.Join("internal", "usecase", "{{DOMAIN}}", "usecases.go.tmpl")
	outputPath = filepath.Join("internal", "usecase", data.DomainSnake, "usecases.go")
	return tg.generateFile(templatePath, outputPath, data)
}

// GenerateHandlerFiles generates handler files
func (tg *TemplateGenerator) GenerateHandlerFiles(data TemplateData) error {
	templatePath := filepath.Join("internal", "interface", "http", "handlers", "{{DOMAIN}}", "handler.go.tmpl")
	outputPath := filepath.Join("internal", "interface", "http", "handlers", data.DomainSnake, fmt.Sprintf("%s.go", data.EntitySnake))
	return tg.generateFile(templatePath, outputPath, data)
}

// GenerateDIFiles generates dependency injection files
func (tg *TemplateGenerator) GenerateDIFiles(data TemplateData) error {
	templatePath := filepath.Join("internal", "di", "{{DOMAIN}}", "di.go.tmpl")
	outputPath := filepath.Join("internal", "di", data.DomainSnake, "di.go")
	return tg.generateFile(templatePath, outputPath, data)
}

// GenerateAllFiles generates all files for a domain
func (tg *TemplateGenerator) GenerateAllFiles(data TemplateData, useConfig bool) error {
	if err := tg.GenerateEntityFiles(data, useConfig); err != nil {
		return fmt.Errorf("failed to generate entity files: %w", err)
	}
	if err := tg.GenerateModelFiles(data); err != nil {
		return fmt.Errorf("failed to generate model files: %w", err)
	}
	if err := tg.GenerateRepositoryFiles(data, useConfig); err != nil {
		return fmt.Errorf("failed to generate repository files: %w", err)
	}
	if err := tg.GenerateUseCaseFiles(data, useConfig); err != nil {
		return fmt.Errorf("failed to generate use case files: %w", err)
	}
	if err := tg.GenerateHandlerFiles(data); err != nil {
		return fmt.Errorf("failed to generate handler files: %w", err)
	}
	if err := tg.GenerateDIFiles(data); err != nil {
		return fmt.Errorf("failed to generate DI files: %w", err)
	}
	return nil
}

// generateFile generates a file from a template
func (tg *TemplateGenerator) generateFile(templatePath, outputPath string, data TemplateData) error {
	// Check if template file exists
	if _, err := os.Stat(templatePath); os.IsNotExist(err) {
		return fmt.Errorf("template file does not exist: %s", templatePath)
	}

	// Read template file
	templateContent, err := os.ReadFile(templatePath)
	if err != nil {
		return fmt.Errorf("failed to read template file: %w", err)
	}

	// Parse template with custom functions
	tmpl, err := template.New(filepath.Base(templatePath)).
		Funcs(template.FuncMap{
			"default": func(defaultVal, val string) string {
				if val == "" {
					return defaultVal
				}
				return val
			},
			"printf":        fmt.Sprintf,
			"toSnakeCase":   ToSnakeCase,
			"toPascalCase":  ToPascalCase,
			"pluralize":     Pluralize,
			"contains":      strings.Contains,
			"eq":            func(a, b interface{}) bool { return a == b },
			"ne":            func(a, b interface{}) bool { return a != b },
		}).
		Parse(string(templateContent))
	if err != nil {
		return fmt.Errorf("failed to parse template: %w", err)
	}

	// Create output directory if it doesn't exist
	outputDir := filepath.Dir(outputPath)
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %w", err)
	}

	// Create output file
	outputFile, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("failed to create output file: %w", err)
	}
	defer outputFile.Close()

	// Execute template
	if err := tmpl.Execute(outputFile, data); err != nil {
		return fmt.Errorf("failed to execute template: %w", err)
	}

	fmt.Printf("Generated %s\n", outputPath)
	return nil
}
