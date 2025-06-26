#!/usr/bin/env python3
"""
Debug script to investigate hierarchical merge validation issues.
"""

import tempfile
import yaml
from pathlib import Path

# Add the project root to the path
import sys
sys.path.append(str(Path(__file__).parent))

from app.domain.configuration_merger import ConfigurationMerger


def debug_merge_validation():
    """Debug merge validation issues."""
    print("🔍 Debugging hierarchical merge validation")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="debug_merge_"))
    
    # Create test configurations
    configs = {
        'domain.yaml': {
            'domain': {'name': 'User', 'description': 'User management domain'},
            'default_settings': {'validation': True, 'logging': True, 'cache_enabled': False},
            'field_types': {'default_string': 'str', 'default_id': 'int'}
        },
        'usecase.yaml': {
            'usecase': {'business_logic': True, 'transaction_management': True},
            'default_settings': {'cache_enabled': True, 'retry_attempts': 3},
            'validation_rules': {'strict_mode': True, 'email_validation': True}
        },
        'repository.yaml': {
            'repository': {'async_operations': True, 'connection_pooling': True},
            'default_settings': {'logging': False, 'query_timeout': 30},
            'database': {'provider': 'postgresql', 'migration_support': True}
        },
        'api.yaml': {
            'api': {'auto_documentation': True, 'cors_enabled': True},
            'default_settings': {'validation': False, 'rate_limiting': True},
            'endpoints': {'prefix': '/api/v1', 'authentication_required': True}
        }
    }
    
    # Write configuration files
    layer_paths = []
    for filename, config in configs.items():
        config_path = temp_dir / filename
        with config_path.open('w') as f:
            yaml.dump(config, f, default_flow_style=False)
        layer_paths.append(config_path)
        print(f"📄 Created {filename}")
    
    # Initialize merger and perform merge
    merger = ConfigurationMerger()
    print("\n🔄 Performing hierarchical merge...")
    
    try:
        result = merger.merge_hierarchical_configurations(layer_paths)
        
        print(f"✅ Merge completed")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Has conflicts: {result.has_conflicts}")
        print(f"📊 Has errors: {result.has_errors}")
        print(f"📊 Is valid: {result.is_valid}")
        
        print(f"\n📋 Validation errors: {len(result.validation_errors)}")
        for error in result.validation_errors:
            print(f"   ❌ {error}")
        
        print(f"\n⚠️  Merge warnings: {len(result.merge_warnings)}")
        for warning in result.merge_warnings:
            print(f"   ⚠️  {warning}")
        
        print(f"\n🔧 Conflicts: {len(result.conflicts)}")
        for conflict in result.conflicts:
            print(f"   ⚡ {conflict.key_path}: {conflict.value1} → {conflict.value2}")
        
        print(f"\n📊 Merged config keys:")
        for key in sorted(result.merged_config.keys()):
            if not key.startswith('_'):
                print(f"   - {key}")
        
        print(f"\n🎯 Merged config length: {len(result.merged_config)}")
        print(f"🎯 Config empty check: {len(result.merged_config) > 0}")
        
        # Check specific validation conditions
        print(f"\n🔍 Validation condition analysis:")
        print(f"   - not has_errors: {not result.has_errors}")
        print(f"   - len(merged_config) > 0: {len(result.merged_config) > 0}")
        print(f"   - Combined (is_valid): {not result.has_errors and len(result.merged_config) > 0}")
        
    except Exception as e:
        print(f"❌ Merge failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print(f"\n🗑️  Cleaned up temporary files")


if __name__ == "__main__":
    debug_merge_validation()