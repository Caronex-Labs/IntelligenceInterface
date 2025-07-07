"""
Interface layer for the FastAPI SQLModel generator.

This module provides both CLI and MCP interfaces for interacting with
the generator services.
"""

from .cli import GeneratorCLI, main as cli_main
from .mcp import GeneratorMCPServer, create_mcp_server

__all__ = [
    "GeneratorCLI",
    "cli_main",
    "GeneratorMCPServer", 
    "create_mcp_server"
]