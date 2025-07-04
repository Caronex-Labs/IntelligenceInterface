# Installing FastAPI SQLModel Generator MCP Server in Claude Desktop

## Quick Installation

### 1. Add to Claude Desktop Configuration

Open your Claude Desktop configuration file:

```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or use your favorite editor
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 2. Add the MCP Server Entry

Add this entry to the `mcpServers` section of your config:

```json
{
  "mcpServers": {
    // ... your existing servers ...
    "fastapi-sqlmodel-generator": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel/mcp_server.py"
      ]
    }
  }
}
```

**Note**: Make sure to update the path to match your actual project location.

### 3. Save and Restart Claude Desktop

1. Save the configuration file
2. Quit Claude Desktop completely (Cmd+Q on macOS)
3. Restart Claude Desktop

### 4. Verify Installation

In a new Claude conversation, you should see "fastapi-sqlmodel-generator" in the MCP servers list when you start using
tools.

## Alternative Installation Methods

### Method 1: Using a Shell Script

Create a launcher script:

```bash
#!/bin/bash
cd /Users/caronex/Work/CaronexLabs/IntelligenceInterface/templates/projects/python_fastapi_sqlmodel
exec uv run python mcp_server.py
```

Then update your config to use the script:

```json
{
  "fastapi-sqlmodel-generator": {
    "command": "/path/to/launcher.sh"
  }
}
```

### Method 2: Using uvx (if published to PyPI)

If you publish the MCP server to PyPI:

```json
{
  "fastapi-sqlmodel-generator": {
    "command": "uvx",
    "args": ["fastapi-sqlmodel-mcp"]
  }
}
```

## Usage in Claude Desktop

Once installed, you can use the generator in Claude conversations:

1. **Initialize a project**:
   ```
   "Please use the fastapi-sqlmodel-generator to create a new project called 'MyAPI' in ~/projects/myapi"
   ```

2. **Generate a domain**:
   ```
   "Use the fastapi-sqlmodel-generator to create a Product domain with fields for name, price, and description"
   ```

3. **Access schemas**:
   ```
   "Show me the schema for EntityDomainConfig from the fastapi-sqlmodel-generator"
   ```

## Troubleshooting

### Server Not Appearing

1. Check the config file syntax is valid JSON
2. Ensure the path to mcp_server.py is correct
3. Check Claude Desktop logs: `~/Library/Logs/Claude/`

### Server Fails to Start

1. Verify uv is installed: `which uv`
2. Test the server manually:
   ```bash
   cd /path/to/project
   uv run python mcp_server.py
   ```
3. Check for Python errors in the logs

### Permission Issues

Make sure the script has execute permissions:

```bash
chmod +x /path/to/mcp_server.py
```

## Environment Variables

If your project needs specific environment variables, add an `env` section:

```json
{
  "fastapi-sqlmodel-generator": {
    "command": "uv",
    "args": [
      "run",
      "python",
      "/path/to/mcp_server.py"
    ],
    "env": {
      "PYTHONPATH": "/path/to/project",
      "LOG_LEVEL": "INFO"
    }
  }
}
```

## Development Mode

For development, you might want verbose logging:

```json
{
  "fastapi-sqlmodel-generator-dev": {
    "command": "uv",
    "args": [
      "run",
      "python",
      "-u",  // Unbuffered output
      "/path/to/mcp_server.py"
    ],
    "env": {
      "LOG_LEVEL": "DEBUG",
      "FASTMCP_DEBUG": "true"
    }
  }
}
```

## Security Considerations

- The MCP server has access to your file system (for project generation)
- It runs with your user permissions
- Generated code is written to directories you specify
- No network access is required (purely local operation)

## Next Steps

1. Test the installation by asking Claude to initialize a test project
2. Review the available tools with "Show me what tools the fastapi-sqlmodel-generator provides"
3. Check out example configurations in the MCP_SERVER.md documentation