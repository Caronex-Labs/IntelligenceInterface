package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// LintResult represents a linting issue
type LintResult struct {
	File        string
	Line        int
	Column      int
	Severity    string // "error", "warning", "info"
	Message     string
	Rule        string
	Suggestion  string
}

// EntityInfo holds information about an entity
type EntityInfo struct {
	Name          string // PascalCase (e.g., "User")
	NameSnake     string // snake_case (e.g., "user")
	NamePlural    string // PascalCase plural (e.g., "Users")
	NamePluralSnake string // snake_case plural (e.g., "users")
	Domain        string // Domain name
	DomainSnake   string // Domain name in snake_case
	FilePath      string // Where the entity was found
}

// Linter performs entity naming consistency checks
type Linter struct {
	entities map[string]*EntityInfo
	results  []LintResult
	verbose  bool
}

var (
	pathFlag    = flag.String("path", ".", "Path to scan for Go files")
	verboseFlag = flag.Bool("verbose", false, "Verbose output")
	fixFlag     = flag.Bool("fix", false, "Attempt to fix issues automatically")
	formatFlag  = flag.String("format", "text", "Output format: text, json, checkstyle")
)

func main() {
	flag.Parse()

	linter := &Linter{
		entities: make(map[string]*EntityInfo),
		results:  []LintResult{},
		verbose:  *verboseFlag,
	}

	if err := linter.Run(*pathFlag); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Output results
	if err := linter.OutputResults(*formatFlag); err != nil {
		fmt.Printf("Error outputting results: %v\n", err)
		os.Exit(1)
	}

	// Exit with error code if issues found
	if linter.HasErrors() {
		os.Exit(1)
	}
}

// Run executes the linter on the given path
func (l *Linter) Run(rootPath string) error {
	// Phase 1: Discover entities
	if err := l.discoverEntities(rootPath); err != nil {
		return fmt.Errorf("failed to discover entities: %w", err)
	}

	if l.verbose {
		fmt.Printf("Discovered %d entities:\n", len(l.entities))
		for name, entity := range l.entities {
			fmt.Printf("  %s (%s) in domain %s\n", name, entity.NameSnake, entity.Domain)
		}
		fmt.Println()
	}

	// Phase 2: Check naming consistency across layers
	if err := l.checkNamingConsistency(rootPath); err != nil {
		return fmt.Errorf("failed to check naming consistency: %w", err)
	}

	return nil
}

// discoverEntities scans for entity template definitions
func (l *Linter) discoverEntities(rootPath string) error {
	entityPath := filepath.Join(rootPath, "internal", "core", "entity")
	if _, err := os.Stat(entityPath); os.IsNotExist(err) {
		return nil // No entities directory
	}

	return filepath.Walk(entityPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Only check template files (.tmpl)
		if !strings.HasSuffix(path, ".tmpl") {
			return nil
		}

		return l.parseTemplateFile(path)
	})
}

// parseTemplateFile parses a Go template file looking for entity patterns
func (l *Linter) parseTemplateFile(filePath string) error {
	src, err := os.ReadFile(filePath)
	if err != nil {
		return err
	}

	// Extract domain from path (e.g., internal/core/entity/{{DOMAIN}}/entity.go.tmpl -> {{DOMAIN}})
	parts := strings.Split(filePath, string(os.PathSeparator))
	for i, part := range parts {
		if part == "entity" && i+1 < len(parts) {
			// domain = parts[i+1] // This will be "{{DOMAIN}}" in templates
			break
		}
	}

	// For template files, we create a standardized entity for validation
	// We use "Entity" as the standard entity name since templates use {{.Entity}}
	entity := &EntityInfo{
		Name:            "Entity",           // Standard template placeholder
		NameSnake:       "entity",          // Standard template placeholder
		NamePlural:      "Entities",        // Standard template placeholder
		NamePluralSnake: "entities",        // Standard template placeholder
		Domain:          "Domain",          // Standard template placeholder
		DomainSnake:     "domain",          // Standard template placeholder
		FilePath:        filePath,
	}
	
	// Check if this template file contains entity-like patterns
	content := string(src)
	if l.isEntityTemplate(content) {
		l.entities["Entity"] = entity
		
		if l.verbose {
			fmt.Printf("Found entity template: %s\n", filePath)
		}
	}

	return nil
}

// isEntityTemplate checks if a template contains entity-like patterns
func (l *Linter) isEntityTemplate(content string) bool {
	// Check for common entity template patterns
	hasEntityRef := strings.Contains(content, "{{.Entity}}")
	hasIDField := strings.Contains(content, "ID") && (strings.Contains(content, "uuid.UUID") || strings.Contains(content, "UUID"))
	hasTimestamps := strings.Contains(content, "CreatedAt") && strings.Contains(content, "UpdatedAt")
	
	return hasEntityRef && hasIDField && hasTimestamps
}

// checkNamingConsistency verifies naming consistency across all layers
func (l *Linter) checkNamingConsistency(rootPath string) error {
	for _, entity := range l.entities {
		// Check repository layer
		l.checkRepositoryNaming(rootPath, entity)
		
		// Check usecase layer
		l.checkUseCaseNaming(rootPath, entity)
		
		// Check handler layer
		l.checkHandlerNaming(rootPath, entity)
		
		// Check DI layer
		l.checkDINaming(rootPath, entity)
		
		// Check model layer
		l.checkModelNaming(rootPath, entity)
	}

	return nil
}

// checkRepositoryNaming checks repository template naming consistency
func (l *Linter) checkRepositoryNaming(rootPath string, entity *EntityInfo) {
	repoPath := filepath.Join(rootPath, "internal", "repository", "{{DOMAIN}}")
	
	// Check repository implementation template file
	repoFile := filepath.Join(repoPath, "repository.go.tmpl")
	if err := l.checkFileNaming(repoFile, entity, "repository"); err == nil {
		l.checkRepositoryContent(repoFile, entity)
	}
	
	// Check repositories registration template file
	regFile := filepath.Join(repoPath, "repositories.go.tmpl")
	if err := l.checkFileNaming(regFile, entity, "repository_registration"); err == nil {
		l.checkRepositoryRegistration(regFile, entity)
	}
}

// checkUseCaseNaming checks usecase template naming consistency
func (l *Linter) checkUseCaseNaming(rootPath string, entity *EntityInfo) {
	usecasePath := filepath.Join(rootPath, "internal", "usecase", "{{DOMAIN}}")
	
	// Check usecase implementation template file
	usecaseFile := filepath.Join(usecasePath, "usecase.go.tmpl")
	if err := l.checkFileNaming(usecaseFile, entity, "usecase"); err == nil {
		l.checkUseCaseContent(usecaseFile, entity)
	}
	
	// Check usecases registration template file
	regFile := filepath.Join(usecasePath, "usecases.go.tmpl")
	if err := l.checkFileNaming(regFile, entity, "usecase_registration"); err == nil {
		l.checkUseCaseRegistration(regFile, entity)
	}
}

// checkHandlerNaming checks handler template naming consistency
func (l *Linter) checkHandlerNaming(rootPath string, entity *EntityInfo) {
	handlerPath := filepath.Join(rootPath, "internal", "interface", "http", "handlers", "{{DOMAIN}}")
	
	// Check handler implementation template file
	handlerFile := filepath.Join(handlerPath, "handler.go.tmpl")
	if err := l.checkFileNaming(handlerFile, entity, "handler"); err == nil {
		l.checkHandlerContent(handlerFile, entity)
	}
	
	// Check handlers registration template file
	regFile := filepath.Join(handlerPath, "handlers.go.tmpl")
	if err := l.checkFileNaming(regFile, entity, "handler_registration"); err == nil {
		l.checkHandlerRegistration(regFile, entity)
	}
}

// checkDINaming checks DI template naming consistency
func (l *Linter) checkDINaming(rootPath string, entity *EntityInfo) {
	diPath := filepath.Join(rootPath, "internal", "di", "{{DOMAIN}}")
	diFile := filepath.Join(diPath, "di.go.tmpl")
	
	if err := l.checkFileNaming(diFile, entity, "di"); err == nil {
		l.checkDIContent(diFile, entity)
	}
}

// checkModelNaming checks model template naming consistency
func (l *Linter) checkModelNaming(rootPath string, entity *EntityInfo) {
	modelPath := filepath.Join(rootPath, "internal", "core", "models", "{{DOMAIN}}")
	modelFile := filepath.Join(modelPath, "model.go.tmpl")
	
	if err := l.checkFileNaming(modelFile, entity, "model"); err == nil {
		l.checkModelContent(modelFile, entity)
	}
}

// checkFileNaming verifies that expected files exist
func (l *Linter) checkFileNaming(filePath string, entity *EntityInfo, layer string) error {
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		l.addResult(LintResult{
			File:     filePath,
			Severity: "error",
			Message:  fmt.Sprintf("Missing %s file for entity %s", layer, entity.Name),
			Rule:     "missing-file",
			Suggestion: fmt.Sprintf("Generate %s file for entity %s", layer, entity.Name),
		})
		return err
	}
	return nil
}

// checkRepositoryContent checks repository template content for naming consistency
func (l *Linter) checkRepositoryContent(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `type\s+I\{\{\.Entity\}\}Repository\s+interface`, Required: true, Message: "Repository interface should use {{.Entity}} template variable"},
		{Pattern: `type\s+\{\{\.Entity\}\}Repository\s+struct`, Required: true, Message: "Repository struct should use {{.Entity}} template variable"},
		{Pattern: `func\s+New\{\{\.Entity\}\}Repository`, Required: true, Message: "Repository constructor should use {{.Entity}} template variable"},
		{Pattern: `func\s+\([^)]*\)\s+Create\s*\(`, Required: true, Message: "Repository should have Create method"},
		{Pattern: `func\s+\([^)]*\)\s+GetByID\s*\(`, Required: true, Message: "Repository should have GetByID method"},
		{Pattern: `func\s+\([^)]*\)\s+List\s*\(`, Required: true, Message: "Repository should have List method"},
		{Pattern: `func\s+\([^)]*\)\s+Update\s*\(`, Required: true, Message: "Repository should have Update method"},
		{Pattern: `func\s+\([^)]*\)\s+Delete\s*\(`, Required: true, Message: "Repository should have Delete method"},
	})
}

// checkUseCaseContent checks usecase template content for naming consistency
func (l *Linter) checkUseCaseContent(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `type\s+I\{\{\.Entity\}\}UseCase\s+interface`, Required: true, Message: "UseCase interface should use {{.Entity}} template variable"},
		{Pattern: `type\s+\{\{\.Entity\}\}UseCase\s+struct`, Required: true, Message: "UseCase struct should use {{.Entity}} template variable"},
		{Pattern: `func\s+New\{\{\.Entity\}\}UseCase`, Required: true, Message: "UseCase constructor should use {{.Entity}} template variable"},
		{Pattern: `\{\{\.EntitySnake\}\}Repo\s+repoPkg\.I\{\{\.Entity\}\}Repository`, Required: true, Message: "UseCase should use template variables for repository field"},
	})
}

// checkHandlerContent checks handler template content for naming consistency
func (l *Linter) checkHandlerContent(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `type\s+Handler\s+struct`, Required: true, Message: "Handler struct should exist"},
		{Pattern: `func\s+NewHandler`, Required: true, Message: "Handler constructor should be named NewHandler"},
		{Pattern: `{{\.EntitySnake}}UseCase\s+usecasePkg\.I{{\.Entity}}UseCase`, Required: true, Message: "Handler should use template variables for usecase field"},
		{Pattern: `func\s+\([^)]*\)\s+handle{{\.Entities}}\s*\(`, Required: true, Message: "Handler should use {{.Entities}} template variable for collection method"},
		{Pattern: `func\s+\([^)]*\)\s+handle{{\.Entity}}ByID\s*\(`, Required: true, Message: "Handler should use {{.Entity}} template variable for item method"},
		{Pattern: `/api/v1/{{\.EntitiesSnake}}`, Required: true, Message: "Handler should use {{.EntitiesSnake}} template variable for routes"},
	})
}

// checkModelContent checks model template content for naming consistency
func (l *Linter) checkModelContent(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `type\s+{{\.Entity}}\s+struct`, Required: true, Message: "Model struct should use {{.Entity}} template variable"},
		{Pattern: `func\s+\({{\.Entity}}\)\s+TableName\s*\(\s*\)\s+string`, Required: true, Message: "Model should have TableName method with correct receiver"},
		{Pattern: `return\s+"{{\.EntitiesSnake}}"`, Required: true, Message: "TableName should return {{.EntitiesSnake}} template variable"},
		{Pattern: `func\s+\([^)]*\)\s+BeforeCreate\s*\(\s*\)\s+error`, Required: true, Message: "Model should have BeforeCreate method"},
	})
}

// checkDIContent checks DI template content for naming consistency
func (l *Linter) checkDIContent(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `func\s+Register{{\.Domain}}\s*\(`, Required: true, Message: "DI should use {{.Domain}} template variable for function name"},
		{Pattern: `repositoryPkg\.Register{{\.Entity}}Repository\(injector\)`, Required: true, Message: "DI should use {{.Entity}} template variable for repository registration"},
		{Pattern: `usecasePkg\.Register{{\.Entity}}UseCase\(injector\)`, Required: true, Message: "DI should use {{.Entity}} template variable for usecase registration"},
		{Pattern: `handlersPkg\.Register{{\.Entity}}Handler\(injector\)`, Required: true, Message: "DI should use {{.Entity}} template variable for handler registration"},
	})
}

// checkRepositoryRegistration checks repository registration template
func (l *Linter) checkRepositoryRegistration(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `func\s+Register\{\{\.Entity\}\}Repository\s*\(`, Required: true, Message: "Should use {{.Entity}} template variable for registration function"},
		{Pattern: `do\.Provide\(injector,\s*New\{\{\.Entity\}\}Repository\)`, Required: true, Message: "Should use {{.Entity}} template variable for constructor"},
		{Pattern: `register_\{\{\.EntitySnake\}\}_repository`, Required: true, Message: "Should use {{.EntitySnake}} template variable for callback name"},
	})
}

// checkUseCaseRegistration checks usecase registration template
func (l *Linter) checkUseCaseRegistration(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `func\s+Register{{\.Entity}}UseCase\s*\(`, Required: true, Message: "Should use {{.Entity}} template variable for registration function"},
		{Pattern: `do\.Provide\(injector,\s*New{{\.Entity}}UseCase\)`, Required: true, Message: "Should use {{.Entity}} template variable for constructor"},
		{Pattern: `register_{{\.EntitySnake}}_usecase`, Required: true, Message: "Should use {{.EntitySnake}} template variable for callback name"},
	})
}

// checkHandlerRegistration checks handler registration template
func (l *Linter) checkHandlerRegistration(filePath string, entity *EntityInfo) {
	l.checkFileContent(filePath, entity, []NamePattern{
		{Pattern: `func\s+Register{{\.Entity}}Handler\s*\(`, Required: true, Message: "Should use {{.Entity}} template variable for registration function"},
		{Pattern: `do\.Provide\(injector,\s*NewHandler\)`, Required: true, Message: "Should register NewHandler constructor"},
		{Pattern: `register_{{\.EntitySnake}}_handler`, Required: true, Message: "Should use {{.EntitySnake}} template variable for callback name"},
	})
}

// NamePattern represents a pattern to check in file content
type NamePattern struct {
	Pattern  string
	Required bool
	Message  string
}

// checkFileContent checks file content against patterns
func (l *Linter) checkFileContent(filePath string, entity *EntityInfo, patterns []NamePattern) {
	content, err := os.ReadFile(filePath)
	if err != nil {
		l.addResult(LintResult{
			File:     filePath,
			Severity: "error", 
			Message:  fmt.Sprintf("Could not read file: %v", err),
			Rule:     "file-read-error",
		})
		return
	}

	contentStr := string(content)
	lines := strings.Split(contentStr, "\n")

	for _, pattern := range patterns {
		regex, err := regexp.Compile(pattern.Pattern)
		if err != nil {
			l.addResult(LintResult{
				File:     filePath,
				Severity: "error",
				Message:  fmt.Sprintf("Invalid regex pattern: %s", pattern.Pattern),
				Rule:     "invalid-regex",
			})
			continue
		}

		found := false
		for _, line := range lines {
			if regex.MatchString(line) {
				found = true
				break
			}
		}

		if pattern.Required && !found {
			l.addResult(LintResult{
				File:     filePath,
				Line:     1,
				Severity: "error",
				Message:  pattern.Message,
				Rule:     "naming-consistency",
				Suggestion: fmt.Sprintf("Ensure pattern '%s' exists in file", pattern.Pattern),
			})
		}
	}
}

// addResult adds a lint result
func (l *Linter) addResult(result LintResult) {
	l.results = append(l.results, result)
}

// HasErrors returns true if any errors were found
func (l *Linter) HasErrors() bool {
	for _, result := range l.results {
		if result.Severity == "error" {
			return true
		}
	}
	return false
}

// OutputResults outputs results in the specified format
func (l *Linter) OutputResults(format string) error {
	switch format {
	case "json":
		return l.outputJSON()
	case "checkstyle":
		return l.outputCheckstyle()
	default:
		return l.outputText()
	}
}

// outputText outputs results in human-readable format
func (l *Linter) outputText() error {
	if len(l.results) == 0 {
		fmt.Println("✅ No issues found!")
		return nil
	}

	errorCount := 0
	warningCount := 0

	for _, result := range l.results {
		switch result.Severity {
		case "error":
			errorCount++
			fmt.Printf("❌ %s:%d:%d: %s [%s]\n", result.File, result.Line, result.Column, result.Message, result.Rule)
		case "warning":
			warningCount++
			fmt.Printf("⚠️  %s:%d:%d: %s [%s]\n", result.File, result.Line, result.Column, result.Message, result.Rule)
		case "info":
			fmt.Printf("ℹ️  %s:%d:%d: %s [%s]\n", result.File, result.Line, result.Column, result.Message, result.Rule)
		}
		
		if result.Suggestion != "" {
			fmt.Printf("   💡 %s\n", result.Suggestion)
		}
	}

	fmt.Printf("\nSummary: %d errors, %d warnings\n", errorCount, warningCount)
	return nil
}

// outputJSON outputs results in JSON format
func (l *Linter) outputJSON() error {
	// Implementation would output JSON format
	fmt.Printf("JSON output not yet implemented\n")
	return nil
}

// outputCheckstyle outputs results in Checkstyle XML format
func (l *Linter) outputCheckstyle() error {
	// Implementation would output Checkstyle XML format
	fmt.Printf("Checkstyle output not yet implemented\n")
	return nil
}

// String manipulation utility functions
func toSnakeCase(s string) string {
	var result strings.Builder
	for i, r := range s {
		if i > 0 && (r >= 'A' && r <= 'Z') {
			result.WriteRune('_')
		}
		result.WriteRune(r | 32) // Convert to lowercase
	}
	return result.String()
}

func toPascalCase(s string) string {
	var result strings.Builder
	nextUpper := true
	for _, r := range s {
		if r == '_' || r == '-' || r == ' ' {
			nextUpper = true
		} else if nextUpper {
			result.WriteRune(r &^ 32) // Convert to uppercase
			nextUpper = false
		} else {
			result.WriteRune(r)
		}
	}
	return result.String()
}

func pluralize(s string) string {
	if strings.HasSuffix(s, "s") || strings.HasSuffix(s, "x") || strings.HasSuffix(s, "z") ||
		strings.HasSuffix(s, "ch") || strings.HasSuffix(s, "sh") {
		return s + "es"
	}
	if strings.HasSuffix(s, "y") && len(s) > 1 {
		return s[:len(s)-1] + "ies"
	}
	if strings.HasSuffix(s, "f") {
		return s[:len(s)-1] + "ves"
	}
	if strings.HasSuffix(s, "fe") {
		return s[:len(s)-2] + "ves"
	}
	return s + "s"
}
