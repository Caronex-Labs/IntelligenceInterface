"""
Simple Template Code Generator.

Handles template + config → code generation using Jinja2.
Input: template file + Pydantic model context
Output: generated code string
"""

from pathlib import Path
from typing import Dict, Any, Union
import time
from jinja2 import Environment, FileSystemLoader, TemplateError
from pydantic import BaseModel

from .type_aliases import PathLike
from ..types.models.internal_models import TemplateContext
from .logging_utils import get_logger, sanitize_log_data, format_file_path, create_error_context

logger = get_logger(__name__)


class TemplateCodeGenerator:
    """Simple template processor: template + config → code."""

    def __init__(self, template_base_dir: PathLike) -> None:
        """
        Initialize template generator.
        
        Args:
            template_base_dir: Base directory containing template files
        """
        self.logger = get_logger(__name__)
        self.template_base_dir = Path(template_base_dir)
        
        self.logger.debug("Initializing template code generator", extra={
            "template_base_dir": format_file_path(template_base_dir),
            "operation": "init_generator"
        })
        
        self._init_jinja_environment()
        
        self.logger.info("Template code generator initialized successfully", extra={
            "template_base_dir": format_file_path(template_base_dir),
            "operation": "init_generator"
        })

    def _init_jinja_environment(self) -> None:
        """Initialize Jinja2 environment with custom filters."""
        self.logger.debug("Initializing Jinja2 environment", extra={
            "template_base_dir": format_file_path(self.template_base_dir),
            "operation": "init_jinja_env"
        })
        
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_base_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
            
            self.logger.debug("Jinja2 environment created with configuration", extra={
                "trim_blocks": True,
                "lstrip_blocks": True,
                "keep_trailing_newline": True,
                "loader_type": "FileSystemLoader",
                "operation": "init_jinja_env"
            })
            
            # Add custom filters
            custom_filters = {
                'to_snake_case': self._to_snake_case,
                'to_pascal_case': self._to_pascal_case,
                'pluralize': self._pluralize
            }
            
            for filter_name, filter_func in custom_filters.items():
                self.jinja_env.filters[filter_name] = filter_func
                self.logger.debug("Registered custom Jinja2 filter", extra={
                    "filter_name": filter_name,
                    "operation": "register_filter"
                })
            
            self.logger.debug("Jinja2 environment initialization completed", extra={
                "custom_filters_count": len(custom_filters),
                "operation": "init_jinja_env"
            })
            
        except Exception as e:
            error_context = create_error_context("init_jinja_env", e, {
                "template_base_dir": format_file_path(self.template_base_dir)
            })
            self.logger.error("Failed to initialize Jinja2 environment", 
                            extra=error_context, exc_info=True)
            raise

    def _to_snake_case(self, text: str) -> str:
        """Convert PascalCase to snake_case."""
        import re
        result = re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
        self.logger.debug("Applied snake_case filter", extra={
            "input": text,
            "output": result,
            "filter": "to_snake_case"
        })
        return result

    def _to_pascal_case(self, text: str) -> str:
        """Convert snake_case to PascalCase."""
        result = ''.join(word.capitalize() for word in text.split('_'))
        self.logger.debug("Applied pascal_case filter", extra={
            "input": text,
            "output": result,
            "filter": "to_pascal_case"
        })
        return result

    def _pluralize(self, text: str) -> str:
        """Simple pluralization."""
        if text.endswith('y'):
            result = text[:-1] + 'ies'
        elif text.endswith(('s', 'sh', 'ch', 'x', 'z')):
            result = text + 'es'
        else:
            result = text + 's'
        
        self.logger.debug("Applied pluralize filter", extra={
            "input": text,
            "output": result,
            "filter": "pluralize"
        })
        return result

    def generate_from_template(self, template_path: PathLike, context: Union[TemplateContext, BaseModel]) -> str:
        """
        Generate code from template and Pydantic model context.
        
        Args:
            template_path: Path to .j2 template file  
            context: Pydantic model containing template context data
            
        Returns:
            Generated code string
            
        Raises:
            FileNotFoundError: If template doesn't exist
            TemplateError: If template processing fails
        """
        start_time = time.time()
        template_path = Path(template_path)
        
        # Convert Pydantic model to dictionary for Jinja2
        config = context.model_dump() if context else {}
        
        # Sanitize config for logging (remove sensitive data)
        sanitized_config = sanitize_log_data(config)
        
        self.logger.debug("Starting template generation", extra={
            "template_path": format_file_path(template_path),
            "template_base_dir": format_file_path(self.template_base_dir),
            "context_type": type(context).__name__ if context else "None",
            "config_keys": list(config.keys()) if config else [],
            "config_size": len(str(config)) if config else 0,
            "operation": "generate_from_template",
            "phase": "start"
        })
        
        # Validate template exists
        if not template_path.exists():
            error_context = {
                "template_path": format_file_path(template_path),
                "template_base_dir": format_file_path(self.template_base_dir),
                "operation": "generate_from_template",
                "error_type": "template_not_found"
            }
            self.logger.error("Template file not found", extra=error_context)
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # Get template file size for performance logging
        try:
            template_size = template_path.stat().st_size
            self.logger.debug("Template file validated", extra={
                "template_path": format_file_path(template_path),
                "template_size_bytes": template_size,
                "operation": "generate_from_template",
                "phase": "validation"
            })
        except Exception as e:
            self.logger.warning("Could not get template file size", extra={
                "template_path": format_file_path(template_path),
                "error": str(e),
                "operation": "generate_from_template"
            })
            template_size = 0
        
        # Get relative path for Jinja2 loader
        try:
            relative_path = template_path.relative_to(self.template_base_dir)
            self.logger.debug("Template path resolved", extra={
                "template_path": format_file_path(template_path),
                "relative_path": str(relative_path),
                "template_base_dir": format_file_path(self.template_base_dir),
                "operation": "generate_from_template",
                "phase": "path_resolution"
            })
        except ValueError as e:
            error_context = create_error_context("generate_from_template", e, {
                "template_path": format_file_path(template_path),
                "template_base_dir": format_file_path(self.template_base_dir),
                "error_type": "path_resolution_error"
            })
            self.logger.error("Template path resolution failed", 
                            extra=error_context, exc_info=True)
            raise ValueError(f"Template {template_path} not under base {self.template_base_dir}")
        
        try:
            # Load template
            template_load_start = time.time()
            template = self.jinja_env.get_template(str(relative_path))
            template_load_time = time.time() - template_load_start
            
            self.logger.debug("Template loaded successfully", extra={
                "template_path": format_file_path(template_path),
                "relative_path": str(relative_path),
                "load_time_seconds": round(template_load_time, 3),
                "operation": "generate_from_template",
                "phase": "template_load"
            })
            
            # Log context details (sanitized)
            context_info = {
                "context_type": type(context).__name__ if context else "None",
                "context_keys": list(config.keys()) if config else [],
                "context_key_count": len(config) if config else 0,
                "context_complexity": self._analyze_context_complexity(context),
                "operation": "generate_from_template",
                "phase": "context_analysis"
            }
            
            # Add sanitized sample of context for debugging (only top-level keys)
            if config:
                sample_context = {}
                for key, value in list(config.items())[:5]:  # Only first 5 keys
                    if isinstance(value, (str, int, float, bool)):
                        sample_context[key] = value
                    else:
                        sample_context[key] = f"<{type(value).__name__}>"
                context_info["context_sample"] = sanitize_log_data(sample_context)
            
            self.logger.debug("Template context analyzed", extra=context_info)
            
            # Render template
            render_start = time.time()
            rendered_content = template.render(**config)
            render_time = time.time() - render_start
            
            total_time = time.time() - start_time
            
            # Log successful generation with performance metrics
            success_context = {
                "template_path": format_file_path(template_path),
                "relative_path": str(relative_path),
                "template_size_bytes": template_size,
                "generated_content_length": len(rendered_content),
                "template_load_time_seconds": round(template_load_time, 3),
                "render_time_seconds": round(render_time, 3),
                "total_time_seconds": round(total_time, 3),
                "operation": "generate_from_template",
                "phase": "complete",
                "status": "success"
            }
            
            self.logger.info("Template generation completed successfully", extra=success_context)
            
            # Log performance category
            if total_time > 1.0:
                self.logger.warning("Template generation took longer than expected", extra={
                    "template_path": format_file_path(template_path),
                    "total_time_seconds": round(total_time, 3),
                    "performance_category": "slow",
                    "operation": "generate_from_template"
                })
            
            return rendered_content
            
        except TemplateError as e:
            total_time = time.time() - start_time
            error_context = create_error_context("generate_from_template", e, {
                "template_path": format_file_path(template_path),
                "relative_path": str(relative_path),
                "template_size_bytes": template_size,
                "total_time_seconds": round(total_time, 3),
                "error_type": "template_rendering_error",
                "jinja_error_type": type(e).__name__
            })
            
            self.logger.error("Template rendering failed", 
                            extra=error_context, exc_info=True)
            raise TemplateError(f"Template rendering failed: {e}")
        
        except Exception as e:
            total_time = time.time() - start_time
            error_context = create_error_context("generate_from_template", e, {
                "template_path": format_file_path(template_path),
                "template_base_dir": format_file_path(self.template_base_dir),
                "total_time_seconds": round(total_time, 3),
                "error_type": "unexpected_error"
            })
            
            self.logger.error("Unexpected error during template generation", 
                            extra=error_context, exc_info=True)
            raise
    
    def _analyze_context_complexity(self, context: Union[BaseModel, None]) -> str:
        """Analyze the complexity of the Pydantic model context."""
        if not context:
            return "empty"
        
        # Get model fields and their types
        model_fields = context.model_fields if hasattr(context, 'model_fields') else {}
        total_fields = len(model_fields)
        
        # Count complex field types (lists, dicts, nested models)
        complex_fields = 0
        for field_info in model_fields.values():
            field_type = getattr(field_info, 'annotation', None)
            if field_type:
                # Check if field type is complex (list, dict, or another BaseModel)
                if hasattr(field_type, '__origin__'):
                    # Generic types like List, Dict, Union
                    complex_fields += 1
                elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
                    # Nested Pydantic models
                    complex_fields += 1
        
        # Analyze actual values for additional complexity
        config = context.model_dump()
        nested_items = sum(1 for v in config.values() if isinstance(v, (dict, list)))
        
        total_complexity_score = total_fields + complex_fields + nested_items
        
        if total_complexity_score <= 5:
            return "simple"
        elif total_complexity_score <= 15:
            return "moderate"
        else:
            return "complex"
