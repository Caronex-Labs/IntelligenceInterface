#!/usr/bin/env python3
"""
Demonstration script for Entity Domain Configuration Support.

This script demonstrates the new EntityDomainLoader functionality that can
load separate domain.yaml and entities.yaml files and merge them into a
unified EntityDomainConfig with advanced features like mixins, base fields,
and domain-level relationship definitions.
"""

import logging
from pathlib import Path

from cli.generate.config import (
    EntityDomainLoader,
    load_entity_domain_configuration,
    load_entity_domain_from_strings,
    ConfigurationError,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def demo_entity_domain_from_strings():
    """Demonstrate loading entity domain configuration from YAML strings."""
    print("\n" + "="*60)
    print("DEMO: Entity Domain Configuration from Strings")
    print("="*60)
    
    # Sample domain.yaml content
    domain_yaml = """
name: "Product"
plural: "Products"
description: "Product management domain"
package: "product"

# Base fields applied to all entities
base_fields:
  - name: "id"
    type: "int"
    required: false
    index: true
    description: "Primary key"
    sqlmodel_field: "Field(primary_key=True)"
  
  - name: "created_at"
    type: "datetime"
    required: false
    default: "datetime.utcnow"
    description: "Creation timestamp"

# Reusable field mixins
mixins:
  - name: "Timestamped"
    description: "Standard timestamp fields"
    fields:
      - name: "created_at"
        type: "datetime"
        default: "datetime.utcnow"
      - name: "updated_at"
        type: "datetime"
        default: "datetime.utcnow"
  
  - name: "Categorized"
    description: "Category relationship"
    fields:
      - name: "category_id"
        type: "int"
        required: true
        sqlmodel_field: "Field(foreign_key='categories.id')"

# Domain relationships
relationships:
  - name: "category_products"
    from_entity: "Category"
    to_entity: "Product"
    type: "one_to_many"
    back_populates: "category"

# SQLModel configuration
sqlmodel_config:
  table_naming: "snake_case"
  field_naming: "snake_case"
  generate_id_fields: true
  timestamp_fields: ["created_at", "updated_at"]
"""
    
    # Sample entities.yaml content
    entities_yaml = """
entities:
  - name: "Category"
    description: "Product category"
    table_name: "categories"
    mixins: ["Timestamped"]
    fields:
      - name: "name"
        type: "str"
        required: true
        unique: true
        index: true
        sqlmodel_field: "Field(index=True, unique=True)"
      
      - name: "description"
        type: "Optional[str]"
        required: false
        description: "Category description"
      
      - name: "is_active"
        type: "bool"
        required: true
        default: "true"
        sqlmodel_field: "Field(default=True)"
  
  - name: "Product"
    description: "Product entity"
    table_name: "products"
    mixins: ["Timestamped", "Categorized"]
    fields:
      - name: "name"
        type: "str"
        required: true
        index: true
        description: "Product name"
        sqlmodel_field: "Field(index=True)"
      
      - name: "price"
        type: "float"
        required: true
        description: "Product price"
        sqlmodel_field: "Field(gt=0)"
      
      - name: "description"
        type: "Optional[str]"
        required: false
        description: "Product description"
      
      - name: "in_stock"
        type: "bool"
        required: true
        default: "true"
        description: "Stock availability"
        sqlmodel_field: "Field(default=True)"
    
    relationships:
      - entity: "Category"
        type: "many_to_one"
        back_populates: "products"
        foreign_key: "categories.id"

# API endpoints
endpoints:
  - method: "POST"
    path: "/categories/"
    operation: "create_category"
    description: "Create product category"
  
  - method: "GET"
    path: "/categories/"
    operation: "list_categories"
    description: "List categories"
  
  - method: "POST"
    path: "/products/"
    operation: "create_product"
    description: "Create product"
  
  - method: "GET"
    path: "/products/"
    operation: "list_products"
    description: "List products"
  
  - method: "GET"
    path: "/categories/{category_id}/products/"
    operation: "list_category_products"
    description: "List products in category"

metadata:
  entities_count: 2
  has_relationships: true
  features: ["mixins", "base_fields", "sqlmodel"]
"""
    
    try:
        # Load configuration from strings
        config = load_entity_domain_from_strings(domain_yaml, entities_yaml)
        
        print(f"✅ Successfully loaded entity domain configuration!")
        print(f"   Domain: {config.name} ({config.plural})")
        print(f"   Package: {config.package}")
        print(f"   Base fields: {len(config.base_fields)}")
        print(f"   Mixins: {len(config.mixins)}")
        print(f"   Domain relationships: {len(config.relationships)}")
        print(f"   Entities: {len(config.entities)}")
        print(f"   Endpoints: {len(config.endpoints)}")
        print(f"   SQLModel config: {'Yes' if config.sqlmodel_config else 'No'}")
        
        # Show entity details
        print("\n📋 Entity Details:")
        for entity in config.entities:
            print(f"   • {entity.name}:")
            print(f"     - Fields: {len(entity.fields)}")
            print(f"     - Relationships: {len(entity.relationships)}")
            print(f"     - Mixins: {', '.join(entity.mixins) if entity.mixins else 'none'}")
            print(f"     - Table: {entity.table_name}")
            
            # Show some field details
            for field in entity.fields[:3]:  # First 3 fields
                field_info = f"{field.name}: {field.type}"
                if field.sqlmodel_field:
                    field_info += f" [{field.sqlmodel_field}]"
                print(f"       ◦ {field_info}")
            if len(entity.fields) > 3:
                print(f"       ◦ ... and {len(entity.fields) - 3} more fields")
        
        # Show mixins applied
        print("\n🔧 Mixin Application:")
        for entity in config.entities:
            if entity.mixins:
                print(f"   • {entity.name} uses mixins: {', '.join(entity.mixins)}")
                
        print("\n🔗 Relationships:")
        for entity in config.entities:
            if entity.relationships:
                for rel in entity.relationships:
                    print(f"   • {entity.name} -> {rel.entity} ({rel.type})")
        
        return config
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        if hasattr(e, 'suggestion') and e.suggestion:
            print(f"   💡 Suggestion: {e.suggestion}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def demo_entity_domain_from_files():
    """Demonstrate loading entity domain configuration from fixture files."""
    print("\n" + "="*60)
    print("DEMO: Entity Domain Configuration from Files")
    print("="*60)
    
    # Use the fixture files we created
    fixtures_dir = Path(__file__).parent / "tests" / "fixtures" / "entity_domain"
    
    test_files = [
        ("User Domain", "user_domain.yaml", "user_entities.yaml"),
        ("Blog Domain", "blog_domain.yaml", "blog_entities.yaml"),
    ]
    
    for domain_name, domain_file, entities_file in test_files:
        domain_path = fixtures_dir / domain_file
        entities_path = fixtures_dir / entities_file
        
        if not domain_path.exists() or not entities_path.exists():
            print(f"⚠️  Skipping {domain_name} - fixture files not found")
            continue
            
        print(f"\n📁 Loading {domain_name}...")
        print(f"   Domain file: {domain_path.name}")
        print(f"   Entities file: {entities_path.name}")
        
        try:
            config = load_entity_domain_configuration(domain_path, entities_path)
            
            print(f"✅ Successfully loaded {domain_name}!")
            print(f"   Domain: {config.name} ({config.plural})")
            print(f"   Entities: {len(config.entities)}")
            print(f"   Mixins: {len(config.mixins)}")
            print(f"   Relationships: {len(config.relationships)}")
            print(f"   Endpoints: {len(config.endpoints)}")
            
            # Show complexity metrics
            total_fields = sum(len(entity.fields) for entity in config.entities)
            total_relationships = sum(len(entity.relationships) for entity in config.entities)
            
            print(f"   📊 Complexity:")
            print(f"     - Total fields: {total_fields}")
            print(f"     - Total relationships: {total_relationships}")
            print(f"     - SQLModel fields: {sum(1 for entity in config.entities for field in entity.fields if field.sqlmodel_field)}")
            
        except ConfigurationError as e:
            print(f"❌ Configuration error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def demo_validation_and_error_handling():
    """Demonstrate validation and error handling capabilities."""
    print("\n" + "="*60)
    print("DEMO: Validation and Error Handling")
    print("="*60)
    
    # Test case 1: Invalid domain configuration
    print("\n🔍 Test 1: Invalid domain name")
    invalid_domain = """
name: "123InvalidName"  # Invalid - starts with number
"""
    
    valid_entities = """
entities:
  - name: "Test"
    fields:
      - name: "field1"
        type: "str"
"""
    
    try:
        config = load_entity_domain_from_strings(invalid_domain, valid_entities)
        print(f"❌ Expected validation error but got: {config}")
    except ConfigurationError as e:
        print(f"✅ Caught expected validation error: {type(e).__name__}")
        print(f"   Message: {e}")
    
    # Test case 2: Unknown mixin reference
    print("\n🔍 Test 2: Unknown mixin reference")
    domain_with_mixins = """
name: "Test"
mixins:
  - name: "KnownMixin"
    fields:
      - name: "field1"
        type: "str"
"""
    
    entities_with_unknown_mixin = """
entities:
  - name: "Test"
    mixins: ["UnknownMixin"]
    fields:
      - name: "field2"
        type: "str"
"""
    
    try:
        loader = EntityDomainLoader()
        config = loader.load_from_strings(domain_with_mixins, entities_with_unknown_mixin)
        loader.validate_entity_domain_config(config)
        print(f"❌ Expected validation error but validation passed")
    except ConfigurationError as e:
        print(f"✅ Caught expected validation error: {type(e).__name__}")
        print(f"   Message: {e}")
    
    # Test case 3: Missing file
    print("\n🔍 Test 3: Missing entities file")
    try:
        config = load_entity_domain_configuration(
            Path("/tmp/domain.yaml"),
            Path("/non/existent/entities.yaml")
        )
        print(f"❌ Expected file error but got: {config}")
    except ConfigurationError as e:
        print(f"✅ Caught expected file error: {type(e).__name__}")
        print(f"   Message: {e}")


def main():
    """Run all entity domain configuration demonstrations."""
    print("Entity Domain Configuration Support Demonstration")
    print("This script demonstrates the new EntityDomainLoader functionality")
    print("that enables loading separate domain.yaml and entities.yaml files")
    print("with advanced features like mixins, base fields, and relationships.")
    
    # Run demonstrations
    config = demo_entity_domain_from_strings()
    demo_entity_domain_from_files()
    demo_validation_and_error_handling()
    
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nThe Entity Domain Configuration Support provides:")
    print("  • Separate domain.yaml and entities.yaml file loading")
    print("  • Configuration merging with field inheritance")
    print("  • Reusable field mixins")
    print("  • Domain-level relationship definitions")
    print("  • SQLModel-specific field configurations")
    print("  • Comprehensive validation and error handling")
    print("  • Full compatibility with existing Configuration system")
    print("\nThis foundation enables immediate testing of Entity Template Flow!")
    
    if config:
        print(f"\n🎯 Ready for Entity Template Flow testing with {len(config.entities)} entities!")


if __name__ == "__main__":
    main()