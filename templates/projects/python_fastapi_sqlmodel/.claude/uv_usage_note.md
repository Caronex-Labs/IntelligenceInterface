# UV Usage Note

## Important: Use UV for Python Execution

This project uses `uv` for dependency management and Python execution. Always use `uv run` for running Python scripts and tests.

### Correct Usage Examples:
```bash
# Run Python scripts
uv run python script.py

# Run tests  
uv run python -m pytest tests/
uv run python tests/unit/test_name.py

# Run demos
uv run python demo_script.py

# Install dependencies
uv add package-name
uv sync
```

### Incorrect Usage:
```bash
# DON'T use these - they may fail with missing dependencies
python script.py
python3 script.py
python -m pytest tests/
```

## Why UV?
- Manages virtual environments automatically
- Ensures consistent dependency resolution
- Faster dependency installation and management
- Project-specific Python environments

## Development Workflow
1. Always use `uv run` for Python execution
2. Dependencies are managed in `pyproject.toml`
3. Virtual environment is automatically managed by uv
4. No need to manually activate/deactivate virtual environments

## Status
This note was added during Task uWFUGbrudH80 (Hierarchical Configuration Merging) after encountering dependency issues when not using uv.