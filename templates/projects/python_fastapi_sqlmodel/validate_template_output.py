#!/usr/bin/env python3
"""Quick validation of what our templates actually generate."""

import tempfile
import yaml
from pathlib import Path
from jinja2 import Template

# Add configuration merger
import sys
sys.path.append(str(Path(__file__).parent / "app" / "domain"))
from configuration_merger import ConfigurationMerger

# Create test config
domain_config = {
    "domain": {"name": "user"},
    "field_types": {"string": {"python_type": "str"}, "email": {"python_type": "EmailStr"}},
    "primary_key": {"default_factory": "uuid4", "description": "Unique identifier"},
    "timestamps": {
        "created_at": {"default_factory": "datetime.utcnow", "description": "Creation timestamp"},
        "updated_at": {"default_factory": "datetime.utcnow", "description": "Last update timestamp"}
    },
    "integration": {"pydantic": {"validate_assignment": True}, "fastapi": {"include_examples": True}},
    "generation": {"style": {"use_type_hints": True}}
}

entity_config = {
    "entities": [{
        "name": "User",
        "description": "User entity",
        "table_name": "users", 
        "mixins": ["UUIDMixin", "TimestampMixin"],
        "fields": [
            {"name": "name", "type": "string", "description": "User name", "required": True},
            {"name": "email", "type": "email", "description": "User email", "required": True}
        ]
    }],
    "template_context": {"features": {"enable_soft_delete": False}}
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
exceptions_template_path = template_dir / "exceptions.py.j2"

# Render entities template
if entities_template_path.exists():
    template = Template(entities_template_path.read_text())
    rendered = template.render(**merged_config)
    
    print("ENTITIES TEMPLATE OUTPUT (first 200 chars):")
    print("=" * 50)
    print(rendered[:200])
    print("=" * 50)
    
    # Check for specific text
    if "domain entities" in rendered.lower():
        print("✅ Found 'domain entities' text")
    else:
        print("❌ 'domain entities' text not found")
        
    # Show lines with "domain"
    for i, line in enumerate(rendered.split('\n')[:10], 1):
        if 'domain' in line.lower():
            print(f"Line {i}: {line}")

# Render exceptions template
if exceptions_template_path.exists():
    template = Template(exceptions_template_path.read_text())
    rendered = template.render(**merged_config)
    
    print("\nEXCEPTIONS TEMPLATE OUTPUT (first 200 chars):")
    print("=" * 50)
    print(rendered[:200])
    print("=" * 50)
    
    # Check for specific text
    if "domain exceptions" in rendered.lower():
        print("✅ Found 'domain exceptions' text")
    else:
        print("❌ 'domain exceptions' text not found")

# Cleanup
import shutil
shutil.rmtree(temp_dir)