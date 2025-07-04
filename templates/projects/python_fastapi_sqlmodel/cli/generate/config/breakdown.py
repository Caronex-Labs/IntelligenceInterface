"""
Configuration Breakdown Engine for Co-Location Architecture.

This module handles the critical "external config → co-located config breakdown" functionality.
External configuration files are "one-time use only" - after breakdown, all future changes
happen through co-located configuration files in the app/domain/{DomainName}/ structure.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime

from .models import EntityDomainConfig

logger = logging.getLogger(__name__)


class ConfigBreakdownEngine:
    """
    Engine for breaking down external configurations into co-located structure.
    
    This implements the core workflow:
    1. External config (configs/external_health.yaml) → One-time use
    2. Breakdown into co-located configs (app/domain/HealthStatus/domain.yaml + entities.yaml)
    3. Future changes happen only in co-located files
    """

    def __init__(self):
        """Initialize the breakdown engine."""
        self.breakdown_metadata = {
            "breakdown_timestamp": datetime.utcnow().isoformat(),
            "breakdown_engine_version": "1.0.0",
            "workflow_type": "external_to_colocated"
        }

    def is_external_config(self, config_path: Path) -> bool:
        """
        Determine if a configuration file is an external config that needs breakdown.
        
        External configs have nested structure: domain: { name: "X" }, entities: [...]
        Co-located configs have flat structure: name: "X", description: "...", package: "..."
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            True if this is an external config file, False if co-located
        """
        try:
            # Load the config to check its structure
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                logger.warning(f"Empty config file {config_path}, treating as co-located")
                return False
            
            # External config: has nested domain.name structure AND entities
            if 'domain' in config_data and 'entities' in config_data:
                domain_section = config_data['domain']
                if isinstance(domain_section, dict) and 'name' in domain_section:
                    logger.info(f"Detected external config: {config_path} (nested domain.name structure)")
                    return True
            
            # Co-located domain config: has name directly at root (not nested under domain)
            if 'name' in config_data and 'domain' not in config_data:
                logger.info(f"Detected co-located domain config: {config_path} (flat name structure)")
                return False
                
            # Co-located entities config: has entities but no nested domain structure  
            if 'entities' in config_data and 'domain' not in config_data:
                logger.info(f"Detected co-located entities config: {config_path} (entities without nested domain)")
                return False
                
            # If it has a nested domain structure but no entities, treat as unclear (default to co-located)
            if 'domain' in config_data and 'entities' not in config_data:
                logger.warning(f"Config has nested domain but no entities: {config_path}, treating as co-located")
                return False
                
            # Default to co-located for safety (most common case)
            logger.warning(f"Unclear config structure in {config_path}, defaulting to co-located")
            return False
            
        except Exception as e:
            logger.error(f"Error analyzing config file {config_path}: {e}")
            # Default to co-located for safety (most common case)
            return False

    def breakdown_external_config(
        self, 
        external_config_path: Path, 
        output_base_dir: Path
    ) -> Tuple[Path, Path, Dict[str, Any]]:
        """
        Break down an external configuration into co-located structure.
        
        Args:
            external_config_path: Path to external config file
            output_base_dir: Base output directory (e.g., ./app)
            
        Returns:
            Tuple of (domain_config_path, entities_config_path, breakdown_info)
        """
        logger.info(f"Breaking down external config: {external_config_path}")
        
        # Load external config
        with open(external_config_path, 'r') as f:
            external_data = yaml.safe_load(f)
        
        # Validate it's actually external config
        if not self.is_external_config(external_config_path):
            raise ValueError(f"Configuration {external_config_path} is not an external config")
        
        # Extract domain information
        domain_info = external_data.get('domain', {})
        domain_name = domain_info.get('name')
        
        if not domain_name:
            raise ValueError("External config must have domain.name specified")
        
        # Create co-located directory structure
        domain_dir = output_base_dir / "domain" / domain_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Split configuration into domain and entities parts
        domain_config, entities_config = self._split_configuration(external_data)
        
        # Add breakdown metadata
        breakdown_info = {
            **self.breakdown_metadata,
            "source_file": str(external_config_path),
            "domain_name": domain_name,
            "breakdown_timestamp": datetime.utcnow().isoformat(),
            "output_directory": str(domain_dir)
        }
        
        domain_config['breakdown_metadata'] = breakdown_info
        entities_config['breakdown_metadata'] = breakdown_info
        
        # Write co-located configs
        domain_config_path = domain_dir / "domain.yaml"
        entities_config_path = domain_dir / "entities.yaml"
        
        with open(domain_config_path, 'w') as f:
            yaml.safe_dump(domain_config, f, default_flow_style=False, sort_keys=False)
        
        with open(entities_config_path, 'w') as f:
            yaml.safe_dump(entities_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info("✅ Breakdown complete:")
        logger.info(f"   📄 Domain config: {domain_config_path}")
        logger.info(f"   📄 Entities config: {entities_config_path}")
        
        return domain_config_path, entities_config_path, breakdown_info

    def _split_configuration(self, external_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Split external configuration into domain and entities parts.
        
        Args:
            external_data: The loaded external configuration
            
        Returns:
            Tuple of (domain_config_dict, entities_config_dict)
        """
        domain_info = external_data.get('domain', {})
        
        # Build domain configuration
        domain_config = {
            'name': domain_info.get('name'),
            'description': domain_info.get('description'),
            'package': domain_info.get('package'),
        }
        
        # Add optional domain fields if present
        if 'plural' in domain_info:
            domain_config['plural'] = domain_info['plural']
        
        # Extract base fields if specified in domain
        if 'base_fields' in domain_info:
            domain_config['base_fields'] = domain_info['base_fields']
        
        # Add default base fields for UUID-based entities
        if 'base_fields' not in domain_config:
            domain_config['base_fields'] = [
                {
                    'name': 'id',
                    'type': 'str',
                    'required': True,
                    'primary_key': True,
                    'sqlmodel_field': 'Field(primary_key=True, default_factory=uuid4)'
                },
                {
                    'name': 'created_at',
                    'type': 'datetime',
                    'required': True,
                    'sqlmodel_field': 'Field(default_factory=datetime.utcnow)'
                },
                {
                    'name': 'updated_at',
                    'type': 'datetime',
                    'required': True,
                    'sqlmodel_field': 'Field(default_factory=datetime.utcnow)'
                }
            ]
        
        # Add SQLModel configuration
        if 'sqlmodel_config' not in domain_config:
            domain_config['sqlmodel_config'] = {
                'table_naming': 'snake_case',
                'field_naming': 'snake_case',
                'generate_id_fields': True,
                'timestamp_fields': ['created_at', 'updated_at']
            }
        
        # Build entities configuration
        entities_config = {}
        
        # Add entities from external config
        if 'entities' in external_data:
            entities_config['entities'] = external_data['entities']
        
        # Add endpoints if present
        if 'endpoints' in external_data:
            entities_config['endpoints'] = external_data['endpoints']
        else:
            # Generate default CRUD endpoints
            entities_config['endpoints'] = [
                {'method': 'POST', 'path': '/', 'operation': 'create', 'description': f'Create a new {domain_info.get("name", "entity").lower()}'},
                {'method': 'GET', 'path': '/{id}', 'operation': 'get_by_id', 'description': f'Get {domain_info.get("name", "entity").lower()} by ID'},
                {'method': 'GET', 'path': '/', 'operation': 'list', 'description': f'List all {domain_info.get("plural", "entities").lower()}'},
                {'method': 'PUT', 'path': '/{id}', 'operation': 'update', 'description': f'Update {domain_info.get("name", "entity").lower()}'},
                {'method': 'DELETE', 'path': '/{id}', 'operation': 'delete', 'description': f'Delete {domain_info.get("name", "entity").lower()}'}
            ]
        
        # Add any additional metadata
        if 'metadata' in external_data:
            entities_config['metadata'] = external_data['metadata']
        
        return domain_config, entities_config

    def load_colocated_config(self, domain_dir: Path) -> EntityDomainConfig:
        """
        Load configuration from co-located files.
        
        Args:
            domain_dir: Path to domain directory containing domain.yaml and entities.yaml
            
        Returns:
            EntityDomainConfig instance with merged configuration
        """
        domain_config_path = domain_dir / "domain.yaml"
        entities_config_path = domain_dir / "entities.yaml"
        
        if not domain_config_path.exists():
            raise FileNotFoundError(f"Domain config not found: {domain_config_path}")
        
        if not entities_config_path.exists():
            raise FileNotFoundError(f"Entities config not found: {entities_config_path}")
        
        # Load domain configuration
        with open(domain_config_path, 'r') as f:
            domain_data = yaml.safe_load(f)
        
        # Load entities configuration
        with open(entities_config_path, 'r') as f:
            entities_data = yaml.safe_load(f)
        
        # Merge configurations into EntityDomainConfig structure
        merged_config = {
            # Domain-level config
            'name': domain_data.get('name'),
            'plural': domain_data.get('plural'),
            'description': domain_data.get('description'),
            'package': domain_data.get('package'),
            
            # Domain-level configurations
            'base_fields': domain_data.get('base_fields', []),
            'mixins': domain_data.get('mixins', []),
            'relationships': domain_data.get('relationships', []),
            'sqlmodel_config': domain_data.get('sqlmodel_config'),
            
            # Entity configurations from entities.yaml
            'entities': entities_data.get('entities', []),
            'endpoints': entities_data.get('endpoints', []),
            'metadata': entities_data.get('metadata', {})
        }
        
        # Add breakdown metadata if present
        if 'breakdown_metadata' in domain_data:
            merged_config['metadata']['breakdown_metadata'] = domain_data['breakdown_metadata']
        elif 'breakdown_metadata' in entities_data:
            merged_config['metadata']['breakdown_metadata'] = entities_data['breakdown_metadata']
        
        logger.info(f"✅ Loaded co-located config from {domain_dir}")
        logger.info(f"   📄 Domain: {merged_config['name']}")
        logger.info(f"   📄 Entities: {len(merged_config['entities'])} entities")
        logger.info(f"   📄 Endpoints: {len(merged_config['endpoints'])} endpoints")
        
        return EntityDomainConfig(**merged_config)

    def get_breakdown_status(self, domain_dir: Path) -> Dict[str, Any]:
        """
        Get breakdown status for a domain directory.
        
        Args:
            domain_dir: Path to domain directory
            
        Returns:
            Dictionary with breakdown status information
        """
        domain_config_path = domain_dir / "domain.yaml"
        entities_config_path = domain_dir / "entities.yaml"
        
        status = {
            'is_colocated': domain_config_path.exists() and entities_config_path.exists(),
            'domain_config_exists': domain_config_path.exists(),
            'entities_config_exists': entities_config_path.exists(),
            'domain_dir': str(domain_dir),
            'breakdown_metadata': None
        }
        
        # Try to load breakdown metadata
        if status['domain_config_exists']:
            try:
                with open(domain_config_path, 'r') as f:
                    domain_data = yaml.safe_load(f)
                    if 'breakdown_metadata' in domain_data:
                        status['breakdown_metadata'] = domain_data['breakdown_metadata']
            except Exception as e:
                logger.warning(f"Could not load breakdown metadata from {domain_config_path}: {e}")
        
        return status