"""
Domain Generation Helper Classes

Provides helper utilities for domain code generation, template processing,
and result management. Integrates with the existing configuration system
and template structure.
"""

import ast
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import jinja2

# Import existing configuration system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.generate.config.loader import ConfigurationLoader, EntityDomainLoader
from cli.generate.config.models import Configuration
from cli.generate.config.configuration_merger import ConfigurationMerger


@dataclass
class FileGenerationResult:
    """Result of generating a single file."""
    file_path: Path
    template_path: str
    success: bool
    content_length: int
    generated_at: datetime
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Complete result of domain generation process."""
    domain_name: str
    output_dir: Path
    success: bool
    generated_files: List[FileGenerationResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    configuration_used: Optional[Dict[str, Any]] = None
    
    @property
    def total_files_generated(self) -> int:
        """Total number of files successfully generated."""
        return len([f for f in self.generated_files if f.success])
    
    @property
    def total_errors(self) -> int:
        """Total number of errors across all files."""
        return len(self.errors) + sum(len(f.errors) for f in self.generated_files)
    
    @property
    def total_warnings(self) -> int:
        """Total number of warnings across all files."""
        return len(self.warnings) + sum(len(f.warnings) for f in self.generated_files)


class TemplateProcessor:
    """Jinja2 template processor for domain generation."""
    
    def __init__(self, template_dir: Path):
        """Initialize template processor with template directory."""
        self.template_dir = template_dir
        self.logger = logging.getLogger(__name__)
        
        # Setup Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['title'] = lambda s: s.title() if s else ""
        self.env.filters['lower'] = lambda s: s.lower() if s else ""
        self.env.filters['upper'] = lambda s: s.upper() if s else ""
    
    def render_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with given context.
        
        Args:
            template_path: Path to template file relative to template_dir
            context: Template variables
            
        Returns:
            Rendered template content
        """
        try:
            template = self.env.get_template(template_path)
            return template.render(**context)
        except jinja2.TemplateError as e:
            self.logger.error(f"Template rendering error for {template_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error rendering {template_path}: {e}")
            raise
    
    def validate_template_syntax(self, template_path: str) -> List[str]:
        """
        Validate template syntax without rendering.
        
        Returns:
            List of syntax errors (empty if valid)
        """
        errors = []
        try:
            template_content = (self.template_dir / template_path).read_text()
            self.env.parse(template_content)
        except jinja2.TemplateSyntaxError as e:
            errors.append(f"Syntax error in {template_path}: {e}")
        except FileNotFoundError:
            errors.append(f"Template not found: {template_path}")
        except Exception as e:
            errors.append(f"Error validating {template_path}: {e}")
        
        return errors


class DomainGeneratorHelper:
    """
    Helper class for domain generation operations.
    
    Integrates with the existing configuration loading system and provides
    utilities for template processing, file generation, and validation.
    """
    
    def __init__(self, template_base_dir: Optional[Path] = None):
        """
        Initialize domain generator helper.
        
        Args:
            template_base_dir: Base directory for templates. Defaults to app/ directory.
        """
        self.logger = logging.getLogger(__name__)
        
        # Set template base directory
        if template_base_dir is None:
            # Default to app/ directory relative to this file
            current_dir = Path(__file__).parent.parent.parent
            self.template_base_dir = current_dir / "app"
        else:
            self.template_base_dir = template_base_dir
            
        self.logger.info(f"Template base directory: {self.template_base_dir}")
        
        # Initialize configuration components
        self.config_loader = ConfigurationLoader()
        self.entity_loader = EntityDomainLoader()
        self.config_merger = ConfigurationMerger()
        
        # Template processors for each layer
        self.template_processors = {}
        self._init_template_processors()
    
    def _init_template_processors(self):
        """Initialize template processors for each architectural layer."""
        layers = ['domain', 'repository', 'usecase', 'interface']
        
        for layer in layers:
            layer_dir = self.template_base_dir / layer
            if layer_dir.exists():
                self.template_processors[layer] = TemplateProcessor(layer_dir)
                self.logger.debug(f"Initialized template processor for {layer} layer")
            else:
                self.logger.warning(f"Template directory not found for {layer} layer: {layer_dir}")
    
    def _create_jinja_processor(self) -> TemplateProcessor:
        """Create Jinja2 processor for application-level templates."""
        return TemplateProcessor(self.template_base_dir)
    
    def load_domain_configuration(self, domain_name: str, config_dir: Path):
        """
        Load complete domain configuration using existing system.
        
        Args:
            domain_name: Name of the domain
            config_dir: Directory containing configuration files
            
        Returns:
            Complete configuration object
        """
        try:
            # Load base configuration
            domain_config_path = config_dir / f"{domain_name}_domain.yaml"
            entities_config_path = config_dir / f"{domain_name}_entities.yaml"
            
            if not domain_config_path.exists():
                # Try alternative naming
                domain_config_path = config_dir / "domain.yaml"
            if not entities_config_path.exists():
                entities_config_path = config_dir / "entities.yaml"
            
            # Use existing entity domain loader
            configuration = self.entity_loader.load_from_files(
                domain_file=domain_config_path,
                entities_file=entities_config_path
            )
            
            self.logger.info(f"Loaded configuration for domain: {domain_name}")
            return configuration
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration for {domain_name}: {e}")
            raise
    
    def generate_layer_files(
        self, 
        layer: str, 
        domain_name: str, 
        configuration: Configuration,
        output_dir: Path
    ) -> List[FileGenerationResult]:
        """
        Generate files for a specific architectural layer.
        
        Args:
            layer: Layer name (domain, repository, usecase, interface)
            domain_name: Domain name for generation
            configuration: Complete configuration object
            output_dir: Output directory for generated files
            
        Returns:
            List of file generation results
        """
        results = []
        
        if layer not in self.template_processors:
            self.logger.error(f"No template processor for layer: {layer}")
            return results
        
        processor = self.template_processors[layer]
        layer_output_dir = output_dir / layer / domain_name
        layer_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get template files for this layer
        template_files = self._get_layer_template_files(layer, domain_name)
        
        # Build comprehensive template context from loaded configuration
        # Handle both Configuration (with nested domain) and EntityDomainConfig (flat structure)
        if hasattr(configuration, 'domain') and configuration.domain is not None:
            # Configuration model with nested domain
            domain_info = configuration.domain
            domain_plural = getattr(domain_info, 'plural', None) or domain_info.get('plural', f"{domain_name}s") if isinstance(domain_info, dict) else getattr(domain_info, 'plural', f"{domain_name}s")
        else:
            # EntityDomainConfig model with flat structure or dictionary
            if isinstance(configuration, dict):
                domain_plural = configuration.get('domain', {}).get('plural', f"{domain_name}s")
                domain_info = configuration.get('domain', {})
            else:
                domain_plural = getattr(configuration, 'plural', f"{domain_name}s")
                domain_info = configuration
        
        entities_list = getattr(configuration, 'entities', []) if not isinstance(configuration, dict) else configuration.get('entities', [])
        
        # Helper function to get attribute from object or dict
        def get_attr_or_key(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            else:
                return getattr(obj, key, default)
        
        context = {
            'domain': domain_name,  # Templates expect domain as string for {{domain|title}} filter
            'domain_name_plural': domain_plural,  # For {{domain_name_plural|title}} filters
            'domain_info': {
                'name': get_attr_or_key(domain_info, 'name', domain_name),
                'title': get_attr_or_key(domain_info, 'name', domain_name).title(),
                'plural': domain_plural,
                'description': get_attr_or_key(domain_info, 'description', ''),
                'package': get_attr_or_key(domain_info, 'package', domain_name)
            },
            'configuration': configuration,
            'entities': entities_list,
            'relationships': getattr(configuration, 'relationships', []),
            'template_context': {
                'features': {
                    'enable_audit_log': True,
                    'enable_caching': False,
                    'enable_full_text_search': False,
                    'enable_soft_delete': True,
                    'enable_validation': True
                },
                'database': {
                    'provider': 'postgresql',
                    'dialect': 'asyncpg'
                },
                'integration': {
                    'enable_api_docs': True,
                    'enable_testing': True,
                    'enable_logging': True
                }
            },
            # Add missing template variables - comprehensive set to satisfy all templates
            'integration': {
                'enable_api_docs': True,
                'enable_testing': True,
                'enable_logging': True,
                'pydantic': {
                    'validate_assignment': True,
                    'use_enum_values': True,
                    'allow_population_by_field_name': True
                },
                'style': {
                    'line_length': 88,
                    'code_formatting': 'black'
                },
                'performance': {
                    'enable_caching': False,
                    'enable_profiling': False
                },
                'transactions': {
                    'enable_rollback': True,
                    'isolation_level': 'READ_COMMITTED'
                },
                'fastapi': {
                    'enable_openapi': True,
                    'enable_cors': True,
                    'enable_middleware': True
                }
            },
            'primary_key': {
                'default_factory': 'uuid4',
                'description': 'Primary key'
            },
            'timestamps': {
                'created_at': {'default_factory': 'datetime.utcnow'},
                'updated_at': {'default_factory': 'datetime.utcnow'}
            },
            'style': {
                'line_length': 88,
                'code_formatting': 'black'
            },
            'performance': {
                'enable_caching': False,
                'enable_profiling': False
            },
            'transactions': {
                'enable_rollback': True,
                'isolation_level': 'READ_COMMITTED'
            }
        }
        
        # Add layer-specific context
        if layer == 'domain':
            # For domain layer, process entities and their fields with SQLModel field configuration
            processed_entities = []
            primary_entity = None
            
            for entity in entities_list:
                # Handle both entity objects and dictionaries
                if hasattr(entity, 'dict'):
                    entity_dict = entity.dict()
                elif hasattr(entity, '__dict__'):
                    entity_dict = entity.__dict__.copy()
                else:
                    entity_dict = entity if isinstance(entity, dict) else {}
                
                # Process entity fields with SQLModel configuration
                processed_fields = []
                entity_fields = entity_dict.get('fields', [])
                
                for field in entity_fields:
                    # Process field configuration to extract SQLModel Field() parameters
                    field_config = self._process_field_configuration(field)
                    
                    # Create enhanced field dict with both original and processed config
                    enhanced_field = {
                        # Original field data
                        **(field.dict() if hasattr(field, 'dict') else (field.__dict__ if hasattr(field, '__dict__') else field)),
                        # Processed configuration
                        'field_config': field_config,
                        'python_type': field_config['python_type'],
                        'sqlmodel_field_params': field_config['sqlmodel_field_params'],
                        'has_default': field_config['has_default'],
                        'is_required': field_config['is_required']
                    }
                    
                    processed_fields.append(enhanced_field)
                
                # Create processed entity with enhanced fields
                processed_entity = {
                    **entity_dict,
                    'fields': processed_fields
                }
                
                processed_entities.append(processed_entity)
                
                # Set primary entity (first one)
                if primary_entity is None:
                    primary_entity = processed_entity
            
            # Update context with processed entities
            context['entities'] = processed_entities
            
            context.update({
                'entity': primary_entity,  # Single entity for templates that expect this
                'entity_config': getattr(configuration, 'entity_config', {}),
                'mixins': getattr(configuration, 'mixins', {}),
                'base_fields': getattr(configuration, 'base_fields', {}),
                'domain_relationships': getattr(configuration, 'domain_relationships', []),
                'generation': {
                    'methods': [],
                    'enabled': True,
                    'style': {
                        'use_type_hints': True,
                        'line_length': 88
                    }
                },
                # Add common template variables
                'field_types': {
                    'str': {'python_type': 'str', 'sqlmodel_type': 'str'},
                    'int': {'python_type': 'int', 'sqlmodel_type': 'int'},
                    'float': {'python_type': 'float', 'sqlmodel_type': 'float'},
                    'bool': {'python_type': 'bool', 'sqlmodel_type': 'bool'},
                    'datetime': {'python_type': 'datetime', 'sqlmodel_type': 'datetime'},
                    'Optional[str]': {'python_type': 'Optional[str]', 'sqlmodel_type': 'Optional[str]'},
                    'EmailStr': {'python_type': 'EmailStr', 'sqlmodel_type': 'EmailStr'},
                    'List[str]': {'python_type': 'List[str]', 'sqlmodel_type': 'List[str]'}
                }
            })
        elif layer == 'repository':
            # For repository layer, add the first entity as the primary entity context
            primary_entity = entities_list[0] if entities_list else None
            # Extract actual entity name from configuration, not domain name
            if primary_entity:
                if hasattr(primary_entity, 'name'):
                    primary_entity_name = primary_entity.name
                elif isinstance(primary_entity, dict):
                    primary_entity_name = primary_entity.get('name', domain_name.title())
                else:
                    primary_entity_name = getattr(primary_entity, 'name', domain_name.title())
            else:
                primary_entity_name = domain_name.title()
            
            context.update({
                'entity': primary_entity,  # Single entity for templates that expect this
                'entity_name': primary_entity_name,  # For {{entity_name}} template variable
                'primary_entity_name': primary_entity_name,  # For {{primary_entity_name}} template variable
                'repository': {
                    'name': f"{domain_name.title()}Repository",
                    'description': f"Async repository for {primary_entity_name} entity data access",
                    'interface': f"{primary_entity_name}RepositoryProtocol",
                    'implementation': f"SQLModel{primary_entity_name}Repository",
                    'package': f"app.repository.{domain_name}",
                    'version': "1.0.0",
                    'crud_operations': {
                        'create': {
                            'enabled': True,
                            'validation': True,
                            'return_created': True,
                            'auto_refresh': True,
                            'business_rules_validation': True,
                            'duplicate_handling': 'raise_error'
                        },
                        'read': {
                            'enabled': True,
                            'soft_delete_aware': True,
                            'eager_loading': False,
                            'relationship_loading': 'lazy',
                            'cache_results': False,
                            'include_deleted': False
                        },
                        'update': {
                            'enabled': True,
                            'partial_updates': True,
                            'optimistic_locking': False,
                            'auto_refresh': True,
                            'business_rules_validation': True,
                            'track_changes': True
                        },
                        'delete': {
                            'enabled': True,
                            'soft_delete': True,
                            'hard_delete': False,
                            'cascade_handling': True,
                            'orphan_removal': False,
                            'business_rules_validation': True
                        },
                        'list': {
                            'enabled': True,
                            'pagination': True,
                            'filtering': True,
                            'sorting': True,
                            'search': True,
                            'max_page_size': 100,
                            'default_page_size': 20,
                            'max_total_results': 10000
                        }
                    },
                    'async_operations': {
                        'enabled': True,
                        'session_management': 'dependency_injection',
                        'connection_pooling': True,
                        'transaction_support': True,
                        'connection_timeout': 30,
                        'query_timeout': 60,
                        'max_retries': 3,
                        'retry_delay': 1.0
                    },
                    'database': {
                        'provider': 'postgresql', 
                        'dialect': 'asyncpg',
                        'migration_support': True,
                        'schema_validation': True,
                        'connection_pool': {
                            'min_size': 5,
                            'max_size': 20,
                            'overflow': 30,
                            'timeout': 30
                        },
                        'session_config': {
                            'autocommit': False,
                            'autoflush': True,
                            'expire_on_commit': True
                        }
                    },
                    'caching': {
                        'enabled': False,
                        'backend': 'redis',
                        'default_ttl': 300,
                        'cache_key_prefix': f"{domain_name}_repo",
                        'invalidation_patterns': ['on_create', 'on_update', 'on_delete']
                    },
                    'performance': {
                        'query_logging': True,
                        'slow_query_threshold': 1.0,
                        'explain_analyze': False,
                        'connection_pooling': True,
                        'prepared_statements': True,
                        'batch_operations': True,
                        'bulk_operations': {
                            'batch_size': 1000,
                            'use_bulk_insert': True,
                            'use_bulk_update': True
                        },
                        'query_performance': {
                            'max_execution_time': 1.0,
                            'connection_pool_efficiency': 0.8,
                            'cache_hit_ratio': 0.7
                        }
                    },
                    'transactions': {
                        'auto_transaction': True,
                        'isolation_level': 'READ_COMMITTED',
                        'timeout': 30,
                        'rollback_on_error': True,
                        'savepoint_support': True,
                        'nested_transactions': False
                    },
                    'error_handling': {
                        'retry_on_connection_error': True,
                        'retry_attempts': 3,
                        'retry_delay': 1.0,
                        'log_errors': True,
                        'raise_on_constraint_violation': True,
                        'raise_on_not_found': False,
                        'custom_exceptions': [
                            {
                                'name': f"{primary_entity_name}NotFoundError",
                                'base': 'ValueError',
                                'message': f"{primary_entity_name} not found"
                            },
                            {
                                'name': f"{primary_entity_name}DuplicateError",
                                'base': 'ValueError', 
                                'message': f"{primary_entity_name} already exists"
                            },
                            {
                                'name': f"{primary_entity_name}ValidationError",
                                'base': 'ValueError',
                                'message': f"{primary_entity_name} validation failed"
                            }
                        ]
                    },
                    'query_methods': [
                        {
                            'name': 'find_by_id',
                            'description': f"Find {domain_name} by unique identifier",
                            'parameters': [
                                {'name': 'entity_id', 'type': 'UUID', 'required': True}
                            ],
                            'return_type': f"Optional[{primary_entity_name}]",
                            'query_type': 'single',
                            'cache': False,
                            'eager_load': []
                        },
                        {
                            'name': 'find_by_email',
                            'description': f"Find {domain_name} by email address",
                            'parameters': [
                                {'name': 'email', 'type': 'str', 'required': True}
                            ],
                            'return_type': f"Optional[{primary_entity_name}]",
                            'query_type': 'single',
                            'cache': True,
                            'cache_ttl': 300,
                            'unique_constraint': True
                        },
                        {
                            'name': 'find_active_entities',
                            'description': f"Find all active {domain_name} entities",
                            'parameters': [],
                            'return_type': f"List[{primary_entity_name}]",
                            'query_type': 'list',
                            'filters': [
                                {'field': 'status', 'operator': 'eq', 'value': 'active'}
                            ],
                            'soft_delete_aware': True
                        },
                        {
                            'name': 'find_by_status',
                            'description': f"Find {domain_name} entities by status",
                            'parameters': [
                                {
                                    'name': 'status',
                                    'type': 'str',
                                    'required': True,
                                    'validation': {
                                        'choices': ['active', 'inactive', 'pending']
                                    }
                                }
                            ],
                            'return_type': f"List[{primary_entity_name}]",
                            'query_type': 'list',
                            'cache': False
                        },
                        {
                            'name': 'count_by_status',
                            'description': f"Count {domain_name} entities by status",
                            'parameters': [
                                {'name': 'status', 'type': 'str', 'required': True}
                            ],
                            'return_type': 'int',
                            'query_type': 'aggregate',
                            'aggregate_function': 'count'
                        },
                        {
                            'name': 'search_by_name',
                            'description': f"Search {domain_name} entities by name using full-text search",
                            'parameters': [
                                {
                                    'name': 'search_term',
                                    'type': 'str',
                                    'required': True,
                                    'validation': {
                                        'min_length': 2,
                                        'max_length': 100
                                    }
                                }
                            ],
                            'return_type': f"List[{primary_entity_name}]",
                            'query_type': 'search',
                            'search_fields': ['name'],
                            'search_type': 'ilike'
                        }
                    ]
                }
            })
        elif layer == 'usecase':
            # For usecase layer, create comprehensive context for business logic orchestration
            primary_entity = entities_list[0] if entities_list else None
            # Extract actual entity name from configuration, not domain name
            if primary_entity:
                if hasattr(primary_entity, 'name'):
                    primary_entity_name = primary_entity.name
                elif isinstance(primary_entity, dict):
                    primary_entity_name = primary_entity.get('name', domain_name.title())
                else:
                    primary_entity_name = getattr(primary_entity, 'name', domain_name.title())
            else:
                primary_entity_name = domain_name.title()
            
            # Create comprehensive usecase configuration based on User domain test config
            usecase_context = {
                'name': f"{domain_name.title()}Management",
                'description': f"{primary_entity_name} management use case orchestration",
                'methods': [
                    {
                        'name': f'create_{domain_name}',
                        'input_schema': f'Create{primary_entity_name}Request',
                        'output_schema': f'{primary_entity_name}Response',
                        'transaction_boundary': True,
                        'dependencies': {
                            'repositories': [f'{domain_name}_repository'],
                            'services': ['validation_service', 'audit_service']
                        },
                        'business_rules': ['data_validation', 'business_constraints'],
                        'orchestration_steps': [
                            f'validate_{domain_name}_data',
                            f'create_{domain_name}_record',
                            f'publish_{domain_name}_created_event'
                        ],
                        'description': f'Create a new {domain_name} with comprehensive validation'
                    },
                    {
                        'name': f'get_{domain_name}_by_id',
                        'input_schema': f'Get{primary_entity_name}Request',
                        'output_schema': f'{primary_entity_name}Response',
                        'transaction_boundary': False,
                        'dependencies': {
                            'repositories': [f'{domain_name}_repository']
                        },
                        'business_rules': [f'{domain_name}_exists', 'access_permitted'],
                        'orchestration_steps': [
                            'validate_access_permissions',
                            f'retrieve_{domain_name}_data'
                        ],
                        'description': f'Retrieve {domain_name} by ID with access control validation'
                    },
                    {
                        'name': f'update_{domain_name}',
                        'input_schema': f'Update{primary_entity_name}Request',
                        'output_schema': f'{primary_entity_name}Response',
                        'transaction_boundary': True,
                        'dependencies': {
                            'repositories': [f'{domain_name}_repository'],
                            'services': ['validation_service', 'audit_service']
                        },
                        'business_rules': [f'{domain_name}_exists', 'update_allowed', 'data_integrity'],
                        'orchestration_steps': [
                            'validate_update_permissions',
                            'validate_update_data',
                            f'update_{domain_name}_record',
                            f'publish_{domain_name}_updated_event'
                        ],
                        'description': f'Update {domain_name} with permission checks and audit logging'
                    },
                    {
                        'name': f'delete_{domain_name}',
                        'input_schema': f'Delete{primary_entity_name}Request',
                        'output_schema': 'DeleteResponse',
                        'transaction_boundary': True,
                        'dependencies': {
                            'repositories': [f'{domain_name}_repository'],
                            'services': ['audit_service']
                        },
                        'business_rules': [f'{domain_name}_exists', 'deletion_allowed'],
                        'orchestration_steps': [
                            'validate_deletion_permissions',
                            f'delete_{domain_name}_record',
                            f'publish_{domain_name}_deleted_event'
                        ],
                        'description': f'Delete {domain_name} with validation and audit logging'
                    }
                ],
                'dependencies': {
                    'repositories': [f'{domain_name}_repository'],
                    'services': ['validation_service', 'audit_service'],
                    'external_apis': []
                },
                'error_handling': {
                    'aggregation_strategy': 'collect_all_errors',
                    'early_termination': False,
                    'custom_exceptions': [
                        {
                            'rule': 'data_validation',
                            'exception': f'{primary_entity_name}ValidationError'
                        },
                        {
                            'rule': f'{domain_name}_exists',
                            'exception': f'{primary_entity_name}NotFoundError'
                        }
                    ]
                },
                'service_composition': {
                    'transaction_manager': 'database_transaction_manager',
                    'event_publisher': 'domain_event_publisher',
                    'logger': 'structured_logger'
                }
            }
            
            # Create comprehensive business rules configuration
            business_rules_context = {
                'rules': [
                    {
                        'name': 'data_validation',
                        'type': 'validation',
                        'condition': f'{domain_name}_data.is_valid and {domain_name}_data.fields_are_complete',
                        'error_message': f'{primary_entity_name} data validation failed - invalid or incomplete data',
                        'severity': 'error',
                        'context': f'{domain_name}_management',
                        'custom_exception': f'{primary_entity_name}ValidationError'
                    },
                    {
                        'name': f'{domain_name}_exists',
                        'type': 'constraint',
                        'condition': f'{domain_name}.id exists in database',
                        'error_message': f'{primary_entity_name} not found in the system',
                        'severity': 'error',
                        'context': f'{domain_name}_management',
                        'custom_exception': f'{primary_entity_name}NotFoundError'
                    },
                    {
                        'name': 'update_allowed',
                        'type': 'business_logic',
                        'condition': f'{domain_name}.can_be_updated and not {domain_name}.is_locked',
                        'error_message': f'{primary_entity_name} update not allowed for this record',
                        'severity': 'error',
                        'context': f'{domain_name}_management',
                        'custom_exception': f'{primary_entity_name}UpdateNotAllowedError'
                    },
                    {
                        'name': 'access_permitted',
                        'type': 'security',
                        'condition': f'user_context.can_access_{domain_name}({domain_name}.id)',
                        'error_message': f'Access denied to {domain_name} information',
                        'severity': 'error',
                        'context': f'{domain_name}_management',
                        'custom_exception': 'AccessDeniedError'
                    },
                    {
                        'name': 'business_constraints',
                        'type': 'validation',
                        'condition': f'{domain_name}_data.meets_business_requirements',
                        'error_message': f'{primary_entity_name} does not meet business requirements',
                        'severity': 'error',
                        'context': f'{domain_name}_management',
                        'custom_exception': 'BusinessConstraintViolationError'
                    },
                    {
                        'name': 'deletion_allowed',
                        'type': 'business_logic',
                        'condition': f'{domain_name}.can_be_deleted and not {domain_name}.has_dependencies',
                        'error_message': f'{primary_entity_name} cannot be deleted due to constraints',
                        'severity': 'error',
                        'context': f'{domain_name}_management',
                        'custom_exception': f'{primary_entity_name}DeletionNotAllowedError'
                    },
                    {
                        'name': 'data_integrity',
                        'type': 'constraint',
                        'condition': 'updated_data.maintains_referential_integrity',
                        'error_message': 'Data update would violate referential integrity constraints',
                        'severity': 'error',
                        'context': f'{domain_name}_management',
                        'custom_exception': 'DataIntegrityError'
                    }
                ],
                'validation_groups': [
                    {
                        'name': f'{domain_name}_creation',
                        'rules': ['data_validation', 'business_constraints'],
                        'execution_order': ['data_validation', 'business_constraints'],
                        'description': f'Comprehensive validation rules for {domain_name} creation process'
                    },
                    {
                        'name': f'{domain_name}_access',
                        'rules': [f'{domain_name}_exists', 'access_permitted'],
                        'execution_order': [f'{domain_name}_exists', 'access_permitted'],
                        'description': f'Validation rules for {domain_name} access operations'
                    },
                    {
                        'name': f'{domain_name}_modification',
                        'rules': [f'{domain_name}_exists', 'update_allowed', 'data_integrity'],
                        'execution_order': [f'{domain_name}_exists', 'update_allowed', 'data_integrity'],
                        'description': f'Validation rules for {domain_name} modification operations'
                    },
                    {
                        'name': f'{domain_name}_deletion',
                        'rules': [f'{domain_name}_exists', 'deletion_allowed'],
                        'execution_order': [f'{domain_name}_exists', 'deletion_allowed'],
                        'description': f'Validation rules for {domain_name} deletion operations'
                    }
                ],
                'error_handling': {
                    'aggregation_strategy': 'collect_all_errors',
                    'early_termination': False,
                    'custom_exceptions': [
                        {
                            'rule': 'data_validation',
                            'exception': f'{primary_entity_name}ValidationError'
                        },
                        {
                            'rule': f'{domain_name}_exists',
                            'exception': f'{primary_entity_name}NotFoundError'
                        },
                        {
                            'rule': 'update_allowed',
                            'exception': f'{primary_entity_name}UpdateNotAllowedError'
                        },
                        {
                            'rule': 'access_permitted',
                            'exception': 'AccessDeniedError'
                        },
                        {
                            'rule': 'business_constraints',
                            'exception': 'BusinessConstraintViolationError'
                        },
                        {
                            'rule': 'deletion_allowed',
                            'exception': f'{primary_entity_name}DeletionNotAllowedError'
                        },
                        {
                            'rule': 'data_integrity',
                            'exception': 'DataIntegrityError'
                        }
                    ]
                }
            }
            
            context.update({
                'entity': primary_entity,  # Single entity for templates that expect this
                'entity_name': primary_entity_name,  # For {{entity_name}} template variable
                'primary_entity_name': primary_entity_name,  # For {{primary_entity_name}} template variable
                'usecase': usecase_context,
                'business_rules': business_rules_context,
                # Note: domain_name_plural is already set in the main context above
            })
        elif layer == 'interface':
            # For interface layer, create comprehensive context for FastAPI router generation
            primary_entity = entities_list[0] if entities_list else None
            # Extract actual entity name from configuration, not domain name
            if primary_entity:
                if hasattr(primary_entity, 'name'):
                    primary_entity_name = primary_entity.name
                elif isinstance(primary_entity, dict):
                    primary_entity_name = primary_entity.get('name', domain_name.title())
                else:
                    primary_entity_name = getattr(primary_entity, 'name', domain_name.title())
            else:
                primary_entity_name = domain_name.title()
            
            # Create comprehensive interface configuration for FastAPI endpoints
            interface_context = {
                'name': f"{domain_name.title()}API",
                'version': "1.0.0",
                'description': f"REST API for {primary_entity_name} operations",
                'api': {
                    'prefix': f"/api/v1/{domain_plural}",
                    'tags': [domain_plural],
                    'include_in_schema': True
                },
                'endpoints': [
                    {
                        'method': 'POST',
                        'path': '/',
                        'operation_id': f'create_{domain_name}',
                        'summary': f'Create a new {domain_name}',
                        'description': f'Create a new {domain_name} with the provided data',
                        'request_model': f'Create{primary_entity_name}Request',
                        'response_model': f'{primary_entity_name}Response',
                        'status_code': 201,
                        'authentication_required': True,
                        'permissions': ['create'],
                        'rate_limit': {'requests': 10, 'window': 60}
                    },
                    {
                        'method': 'GET',
                        'path': f'/{{{domain_name}_id}}',
                        'operation_id': f'get_{domain_name}_by_id',
                        'summary': f'Get {domain_name} by ID',
                        'description': f'Retrieve a specific {domain_name} by its unique identifier',
                        'response_model': f'{primary_entity_name}Response',
                        'status_code': 200,
                        'authentication_required': True,
                        'permissions': ['read'],
                        'cache': {'enabled': True, 'ttl': 300}
                    },
                    {
                        'method': 'PUT',
                        'path': f'/{{{domain_name}_id}}',
                        'operation_id': f'update_{domain_name}',
                        'summary': f'Update {domain_name}',
                        'description': f'Update an existing {domain_name} with new data',
                        'request_model': f'Update{primary_entity_name}Request',
                        'response_model': f'{primary_entity_name}Response',
                        'status_code': 200,
                        'authentication_required': True,
                        'permissions': ['update']
                    },
                    {
                        'method': 'DELETE',
                        'path': f'/{{{domain_name}_id}}',
                        'operation_id': f'delete_{domain_name}',
                        'summary': f'Delete {domain_name}',
                        'description': f'Delete an existing {domain_name}',
                        'response_model': 'DeleteResponse',
                        'status_code': 200,
                        'authentication_required': True,
                        'permissions': ['delete']
                    },
                    {
                        'method': 'GET',
                        'path': '/',
                        'operation_id': f'list_{domain_plural}',
                        'summary': f'List {domain_plural}',
                        'description': f'Retrieve a list of {domain_plural} with optional filtering and pagination',
                        'response_model': f'List{domain_plural.title()}Response',
                        'status_code': 200,
                        'authentication_required': True,
                        'permissions': ['list'],
                        'parameters': [
                            {'name': 'skip', 'type': 'query', 'description': 'Number of items to skip', 'default': 0, 'minimum': 0},
                            {'name': 'limit', 'type': 'query', 'description': 'Maximum number of items to return', 'default': 100, 'minimum': 1, 'maximum': 1000},
                            {'name': 'search', 'type': 'query', 'description': 'Search term for filtering', 'required': False},
                            {'name': 'status', 'type': 'query', 'description': 'Filter by status', 'required': False}
                        ]
                    }
                ],
                'authentication': {
                    'enabled': True,
                    'scheme': 'Bearer',
                    'auto_error': False,
                    'description': 'JWT Bearer token authentication'
                },
                'authorization': {
                    'enabled': True,
                    'default_permissions': ['read'],
                    'admin_roles': ['admin', f'{domain_name}_admin', 'super_admin']
                },
                'rate_limiting': {
                    'enabled': True,
                    'default_limit': 100,
                    'default_window': 60,
                    'identifier': 'ip_address'
                },
                'caching': {
                    'enabled': True,
                    'default_ttl': 300,
                    'cache_key_prefix': f'{domain_name}_api'
                },
                'middleware': {
                    'cors': {
                        'enabled': True,
                        'allow_origins': ['*'],
                        'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                        'allow_headers': ['*'],
                        'allow_credentials': True
                    },
                    'compression': {'enabled': True, 'minimum_size': 1000},
                    'request_logging': {'enabled': True, 'include_headers': False, 'include_body': False},
                    'response_time': {'enabled': True, 'header_name': 'X-Response-Time'}
                },
                'error_handling': {
                    'include_stack_trace': False,
                    'log_errors': True,
                    'custom_error_handlers': [
                        {'exception': f'{primary_entity_name}ValidationError', 'status_code': 400, 'message': 'Validation failed'},
                        {'exception': f'{primary_entity_name}NotFoundError', 'status_code': 404, 'message': 'Resource not found'},
                        {'exception': 'BusinessConstraintViolationError', 'status_code': 422, 'message': 'Business rule violation'},
                        {'exception': 'UnauthorizedOperationError', 'status_code': 403, 'message': 'Access denied'}
                    ]
                },
                'openapi': {
                    'title': f'{primary_entity_name} API',
                    'description': f'REST API for managing {primary_entity_name} resources',
                    'version': '1.0.0',
                    'contact': {'name': 'API Support', 'email': 'api-support@example.com'},
                    'license': {'name': 'MIT', 'url': 'https://opensource.org/licenses/MIT'},
                    'tags': [{'name': domain_plural, 'description': f'{primary_entity_name} operations'}],
                    'servers': [
                        {'url': 'http://localhost:8000', 'description': 'Development server'},
                        {'url': 'https://api.example.com', 'description': 'Production server'}
                    ]
                },
                'health_check': {'enabled': True, 'path': '/health', 'include_in_schema': False},
                'metrics': {'enabled': True, 'path': '/metrics', 'include_in_schema': False, 'collect_request_metrics': True, 'collect_error_metrics': True},
                'security': {
                    'include_security_headers': True,
                    'content_security_policy': "default-src 'self'",
                    'x_frame_options': 'DENY',
                    'x_content_type_options': 'nosniff'
                }
            }
            
            context.update({
                'entity': primary_entity,  # Single entity for templates that expect this
                'entity_name': primary_entity_name,  # For {{entity_name}} template variable
                'primary_entity_name': primary_entity_name,  # For {{primary_entity_name}} template variable
                'interface': interface_context,
                # Note: domain_name_plural is already set in the main context above
            })
        
        # Generate each template file
        for template_file in template_files:
            try:
                result = self._generate_single_file(
                    processor, template_file, context, layer_output_dir
                )
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Failed to generate {template_file}: {e}")
                results.append(FileGenerationResult(
                    file_path=layer_output_dir / template_file.replace('.j2', ''),
                    template_path=template_file,
                    success=False,
                    content_length=0,
                    generated_at=datetime.now(),
                    errors=[str(e)]
                ))
        
        return results
    
    def _get_layer_template_files(self, layer: str, domain_name: str) -> List[str]:
        """Get list of template files for a specific layer."""
        layer_template_dir = self.template_base_dir / layer / "{{domain}}"
        
        if not layer_template_dir.exists():
            self.logger.warning(f"Template directory not found: {layer_template_dir}")
            return []
        
        # Find all .j2 template files
        template_files = []
        for template_path in layer_template_dir.glob("*.j2"):
            # Use relative path from layer directory
            relative_path = f"{{{{domain}}}}/{template_path.name}"
            template_files.append(relative_path)
        
        return template_files
    
    def _generate_single_file(
        self, 
        processor: TemplateProcessor, 
        template_file: str,
        context: Dict[str, Any],
        output_dir: Path
    ) -> FileGenerationResult:
        """Generate a single file from template."""
        start_time = datetime.now()
        
        # Determine output filename (remove .j2 extension)
        output_filename = template_file.replace('{{domain}}/', '').replace('.j2', '')
        output_path = output_dir / output_filename
        
        try:
            # Render template
            content = processor.render_template(template_file, context)
            
            # Write file first so we can validate it
            output_path.write_text(content)
            
            # Validate generated Python code
            validation_results = self._validate_generated_code(content, output_filename, output_path)
            
            return FileGenerationResult(
                file_path=output_path,
                template_path=template_file,
                success=True,
                content_length=len(content),
                generated_at=start_time,
                warnings=validation_results.get('warnings', []),
                validation_results=validation_results
            )
            
        except Exception as e:
            return FileGenerationResult(
                file_path=output_path,
                template_path=template_file,
                success=False,
                content_length=0,
                generated_at=start_time,
                errors=[str(e)]
            )
    
    def _validate_generated_code(self, content: str, filename: str, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Validate generated Python code using comprehensive validation."""
        results = {
            'syntax_valid': False,
            'ast_parsed': False,
            'imports_valid': True,
            'warnings': [],
            'errors': [],
            'validation_details': {}
        }
        
        if not filename.endswith('.py'):
            # Non-Python file, skip validation
            results['syntax_valid'] = True
            return results
        
        # If we have an output path, use enhanced validation
        if output_path and output_path.exists():
            try:
                from cli.validate import validate_generated_python_file, validate_imports_in_file
                
                # AST and syntax validation
                syntax_errors = validate_generated_python_file(output_path)
                syntax_error_count = sum(1 for e in syntax_errors if e.severity == "error")
                syntax_warning_count = sum(1 for e in syntax_errors if e.severity == "warning")
                
                results['syntax_valid'] = syntax_error_count == 0
                results['ast_parsed'] = syntax_error_count == 0
                
                # Collect syntax errors and warnings
                for error in syntax_errors:
                    if error.severity == "error":
                        results['errors'].append(f"Line {error.line_number}: {error.message}")
                    elif error.severity == "warning":
                        results['warnings'].append(f"Line {error.line_number}: {error.message}")
                
                # Import validation
                if output_path.parent.parent.exists():  # Project root should be 2 levels up
                    project_root = output_path.parent.parent
                    import_errors = validate_imports_in_file(output_path, project_root)
                    import_error_count = sum(1 for e in import_errors if e.severity == "error")
                    
                    results['imports_valid'] = import_error_count == 0
                    
                    # Collect import errors
                    for error in import_errors:
                        if error.severity == "error":
                            results['errors'].append(f"Import error: {error.message}")
                        elif error.severity == "warning":
                            results['warnings'].append(f"Import warning: {error.message}")
                
                # Store detailed validation results
                results['validation_details'] = {
                    'syntax_errors': len([e for e in syntax_errors if e.severity == "error"]),
                    'syntax_warnings': len([e for e in syntax_errors if e.severity == "warning"]),
                    'import_errors': len([e for e in import_errors if e.severity == "error"]) if 'import_errors' in locals() else 0,
                    'import_warnings': len([e for e in import_errors if e.severity == "warning"]) if 'import_errors' in locals() else 0
                }
                
            except ImportError:
                # Fallback to basic validation if enhanced validation not available
                self.logger.warning("Enhanced validation not available, falling back to basic validation")
                return self._basic_validate_generated_code(content, filename)
            except Exception as e:
                self.logger.warning(f"Enhanced validation failed, falling back to basic validation: {e}")
                return self._basic_validate_generated_code(content, filename)
        else:
            # Fallback to basic validation
            return self._basic_validate_generated_code(content, filename)
        
        return results
    
    def _basic_validate_generated_code(self, content: str, filename: str) -> Dict[str, Any]:
        """Basic validation fallback for generated Python code."""
        results = {
            'syntax_valid': False,
            'ast_parsed': False,
            'imports_valid': True,
            'warnings': [],
            'errors': [],
            'validation_details': {}
        }
        
        if not filename.endswith('.py'):
            # Non-Python file, skip validation
            results['syntax_valid'] = True
            return results
        
        try:
            # Parse AST to validate syntax
            ast.parse(content)
            results['syntax_valid'] = True
            results['ast_parsed'] = True
            
        except SyntaxError as e:
            results['errors'].append(f"Syntax error: {e}")
        except Exception as e:
            results['errors'].append(f"AST parsing error: {e}")
        
        # Basic code quality checks
        if 'TODO' in content:
            results['warnings'].append("Contains TODO comments")
        
        if content.count('\n') < 10:
            results['warnings'].append("Generated file is very short")
        
        # Check for unresolved template variables
        import re
        template_patterns = [r'\{\{.*?\}\}', r'\{%.*?%\}']
        for pattern in template_patterns:
            if re.search(pattern, content):
                results['errors'].append("Contains unresolved template variables")
                break
        
        return results
    
    def validate_generated_files(self, output_files: List[Path], project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Comprehensive validation of all generated files.
        
        Args:
            output_files: List of generated file paths
            project_root: Root directory of the project for import resolution
            
        Returns:
            Comprehensive validation report
        """
        validation_report = {
            'total_files': len(output_files),
            'python_files': 0,
            'syntax_errors': 0,
            'import_errors': 0,
            'warnings': 0,
            'files_with_errors': [],
            'validation_details': {},
            'summary': '',
            'success': True
        }
        
        try:
            from cli.validate import validate_generated_python_file, validate_imports_in_file
            
            python_files = [f for f in output_files if f.suffix == '.py' and f.exists()]
            validation_report['python_files'] = len(python_files)
            
            total_syntax_errors = 0
            total_import_errors = 0
            total_warnings = 0
            
            for file_path in python_files:
                file_report = {
                    'syntax_errors': [],
                    'import_errors': [],
                    'warnings': [],
                    'has_errors': False
                }
                
                # Syntax validation
                syntax_errors = validate_generated_python_file(file_path)
                for error in syntax_errors:
                    if error.severity == "error":
                        file_report['syntax_errors'].append({
                            'line': error.line_number,
                            'message': error.message,
                            'suggestion': error.suggestion
                        })
                        total_syntax_errors += 1
                        file_report['has_errors'] = True
                    elif error.severity == "warning":
                        file_report['warnings'].append({
                            'line': error.line_number,
                            'message': error.message,
                            'type': 'syntax'
                        })
                        total_warnings += 1
                
                # Import validation
                if project_root:
                    import_errors = validate_imports_in_file(file_path, project_root)
                    for error in import_errors:
                        if error.severity == "error":
                            file_report['import_errors'].append({
                                'line': error.line_number,
                                'module': error.module_name,
                                'message': error.message,
                                'suggestion': error.suggestion
                            })
                            total_import_errors += 1
                            file_report['has_errors'] = True
                        elif error.severity == "warning":
                            file_report['warnings'].append({
                                'line': error.line_number,
                                'message': error.message,
                                'type': 'import'
                            })
                            total_warnings += 1
                
                validation_report['validation_details'][str(file_path)] = file_report
                
                if file_report['has_errors']:
                    validation_report['files_with_errors'].append(str(file_path))
            
            # Update totals
            validation_report['syntax_errors'] = total_syntax_errors
            validation_report['import_errors'] = total_import_errors  
            validation_report['warnings'] = total_warnings
            validation_report['success'] = total_syntax_errors == 0 and total_import_errors == 0
            
            # Generate summary
            if validation_report['success']:
                validation_report['summary'] = f"✅ All {len(python_files)} Python files validated successfully"
                if total_warnings > 0:
                    validation_report['summary'] += f" ({total_warnings} warnings)"
            else:
                error_count = total_syntax_errors + total_import_errors
                validation_report['summary'] = f"❌ Validation failed: {error_count} errors across {len(validation_report['files_with_errors'])} files"
                
        except ImportError:
            validation_report['summary'] = "⚠️ Enhanced validation not available - install validation dependencies"
            validation_report['success'] = True  # Don't fail generation due to missing validation
        except Exception as e:
            validation_report['summary'] = f"⚠️ Validation error: {e}"
            validation_report['success'] = True  # Don't fail generation due to validation errors
            self.logger.warning(f"Validation failed: {e}")
        
        return validation_report
    
    def format_validation_report(self, validation_report: Dict[str, Any]) -> str:
        """Format validation report for display."""
        output = []
        
        # Summary
        output.append(validation_report['summary'])
        
        if not validation_report['success'] and validation_report.get('files_with_errors'):
            output.append("\n📄 Files with errors:")
            
            for file_path in validation_report['files_with_errors']:
                file_details = validation_report['validation_details'].get(file_path, {})
                rel_path = Path(file_path).name  # Just show filename for brevity
                
                output.append(f"\n  📁 {rel_path}")
                
                # Syntax errors
                for error in file_details.get('syntax_errors', []):
                    output.append(f"    ❌ Line {error['line']}: {error['message']}")
                    if error.get('suggestion'):
                        output.append(f"       💡 {error['suggestion']}")
                
                # Import errors
                for error in file_details.get('import_errors', []):
                    output.append(f"    ❌ Line {error['line']}: {error['message']} (module: {error['module']})")
                    if error.get('suggestion'):
                        output.append(f"       💡 {error['suggestion']}")
        
        # Show warnings if any
        total_warnings = validation_report.get('warnings', 0)
        if total_warnings > 0:
            output.append(f"\n⚠️ {total_warnings} warnings found across generated files")
        
        return "\n".join(output)
    
    def _parse_sqlmodel_field(self, sqlmodel_field_str: str) -> Dict[str, Any]:
        """
        Parse SQLModel Field() string and extract parameters.
        
        Args:
            sqlmodel_field_str: String like "Field(primary_key=True, default_factory=uuid4)"
            
        Returns:
            Dictionary with parsed Field() parameters
        """
        if not sqlmodel_field_str or not isinstance(sqlmodel_field_str, str) or not sqlmodel_field_str.strip().startswith('Field('):
            return {}
        
        try:
            # Extract content between Field( and )
            content = sqlmodel_field_str.strip()[6:-1]  # Remove 'Field(' and ')'
            
            if not content.strip():
                return {}
            
            params = {}
            current_param = ""
            in_quotes = False
            quote_char = None
            paren_depth = 0
            
            i = 0
            while i < len(content):
                char = content[i]
                
                # Handle quotes
                if char in ['"', "'"] and not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_param += char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    quote_char = None
                    current_param += char
                elif in_quotes:
                    current_param += char
                # Handle parentheses for nested function calls
                elif char == '(' and not in_quotes:
                    paren_depth += 1
                    current_param += char
                elif char == ')' and not in_quotes:
                    paren_depth -= 1
                    current_param += char
                # Handle parameter separation
                elif char == ',' and not in_quotes and paren_depth == 0:
                    # Process current parameter
                    param_str = current_param.strip()
                    if '=' in param_str:
                        key, value = param_str.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convert string booleans to Python booleans
                        if value.lower() == 'true':
                            params[key] = True
                        elif value.lower() == 'false':
                            params[key] = False
                        # Remove quotes from string values
                        elif value.startswith(('"', "'")) and value.endswith(('"', "'")):
                            params[key] = value[1:-1]
                        # Handle numeric values
                        elif value.isdigit():
                            params[key] = int(value)
                        elif value.replace('.', '').isdigit():
                            params[key] = float(value)
                        else:
                            # Keep as string for function calls like uuid4, datetime.utcnow
                            params[key] = value
                    
                    current_param = ""
                else:
                    current_param += char
                
                i += 1
            
            # Process the last parameter
            param_str = current_param.strip()
            if param_str and '=' in param_str:
                key, value = param_str.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert string booleans to Python booleans
                if value.lower() == 'true':
                    params[key] = True
                elif value.lower() == 'false':
                    params[key] = False
                # Remove quotes from string values
                elif value.startswith(('"', "'")) and value.endswith(('"', "'")):
                    params[key] = value[1:-1]
                # Handle numeric values
                elif value.isdigit():
                    params[key] = int(value)
                elif value.replace('.', '').isdigit():
                    params[key] = float(value)
                else:
                    # Keep as string for function calls like uuid4, datetime.utcnow
                    params[key] = value
            
            return params
            
        except Exception as e:
            self.logger.warning(f"Failed to parse sqlmodel_field '{sqlmodel_field_str}': {e}")
            return {}
    
    def _process_field_configuration(self, field_config) -> Dict[str, Any]:
        """
        Process field configuration and extract SQLModel Field() parameters.
        
        Args:
            field_config: FieldConfig object or dict with potential sqlmodel_field string
            
        Returns:
            Dictionary with processed field attributes including:
            - python_type: The Python type for the field
            - sqlmodel_field_params: Dict of Field() parameters
            - has_default: Boolean indicating if field has default value
            - is_required: Boolean for field requirement
        """
        # Handle both FieldConfig objects and dictionaries
        if hasattr(field_config, 'dict'):
            field_dict = field_config.dict()
        elif hasattr(field_config, '__dict__'):
            field_dict = field_config.__dict__
        else:
            field_dict = field_config if isinstance(field_config, dict) else {}
        
        # Extract basic field information
        field_name = field_dict.get('name', '')
        field_type = field_dict.get('type', 'str')
        required = field_dict.get('required', True)
        default = field_dict.get('default')
        sqlmodel_field_str = field_dict.get('sqlmodel_field', '')
        
        # Parse SQLModel Field() parameters
        sqlmodel_params = self._parse_sqlmodel_field(sqlmodel_field_str)
        
        # Handle datetime defaults - use default_factory for datetime functions
        if default and 'datetime.' in str(default):
            sqlmodel_params['default_factory'] = default
            sqlmodel_params.pop('default', None)  # Remove default if it exists
        elif default:
            # Convert string booleans to Python booleans for defaults
            if str(default).lower() == 'true':
                sqlmodel_params['default'] = True
            elif str(default).lower() == 'false':
                sqlmodel_params['default'] = False
            else:
                sqlmodel_params['default'] = default
        
        # Determine if field has a default value
        has_default = bool(default or 'default' in sqlmodel_params or 'default_factory' in sqlmodel_params)
        
        # Convert FieldType enum to proper Python type
        python_type = self._convert_field_type_to_python_type(field_type)
        
        return {
            'python_type': python_type,
            'sqlmodel_field_params': sqlmodel_params,
            'has_default': has_default,
            'is_required': required and not has_default,
            'field_name': field_name,
            'original_config': field_dict
        }
    
    def _convert_field_type_to_python_type(self, field_type) -> str:
        """
        Convert FieldType enum to proper Python type string.
        
        Args:
            field_type: FieldType enum value or string
            
        Returns:
            Proper Python type string
        """
        # Handle FieldType enum values
        if hasattr(field_type, 'value'):
            # It's an enum, get the value
            type_str = field_type.value
        else:
            # It's already a string, clean it up
            type_str = str(field_type).strip('\'"')
        
        # If it's still an enum name (e.g., "FieldType.OPTIONAL_STR"), extract the value
        if type_str.startswith('FieldType.'):
            # Import FieldType to get the actual enum value
            try:
                from cli.generate.config.models import FieldType
                enum_name = type_str.split('.')[1]  # Get "OPTIONAL_STR" from "FieldType.OPTIONAL_STR"
                if hasattr(FieldType, enum_name):
                    enum_value = getattr(FieldType, enum_name)
                    return enum_value.value if hasattr(enum_value, 'value') else str(enum_value)
            except ImportError:
                self.logger.warning(f"Could not import FieldType for conversion of {type_str}")
        
        # Return the cleaned type string
        return type_str
    
    def generate_complete_domain(
        self, 
        domain_name: str, 
        config_dir: Path,
        output_dir: Path,
        layers: Optional[List[str]] = None
    ) -> GenerationResult:
        """
        Generate complete domain with all layers.
        
        Args:
            domain_name: Name of the domain to generate
            config_dir: Directory containing configuration files
            output_dir: Output directory for generated code
            layers: List of layers to generate (default: all)
            
        Returns:
            Complete generation result
        """
        start_time = datetime.now()
        
        if layers is None:
            layers = ['domain', 'repository', 'usecase', 'interface']
        
        result = GenerationResult(
            domain_name=domain_name,
            output_dir=output_dir,
            success=False
        )
        
        try:
            # Load configuration
            configuration = self.load_domain_configuration(domain_name, config_dir)
            result.configuration_used = configuration.dict() if hasattr(configuration, 'dict') else {}
            
            # Generate each layer
            for layer in layers:
                self.logger.info(f"Generating {layer} layer for {domain_name}")
                
                layer_results = self.generate_layer_files(
                    layer, domain_name, configuration, output_dir
                )
                result.generated_files.extend(layer_results)
                
                # Check for critical errors
                layer_errors = [f for f in layer_results if not f.success]
                if layer_errors:
                    result.errors.append(f"Failed to generate {len(layer_errors)} files in {layer} layer")
            
            # Calculate final result
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            result.success = result.total_errors == 0
            
            if result.success:
                self.logger.info(f"Successfully generated {domain_name} domain in {execution_time:.2f}s")
            else:
                self.logger.error(f"Domain generation completed with {result.total_errors} errors")
            
        except Exception as e:
            result.errors.append(str(e))
            result.execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Domain generation failed: {e}")
        
        return result
    
    def cleanup_output_directory(self, output_dir: Path, domain_name: str):
        """Clean up output directory for a specific domain."""
        try:
            domain_dirs = [
                output_dir / 'domain' / domain_name,
                output_dir / 'repository' / domain_name,  
                output_dir / 'usecase' / domain_name,
                output_dir / 'interface' / domain_name
            ]
            
            for domain_dir in domain_dirs:
                if domain_dir.exists():
                    shutil.rmtree(domain_dir)
                    self.logger.debug(f"Cleaned up directory: {domain_dir}")
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup output directory: {e}")
            raise
    
    def generate_complete_application(
        self,
        app_name: str,
        domains: List[str],
        config_dir: Path,
        output_dir: Path,
        app_config: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        Generate complete FastAPI application with all domains and layers.
        
        Args:
            app_name: Name of the application
            domains: List of domain names to include
            config_dir: Directory containing domain configurations
            output_dir: Output directory for generated application
            app_config: Additional application configuration
            
        Returns:
            Complete application generation result
        """
        start_time = datetime.now()
        
        result = GenerationResult(
            domain_name=f"complete_app_{app_name}",
            output_dir=output_dir,
            success=False
        )
        
        try:
            self.logger.info(f"Generating complete application: {app_name}")
            
            # Default application configuration
            if app_config is None:
                app_config = {}
            
            # Load all domain configurations
            domain_configs = {}
            for domain_name in domains:
                try:
                    # Try loading as single file config first
                    single_config_path = config_dir / f"{domain_name}.yaml"
                    if single_config_path.exists():
                        config = self.config_loader.load_from_file(single_config_path)
                        domain_configs[domain_name] = config
                    else:
                        # Fall back to two-file approach
                        config = self.load_domain_configuration(domain_name, config_dir)
                        domain_configs[domain_name] = config
                except Exception as e:
                    result.errors.append(f"Failed to load configuration for domain '{domain_name}': {e}")
                    continue
            
            if not domain_configs:
                raise ValueError("No valid domain configurations found")
            
            # Generate all domain layers first
            for domain_name in domain_configs.keys():
                self.logger.info(f"Generating domain: {domain_name}")
                
                domain_result = self.generate_complete_domain(
                    domain_name, config_dir, output_dir
                )
                result.generated_files.extend(domain_result.generated_files)
                result.errors.extend(domain_result.errors)
                result.warnings.extend(domain_result.warnings)
            
            # Generate application-level files
            app_files_result = self._generate_application_files(
                app_name, domains, domain_configs, output_dir, app_config
            )
            result.generated_files.extend(app_files_result)
            
            # Calculate final result
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            result.success = len(result.errors) == 0
            
            if result.success:
                self.logger.info(f"Successfully generated complete application '{app_name}' in {execution_time:.2f}s")
                self.logger.info(f"Generated {len(result.generated_files)} files total")
            else:
                self.logger.error(f"Application generation completed with {len(result.errors)} errors")
            
        except Exception as e:
            result.errors.append(str(e))
            result.execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Complete application generation failed: {e}")
        
        return result
    
    def _generate_application_files(
        self,
        app_name: str,
        domains: List[str],
        domain_configs: Dict[str, Any],
        output_dir: Path,
        app_config: Dict[str, Any]
    ) -> List[FileGenerationResult]:
        """Generate application-level files (main.py, config.py, etc.)."""
        results = []
        
        # Create Jinja2 processor for application templates
        processor = self._create_jinja_processor()
        
        # Prepare application context
        app_context = self._create_application_context(
            app_name, domains, domain_configs, app_config
        )
        
        # Application templates to generate
        app_templates = [
            ('main.py.j2', 'main.py'),
            ('config.py.j2', 'config.py'), 
            ('database.py.j2', 'database.py'),
            ('__init__.py.j2', '__init__.py'),
            ('interface/exceptions.py.j2', 'interface/exceptions.py'),
            ('../docker-compose.yml.j2', 'docker-compose.yml'),
            ('../README.md.j2', 'README.md'),
        ]
        
        # Generate each application file
        for template_path, output_filename in app_templates:
            try:
                # Determine output path
                if output_filename in ['docker-compose.yml', 'README.md']:
                    output_file_path = output_dir / output_filename
                elif output_filename == 'interface/exceptions.py':
                    interface_dir = output_dir / 'app' / 'interface'
                    interface_dir.mkdir(parents=True, exist_ok=True)
                    output_file_path = interface_dir / 'exceptions.py'
                else:
                    app_dir = output_dir / 'app'
                    app_dir.mkdir(parents=True, exist_ok=True)
                    output_file_path = app_dir / output_filename
                
                # Load and render template
                if template_path.startswith('../'):
                    # Root level template
                    template_file = template_path[3:]  # Remove '../' prefix
                else:
                    # App level template
                    template_file = template_path
                
                content = processor.render_template(template_file, app_context)
                
                # Write file
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                output_file_path.write_text(content, encoding='utf-8')
                
                results.append(FileGenerationResult(
                    file_path=output_file_path,
                    template_path=template_file,
                    success=True,
                    content_length=len(content),
                    generated_at=datetime.now()
                ))
                
                self.logger.debug(f"Generated application file: {output_file_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to generate {output_filename}: {e}")
                results.append(FileGenerationResult(
                    file_path=output_dir / output_filename,
                    template_path=template_path,
                    success=False,
                    content_length=0,
                    generated_at=datetime.now(),
                    errors=[str(e)]
                ))
        
        return results
    
    def _create_application_context(
        self,
        app_name: str,
        domains: List[str],
        domain_configs: Dict[str, Any],
        app_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create context for application-level templates."""
        
        # Extract domain information
        domain_list = []
        for domain_name in domains:
            config = domain_configs.get(domain_name, {})
            domain_info = getattr(config, 'domain', {}) if hasattr(config, 'domain') else {}
            
            domain_list.append({
                'name': domain_name,
                'name_plural': domain_info.get('plural', f"{domain_name}s"),
                'title': domain_name.title(),
                'description': domain_info.get('description', f'{domain_name.title()} domain'),
                'package': domain_info.get('package', domain_name)
            })
        
        # Application information
        app_info = app_config.get('app_info', {})
        
        # Database configuration
        database_type = app_config.get('database_type', 'sqlite')
        database_url = app_config.get('database_url')
        if database_url is None:
            if database_type == 'postgresql':
                database_url = 'postgresql://user:password@db:5432/appdb'
            elif database_type == 'mysql':
                database_url = 'mysql://user:password@db:3306/appdb'
            else:
                database_url = f'sqlite:///./{app_name}.db'
        
        # Features configuration
        features = app_config.get('features', {})
        default_features = {
            'caching_enabled': False,
            'celery_enabled': False,
            'monitoring_enabled': False,
            'redis_enabled': False,
            'documentation_enabled': False
        }
        features = {**default_features, **features}
        
        # Deployment configuration
        deployment_type = app_config.get('deployment_type', 'docker')
        
        return {
            'app_name': app_name,
            'app_info': {
                'title': app_info.get('title', f'{app_name.title()} API'),
                'description': app_info.get('description', f'FastAPI application for {app_name}'),
                'version': app_info.get('version', '1.0.0')
            },
            'domains': domain_list,
            'database_type': database_type,
            'database_url': database_url,
            'features': features,
            'deployment_type': deployment_type,
            # Add template helper functions
            'now': datetime.now(),
            'timestamp': datetime.now().isoformat()
        }


def generate_with_co_location(domain_name: str, project_dir: Path) -> GenerationResult:
    """
    Generate domain with co-location support, integrating with existing generation pipeline.
    
    Args:
        domain_name: Name of the domain to generate
        project_dir: Root directory of the project
        
    Returns:
        GenerationResult with co-location metadata
    """
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    logger.info(f"Generating domain '{domain_name}' with co-location support")
    
    start_time = datetime.now()
    
    result = GenerationResult(
        domain_name=domain_name,
        output_dir=project_dir,
        success=False
    )
    
    try:
        # Initialize domain generator helper
        helper = DomainGeneratorHelper()
        
        # Check for co-located configurations and templates
        domain_dir = project_dir / 'app' / 'domain' / domain_name
        
        # Load configuration using co-location loader
        from cli.generate.config.loader import CoLocationConfigLoader
        co_loader = CoLocationConfigLoader()
        
        if co_loader.has_co_located_configs(domain_dir):
            logger.info(f"Found co-located configurations in {domain_dir}")
            config = co_loader.load_co_located_configs(domain_dir)
        else:
            logger.info("No co-located configs found, falling back to traditional config loading")
            config_dir = project_dir / 'configs'
            config = helper.load_domain_configuration(domain_name, config_dir)
        
        # Ensure templates are co-located for future customization
        ensure_templates_co_located(domain_name, domain_dir)
        
        # Generate domain using existing pipeline with co-location metadata
        layers = ['domain', 'repository', 'usecase', 'interface']
        
        for layer in layers:
            logger.info(f"Generating {layer} layer for {domain_name}")
            
            layer_results = helper.generate_layer_files(
                layer, domain_name, config, project_dir
            )
            result.generated_files.extend(layer_results)
            
            # Check for critical errors
            layer_errors = [f for f in layer_results if not f.success]
            if layer_errors:
                result.errors.append(f"Failed to generate {len(layer_errors)} files in {layer} layer")
        
        # Calculate final result
        execution_time = (datetime.now() - start_time).total_seconds()
        result.execution_time = execution_time
        result.success = result.total_errors == 0
        
        # Add co-location metadata to result
        if hasattr(config, 'co_location') and config.co_location:
            result.configuration_used = config.dict() if hasattr(config, 'dict') else {}
            result.configuration_used['co_location_info'] = {
                'template_source': config.co_location.template_source,
                'config_source': config.co_location.config_source,
                'generation_mode': config.co_location.generation_mode
            }
        
        if result.success:
            logger.info(f"Successfully generated {domain_name} domain with co-location in {execution_time:.2f}s")
        else:
            logger.error(f"Co-location generation completed with {result.total_errors} errors")
        
    except Exception as e:
        result.errors.append(str(e))
        result.execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Co-location generation failed: {e}")
    
    return result


def ensure_templates_co_located(domain_name: str, output_dir: Path) -> List[str]:
    """
    Ensure templates are co-located to domain directory for customization.
    
    Args:
        domain_name: Name of the domain
        output_dir: Target domain directory
        
    Returns:
        List of template files that were copied
    """
    import logging
    
    logger = logging.getLogger(__name__)
    copied_templates = []
    
    try:
        # Find template base directory (go up from cli/helpers to root)
        template_base = Path(__file__).parent.parent.parent
        
        # Templates to copy for domain co-location
        domain_templates = [
            ('app/domain/{{domain}}/entities.py.j2', 'entities.py.j2'),
            ('app/domain/{{domain}}/exceptions.py.j2', 'exceptions.py.j2'),
            ('app/domain/{{domain}}/test_entities.py.j2', 'test_entities.py.j2'),
            ('app/domain/{{domain}}/test_exceptions.py.j2', 'test_exceptions.py.j2'),
        ]
        
        # Configuration templates
        config_templates = [
            ('app/domain/{{domain}}/domain.yaml', 'domain.yaml'),
            ('app/domain/{{domain}}/entities.yaml', 'entities.yaml')
        ]
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy template files
        for template_path, target_filename in domain_templates + config_templates:
            source_file = template_base / template_path
            target_file = output_dir / target_filename
            
            if source_file.exists() and not target_file.exists():
                try:
                    shutil.copy2(source_file, target_file)
                    copied_templates.append(target_filename)
                    logger.debug(f"Copied template: {target_filename}")
                except Exception as e:
                    logger.warning(f"Failed to copy template {template_path}: {e}")
        
        # Support template versioning and updates
        if copied_templates:
            _create_template_version_file(output_dir, copied_templates)
        
        logger.info(f"Ensured {len(copied_templates)} templates are co-located")
        
    except Exception as e:
        logger.error(f"Failed to ensure templates co-located: {e}")
    
    return copied_templates


def _create_template_version_file(output_dir: Path, templates: List[str]) -> None:
    """
    Create a version file for template tracking and updates.
    
    Args:
        output_dir: Directory containing co-located templates
        templates: List of template files
    """
    import yaml
    from datetime import datetime
    
    version_info = {
        'template_version': '1.0.0',
        'copied_at': datetime.now().isoformat(),
        'templates': templates,
        'source': 'global_templates',
        'customization_status': 'original'
    }
    
    version_file = output_dir / '.template_version.yaml'
    with open(version_file, 'w') as f:
        yaml.dump(version_info, f, default_flow_style=False)


def copy_templates_to_domain(domain_name: str, target_dir: Path) -> str:
    """
    Copy relevant templates to domain directory after generation.
    
    This supports the co-location architecture where templates live alongside
    generated code for easy customization.
    
    Args:
        domain_name: Name of the domain
        target_dir: Target domain directory
        
    Returns:
        Status message about template copying
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        copied_templates = ensure_templates_co_located(domain_name, target_dir)
        
        if copied_templates:
            return f"Copied {len(copied_templates)} templates for customization: {', '.join(copied_templates)}"
        else:
            return "Templates already exist or source templates not found"
            
    except Exception as e:
        logger.error(f"Failed to copy templates to domain: {e}")
        return f"Template copying failed: {e}"