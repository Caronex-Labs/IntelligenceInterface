"""
Layer Generator for FastAPI SQLModel Generator.

Handles generation of individual layers (core, repository, usecase, service, interface).
Provides unified interface for all layer generation operations.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from ..utils.logging_utils import get_logger
from ..utils.config_processor import ConfigProcessor, ConfigProcessingError
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import LayerInfo, GenerationResult
from ..services.core import CoreLayerGenerator
from ..services.interface import InterfaceLayerGenerator
from ..services.repository import RepositoryLayerGenerator
from ..services.usecase import UseCaseLayerGenerator
from ..services.service import ServiceLayerGenerator

logger = get_logger(__name__)


class LayerGenerator:
    """
    Core layer generation class.
    
    Provides unified interface for generating individual layers
    while maintaining proper dependency order and validation.
    """

    AVAILABLE_LAYERS = ["core", "repository", "usecase", "service", "interface"]
    LAYER_DEPENDENCIES = {
        "core": [],
        "repository": ["core"],
        "usecase": ["core", "repository"],
        "service": ["core", "repository", "usecase"],
        "interface": ["core", "repository", "usecase", "service"]
    }

    def __init__(self, target_dir: PathLike) -> None:
        """
        Initialize layer generator.
        
        Args:
            target_dir: Target project directory
        """
        self.target_dir = Path(target_dir)
        self.logger = get_logger(__name__)
        
        # Initialize service generators
        self.generators = {
            "core": CoreLayerGenerator(str(self.target_dir)),
            "interface": InterfaceLayerGenerator(str(self.target_dir)),
            "repository": RepositoryLayerGenerator(str(self.target_dir)),
            "usecase": UseCaseLayerGenerator(str(self.target_dir)),
            "service": ServiceLayerGenerator(str(self.target_dir))
        }
        
        self.logger.debug("LayerGenerator initialized", extra={
            "target_dir": str(self.target_dir),
            "available_layers": self.AVAILABLE_LAYERS,
            "operation": "init"
        })

    def generate_layer(self, layer_type: str, config_path: str) -> GenerationResult:
        """
        Generate a specific layer from configuration.
        
        Args:
            layer_type: Type of layer to generate ("core", "repository", "usecase", "service", "interface")
            config_path: Path to configuration file
            
        Returns:
            GenerationResult with operation details
        """
        result = GenerationResult(
            success=False,
            operation_type=f"generate_{layer_type}_layer"
        )
        
        self.logger.debug("Starting layer generation", extra={
            "layer_type": layer_type,
            "config_path": config_path,
            "operation": "generate_layer"
        })
        
        try:
            # Validate layer type
            if layer_type not in self.AVAILABLE_LAYERS:
                error_msg = f"Unknown layer type: {layer_type}. Available: {self.AVAILABLE_LAYERS}"
                result.add_error(error_msg)
                return result
            
            # Validate config file exists
            config_file = Path(config_path)
            if not config_file.exists():
                error_msg = f"Configuration file not found: {config_path}"
                result.add_error(error_msg)
                return result
            
            # Extract domain name for logging
            domain_name = self._extract_domain_name_from_config(config_path)
            result.metadata["domain_name"] = domain_name
            result.metadata["layer_type"] = layer_type
            result.metadata["config_path"] = config_path
            
            with self.logger.timed_operation("layer_generation", extra={
                "layer_type": layer_type,
                "domain_name": domain_name
            }):
                # Get appropriate generator
                generator = self.generators[layer_type]
                
                # Generate the layer - assuming generators will be updated to return GenerationResult
                # For now, handle the current boolean return
                success = generator.get_from_config(config_path)
                
                if success:
                    result.success = True
                    # Note: Specific files generated will be populated when generators are updated
                    result.add_generated_file(f"{layer_type}_layer_generated")
                else:
                    result.add_error(f"Layer generation failed for {layer_type}")
            
            if result.success:
                self.logger.info("Layer generated successfully", extra={
                    "layer_type": layer_type,
                    "domain_name": domain_name,
                    "config_path": config_path,
                    "operation": "generate_layer",
                    "phase": "complete"
                })
            else:
                self.logger.error("Layer generation failed", extra={
                    "layer_type": layer_type,
                    "domain_name": domain_name,
                    "config_path": config_path,
                    "operation": "generate_layer",
                    "phase": "failed"
                })
            
            return result
            
        except Exception as e:
            error_msg = f"Layer generation failed: {str(e)}"
            result.add_error(error_msg)
            self.logger.error("Layer generation failed", exc_info=True, extra={
                "layer_type": layer_type,
                "config_path": config_path,
                "operation": "generate_layer",
                "phase": "failed"
            })
            return result

    def generate_core_layer(self, config_path: str) -> GenerationResult:
        """
        Generate core layer (entities, exceptions).
        
        Args:
            config_path: Path to domain configuration file
            
        Returns:
            GenerationResult with operation details
        """
        return self.generate_layer("core", config_path)

    def generate_repository_layer(self, config_path: str) -> GenerationResult:
        """
        Generate repository layer (protocols, implementations).
        
        Args:
            config_path: Path to domain configuration file
            
        Returns:
            GenerationResult with operation details
        """
        return self.generate_layer("repository", config_path)

    def generate_usecase_layer(self, config_path: str) -> GenerationResult:
        """
        Generate use case layer (business logic orchestration).
        
        Args:
            config_path: Path to use case configuration file
            
        Returns:
            GenerationResult with operation details
        """
        return self.generate_layer("usecase", config_path)

    def generate_service_layer(self, config_path: str) -> GenerationResult:
        """
        Generate service layer (domain-agnostic services).
        
        Args:
            config_path: Path to service configuration file
            
        Returns:
            GenerationResult with operation details
        """
        return self.generate_layer("service", config_path)

    def generate_interface_layer(self, config_path: str) -> GenerationResult:
        """
        Generate interface layer (FastAPI routes, dependencies).
        
        Args:
            config_path: Path to interface configuration file
            
        Returns:
            GenerationResult with operation details
        """
        return self.generate_layer("interface", config_path)

    def get_available_layers(self) -> list[str]:
        """
        Get list of available layer types.
        
        Returns:
            List of available layer types
        """
        return self.AVAILABLE_LAYERS.copy()

    def get_layer_dependencies(self, layer_type: str) -> list[str]:
        """
        Get dependencies for a specific layer type.
        
        Args:
            layer_type: Layer type to check
            
        Returns:
            List of layer dependencies
        """
        return self.LAYER_DEPENDENCIES.get(layer_type, []).copy()

    def validate_layer_order(self, layers: list[str]) -> bool:
        """
        Validate that layers are in correct dependency order.
        
        Args:
            layers: List of layers in order
            
        Returns:
            True if order is valid
        """
        self.logger.debug("Validating layer order", extra={
            "layers": layers,
            "operation": "validate_layer_order"
        })
        
        try:
            generated_layers = set()
            
            for layer in layers:
                if layer not in self.AVAILABLE_LAYERS:
                    self.logger.warning("Unknown layer in validation", extra={
                        "layer": layer,
                        "available_layers": self.AVAILABLE_LAYERS
                    })
                    return False
                
                # Check dependencies
                dependencies = self.LAYER_DEPENDENCIES.get(layer, [])
                for dep in dependencies:
                    if dep not in generated_layers:
                        self.logger.warning("Layer dependency not satisfied", extra={
                            "layer": layer,
                            "missing_dependency": dep,
                            "generated_layers": list(generated_layers)
                        })
                        return False
                
                generated_layers.add(layer)
            
            self.logger.debug("Layer order validation successful", extra={
                "layers": layers,
                "operation": "validate_layer_order",
                "phase": "complete"
            })
            return True
            
        except Exception as e:
            self.logger.error("Layer order validation failed", exc_info=True, extra={
                "layers": layers,
                "operation": "validate_layer_order",
                "phase": "failed"
            })
            return False

    def get_optimal_layer_order(self, layers: list[str]) -> list[str]:
        """
        Get optimal generation order for given layers.
        
        Args:
            layers: List of layers to order
            
        Returns:
            Layers in optimal dependency order
        """
        self.logger.debug("Computing optimal layer order", extra={
            "input_layers": layers,
            "operation": "get_optimal_layer_order"
        })
        
        try:
            # Filter to valid layers only
            valid_layers = [layer for layer in layers if layer in self.AVAILABLE_LAYERS]
            
            # Sort by dependency order
            ordered_layers = []
            remaining_layers = set(valid_layers)
            
            while remaining_layers:
                # Find layers with all dependencies satisfied
                ready_layers = []
                
                for layer in remaining_layers:
                    dependencies = self.LAYER_DEPENDENCIES.get(layer, [])
                    if all(dep in ordered_layers or dep not in valid_layers for dep in dependencies):
                        ready_layers.append(layer)
                
                if not ready_layers:
                    # Circular dependency or invalid state
                    self.logger.warning("Cannot resolve layer dependencies", extra={
                        "remaining_layers": list(remaining_layers),
                        "ordered_layers": ordered_layers
                    })
                    break
                
                # Sort ready layers by priority (core first, interface last)
                priority_order = ["core", "repository", "usecase", "service", "interface"]
                ready_layers.sort(key=lambda x: priority_order.index(x) if x in priority_order else 999)
                
                # Add first ready layer
                next_layer = ready_layers[0]
                ordered_layers.append(next_layer)
                remaining_layers.remove(next_layer)
            
            self.logger.debug("Optimal layer order computed", extra={
                "input_layers": layers,
                "output_layers": ordered_layers,
                "operation": "get_optimal_layer_order",
                "phase": "complete"
            })
            
            return ordered_layers
            
        except Exception as e:
            self.logger.error("Layer order computation failed", exc_info=True, extra={
                "input_layers": layers,
                "operation": "get_optimal_layer_order",
                "phase": "failed"
            })
            return layers  # Return original order as fallback

    def _extract_domain_name_from_config(self, config_path: str) -> str:
        """Extract domain name from configuration file."""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Try multiple config formats
            domain_name = (
                config_data.get('domain', {}).get('name') or
                config_data.get('use_case', {}).get('domain') or
                config_data.get('service', {}).get('name') or
                config_data.get('interface', {}).get('domain') or
                'Unknown'
            )
            
            return domain_name
        except Exception:
            # Fallback to extracting from path
            return Path(config_path).parent.name
