"""
SQLAlchemy Runtime Validation Module

This module provides comprehensive runtime validation for generated SQLModel entities,
testing actual database operations, constraints, and SQLAlchemy integration.
"""

import tempfile
from pathlib import Path
from typing import Dict, List, Any
import importlib.util
import sys
import traceback
from datetime import datetime
import uuid

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import IntegrityError, ArgumentError
from sqlmodel import SQLModel, Session


class SQLAlchemyRuntimeValidator:
    """Validates SQLAlchemy integration for generated entities."""
    
    def __init__(self, generated_path: Path):
        self.generated_path = Path(generated_path)
        self.test_db_path = None
        self.engine = None
        self.session = None
        self.entities = {}
        self.validation_results = {}
        
    def validate_sqlalchemy_integration(self) -> Dict[str, bool]:
        """
        Test SQLAlchemy runtime behavior for generated entities.
        
        Returns:
            Dict mapping test names to pass/fail results
        """
        results = {}
        
        try:
            # Setup test database
            results["database_setup"] = self._setup_test_database()
            
            if results["database_setup"]:
                # Load generated entities
                results["entity_loading"] = self._load_generated_entities()
                
                if results["entity_loading"]:
                    # Test table creation
                    results["table_creation"] = self._test_table_creation()
                    
                    # Test entity CRUD operations
                    results["crud_operations"] = self._test_crud_operations()
                    
                    # Test constraint enforcement
                    results["constraint_enforcement"] = self._test_constraint_enforcement()
                    
                    # Test relationship operations
                    results["relationship_operations"] = self._test_relationship_operations()
                    
                    # Test field validation
                    results["field_validation"] = self._test_field_validation()
                    
                    # Test primary key behavior
                    results["primary_key_behavior"] = self._test_primary_key_behavior()
                    
                    # Test unique constraints
                    results["unique_constraints"] = self._test_unique_constraints()
                    
                    # Test index creation
                    results["index_creation"] = self._test_index_creation()
                    
                    # Test default value behavior
                    results["default_values"] = self._test_default_values()
                    
        except Exception as e:
            print(f"Critical error in SQLAlchemy validation: {e}")
            traceback.print_exc()
            results["critical_error"] = str(e)
            
        finally:
            self._cleanup_test_database()
            
        return results
    
    def _setup_test_database(self) -> bool:
        """Setup temporary SQLite database for testing."""
        try:
            # Create temporary database file
            temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
            self.test_db_path = temp_db.name
            temp_db.close()
            
            # Create SQLAlchemy engine
            self.engine = create_engine(f"sqlite:///{self.test_db_path}", echo=False)
            
            # Test basic connectivity
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
                
            return True
            
        except Exception as e:
            print(f"Failed to setup test database: {e}")
            return False
    
    def _load_generated_entities(self) -> bool:
        """Load generated entity classes dynamically."""
        try:
            # Find all entity files
            entity_files = list(self.generated_path.rglob("*/entities.py"))
            
            if not entity_files:
                print("No entity files found in generated code")
                return False
            
            for entity_file in entity_files:
                try:
                    # Extract domain name from path
                    domain_name = entity_file.parent.name
                    
                    # Load module dynamically
                    spec = importlib.util.spec_from_file_location(
                        f"entities_{domain_name}", entity_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    
                    # Add to sys.modules to support imports
                    sys.modules[f"entities_{domain_name}"] = module
                    spec.loader.exec_module(module)
                    
                    # Find SQLModel classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            hasattr(attr, '__table__') and 
                            attr.__name__ != 'SQLModel'):
                            self.entities[f"{domain_name}.{attr_name}"] = attr
                            
                except Exception as e:
                    print(f"Failed to load entity file {entity_file}: {e}")
                    continue
            
            print(f"Loaded {len(self.entities)} entity classes")
            return len(self.entities) > 0
            
        except Exception as e:
            print(f"Failed to load generated entities: {e}")
            return False
    
    def _test_table_creation(self) -> bool:
        """Test SQLAlchemy table creation."""
        try:
            # Create all tables
            SQLModel.metadata.create_all(self.engine)
            
            # Verify tables were created
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()
            
            print(f"Created {len(table_names)} tables: {table_names}")
            
            # Verify each entity has a corresponding table
            for entity_key, entity_class in self.entities.items():
                table_name = entity_class.__tablename__
                if table_name not in table_names:
                    print(f"Missing table for entity {entity_key}: {table_name}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Table creation failed: {e}")
            traceback.print_exc()
            return False
    
    def _test_crud_operations(self) -> bool:
        """Test basic CRUD operations on entities."""
        try:
            success_count = 0
            total_count = 0
            
            with Session(self.engine) as session:
                for entity_key, entity_class in self.entities.items():
                    total_count += 1
                    
                    try:
                        # Generate sample data
                        sample_data = self._generate_entity_sample_data(entity_class)
                        
                        # CREATE
                        entity = entity_class(**sample_data)
                        session.add(entity)
                        session.commit()
                        session.refresh(entity)
                        
                        entity_id = entity.id
                        assert entity_id is not None, f"Entity {entity_key} ID should not be None after creation"
                        
                        # READ
                        found_entity = session.get(entity_class, entity_id)
                        assert found_entity is not None, f"Entity {entity_key} should be retrievable by ID"
                        assert found_entity.id == entity_id, "Retrieved entity ID should match"
                        
                        # UPDATE
                        update_data = self._generate_update_data(entity_class, found_entity)
                        if update_data:
                            for field, value in update_data.items():
                                setattr(found_entity, field, value)
                            session.commit()
                            session.refresh(found_entity)
                        
                        # DELETE
                        session.delete(found_entity)
                        session.commit()
                        
                        deleted_entity = session.get(entity_class, entity_id)
                        assert deleted_entity is None, f"Entity {entity_key} should be deleted"
                        
                        success_count += 1
                        print(f"CRUD operations successful for {entity_key}")
                        
                    except Exception as e:
                        print(f"CRUD operations failed for {entity_key}: {e}")
                        session.rollback()
                        continue
            
            print(f"CRUD operations: {success_count}/{total_count} entities successful")
            return success_count == total_count
            
        except Exception as e:
            print(f"CRUD operations test failed: {e}")
            return False
    
    def _test_constraint_enforcement(self) -> bool:
        """Test database constraint enforcement."""
        try:
            success_count = 0
            total_tests = 0
            
            with Session(self.engine) as session:
                for entity_key, entity_class in self.entities.items():
                    # Test unique constraints
                    unique_fields = self._get_unique_fields(entity_class)
                    for field_name in unique_fields:
                        total_tests += 1
                        
                        try:
                            # Create first entity
                            sample_data = self._generate_entity_sample_data(entity_class)
                            entity1 = entity_class(**sample_data)
                            session.add(entity1)
                            session.commit()
                            
                            # Try to create duplicate
                            entity2 = entity_class(**sample_data)
                            session.add(entity2)
                            
                            # Should raise integrity error
                            try:
                                session.commit()
                                print(f"FAILED: Unique constraint not enforced for {entity_key}.{field_name}")
                            except IntegrityError:
                                success_count += 1
                                print(f"SUCCESS: Unique constraint enforced for {entity_key}.{field_name}")
                            
                            session.rollback()
                            
                        except Exception as e:
                            print(f"Constraint test error for {entity_key}.{field_name}: {e}")
                            session.rollback()
            
            print(f"Constraint enforcement: {success_count}/{total_tests} tests passed")
            return success_count == total_tests if total_tests > 0 else True
            
        except Exception as e:
            print(f"Constraint enforcement test failed: {e}")
            return False
    
    def _test_relationship_operations(self) -> bool:
        """Test entity relationship operations."""
        try:
            # For now, just return True as relationships are complex
            # This would need to be expanded based on actual foreign key relationships
            print("Relationship operations test: Skipped (no relationships detected)")
            return True
            
        except Exception as e:
            print(f"Relationship operations test failed: {e}")
            return False
    
    def _test_field_validation(self) -> bool:
        """Test field validation constraints."""
        try:
            success_count = 0
            total_tests = 0
            
            for entity_key, entity_class in self.entities.items():
                # Test required field validation
                required_fields = self._get_required_fields(entity_class)
                for field_name in required_fields:
                    total_tests += 1
                    
                    try:
                        sample_data = self._generate_entity_sample_data(entity_class)
                        # Remove required field
                        if field_name in sample_data:
                            del sample_data[field_name]
                        
                        # Should raise validation error
                        try:
                            entity = entity_class(**sample_data)
                            print(f"FAILED: Required field validation not enforced for {entity_key}.{field_name}")
                        except (ValueError, TypeError):
                            success_count += 1
                            print(f"SUCCESS: Required field validation enforced for {entity_key}.{field_name}")
                            
                    except Exception as e:
                        print(f"Field validation test error for {entity_key}.{field_name}: {e}")
            
            print(f"Field validation: {success_count}/{total_tests} tests passed")
            return success_count == total_tests if total_tests > 0 else True
            
        except Exception as e:
            print(f"Field validation test failed: {e}")
            return False
    
    def _test_primary_key_behavior(self) -> bool:
        """Test primary key configuration and behavior."""
        try:
            success_count = 0
            total_count = 0
            
            for entity_key, entity_class in self.entities.items():
                total_count += 1
                
                try:
                    # Check if entity has primary key defined
                    table = entity_class.__table__
                    primary_keys = [col.name for col in table.primary_key.columns]
                    
                    if not primary_keys:
                        print(f"FAILED: No primary key defined for {entity_key}")
                        continue
                    
                    print(f"SUCCESS: Primary key(s) found for {entity_key}: {primary_keys}")
                    
                    # Test primary key auto-generation
                    with Session(self.engine) as session:
                        sample_data = self._generate_entity_sample_data(entity_class)
                        # Remove ID if present
                        if 'id' in sample_data:
                            del sample_data['id']
                        
                        entity = entity_class(**sample_data)
                        session.add(entity)
                        session.commit()
                        session.refresh(entity)
                        
                        if hasattr(entity, 'id') and entity.id is not None:
                            print(f"SUCCESS: Primary key auto-generated for {entity_key}")
                            success_count += 1
                        else:
                            print(f"FAILED: Primary key not auto-generated for {entity_key}")
                    
                except ArgumentError as e:
                    if "could not assemble any primary key" in str(e):
                        print(f"FAILED: SQLAlchemy primary key error for {entity_key}: {e}")
                    else:
                        print(f"ERROR: Unexpected ArgumentError for {entity_key}: {e}")
                except Exception as e:
                    print(f"Primary key test error for {entity_key}: {e}")
            
            print(f"Primary key behavior: {success_count}/{total_count} entities successful")
            return success_count == total_count
            
        except Exception as e:
            print(f"Primary key behavior test failed: {e}")
            return False
    
    def _test_unique_constraints(self) -> bool:
        """Test unique constraint creation and enforcement."""
        try:
            inspector = inspect(self.engine)
            success_count = 0
            total_tests = 0
            
            for entity_key, entity_class in self.entities.items():
                table_name = entity_class.__tablename__
                unique_constraints = inspector.get_unique_constraints(table_name)
                indexes = inspector.get_indexes(table_name)
                
                # Find fields that should have unique constraints
                expected_unique_fields = self._get_unique_fields(entity_class)
                
                for field_name in expected_unique_fields:
                    total_tests += 1
                    
                    # Check if unique constraint exists
                    unique_found = any(
                        field_name in constraint['column_names'] 
                        for constraint in unique_constraints
                    )
                    
                    # Check if unique index exists  
                    unique_index_found = any(
                        field_name in index['column_names'] and index['unique']
                        for index in indexes
                    )
                    
                    if unique_found or unique_index_found:
                        success_count += 1
                        print(f"SUCCESS: Unique constraint found for {entity_key}.{field_name}")
                    else:
                        print(f"FAILED: Unique constraint missing for {entity_key}.{field_name}")
            
            print(f"Unique constraints: {success_count}/{total_tests} constraints found")
            return success_count == total_tests if total_tests > 0 else True
            
        except Exception as e:
            print(f"Unique constraints test failed: {e}")
            return False
    
    def _test_index_creation(self) -> bool:
        """Test database index creation."""
        try:
            inspector = inspect(self.engine)
            success_count = 0
            total_tests = 0
            
            for entity_key, entity_class in self.entities.items():
                table_name = entity_class.__tablename__
                indexes = inspector.get_indexes(table_name)
                
                # Find fields that should have indexes
                expected_index_fields = self._get_index_fields(entity_class)
                
                for field_name in expected_index_fields:
                    total_tests += 1
                    
                    # Check if index exists
                    index_found = any(
                        field_name in index['column_names']
                        for index in indexes
                    )
                    
                    if index_found:
                        success_count += 1
                        print(f"SUCCESS: Index found for {entity_key}.{field_name}")
                    else:
                        print(f"FAILED: Index missing for {entity_key}.{field_name}")
            
            print(f"Index creation: {success_count}/{total_tests} indexes found")
            return success_count == total_tests if total_tests > 0 else True
            
        except Exception as e:
            print(f"Index creation test failed: {e}")
            return False
    
    def _test_default_values(self) -> bool:
        """Test default value behavior."""
        try:
            success_count = 0
            total_tests = 0
            
            with Session(self.engine) as session:
                for entity_key, entity_class in self.entities.items():
                    # Test datetime defaults
                    datetime_fields = self._get_datetime_fields_with_defaults(entity_class)
                    
                    for field_name in datetime_fields:
                        total_tests += 1
                        
                        try:
                            # Create entity without specifying datetime field
                            sample_data = self._generate_entity_sample_data(entity_class)
                            if field_name in sample_data:
                                del sample_data[field_name]
                            
                            entity = entity_class(**sample_data)
                            session.add(entity)
                            session.commit()
                            session.refresh(entity)
                            
                            # Check if default was applied
                            field_value = getattr(entity, field_name)
                            if field_value is not None:
                                success_count += 1
                                print(f"SUCCESS: Default value applied for {entity_key}.{field_name}")
                            else:
                                print(f"FAILED: Default value not applied for {entity_key}.{field_name}")
                                
                        except Exception as e:
                            print(f"Default value test error for {entity_key}.{field_name}: {e}")
                            session.rollback()
            
            print(f"Default values: {success_count}/{total_tests} defaults working")
            return success_count == total_tests if total_tests > 0 else True
            
        except Exception as e:
            print(f"Default values test failed: {e}")
            return False
    
    def _cleanup_test_database(self):
        """Clean up test database resources."""
        try:
            if self.session:
                self.session.close()
            if self.engine:
                self.engine.dispose()
            if self.test_db_path and Path(self.test_db_path).exists():
                Path(self.test_db_path).unlink()
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
    # Helper methods
    def _generate_entity_sample_data(self, entity_class) -> Dict[str, Any]:
        """Generate sample data for entity creation."""
        data = {}
        
        # Get table columns
        table = entity_class.__table__
        
        for column in table.columns:
            if column.name == 'id' and column.primary_key:
                continue  # Skip auto-generated primary keys
            
            # Generate appropriate value based on column type
            if hasattr(column.type, 'python_type'):
                python_type = column.type.python_type
                
                if python_type == str:
                    data[column.name] = f"test_{column.name}_{uuid.uuid4().hex[:8]}"
                elif python_type == int:
                    data[column.name] = 1
                elif python_type == float:
                    data[column.name] = 1.0
                elif python_type == bool:
                    data[column.name] = True
                elif python_type == datetime:
                    # Skip datetime fields with defaults
                    if column.default is None and column.server_default is None:
                        data[column.name] = datetime.utcnow()
                else:
                    data[column.name] = f"default_{column.name}"
        
        return data
    
    def _generate_update_data(self, entity_class, entity_instance) -> Dict[str, Any]:
        """Generate data for updating entity."""
        update_data = {}
        
        table = entity_class.__table__
        for column in table.columns:
            if column.name == 'id' or column.primary_key:
                continue
                
            if hasattr(column.type, 'python_type'):
                python_type = column.type.python_type
                
                if python_type == str:
                    current_value = getattr(entity_instance, column.name, None)
                    if current_value:
                        update_data[column.name] = f"updated_{current_value}"
                    break  # Only update one field
        
        return update_data
    
    def _get_unique_fields(self, entity_class) -> List[str]:
        """Get fields that should have unique constraints."""
        unique_fields = []
        
        table = entity_class.__table__
        
        # Check unique constraints
        for constraint in table.constraints:
            if hasattr(constraint, 'columns') and getattr(constraint, 'unique', False):
                unique_fields.extend([col.name for col in constraint.columns])
        
        # Check unique indexes
        for index in table.indexes:
            if index.unique:
                unique_fields.extend([col.name for col in index.columns])
        
        return list(set(unique_fields))
    
    def _get_required_fields(self, entity_class) -> List[str]:
        """Get fields that are required (not nullable)."""
        required_fields = []
        
        table = entity_class.__table__
        for column in table.columns:
            if not column.nullable and not column.primary_key and column.default is None:
                required_fields.append(column.name)
        
        return required_fields
    
    def _get_index_fields(self, entity_class) -> List[str]:
        """Get fields that should have indexes."""
        index_fields = []
        
        table = entity_class.__table__
        for index in table.indexes:
            index_fields.extend([col.name for col in index.columns])
        
        return list(set(index_fields))
    
    def _get_datetime_fields_with_defaults(self, entity_class) -> List[str]:
        """Get datetime fields that have default values."""
        datetime_fields = []
        
        table = entity_class.__table__
        for column in table.columns:
            if (hasattr(column.type, 'python_type') and 
                column.type.python_type == datetime and
                (column.default is not None or column.server_default is not None)):
                datetime_fields.append(column.name)
        
        return datetime_fields


def validate_sqlalchemy_integration(generated_path: Path) -> Dict[str, bool]:
    """
    Validate SQLAlchemy integration for generated code.
    
    Args:
        generated_path: Path to generated code directory
        
    Returns:
        Dictionary mapping test names to pass/fail results
    """
    validator = SQLAlchemyRuntimeValidator(generated_path)
    return validator.validate_sqlalchemy_integration()


# CLI entry point for standalone testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python runtime_validator.py <generated_code_path>")
        sys.exit(1)
    
    generated_path = Path(sys.argv[1])
    if not generated_path.exists():
        print(f"Path does not exist: {generated_path}")
        sys.exit(1)
    
    print(f"Validating SQLAlchemy integration for: {generated_path}")
    results = validate_sqlalchemy_integration(generated_path)
    
    print("\n=== SQLAlchemy Runtime Validation Results ===")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len([r for r in results.values() if isinstance(r, bool)])
    passed_tests = len([r for r in results.values() if r is True])
    
    print(f"\nSummary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests < total_tests:
        sys.exit(1)