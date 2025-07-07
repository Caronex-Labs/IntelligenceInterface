"""
Centralized logging utilities for the generator package.

This module provides structured logging capabilities with JSON formatting,
configurable log levels, and consistent logging patterns across the entire
generator package.
"""

import json
import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .type_aliases import PathLike


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Create base log entry
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "component": "generator"
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }
        
        # Add extra context data if present
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        # Add any additional attributes that were passed via extra parameter
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName', 
                          'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info',
                          'extra_data']:
                try:
                    # Sanitize the value before adding to log
                    sanitized_value = sanitize_log_data(value)
                    log_entry[key] = sanitized_value
                except Exception:
                    # If sanitization fails, convert to string
                    log_entry[key] = str(value)
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class PlainTextFormatter(logging.Formatter):
    """Human-readable plain text formatter."""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class ContextualLogger:
    """Logger wrapper that provides contextual logging capabilities."""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._base_context = {"component": "generator"}
    
    def _log_with_context(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None, 
                         exc_info: bool = False, **kwargs):
        """Log with merged context."""
        merged_extra = self._base_context.copy()
        if extra:
            merged_extra.update(extra)
        merged_extra.update(kwargs)
        
        # Sanitize the extra data
        sanitized_extra = sanitize_log_data(merged_extra)
        
        self._logger.log(level, msg, extra=sanitized_extra, exc_info=exc_info)
    
    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, msg, extra, **kwargs)
    
    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, msg, extra, **kwargs)
    
    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, msg, extra, **kwargs)
    
    def error(self, msg: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, msg, extra, exc_info=exc_info, **kwargs)
    
    def critical(self, msg: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, msg, extra, exc_info=exc_info, **kwargs)
    
    def timed_operation(self, operation_name: str, extra: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations."""
        return TimedOperation(self, operation_name, extra)


class TimedOperation:
    """Context manager for timing operations and logging results."""
    
    def __init__(self, logger: ContextualLogger, operation_name: str, extra: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.operation_name = operation_name
        self.extra = extra or {}
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation_name}", 
                         extra={**self.extra, "operation": self.operation_name, "phase": "start"})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        context = {
            **self.extra,
            "operation": self.operation_name,
            "duration_seconds": round(duration, 3),
            "phase": "complete"
        }
        
        if exc_type is None:
            self.logger.info(f"Operation completed: {self.operation_name}", extra=context)
        else:
            context["error_type"] = exc_type.__name__ if exc_type else None
            self.logger.error(f"Operation failed: {self.operation_name}", 
                            extra=context, exc_info=True)


# Global configuration state
_logging_configured = False
_current_config = {}


def configure_logging(
    level: Union[int, str] = logging.INFO,
    json_format: bool = True,
    force_reconfigure: bool = False
) -> None:
    """
    Configure logging for the generator package.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting (True) or plain text (False)
        force_reconfigure: Force reconfiguration even if already configured
    """
    global _logging_configured, _current_config
    
    # Check environment variable overrides
    env_level = os.getenv('GENERATOR_LOG_LEVEL')
    if env_level:
        try:
            level = getattr(logging, env_level.upper())
        except AttributeError:
            # If invalid level, keep the provided level
            pass
    
    env_format = os.getenv('GENERATOR_LOG_FORMAT')
    if env_format:
        json_format = env_format.lower() in ('json', 'true', '1')
    
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Check if already configured with same settings
    new_config = {
        'level': level,
        'json_format': json_format
    }
    
    if _logging_configured and not force_reconfigure and _current_config == new_config:
        return
    
    # Get root logger for the generator package
    root_logger = logging.getLogger('generator')
    
    # Clear existing handlers if reconfiguring
    if force_reconfigure or _logging_configured:
        root_logger.handlers.clear()
    
    # Set up formatter
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = PlainTextFormatter()
    
    # Set up handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    
    # Configure logger
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    root_logger.propagate = False
    
    # Update global state
    _logging_configured = True
    _current_config = new_config


def get_logger(name: str) -> ContextualLogger:
    """
    Get a logger instance with consistent naming and configuration.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        ContextualLogger instance with pre-configured context
    """
    # Ensure logging is configured
    if not _logging_configured:
        configure_logging()
    
    # Create logger with generator prefix if not already present
    if not name.startswith('generator'):
        if name == '__main__':
            logger_name = 'generator.main'
        else:
            # Extract relative module path
            parts = name.split('.')
            if 'generator' in parts:
                # Find generator in the path and use everything after it
                generator_index = parts.index('generator')
                relative_parts = parts[generator_index:]
                logger_name = '.'.join(relative_parts)
            else:
                logger_name = f'generator.{name}'
    else:
        logger_name = name
    
    # Get the actual logger
    logger = logging.getLogger(logger_name)
    
    # Return wrapped logger with contextual capabilities
    return ContextualLogger(logger)


def sanitize_log_data(data: Any) -> Any:
    """
    Sanitize sensitive data from log contexts.
    
    Args:
        data: Data to sanitize
    
    Returns:
        Sanitized data with sensitive information masked
    """
    if data is None:
        return None
    
    # Sensitive field patterns (case-insensitive)
    sensitive_patterns = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
        'credential', 'api_key', 'access_token', 'refresh_token', 'private_key',
        'database_url', 'db_url', 'connection_string'
    }
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_lower = str(key).lower()
            if any(pattern in key_lower for pattern in sensitive_patterns):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = sanitize_log_data(value)
        return sanitized
    
    elif isinstance(data, (list, tuple)):
        return [sanitize_log_data(item) for item in data]
    
    elif isinstance(data, str):
        # Check if string looks like a sensitive value (basic heuristics)
        if len(data) > 20 and any(char in data for char in ['=', ':', '//', 'postgresql://', 'mysql://']):
            return "***REDACTED***"
        return data
    
    else:
        # For other types, return as-is
        return data


def format_file_path(path: PathLike) -> str:
    """
    Format file paths consistently for logging.
    
    Args:
        path: File path to format
    
    Returns:
        Formatted path string
    """
    if isinstance(path, str):
        path = Path(path)
    
    try:
        # Try to get relative path from current working directory
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        # If not relative to cwd, return absolute path
        return str(path.absolute())


def format_domain_name(domain: str) -> str:
    """
    Format domain names consistently for logging.
    
    Args:
        domain: Domain name to format
    
    Returns:
        Formatted domain name
    """
    if not domain:
        return "unknown"
    
    # Convert to lowercase and remove special characters for consistency
    formatted = domain.lower().strip()
    
    # Remove common prefixes/suffixes
    if formatted.endswith('_domain'):
        formatted = formatted[:-7]
    if formatted.endswith('domain'):
        formatted = formatted[:-6]
    
    return formatted


def create_error_context(
    operation: str,
    error: Exception,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create structured error context for logging.
    
    Args:
        operation: Name of the operation that failed
        error: The exception that occurred
        additional_context: Additional context information
    
    Returns:
        Structured error context dictionary
    """
    context = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    
    if additional_context:
        context.update(sanitize_log_data(additional_context))
    
    return context


def log_performance_metrics(
    logger: ContextualLogger,
    operation: str,
    duration: float,
    additional_metrics: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log performance metrics for operations.
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        additional_metrics: Additional metrics to log
    """
    metrics = {
        "operation": operation,
        "duration_seconds": round(duration, 3),
        "performance_category": _categorize_performance(duration)
    }
    
    if additional_metrics:
        metrics.update(sanitize_log_data(additional_metrics))
    
    logger.info(f"Performance metrics for {operation}", extra=metrics)


def _categorize_performance(duration: float) -> str:
    """Categorize performance based on duration."""
    if duration < 0.1:
        return "fast"
    elif duration < 1.0:
        return "normal"
    elif duration < 5.0:
        return "slow"
    else:
        return "very_slow"
