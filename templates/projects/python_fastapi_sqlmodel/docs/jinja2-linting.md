# Jinja2 Template Linting and Formatting

This project includes comprehensive linting and formatting tools for Jinja2 templates to ensure consistent code quality
and catch syntax errors automatically.

## Tools Overview

### djLint - Template Formatter and Linter

- **Purpose**: Primary tool for Jinja2 template formatting and auto-fixing
- **Features**:
    - Automatic formatting with 2000%+ performance improvements
    - Syntax error detection
    - Code style enforcement
    - Integration with VS Code
- **Auto-fix**: ✅ Yes - can automatically fix most formatting issues

### j2lint - Advanced Validation

- **Purpose**: Comprehensive Jinja2 style guide validation
- **Features**:
    - AVD (Arista Validated Design) style guide compliance
    - Advanced syntax validation
    - Custom rule configuration
    - Variable naming conventions
- **Auto-fix**: ❌ No - validation only

## Configuration

Both tools are configured in `pyproject.toml`:

```toml
[tool.djlint]
profile = "jinja"
extension = "j2"
indent = 2
max_line_length = 120
format_css = true
format_js = true
ignore = "H021,H030,H031"

[tool.j2lint]
rules = [
    "S0",   # Jinja2 syntax should be correct
    "S1",   # Single space between curly brackets and variable names  
    "S2",   # Filters should be enclosed by spaces
    "S3",   # Jinja statements must be enclosed by 1 space
    "S7",   # Jinja statements should be on separate lines
    "S8",   # Avoid {%- or {%+ or -%} delimiters
    "VAR-1", # Variables should use lower case
    "VAR-2"  # Multi-word variables should use underscore
]
```

## Usage

### Manual Linting

#### Using the Custom Script

```bash
# Lint all templates in current directory
uv run python scripts/lint_templates.py

# Auto-fix all templates
uv run python scripts/lint_templates.py --fix

# Lint specific directory
uv run python scripts/lint_templates.py app/interface/

# Lint specific file
uv run python scripts/lint_templates.py app/__init__.py.j2

# Use only djLint (skip j2lint)
uv run python scripts/lint_templates.py --djlint-only

# Use only j2lint (skip djLint)
uv run python scripts/lint_templates.py --j2lint-only
```

#### Using Tools Directly

```bash
# djLint - lint templates
uv run djlint app/ --profile=jinja

# djLint - auto-fix templates
uv run djlint app/ --profile=jinja --reformat

# j2lint - validate templates
uv run j2lint app/__init__.py.j2
```

### Automated Linting with Pre-commit

Install pre-commit hooks:

```bash
uv run pre-commit install
```

The hooks will automatically:

1. Format templates with djLint on commit
2. Validate templates with j2lint
3. Check basic file formatting

### VS Code Integration

For real-time linting in VS Code:

1. Install the djLint extension:
    - Open VS Code
    - Go to Extensions tab
    - Search for "djlint"
    - Install the extension

2. Configure VS Code settings (`settings.json`):

```json
{
  "[jinja][jinja-html]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "monosans.djlint"
  }
}
```

## Common Issues and Solutions

### djLint Issues

#### Issue: Variables not wrapped in whitespace

```jinja2
# Before (incorrect)
{{variable_name}}

# After (correct)  
{{ variable_name }}
```

#### Issue: Extra blank lines

```jinja2
# Before (incorrect)
function_call()



# After (correct)
function_call()
```

### j2lint Issues

#### Issue: Filters not enclosed by spaces

```jinja2
# Before (incorrect)
{{ domain_name_plural|title }}

# After (correct)
{{ domain_name_plural | title }}
```

#### Issue: Variable naming conventions

```jinja2
# Before (incorrect)
{{ MyVariableName }}

# After (correct)
{{ my_variable_name }}
```

## Integration with CI/CD

Add to your GitHub Actions workflow:

```yaml
- name: Lint Jinja2 Templates
  run: |
    uv sync --group dev
    uv run python scripts/lint_templates.py --fix
    # Check if any files were modified
    if [ -n "$(git status --porcelain)" ]; then
      echo "Templates were auto-fixed. Please commit these changes."
      git diff
      exit 1
    fi
```

## Template Quality Rules

### Mandatory (djLint auto-fixes these)

- Variables must be wrapped with spaces: `{{ variable }}`
- Consistent indentation (2 spaces)
- No trailing whitespace
- Proper line endings

### Recommended (j2lint validates these)

- Filters enclosed by spaces: `{{ var | filter }}`
- Lower case variable names: `{{ my_var }}`
- Underscore for multi-word variables: `{{ my_long_var }}`
- Jinja statements on separate lines
- Avoid whitespace control delimiters (`{%-`, `-%}`)

## Performance

- **djLint**: Extremely fast with 2000%+ performance improvements
- **j2lint**: Fast validation suitable for large codebases
- **Combined**: Typical project linting completes in seconds

## Troubleshooting

### Tool Installation Issues

```bash
# Reinstall tools
uv remove djlint j2lint
uv add djlint
uv add git+https://github.com/aristanetworks/j2lint.git
```

### Pre-commit Issues

```bash
# Reinstall hooks
uv run pre-commit uninstall
uv run pre-commit install

# Update hooks
uv run pre-commit autoupdate
```

### VS Code Issues

- Ensure djLint extension is installed and enabled
- Check that file associations are correct for `.j2` files
- Verify workspace settings include djLint configuration