# Template Customization Guide

This directory contains template files (.j2) and configuration files (.yaml) that you can customize for your specific project requirements.

## Template Structure

### Core Application Templates
- `app/main.py.j2` - FastAPI application entry point
- `app/config.py.j2` - Application configuration
- `app/database.py.j2` - Database connection and setup
- `app/interface/exceptions.py.j2` - Global exception handlers

### Core Layer Templates
- `app/core/{{domain}}/entities.py.j2` - Entity definitions
- `app/core/{{domain}}/exceptions.py.j2` - Domain-specific exceptions

### Repository Layer Templates
- `app/repository/{{domain}}/repository.py.j2` - Data access layer
- `app/repository/{{domain}}/protocols.py.j2` - Repository interfaces

### Use Case Layer Templates
- `app/usecase/{{domain}}/usecase.py.j2` - Business logic
- `app/usecase/{{domain}}/schemas.py.j2` - Data transfer objects

### Interface Layer Templates
- `app/interface/{{domain}}/router.py.j2` - API routes
- `app/interface/{{domain}}/dependencies.py.j2` - Dependency injection

## Configuration Files

Configuration files define default settings for each layer:
- `domain.yaml` - Domain configuration
- `entities.yaml` - Entity definitions
- `repository.yaml` - Repository settings
- `usecase.yaml` - Use case configuration
- `business-rules.yaml` - Business logic rules
- `interface.yaml` - API interface settings

## Customizing Templates

1. **Modify existing templates**: Edit .j2 files to change generated code structure
2. **Add custom variables**: Define variables in configuration files
3. **Create new templates**: Add new .j2 files for additional functionality
4. **Update configurations**: Modify .yaml files to change defaults

## Regenerating Code

After customizing templates, regenerate your domain code:

```bash
# Generate specific domain using system-installed CLI
fastapi-sqlmodel-generator generate --config your_domain.yaml --output ./app

# Or use the CLI tool if installed
testauthproject-cli generate --domain your_domain --template-dir templates/
```

## Best Practices

1. **Backup originals**: Keep copies of original templates before modification
2. **Test changes**: Regenerate test domains to validate template changes
3. **Document modifications**: Record changes for team collaboration
4. **Version control**: Commit template changes with clear commit messages

## Template Variables

Common variables available in templates:
- `{{app_name}}` - Application name
- `{{domain}}` - Domain name
- `{{domain_plural}}` - Plural domain name
- `{{package_name}}` - Python package name
- `{{database_type}}` - Database type (sqlite, postgresql, mysql)

Project: testauthproject
Generated: 2025-07-05 14:21:46
