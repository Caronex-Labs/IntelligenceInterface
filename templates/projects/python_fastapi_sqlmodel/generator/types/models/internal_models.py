"""
Internal Pydantic models for type-safe data structures.

This module defines internal data models used throughout the generator system
for passing structured data between functions, replacing generic dictionaries
with strongly typed Pydantic models for better type safety and validation.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import logging

from .config_models import EntityConfig, DomainConfig, EndpointConfig

logger = logging.getLogger(__name__)


class TemplateContext(BaseModel):
    """Context data for Jinja2 template rendering."""
    
    domain: str = Field(..., description="Domain name")
    entities: List[EntityConfig] = Field(default_factory=list, description="Entity configurations")
    endpoints: List[EndpointConfig] = Field(default_factory=list, description="API endpoint configurations")
    package_name: Optional[str] = Field(default=None, description="Python package name")
    plural_name: Optional[str] = Field(default=None, description="Plural form of domain name")
    description: Optional[str] = Field(default=None, description="Domain description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional template metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    @field_validator('domain')
    def validate_domain_name(cls, v):
        """Validate domain name follows Python naming conventions."""
        if not v.isidentifier():
            raise ValueError(f"Domain name '{v}' is not a valid Python identifier")
        return v
    
    @field_validator('package_name')
    def validate_package_name(cls, v):
        """Validate package name if provided."""
        if v is not None and not v.replace('_', '').isalnum():
            raise ValueError(f"Package name '{v}' is not a valid Python package name")
        return v


class GenerationResult(BaseModel):
    """Result of a code generation operation."""
    
    success: bool = Field(..., description="Whether the operation succeeded")
    files_generated: List[str] = Field(default_factory=list, description="List of files that were generated")
    files_modified: List[str] = Field(default_factory=list, description="List of files that were modified")
    files_skipped: List[str] = Field(default_factory=list, description="List of files that were skipped")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages")
    operation_type: Optional[str] = Field(default=None, description="Type of operation performed")
    duration_seconds: Optional[float] = Field(default=None, description="Operation duration in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional operation metadata")
    
    @field_validator('files_generated', 'files_modified', 'files_skipped')
    def validate_file_paths(cls, v):
        """Validate file paths are not empty strings."""
        return [path for path in v if path.strip()]
    
    def add_error(self, error: str) -> None:
        """Add an error message and mark operation as failed."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def add_generated_file(self, file_path: str) -> None:
        """Add a generated file to the result."""
        if file_path.strip():
            self.files_generated.append(file_path)
    
    def add_modified_file(self, file_path: str) -> None:
        """Add a modified file to the result."""
        if file_path.strip():
            self.files_modified.append(file_path)
    
    def add_skipped_file(self, file_path: str) -> None:
        """Add a skipped file to the result."""
        if file_path.strip():
            self.files_skipped.append(file_path)
    
    @property
    def total_files_affected(self) -> int:
        """Total number of files affected by the operation."""
        return len(self.files_generated) + len(self.files_modified) + len(self.files_skipped)
    
    @property
    def has_errors(self) -> bool:
        """Whether the operation had any errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Whether the operation had any warnings."""
        return len(self.warnings) > 0


class LayerInfo(BaseModel):
    """Metadata about a layer in the architecture."""
    
    name: str = Field(..., description="Layer name")
    type: str = Field(..., description="Layer type (core, repository, usecase, interface, service)")
    dependencies: List[str] = Field(default_factory=list, description="List of layer dependencies")
    description: Optional[str] = Field(default=None, description="Layer description")
    status: str = Field(default="unknown", description="Layer status (configured, generated, error)")
    config_files: List[str] = Field(default_factory=list, description="Configuration files for this layer")
    generated_files: List[str] = Field(default_factory=list, description="Files generated for this layer")
    domains: List[str] = Field(default_factory=list, description="Domains that use this layer")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional layer metadata")
    
    @field_validator('name')
    def validate_layer_name(cls, v):
        """Validate layer name."""
        if not v.strip():
            raise ValueError("Layer name cannot be empty")
        return v.strip()
    
    @field_validator('type')
    def validate_layer_type(cls, v):
        """Validate layer type."""
        allowed_types = ["core", "repository", "usecase", "interface", "service", "base"]
        if v not in allowed_types:
            raise ValueError(f"Layer type '{v}' must be one of {allowed_types}")
        return v
    
    @field_validator('status')
    def validate_status(cls, v):
        """Validate layer status."""
        allowed_statuses = ["unknown", "configured", "generated", "error", "blank"]
        if v not in allowed_statuses:
            raise ValueError(f"Layer status '{v}' must be one of {allowed_statuses}")
        return v
    
    @field_validator('dependencies')
    def validate_dependencies(cls, v):
        """Validate dependencies are not empty strings."""
        return [dep for dep in v if dep.strip()]


class SchemaInfo(BaseModel):
    """Information about a schema or configuration structure."""
    
    name: str = Field(..., description="Schema name")
    schema_definition: Dict[str, Any] = Field(..., description="JSON schema definition")
    format: str = Field(default="json", description="Schema format (json, yaml)")
    version: Optional[str] = Field(default=None, description="Schema version")
    description: Optional[str] = Field(default=None, description="Schema description")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Example configurations")
    usage_notes: List[str] = Field(default_factory=list, description="Usage notes and tips")
    validation_rules: List[str] = Field(default_factory=list, description="Additional validation rules")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional schema metadata")
    
    @field_validator('name')
    def validate_schema_name(cls, v):
        """Validate schema name."""
        if not v.strip():
            raise ValueError("Schema name cannot be empty")
        return v.strip()
    
    @field_validator('format')
    def validate_format(cls, v):
        """Validate schema format."""
        allowed_formats = ["json", "yaml", "toml", "xml"]
        if v not in allowed_formats:
            raise ValueError(f"Schema format '{v}' must be one of {allowed_formats}")
        return v
    
    def add_example(self, example: Dict[str, Any], description: Optional[str] = None) -> None:
        """Add an example configuration."""
        example_entry = example.copy()
        if description:
            example_entry["_description"] = description
        self.examples.append(example_entry)
    
    def add_usage_note(self, note: str) -> None:
        """Add a usage note."""
        if note.strip():
            self.usage_notes.append(note.strip())
    
    def add_validation_rule(self, rule: str) -> None:
        """Add a validation rule."""
        if rule.strip():
            self.validation_rules.append(rule.strip())


class ValidationContext(BaseModel):
    """Context for validation operations."""
    
    config_type: str = Field(..., description="Type of configuration being validated")
    file_path: str = Field(..., description="Path to the file being validated")
    errors: List[str] = Field(default_factory=list, description="Validation error messages")
    warnings: List[str] = Field(default_factory=list, description="Validation warning messages")
    line_numbers: Dict[str, int] = Field(default_factory=dict, description="Line numbers for errors/warnings")
    validation_rules: List[str] = Field(default_factory=list, description="Validation rules applied")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")
    
    @field_validator('config_type')
    def validate_config_type(cls, v):
        """Validate configuration type."""
        if not v.strip():
            raise ValueError("Configuration type cannot be empty")
        return v.strip()
    
    @field_validator('file_path')
    def validate_file_path(cls, v):
        """Validate file path."""
        if not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()
    
    def add_error(self, error: str, line_number: Optional[int] = None) -> None:
        """Add a validation error."""
        if error.strip():
            self.errors.append(error.strip())
            if line_number is not None:
                self.line_numbers[error.strip()] = line_number
    
    def add_warning(self, warning: str, line_number: Optional[int] = None) -> None:
        """Add a validation warning."""
        if warning.strip():
            self.warnings.append(warning.strip())
            if line_number is not None:
                self.line_numbers[warning.strip()] = line_number
    
    def add_validation_rule(self, rule: str) -> None:
        """Add a validation rule that was applied."""
        if rule.strip():
            self.validation_rules.append(rule.strip())
    
    @property
    def is_valid(self) -> bool:
        """Whether the validation passed (no errors)."""
        return len(self.errors) == 0
    
    @property
    def has_warnings(self) -> bool:
        """Whether the validation had warnings."""
        return len(self.warnings) > 0
    
    @property
    def total_issues(self) -> int:
        """Total number of validation issues (errors + warnings)."""
        return len(self.errors) + len(self.warnings)


class OperationMetrics(BaseModel):
    """Metrics for tracking operation performance and statistics."""
    
    operation_name: str = Field(..., description="Name of the operation")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Operation start time")
    end_time: Optional[datetime] = Field(default=None, description="Operation end time")
    duration_seconds: Optional[float] = Field(default=None, description="Operation duration in seconds")
    files_processed: int = Field(default=0, description="Number of files processed")
    lines_generated: int = Field(default=0, description="Number of lines generated")
    templates_used: List[str] = Field(default_factory=list, description="Templates used in operation")
    memory_usage_mb: Optional[float] = Field(default=None, description="Peak memory usage in MB")
    success_rate: Optional[float] = Field(default=None, description="Success rate as percentage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metrics metadata")
    
    @field_validator('operation_name')
    def validate_operation_name(cls, v):
        """Validate operation name."""
        if not v.strip():
            raise ValueError("Operation name cannot be empty")
        return v.strip()
    
    def mark_completed(self) -> None:
        """Mark the operation as completed and calculate duration."""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def add_template_used(self, template_name: str) -> None:
        """Add a template to the list of used templates."""
        if template_name.strip() and template_name not in self.templates_used:
            self.templates_used.append(template_name.strip())
    
    @property
    def is_completed(self) -> bool:
        """Whether the operation has completed."""
        return self.end_time is not None
    
    @property
    def files_per_second(self) -> Optional[float]:
        """Files processed per second."""
        if self.duration_seconds and self.duration_seconds > 0:
            return self.files_processed / self.duration_seconds
        return None
    
    @property
    def lines_per_second(self) -> Optional[float]:
        """Lines generated per second."""
        if self.duration_seconds and self.duration_seconds > 0:
            return self.lines_generated / self.duration_seconds
        return None