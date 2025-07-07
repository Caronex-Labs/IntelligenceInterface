"""
MCP interface for the FastAPI SQLModel generator.

This module provides an MCP (Model Context Protocol) server interface for 
project initialization and code generation across all architectural layers.
"""

from .server import GeneratorMCPServer, create_mcp_server

__all__ = ["GeneratorMCPServer", "create_mcp_server"]