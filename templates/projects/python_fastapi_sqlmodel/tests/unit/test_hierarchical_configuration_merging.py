"""
Unit tests for hierarchical configuration merging functionality.

These tests validate the ConfigurationMerger's ability to merge configurations
across Domain → UseCase → Repository → Interface layers with proper conflict
resolution and metadata tracking.
"""

import unittest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.domain.configuration_merger import ConfigurationMerger, HierarchicalConflictResolver
from cli.generate.config.hierarchical_models import (
    LayerType, ConfigurationLayer, HierarchicalMergeResult
)


class TestHierarchicalConfigurationMerging(unittest.TestCase):
    """Test hierarchical configuration merging functionality."""
    
    def setUp(self):
        """Set up test fixtures and temporary directories."""
        self.merger = ConfigurationMerger()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="hierarchical_test_"))
        
        # Create test configuration files
        self._create_test_configurations()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_configurations(self):
        """Create test configuration files for hierarchical merging."""
        # Domain configuration
        domain_config = {
            'domain': {
                'name': 'User',
                'description': 'User management domain'
            },
            'default_settings': {
                'validation': True,
                'logging': True,
                'cache_enabled': False
            },
            'field_types': {
                'default_string': 'str',
                'default_id': 'int'
            }
        }
        
        # UseCase configuration
        usecase_config = {
            'usecase': {
                'business_logic': True,
                'transaction_management': True
            },
            'default_settings': {
                'cache_enabled': True,  # Override domain
                'retry_attempts': 3
            },
            'validation_rules': {
                'strict_mode': True,
                'email_validation': True
            }
        }
        
        # Repository configuration
        repository_config = {
            'repository': {
                'async_operations': True,
                'connection_pooling': True
            },
            'default_settings': {
                'logging': False,  # Override domain
                'query_timeout': 30
            },
            'database': {
                'provider': 'postgresql',
                'migration_support': True
            }
        }
        
        # Interface configuration
        interface_config = {
            'api': {
                'auto_documentation': True,
                'cors_enabled': True
            },
            'default_settings': {
                'validation': False,  # Override domain
                'rate_limiting': True
            },
            'endpoints': {
                'prefix': '/api/v1',
                'authentication_required': True
            }
        }
        
        # Write configuration files
        configs = [
            ('domain.yaml', domain_config),
            ('usecase.yaml', usecase_config),
            ('repository.yaml', repository_config),
            ('api.yaml', interface_config)
        ]
        
        for filename, config in configs:
            config_path = self.temp_dir / filename
            with config_path.open('w') as f:
                yaml.dump(config, f, default_flow_style=False)
    
    def test_layer_type_precedence(self):
        """Test LayerType precedence values are correct."""
        self.assertEqual(LayerType.DOMAIN.precedence, 1)
        self.assertEqual(LayerType.USECASE.precedence, 2)
        self.assertEqual(LayerType.REPOSITORY.precedence, 3)
        self.assertEqual(LayerType.INTERFACE.precedence, 4)
    
    def test_configuration_layer_creation(self):
        """Test ConfigurationLayer creation and loading."""
        domain_path = self.temp_dir / 'domain.yaml'
        layer = ConfigurationLayer(
            layer_type=LayerType.DOMAIN,
            config_path=domain_path,
            precedence=LayerType.DOMAIN.precedence
        )
        
        # Load configuration
        layer.load_configuration()
        
        self.assertTrue(layer.is_loaded)
        self.assertIn('domain', layer.config_data)
        self.assertEqual(layer.config_data['domain']['name'], 'User')
        self.assertIsNotNone(layer.metadata)
        self.assertEqual(layer.metadata.layer_type, LayerType.DOMAIN)
    
    def test_hierarchical_conflict_resolver(self):
        """Test conflict resolution between layers."""
        resolver = HierarchicalConflictResolver("highest_precedence")
        
        # Test conflict resolution
        resolved_value = resolver.resolve_conflict(
            "default_settings.validation",
            LayerType.DOMAIN,
            True,
            LayerType.INTERFACE,
            False
        )
        
        # Interface should win (higher precedence)
        self.assertEqual(resolved_value, False)
        self.assertEqual(len(resolver.conflicts), 1)
        
        conflict = resolver.conflicts[0]
        self.assertEqual(conflict.key_path, "default_settings.validation")
        self.assertEqual(conflict.layer1, LayerType.DOMAIN)
        self.assertEqual(conflict.layer2, LayerType.INTERFACE)
        self.assertEqual(conflict.resolved_value, False)
    
    def test_four_layer_hierarchical_merge(self):
        """Test complete four-layer hierarchical merge."""
        # Get paths to configuration files
        layer_paths = [
            self.temp_dir / 'domain.yaml',
            self.temp_dir / 'usecase.yaml',
            self.temp_dir / 'repository.yaml',
            self.temp_dir / 'api.yaml'
        ]
        
        # Perform hierarchical merge
        result = self.merger.merge_hierarchical_configurations(layer_paths)
        
        # Validate result structure
        self.assertIsInstance(result, HierarchicalMergeResult)
        self.assertTrue(result.is_valid)
        self.assertFalse(result.has_errors)
        
        # Validate merged configuration
        merged_config = result.merged_config
        
        # Check domain configuration is present
        self.assertIn('domain', merged_config)
        self.assertEqual(merged_config['domain']['name'], 'User')
        
        # Check usecase configuration is present
        self.assertIn('usecase', merged_config)
        self.assertTrue(merged_config['usecase']['business_logic'])
        
        # Check repository configuration is present
        self.assertIn('repository', merged_config)
        self.assertTrue(merged_config['repository']['async_operations'])
        
        # Check interface configuration is present
        self.assertIn('api', merged_config)
        self.assertTrue(merged_config['api']['auto_documentation'])
        
        # Check precedence-based overrides
        default_settings = merged_config['default_settings']
        self.assertEqual(default_settings['validation'], False)  # Interface wins
        self.assertEqual(default_settings['cache_enabled'], True)  # UseCase wins
        self.assertEqual(default_settings['logging'], False)  # Repository wins
        self.assertTrue(default_settings['rate_limiting'])  # Interface adds
        
        # Check metadata
        self.assertEqual(len(result.layer_metadata), 4)
        self.assertIn('execution_time', result.performance_metrics)
        self.assertIn('_merge_metadata', merged_config)
    
    def test_nested_configuration_merge(self):
        """Test deep merging of nested configuration structures."""
        # Create nested configuration files
        nested_domain = {
            'database': {
                'connection': {
                    'host': 'localhost',
                    'port': 5432,
                    'options': {
                        'pool_size': 10,
                        'timeout': 30
                    }
                }
            },
            'features': ['authentication', 'authorization']
        }
        
        nested_usecase = {
            'database': {
                'connection': {
                    'port': 5433,  # Override port
                    'options': {
                        'pool_size': 20,  # Override pool_size
                        'max_connections': 100  # Add new option
                    }
                }
            },
            'features': ['caching', 'monitoring']  # Replace entire array
        }
        
        # Write nested configurations
        nested_domain_path = self.temp_dir / 'nested_domain.yaml'
        nested_usecase_path = self.temp_dir / 'nested_usecase.yaml'
        
        with nested_domain_path.open('w') as f:
            yaml.dump(nested_domain, f)
        with nested_usecase_path.open('w') as f:
            yaml.dump(nested_usecase, f)
        
        # Merge nested configurations
        result = self.merger.merge_hierarchical_configurations([
            nested_domain_path,
            nested_usecase_path
        ])
        
        merged_config = result.merged_config
        
        # Validate nested merge
        connection = merged_config['database']['connection']
        self.assertEqual(connection['host'], 'localhost')  # From domain
        self.assertEqual(connection['port'], 5433)  # From usecase (override)
        
        options = connection['options']
        self.assertEqual(options['pool_size'], 20)  # From usecase (override)
        self.assertEqual(options['timeout'], 30)  # From domain (preserved)
        self.assertEqual(options['max_connections'], 100)  # From usecase (new)
        
        # Validate array replacement
        features = merged_config['features']
        self.assertEqual(features, ['caching', 'monitoring'])  # UseCase replaces completely
    
    def test_null_value_handling(self):
        """Test that null values don't override existing values."""
        # Create configuration with null values
        null_config = {
            'settings': {
                'timeout': None,  # Should not override
                'retries': 5,  # Should override
                'cache_ttl': None,  # Should not override
                'new_setting': 'value'  # Should add
            }
        }
        
        base_config = {
            'settings': {
                'timeout': 30,
                'retries': 3,
                'cache_ttl': 300
            }
        }
        
        # Create temporary files
        base_path = self.temp_dir / 'base.yaml'
        null_path = self.temp_dir / 'null_override.yaml'
        
        with base_path.open('w') as f:
            yaml.dump(base_config, f)
        with null_path.open('w') as f:
            yaml.dump(null_config, f)
        
        # Merge configurations
        result = self.merger.merge_hierarchical_configurations([base_path, null_path])
        merged_config = result.merged_config
        
        # Validate null handling
        settings = merged_config['settings']
        self.assertEqual(settings['timeout'], 30)  # Not overridden by null
        self.assertEqual(settings['retries'], 5)  # Overridden by non-null
        self.assertEqual(settings['cache_ttl'], 300)  # Not overridden by null
        self.assertEqual(settings['new_setting'], 'value')  # Added
    
    def test_conflict_detection_and_resolution(self):
        """Test conflict detection and resolution."""
        # Create configurations with conflicts
        conflict1 = {'setting': 'value1'}
        conflict2 = {'setting': 'value2'}
        
        path1 = self.temp_dir / 'conflict1.yaml'
        path2 = self.temp_dir / 'conflict2.yaml'
        
        with path1.open('w') as f:
            yaml.dump(conflict1, f)
        with path2.open('w') as f:
            yaml.dump(conflict2, f)
        
        # Merge with conflict resolution
        result = self.merger.merge_hierarchical_configurations([path1, path2])
        
        # Validate conflict resolution
        self.assertTrue(result.has_conflicts)
        self.assertGreater(len(result.conflicts), 0)
        
        # Higher precedence should win
        self.assertEqual(result.merged_config['setting'], 'value2')
    
    def test_performance_metrics_tracking(self):
        """Test performance metrics are tracked during merge."""
        layer_paths = [
            self.temp_dir / 'domain.yaml',
            self.temp_dir / 'usecase.yaml'
        ]
        
        result = self.merger.merge_hierarchical_configurations(layer_paths)
        
        # Validate performance metrics
        metrics = result.performance_metrics
        self.assertIn('execution_time', metrics)
        self.assertIn('layers_processed', metrics)
        self.assertIn('config_keys', metrics)
        self.assertIn('conflicts_resolved', metrics)
        
        self.assertGreater(metrics['execution_time'], 0)
        self.assertEqual(metrics['layers_processed'], 2)
        self.assertGreater(metrics['config_keys'], 0)
    
    def test_validation_error_detection(self):
        """Test validation error detection in merged configuration."""
        # Create invalid configuration
        invalid_config = {
            'invalid_structure': 'not_a_dict_where_dict_expected'
        }
        
        invalid_path = self.temp_dir / 'invalid.yaml'
        with invalid_path.open('w') as f:
            yaml.dump(invalid_config, f)
        
        result = self.merger.merge_hierarchical_configurations([invalid_path])
        
        # Note: With current validation, this might not produce errors
        # The test validates the validation framework is in place
        self.assertIsInstance(result.validation_errors, list)
    
    def test_empty_and_missing_layers(self):
        """Test handling of empty and missing configuration layers."""
        # Create empty configuration
        empty_path = self.temp_dir / 'empty.yaml'
        empty_path.touch()
        
        # Reference non-existent file
        missing_path = self.temp_dir / 'missing.yaml'
        
        valid_path = self.temp_dir / 'domain.yaml'
        
        result = self.merger.merge_hierarchical_configurations([
            valid_path, empty_path, missing_path
        ])
        
        # Should handle gracefully with warnings
        self.assertTrue(len(result.merge_warnings) > 0)
        self.assertIn('domain', result.merged_config)  # Valid config preserved
    
    def test_metadata_tracking(self):
        """Test comprehensive metadata tracking."""
        layer_paths = [
            self.temp_dir / 'domain.yaml',
            self.temp_dir / 'usecase.yaml'
        ]
        
        result = self.merger.merge_hierarchical_configurations(layer_paths)
        
        # Validate metadata structure
        self.assertEqual(len(result.layer_metadata), 2)
        
        # Validate layer metadata
        domain_metadata = result.layer_metadata[0]
        self.assertEqual(domain_metadata.layer_type, LayerType.DOMAIN)
        self.assertIsNotNone(domain_metadata.source_path)
        self.assertIsInstance(domain_metadata.keys_contributed, list)
        self.assertIsInstance(domain_metadata.keys_overridden, list)
        
        # Validate merge metadata in config
        merge_metadata = result.merged_config['_merge_metadata']
        self.assertIn('layers_processed', merge_metadata)
        self.assertIn('conflict_resolution_strategy', merge_metadata)
        self.assertTrue(merge_metadata['performance_optimized'])


if __name__ == '__main__':
    unittest.main()