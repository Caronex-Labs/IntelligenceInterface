"""
CLI interface for the FastAPI SQLModel generator.

This module provides a command-line interface for project initialization and
code generation across all architectural layers.
"""

from .main import main, GeneratorCLI

__all__ = ["main", "GeneratorCLI"]