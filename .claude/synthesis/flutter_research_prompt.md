# Flutter Synthesis Engine Research Prompt

## Context and Purpose

We are building a **synthesis system** - a configuration-driven code generation platform that creates complete, production-ready applications from minimal YAML configuration. We have successfully implemented this for Go backend applications using Go's `text/template` engine, and now need to extend this capability to Flutter mobile applications.

### Synthesis System Overview
- **Input**: 10-20 lines of YAML configuration describing business requirements
- **Output**: Complete, production-ready application with proper architecture
- **Key Feature**: Configuration-driven code generation with smart defaults
- **Preservation**: Custom code regions are preserved during regeneration cycles

### Current Go Implementation Success
Our Go backend synthesis engine generates:
- Complete hexagonal architecture (entity, repository, usecase, handler layers)
- Type-safe interfaces across all layers
- Database models with GORM integration
- HTTP API endpoints with proper validation
- Dependency injection wiring
- Basic test structures

### Flutter Golden Repository Goals
Create a Flutter equivalent that generates:
- Complete Flutter application structure
- BLoC architecture foundation (without specific implementation details)
- State management patterns
- Navigation and routing
- Data layer and API integration
- UI components and screens
- Testing infrastructure

## Technical Requirements

### Core Generation System Requirements
1. **Configuration-Driven**: YAML configuration files that describe the desired Flutter app
2. **Multi-Layer Generation**: Generate coordinated code across multiple architectural layers
3. **Code Preservation**: Ability to regenerate code while preserving custom modifications
4. **Type Safety**: Maintain Dart's strong typing across generated components
5. **Flutter Best Practices**: Generated code must follow Flutter/Dart conventions
6. **Developer Experience**: Simple workflow for iterative development

### Integration Requirements
- Must integrate with existing synthesis CLI tool (written in Go)
- Should follow the same configuration patterns as Go backend synthesis
- Need to support the same three-tier configuration complexity (minimal/standard/full)
- Must support custom code preservation using comment markers

## Specific Research Areas

### 1. Dart source_gen Fundamentals
**Required Information:**
- How source_gen works for Dart code generation
- Architecture and execution model of source_gen
- Capabilities and limitations compared to template-based generation
- Performance characteristics for large-scale code generation
- Integration with Dart's analyzer for type-safe generation

**Key Questions:**
- Can source_gen generate entire file structures, or just code snippets?
- How does source_gen handle cross-file dependencies and imports?
- What are the best practices for complex, multi-file generation scenarios?
- How does source_gen compare to template-based approaches for our use case?

### 2. build_runner Configuration and Workflow
**Required Information:**
- Complete build_runner setup and configuration
- build.yaml configuration options and patterns
- Development workflow integration (watch mode, incremental builds)
- Integration with IDE/editor tooling
- Performance optimization strategies

**Key Questions:**
- How to configure build_runner for custom, complex generators?
- What's the recommended development workflow for iterative generation?
- How to handle build conflicts and dependency resolution?
- Can build_runner be integrated with external CLI tools?

### 3. Custom Generator Development
**Required Information:**
- Step-by-step guide to creating custom source_gen generators
- Generator architecture patterns and best practices
- Handling complex generation scenarios (multiple files, cross-dependencies)
- Error handling and debugging strategies
- Testing approaches for custom generators

**Key Questions:**
- How to create generators that produce multiple related files?
- What's the recommended pattern for generators that need to coordinate across files?
- How to handle generator dependencies and execution order?
- What tools exist for debugging and testing custom generators?

### 4. Flutter Project Structure for Code Generation
**Required Information:**
- Recommended Flutter project structure for generated code
- Where to place generated files in Flutter conventions
- How to organize generators within a Flutter project
- Integration with existing Flutter tooling and workflows

**Key Questions:**
- What's the recommended directory structure for a generation-heavy Flutter project?
- How to organize generated vs. hand-written code?
- Where should custom generators be located within the project?
- How to handle generated asset management and configuration?

### 5. Annotation-Driven Generation Patterns
**Required Information:**
- Dart annotation system for driving code generation
- Best practices for annotation design
- How to create meaningful, developer-friendly annotations
- Integration patterns between annotations and generators

**Key Questions:**
- How to design annotations that capture business intent rather than technical details?
- What are the patterns for complex, nested annotation structures?
- How to validate annotation parameters and provide helpful error messages?
- Can annotations be used to drive multi-file, coordinated generation?

### 6. pubspec.yaml and Dependency Management
**Required Information:**
- Required dependencies for source_gen and build_runner setup
- Version compatibility considerations
- dev_dependencies vs dependencies for generation tools
- Dependency management best practices for generation-heavy projects

**Key Questions:**
- What are the minimum required dependencies for our use case?
- How to handle version conflicts between generation tools?
- What's the recommended approach for managing generator dependencies?
- Are there any known compatibility issues with common Flutter packages?

### 7. BLoC Architecture Preparation
**Required Information:**
- How to structure generated code to be BLoC-ready without implementing BLoC specifics
- Patterns for generating state management foundation
- Integration points where BLoC implementation can be added later
- Code organization patterns that support BLoC architecture

**Key Questions:**
- What foundation code needs to be generated to support BLoC implementation?
- How to structure generated classes to be easily extended with BLoC patterns?
- What interfaces or abstract classes should be generated for BLoC integration?
- How to organize generated code to support event-driven architecture?

### 8. Code Preservation and Regeneration
**Required Information:**
- Patterns for preserving custom code during regeneration
- How to implement comment-based code preservation in Dart
- Strategies for handling file regeneration without losing customizations
- Version control and merge strategies for generated code

**Key Questions:**
- Can source_gen support custom code preservation patterns?
- What are the best practices for marking custom code regions in Dart?
- How to handle partial file regeneration vs. complete file replacement?
- What tools exist for managing generated vs. custom code conflicts?

## Expected Deliverables

### 1. Technical Implementation Guide
- Complete setup instructions for source_gen and build_runner
- Step-by-step guide to creating our first custom generator
- Configuration files and their purposes
- Integration with existing tooling

### 2. Project Structure Recommendations
- Recommended Flutter project directory structure
- Where to place generators, templates, and generated code
- Organization patterns for complex, multi-generator projects
- Integration with version control best practices

### 3. Generator Development Framework
- Base classes or patterns for our custom generators
- Reusable utilities for common generation tasks
- Error handling and logging patterns
- Testing framework for generators

### 4. Configuration Schema Design
- YAML configuration structure for Flutter applications
- Mapping between configuration and generated code
- Validation patterns for configuration files
- Examples of minimal, standard, and full configuration levels

### 5. Development Workflow Documentation
- Day-to-day development process with generation
- Debugging and troubleshooting guide
- Integration with IDE tooling
- Performance optimization strategies

### 6. Basic Generator Example
- Complete, working example of a simple generator
- Demonstrates key concepts and patterns
- Can serve as a template for more complex generators
- Includes testing and documentation

## Success Criteria

The research should enable us to:
1. **Set up a Flutter project** with source_gen and build_runner properly configured
2. **Create a basic custom generator** that can produce coordinated Dart code
3. **Establish the foundation** for BLoC architecture without implementing specifics
4. **Implement code preservation** patterns similar to our Go implementation
5. **Design a configuration schema** that mirrors our successful Go patterns
6. **Create a development workflow** that supports iterative, generation-driven development

## Technical Constraints

- Must work with current stable Flutter and Dart versions
- Should integrate with existing Go-based CLI tooling
- Must support the same configuration-driven approach as our Go implementation
- Need to maintain Dart/Flutter best practices and conventions
- Should be extensible for future architectural patterns beyond BLoC

## Questions for Clarification

1. Are there alternative approaches to source_gen that might better suit our use case?
2. What are the performance implications of large-scale code generation in Flutter projects?
3. Are there existing Flutter code generation tools we should evaluate or integrate with?
4. What are the common pitfalls or challenges teams face with source_gen in complex projects?
5. How do Flutter teams typically handle the balance between generated and custom code?

This research will form the foundation for our Flutter synthesis engine, enabling configuration-driven Flutter application development with the same power and simplicity as our Go backend synthesis system.