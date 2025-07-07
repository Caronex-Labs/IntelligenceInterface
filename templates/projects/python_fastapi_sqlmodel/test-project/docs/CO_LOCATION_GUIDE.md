# Co-Location Architecture Guide

This project supports **co-location architecture** where templates and configurations live alongside generated code for easy customization and maintenance.

## What is Co-Location?

Co-location means that templates (.j2 files) and configuration files (.yaml) are stored in the same directory as the generated code, rather than in separate global directories.

### Traditional Structure:
```
configs/
  user_domain.yaml
  user_entities.yaml
templates/
  app/domain/{{domain}}/entities.py.j2
app/domain/User/
  entities.py
  exceptions.py
```

### Co-Located Structure:
```
app/domain/User/
  entities.py          # Generated code
  exceptions.py        # Generated code
  entities.py.j2       # Template (co-located)
  exceptions.py.j2     # Template (co-located)
  domain.yaml          # Config (co-located)
  entities.yaml        # Config (co-located)
```

## Benefits of Co-Location

1. **Domain Isolation**: Each domain is self-contained with its own templates and configs
2. **Easy Customization**: Modify templates for specific domains without affecting others
3. **Version Control**: Templates and configs are versioned alongside the code they generate
4. **Team Collaboration**: Different teams can work on different domains independently
5. **Template Evolution**: Templates can evolve with domain requirements

## Using Co-Location

### Generating with Co-Location

```bash
# Generate domain using co-located configs and templates (auto-detected)
fastapi-sqlmodel-generator generate --config app/domain/User/domain.yaml --output ./app
```

### Customizing Templates

1. **Modify co-located templates**: Edit `.j2` files in domain directories
2. **Update configurations**: Modify `domain.yaml` and `entities.yaml` files
3. **Regenerate**: Run generation command to apply changes

### Creating New Domains

```bash
# Create domain configs and generate (co-location auto-detected)
fastapi-sqlmodel-generator generate --config external_product.yaml --output ./app
```

## Configuration Hierarchy

Co-location supports configuration merging with this precedence:

1. **Co-located configs** (highest priority)
2. **Domain-specific overrides**
3. **Global defaults** (lowest priority)

### Example Override:
```yaml
# app/domain/User/domain.yaml
name: User
description: "Custom user domain with special requirements"

# Override global SQLModel settings
sqlmodel_config:
  table_naming: PascalCase  # Override global snake_case
  
# Domain-specific base fields
base_fields:
  - name: tenant_id
    type: UUID
    required: true
    description: "Multi-tenant isolation"
```

## Template Customization

### Basic Customization
Edit the `.j2` template files directly:

```jinja2
{# app/domain/User/entities.py.j2 #}
"""
{{ domain }} entities with custom business logic.
Generated: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
"""

from sqlmodel import SQLModel, Field
{% if custom_imports %}
{{ custom_imports }}
{% endif %}

class {{ entity.name }}(SQLModel, table=True):
    """{{ entity.description or entity.name + ' entity' }}"""
    
    {% for field in entity.fields %}
    {{ field.name }}: {{ field.python_type }} = {{ field.sqlmodel_field_params }}
    {% endfor %}
    
    {% if custom_methods %}
    # Custom business methods
    {{ custom_methods }}
    {% endif %}
```

### Advanced Customization
Create domain-specific template variables:

```yaml
# app/domain/User/domain.yaml
template_context:
  custom_imports: |
    from app.security import hash_password
    from app.notifications import send_welcome_email
  custom_methods: |
    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)
    
    def send_welcome(self) -> None:
        send_welcome_email(self.email)
```

## Migration from Traditional to Co-Located

### Migration Process
```bash
# Modern workflow automatically handles migration
# External config → co-located breakdown → generation
fastapi-sqlmodel-generator generate --config configs/user_domain.yaml --output ./app

# This automatically creates co-located structure and generates code
```

## Best Practices

### 1. Template Versioning
Each domain tracks its template version:

```yaml
# .template_version.yaml (auto-generated)
template_version: "1.0.0"
copied_at: "2024-01-15T10:30:00"
templates:
  - entities.py.j2
  - exceptions.py.j2
source: global_templates
customization_status: modified
```

### 2. Backup Before Customization
```bash
# Backup original templates before modification
cp entities.py.j2 entities.py.j2.backup
```

### 3. Document Changes
```yaml
# domain.yaml
metadata:
  customizations:
    - "Added multi-tenant support"
    - "Custom validation for email fields"
    - "Integration with external API"
  last_modified: "2024-01-15"
  modified_by: "development-team"
```

### 4. Test Custom Templates
```bash
# Generate test domain to validate templates
fastapi-sqlmodel-generator generate --config app/domain/TestUser/domain.yaml --output ./app --validate
```

## Troubleshooting

### Template Not Found
- Ensure templates exist in domain directory
- Check template file names match expected patterns
- Verify template syntax with `--validate` flag

### Configuration Conflicts
- Use `--debug` flag to see configuration merging
- Check precedence order (co-located > domain > global)
- Validate YAML syntax in configuration files

### Generation Errors
- Check template variables are defined
- Verify template syntax with Jinja2 validator
- Use `--strict` mode for detailed error reporting

## Integration with Development Workflow

### Git Integration
```gitignore
# .gitignore
# Keep co-located templates and configs in version control
!app/domain/*/domain.yaml
!app/domain/*/entities.yaml
!app/domain/*/*.j2

# Ignore generated files
app/domain/*/entities.py
app/domain/*/exceptions.py
```

### CI/CD Pipeline
```yaml
# .github/workflows/validate-templates.yml
name: Validate Co-Located Templates
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Templates
        run: |
          python -m cli.validate.template_linter app/domain/*/
```

## Future Enhancements

- **Template inheritance**: Base templates with domain overrides
- **Automated migration**: Tools for migrating existing projects
- **Template marketplace**: Sharing templates across projects
- **Real-time validation**: IDE integration for template editing

For more information, see the full documentation at `/docs/` or run:
```bash
fastapi-sqlmodel-generator --help
```
