# Python FastAPI SQLModel Template System

## Project Mission

Create a **general-purpose template system** for generating Python FastAPI + SQLModel backend applications with
hexagonal architecture. This reusable infrastructure enables rapid development of any type of backend application
through YAML-driven domain configuration.

## Core Objectives

### 1. Template System Infrastructure

- **FastAPI hexagonal architecture template** with clean layer separation
- **Python-based code generation tool** (equivalent to Go's cmd/standardize)
- **Template engine** supporting {{DOMAIN}} placeholder replacement
- **Code preservation system** for custom business logic retention
- **YAML configuration processing** for domain definition

### 2. Domain-Agnostic Architecture

- **Hexagonal architecture patterns** for any business domain
- **SQLModel schema generation** with relationships
- **Repository pattern** implementation templates
- **Use case layer** templates for business logic
- **FastAPI handler** templates with proper error handling

### 3. Code Generation Capabilities

- **Domain configuration** via YAML files
- **Template processing** with Python-based engine
- **File generation** with placeholder replacement
- **Custom code preservation** during regeneration
- **Validation** of generated code structure

## Project Context

### Reference Architecture

- **Go Template System**: `/templates/projects/go_backend_gorm/` - sophisticated hexagonal architecture
- **Code Generation Tool**: `cmd/standardize/` with YAML configuration processing
- **Template Framework**: `{{DOMAIN}}` placeholders with custom code preservation
- **Architecture Layers**: entity → model → repository → usecase → handler

### Target Applications

- **General Purpose**: Any Python backend application domain
- **Test Case**: Riskbook financial platform (first real-world validation)
- **Future Use**: Any team can use templates for their specific domains
- **Scalability**: Support simple to complex domain models

## Success Criteria

### Template System Validation

- ✅ Generate working FastAPI application from YAML configuration
- ✅ Support multiple domain entities with relationships
- ✅ Preserve custom code during template regeneration
- ✅ Clean hexagonal architecture separation
- ✅ Comprehensive documentation and examples

### Real-World Testing

- ✅ Generate complex domain applications (e.g., Riskbook)
- ✅ Support various business logic complexities
- ✅ Maintain performance for production workloads
- ✅ Enable rapid development cycles
- ✅ Lessons learned improve template system

## Quality Standards

### Code Generation Quality

- **Reliability**: Consistent, repeatable generation
- **Flexibility**: Support various domain complexities
- **Maintainability**: Clean, readable generated code
- **Documentation**: Auto-generated API docs and guides

### Architecture Quality

- **Separation of Concerns**: Clear hexagonal layers
- **Testability**: Generated code supports comprehensive testing
- **Extensibility**: Easy to add custom business logic
- **Performance**: Optimized for production workloads

## Project Scope

### In Scope

- ✅ General-purpose Python backend template system
- ✅ FastAPI + SQLModel + PostgreSQL stack
- ✅ Hexagonal architecture implementation
- ✅ YAML-driven domain configuration
- ✅ Code generation and preservation tools

### Out of Scope

- ❌ Domain-specific business logic (e.g., financial calculations)
- ❌ Frontend template generation
- ❌ Deployment infrastructure templates
- ❌ Specific industry patterns (but should support them)

## Timeline

### Template Foundation

- Template system architecture and directory structure
- Python code generation tool implementation
- Basic template files with {{DOMAIN}} placeholders
- YAML configuration processing

### Advanced Features

- Code preservation system
- Relationship handling in templates
- Comprehensive template library
- Documentation and examples

### Validation & Refinement

- Generate real-world application using templates
- Performance testing and optimization
- Template improvements based on usage feedback
- Production readiness validation