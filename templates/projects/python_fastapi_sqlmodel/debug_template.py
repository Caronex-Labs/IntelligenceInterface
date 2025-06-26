#!/usr/bin/env python3
"""Debug template output to see exact text generated."""

import sys
import yaml
import tempfile
from pathlib import Path
from jinja2 import Template

# Add configuration merger
sys.path.append(str(Path(__file__).parent / "app" / "domain"))
from configuration_merger import ConfigurationMerger

# Create test config exactly like the test
domain_config = {
    "domain": {
        "name": "user",
        "description": "User domain with hexagonal architecture",
        "package": "app.domain.user",
        "version": "1.0.0"
    },
    "entity": {
        "base_class": "BaseEntity",
        "abstract_base": True,
        "mixins": [
            {
                "name": "UUIDMixin",
                "description": "UUID primary key generation",
                "enabled": True,
                "fields": ["id"]
            },
            {
                "name": "TimestampMixin",
                "description": "Created/updated timestamp fields", 
                "enabled": True,
                "fields": ["created_at", "updated_at"]
            }
        ]
    },
    "primary_key": {
        "type": "UUID",
        "field_name": "id",
        "auto_generate": True,
        "default_factory": "uuid4",
        "description": "Unique identifier"
    },
    "field_types": {
        "string": {
            "python_type": "str",
            "sqlmodel_type": "str"
        },
        "email": {
            "python_type": "EmailStr", 
            "sqlmodel_type": "str",
            "unique": True
        }
    },
    "timestamps": {
        "created_at": {
            "type": "datetime",
            "default_factory": "datetime.utcnow",
            "description": "Creation timestamp"
        },
        "updated_at": {
            "type": "datetime",
            "default_factory": "datetime.utcnow", 
            "description": "Last update timestamp"
        }
    },
    "integration": {
        "pydantic": {
            "validate_assignment": True,
            "use_enum_values": True,
            "allow_population_by_field_name": True
        },
        "fastapi": {
            "include_examples": True
        }
    },
    "generation": {
        "style": {
            "use_type_hints": True
        }
    }
}

entity_config = {
    "entities": [
        {
            "name": "User",
            "description": "User business entity with complete domain modeling",
            "table_name": "users",
            "mixins": ["UUIDMixin", "TimestampMixin"],
            "fields": [
                {
                    "name": "name",
                    "type": "string", 
                    "description": "User full name",
                    "required": True,
                    "validation": {
                        "min_length": 2,
                        "max_length": 100
                    },
                    "example": "John Doe"
                },
                {
                    "name": "email",
                    "type": "email",
                    "description": "User email address",
                    "required": True,
                    "unique": True,
                    "example": "user@example.com"
                }
            ]
        }
    ],
    "template_context": {
        "domain_name": "user",
        "features": {
            "enable_soft_delete": False,
            "enable_audit_log": True
        }
    }
}

# Create temp files
temp_dir = Path(tempfile.mkdtemp())
domain_path = temp_dir / "domain.yaml"
entity_path = temp_dir / "entities.yaml"

with domain_path.open('w') as f:
    yaml.dump(domain_config, f)
with entity_path.open('w') as f:
    yaml.dump(entity_config, f)

# Merge configuration
merger = ConfigurationMerger()
merged_config = merger.merge_domain_configurations(domain_path, entity_path)

# Load template
template_dir = Path(__file__).parent / "app" / "domain" / "{{domain}}"
entities_template_path = template_dir / "entities.py.j2"

print("🔍 Debugging template output...")
print("=" * 60)

if entities_template_path.exists():
    template = Template(entities_template_path.read_text())
    rendered = template.render(**merged_config)
    
    # Show first 10 lines
    lines = rendered.split('\n')
    for i, line in enumerate(lines[:10], 1):
        print(f"{i:2d}: {line}")
    
    print("=" * 60)
    
    # Check specific text
    search_texts = [
        "User domain entities - Generated from Co-located Template",
        "user domain entities - Generated from Co-located Template",
        "domain entities - Generated from Co-located Template",
        "Generated from Co-located Template"
    ]
    
    for text in search_texts:
        if text in rendered:
            print(f"✅ Found: '{text}'")
        else:
            print(f"❌ Not found: '{text}'")

# Cleanup
import shutil
shutil.rmtree(temp_dir)