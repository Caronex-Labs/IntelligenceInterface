# GoHex Backend Makefile

.PHONY: help build run test lint clean dev docker

# Variables
APP_NAME=api
BINARY_NAME=bin/$(APP_NAME)
DOCKER_IMAGE=gohex-backend
GO_FILES=$(shell find . -name "*.go" -type f)

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development commands
build: ## Build the application
	@echo "Building $(APP_NAME)..."
	@mkdir -p bin
	@go build -o $(BINARY_NAME) cmd/api/main.go

run: ## Run the application
	@echo "Running $(APP_NAME)..."
	@go run cmd/api/main.go

dev: ## Run the application in development mode with live reload
	@echo "Starting development server..."
	@which air > /dev/null || (echo "Installing air..." && go install github.com/cosmtrek/air@latest)
	@air

# Testing commands
test: ## Run all tests
	@echo "Running tests..."
	@go test -v ./...

test-coverage: ## Run tests with coverage
	@echo "Running tests with coverage..."
	@go test -v -coverprofile=coverage.out ./...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	@go test -v ./internal/...

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	@go test -v ./test/integration/...

test-e2e: ## Run end-to-end tests
	@echo "Running e2e tests..."
	@go test -v ./test/e2e/...

# Linting and code quality
lint: ## Run GoHex entity linter
	@echo "Running GoHex entity linter..."
	@go run cmd/lint/main.go --path .

lint-verbose: ## Run GoHex entity linter with verbose output
	@echo "Running GoHex entity linter (verbose)..."
	@go run cmd/lint/main.go --path . --verbose

lint-go: ## Run standard Go linters
	@echo "Running golangci-lint..."
	@which golangci-lint > /dev/null || (echo "Installing golangci-lint..." && go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest)
	@golangci-lint run

lint-all: lint lint-go ## Run all linters

# Code formatting
fmt: ## Format Go code
	@echo "Formatting code..."
	@go fmt ./...

fmt-check: ## Check if code is formatted
	@echo "Checking code formatting..."
	@test -z "$$(gofmt -l .)" || (echo "Code is not formatted. Run 'make fmt'" && exit 1)

# Dependency management
deps: ## Download dependencies
	@echo "Downloading dependencies..."
	@go mod download

deps-update: ## Update dependencies
	@echo "Updating dependencies..."
	@go get -u ./...
	@go mod tidy

deps-verify: ## Verify dependencies
	@echo "Verifying dependencies..."
	@go mod verify

# Database commands
db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	@go run cmd/migrate/main.go up

db-migrate-down: ## Rollback database migrations
	@echo "Rolling back database migrations..."
	@go run cmd/migrate/main.go down

db-reset: ## Reset database (drop and recreate)
	@echo "Resetting database..."
	@go run cmd/migrate/main.go reset

# Code generation
generate: ## Run GoHex code generation
	@echo "Running code generation..."
	@go run cmd/engine/main.go generate

generate-domain: ## Generate code for specific domain (usage: make generate-domain DOMAIN=user)
	@echo "Generating code for domain: $(DOMAIN)"
	@go run cmd/engine/main.go --domain $(DOMAIN) domain

generate-entity: ## Generate code for specific entity (usage: make generate-entity DOMAIN=user ENTITY=User)
	@echo "Generating code for entity: $(ENTITY) in domain: $(DOMAIN)"
	@go run cmd/engine/main.go --domain $(DOMAIN) --entity $(ENTITY) entity

generate-dry-run: ## Preview code generation without creating files
	@echo "Previewing code generation..."
	@go run cmd/engine/main.go --dry-run --verbose generate

# Docker commands
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	@docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run application in Docker
	@echo "Running application in Docker..."
	@docker run -p 8080:8080 --env-file .env $(DOCKER_IMAGE)

docker-compose-up: ## Start services with docker-compose
	@echo "Starting services with docker-compose..."
	@docker-compose up -d

docker-compose-down: ## Stop services with docker-compose
	@echo "Stopping services with docker-compose..."
	@docker-compose down

# Cleanup commands
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf bin/
	@rm -f coverage.out coverage.html
	@go clean

clean-deps: ## Clean module cache
	@echo "Cleaning module cache..."
	@go clean -modcache

# Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	@which godoc > /dev/null || (echo "Installing godoc..." && go install golang.org/x/tools/cmd/godoc@latest)
	@echo "Documentation server will be available at http://localhost:6060"
	@godoc -http=:6060

# Security
security-scan: ## Run security scan
	@echo "Running security scan..."
	@which gosec > /dev/null || (echo "Installing gosec..." && go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest)
	@gosec ./...

# Performance
benchmark: ## Run benchmarks
	@echo "Running benchmarks..."
	@go test -bench=. -benchmem ./...

# Validation commands
validate: fmt-check lint-all test ## Run all validation checks (format, lint, test)

validate-ci: deps-verify fmt-check lint-all test security-scan ## Run CI validation pipeline

# Development setup
setup: ## Setup development environment
	@echo "Setting up development environment..."
	@go mod download
	@cp env.example .env
	@echo "Development environment setup complete!"
	@echo "Please edit .env file with your configuration"

# Project initialization
init-project: ## Initialize a new project (usage: make init-project NAME=my-service)
	@echo "Initializing new project: $(NAME)"
	@go run cmd/engine/main.go init --name $(NAME)

# API documentation
api-docs: ## Generate API documentation (OpenAPI/Swagger)
	@echo "Generating API documentation..."
	@which swag > /dev/null || (echo "Installing swag..." && go install github.com/swaggo/swag/cmd/swag@latest)
	@swag init -g cmd/api/main.go -o docs/

# Health check
health: ## Check application health
	@echo "Checking application health..."
	@curl -f http://localhost:8080/health || echo "Application is not running or health check failed"

# Load testing
load-test: ## Run load tests (requires artillery or similar tool)
	@echo "Running load tests..."
	@which artillery > /dev/null || (echo "Please install artillery: npm install -g artillery" && exit 1)
	@artillery run test/load/basic-load-test.yml

# Git hooks
install-hooks: ## Install git hooks
	@echo "Installing git hooks..."
	@cp scripts/pre-commit.sh .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed successfully"

# Environment specific commands
run-prod: ## Run in production mode
	@echo "Running in production mode..."
	@export ENV=production && go run cmd/api/main.go

run-staging: ## Run in staging mode
	@echo "Running in staging mode..."
	@export ENV=staging && go run cmd/api/main.go

# Monitoring
logs: ## Show application logs (requires running application)
	@echo "Showing application logs..."
	@docker logs -f gohex-backend 2>/dev/null || echo "Application container not found"

# Quick development workflow
quick-check: fmt lint test ## Quick development check (format, lint, test)

# Complete workflow
full-check: clean deps validate-ci ## Complete validation workflow

# Help for make variables
vars: ## Show available make variables
	@echo "Available variables:"
	@echo "  APP_NAME     - Application name (default: api)"
	@echo "  DOMAIN       - Domain for code generation"
	@echo "  ENTITY       - Entity for code generation" 
	@echo "  NAME         - Project name for initialization"
	@echo ""
	@echo "Usage examples:"
	@echo "  make generate-domain DOMAIN=user"
	@echo "  make generate-entity DOMAIN=user ENTITY=Profile"
	@echo "  make init-project NAME=my-awesome-service"

# Check if required tools are installed
check-tools: ## Check if required development tools are installed
	@echo "Checking required tools..."
	@which go > /dev/null || (echo "❌ Go is not installed" && exit 1)
	@echo "✅ Go is installed"
	@which docker > /dev/null || echo "⚠️ Docker is not installed (optional)"
	@which docker-compose > /dev/null || echo "⚠️ Docker Compose is not installed (optional)"
	@echo "Tool check complete"
