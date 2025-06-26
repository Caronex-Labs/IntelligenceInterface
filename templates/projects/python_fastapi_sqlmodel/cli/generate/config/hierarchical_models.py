"""
Hierarchical configuration models for multi-layer template system processing.

This module defines models specifically for hierarchical configuration merging
across Domain → UseCase → Repository → Interface layers.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LayerType(str, Enum):
    """Supported template layer types in hierarchical architecture."""
    DOMAIN = "domain"
    USECASE = "usecase" 
    REPOSITORY = "repository"
    INTERFACE = "interface"
    
    @property
    def precedence(self) -> int:
        """Get layer precedence value for merging order."""
        precedence_map = {
            LayerType.DOMAIN: 1,      # Lowest precedence (base layer)
            LayerType.USECASE: 2,     # Use case layer
            LayerType.REPOSITORY: 3,  # Repository layer  
            LayerType.INTERFACE: 4,   # Highest precedence (interface layer)
        }
        return precedence_map[self]


class ConfigurationConflict(BaseModel):
    """Represents a configuration conflict between layers."""
    
    key_path: str = Field(..., description="Dot-separated path to conflicting key")
    layer1: LayerType = Field(..., description="First layer with conflicting value")
    value1: Any = Field(..., description="Value from first layer")
    layer2: LayerType = Field(..., description="Second layer with conflicting value")
    value2: Any = Field(..., description="Value from second layer")
    resolved_value: Any = Field(..., description="Final resolved value")
    resolution_strategy: str = Field(..., description="How conflict was resolved")
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class LayerMergeMetadata(BaseModel):
    """Metadata about a layer merge operation."""
    
    layer_type: LayerType = Field(..., description="Type of configuration layer")
    source_path: Optional[Path] = Field(default=None, description="Path to source configuration file")
    keys_contributed: List[str] = Field(default_factory=list, description="Configuration keys contributed by this layer")
    keys_overridden: List[str] = Field(default_factory=list, description="Keys that this layer overrode from lower layers")
    load_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this layer was loaded")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors for this layer")
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class ConfigurationLayer(BaseModel):
    """Represents a single configuration layer in the hierarchical system."""
    
    layer_type: LayerType = Field(..., description="Type of this configuration layer")
    config_path: Optional[Path] = Field(default=None, description="Path to configuration file")
    config_data: Dict[str, Any] = Field(default_factory=dict, description="Configuration data for this layer")
    precedence: int = Field(..., description="Merge precedence (higher values override lower)")
    is_loaded: bool = Field(default=False, description="Whether configuration has been loaded")
    metadata: Optional[LayerMergeMetadata] = Field(default=None, description="Layer metadata")
    
    @field_validator('precedence')
    def validate_precedence(cls, v, info):
        """Validate precedence matches layer type."""
        if 'layer_type' in info.data:
            layer_type = info.data['layer_type']
            expected_precedence = layer_type.precedence
            if v != expected_precedence:
                logger.warning(f"Precedence {v} doesn't match expected {expected_precedence} for {layer_type}")
        return v
    
    @model_validator(mode='after')
    def generate_metadata(self):
        """Generate layer metadata if not provided."""
        if self.metadata is None:
            self.metadata = LayerMergeMetadata(
                layer_type=self.layer_type,
                source_path=self.config_path
            )
        return self
    
    def load_configuration(self) -> None:
        """Load configuration data from file path."""
        if self.config_path and self.config_path.exists():
            import yaml
            try:
                with self.config_path.open('r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
                self.is_loaded = True
                if self.metadata:
                    self.metadata.load_timestamp = datetime.utcnow()
            except Exception as e:
                logger.error(f"Failed to load configuration from {self.config_path}: {e}")
                if self.metadata:
                    self.metadata.validation_errors.append(f"Load error: {str(e)}")
        else:
            logger.warning(f"Configuration file not found: {self.config_path}")
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class HierarchicalMergeResult(BaseModel):
    """Result of hierarchical configuration merging operation."""
    
    merged_config: Dict[str, Any] = Field(..., description="Final merged configuration")
    layer_metadata: List[LayerMergeMetadata] = Field(default_factory=list, description="Metadata for each processed layer")
    conflicts: List[ConfigurationConflict] = Field(default_factory=list, description="Configuration conflicts detected and resolved")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors from merge process")
    merge_warnings: List[str] = Field(default_factory=list, description="Warnings generated during merge")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics for merge operation")
    merge_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When merge was performed")
    merger_version: str = Field(default="2.0.0", description="Version of merger that performed operation")
    
    @property
    def has_conflicts(self) -> bool:
        """Check if there were any configuration conflicts."""
        return len(self.conflicts) > 0
    
    @property
    def has_errors(self) -> bool:
        """Check if there were any validation errors."""
        return len(self.validation_errors) > 0
    
    @property
    def is_valid(self) -> bool:
        """Check if merge result is valid and ready for use."""
        return not self.has_errors and len(self.merged_config) > 0
    
    def get_conflicts_by_key(self, key_path: str) -> List[ConfigurationConflict]:
        """Get all conflicts for a specific configuration key path."""
        return [conflict for conflict in self.conflicts if conflict.key_path == key_path]
    
    def get_contributing_layers(self, key_path: str) -> List[LayerType]:
        """Get list of layers that contributed to a specific key path."""
        contributing_layers = []
        for metadata in self.layer_metadata:
            if key_path in metadata.keys_contributed:
                contributing_layers.append(metadata.layer_type)
        return contributing_layers
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class HierarchicalConfigurationSpec(BaseModel):
    """Specification for hierarchical configuration processing."""
    
    layers: List[ConfigurationLayer] = Field(..., description="Ordered list of configuration layers")
    conflict_resolution_strategy: str = Field(default="highest_precedence", description="Strategy for resolving conflicts")
    include_metadata: bool = Field(default=True, description="Whether to include detailed metadata in results")
    validate_schema: bool = Field(default=True, description="Whether to validate merged configuration against schema")
    performance_tracking: bool = Field(default=True, description="Whether to track performance metrics")
    
    @field_validator('layers')
    def validate_layer_order(cls, v):
        """Validate that layers are in correct precedence order."""
        if len(v) < 2:
            return v  # Single layer doesn't need ordering validation
        
        for i in range(1, len(v)):
            current_precedence = v[i].precedence
            previous_precedence = v[i-1].precedence
            
            if current_precedence <= previous_precedence:
                logger.warning(f"Layer precedence order may be incorrect: "
                             f"{v[i-1].layer_type}({previous_precedence}) -> {v[i].layer_type}({current_precedence})")
        
        return v
    
    @field_validator('conflict_resolution_strategy')
    def validate_resolution_strategy(cls, v):
        """Validate conflict resolution strategy."""
        allowed_strategies = [
            "highest_precedence",
            "merge_arrays", 
            "fail_on_conflict",
            "custom"
        ]
        if v not in allowed_strategies:
            raise ValueError(f"Conflict resolution strategy '{v}' must be one of {allowed_strategies}")
        return v
    
    def get_layers_by_type(self, layer_type: LayerType) -> List[ConfigurationLayer]:
        """Get all layers of a specific type."""
        return [layer for layer in self.layers if layer.layer_type == layer_type]
    
    def get_layer_by_precedence(self, precedence: int) -> Optional[ConfigurationLayer]:
        """Get layer by precedence value."""
        return next((layer for layer in self.layers if layer.precedence == precedence), None)
    
    model_config = {
        "arbitrary_types_allowed": True
    }