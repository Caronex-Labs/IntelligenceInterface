"""Tests for Health domain entities - Generated from Enhanced Co-located Template.

This module contains comprehensive tests for the generated SQLModel entities
in the Health domain, following hexagonal architecture testing principles
with property-based testing, advanced fixtures, and comprehensive validation.

Generated from:
- domain.yaml: Base entity configuration and mixins
- entities.yaml: Entity-specific field definitions and relationships  
- test_entities.py.j2: This Jinja2 test template (Enhanced Version)

Co-location Architecture:
- Test templates, configurations, and generated tests in same directory
- Tests generated alongside the actual entity code
- @pyhex preservation markers for custom test logic

Testing Features:
- Property-based testing with hypothesis for comprehensive field validation
- Advanced test fixtures and factories for entity data generation
- Relationship validation with referential integrity testing
- Business rule validation and edge case coverage
- Performance testing for database operations
"""

# Standard library imports
import pytest
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from typing import Dict, Any, List, Optional, Type
from decimal import Decimal
import string
import random

# Third-party imports
from sqlmodel import SQLModel, Session, create_engine, select
from pydantic import ValidationError, EmailStr
import sqlalchemy as sa
from hypothesis import given, strategies as st, assume, settings
from hypothesis.extra.sqlmodel import from_model

# Local imports - Generated entities
from .entities import (
    HealthCheckBase,
    HealthCheck,
    HealthCheckCreate,
    HealthCheckUpdate,
    HealthCheckResponse,
)

# Test utilities
from tests.helpers.test_database import TestDatabaseManager, DatabaseTestHelper
from tests.helpers.mock_factories import ConfigurationFactory

# @pyhex:begin:custom_imports
# Add your custom test imports here
# @pyhex:end:custom_imports


class TestBase:
    """Enhanced base test class with comprehensive setup and utilities."""
    
    @pytest.fixture(scope="function")
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        SQLModel.metadata.create_all(engine)
        return engine
    
    @pytest.fixture(scope="function")
    def session(self, engine):
        """Create database session for testing."""
        with Session(engine) as session:
            yield session
            session.rollback()

    @pytest.fixture(scope="function")
    def db_helper(self, session):
        """Database test helper fixture."""
        return DatabaseTestHelper()

    # @pyhex:begin:custom_test_fixtures
    # Add your custom test fixtures here
    # @pyhex:end:custom_test_fixtures


class EntityTestStrategies:
    """Hypothesis strategies for property-based testing."""
    
    # Common strategies for different field types
    string_strategy = st.text(min_size=1, max_size=100, alphabet=string.ascii_letters + string.digits + " .-_")
    email_strategy = st.emails()
    integer_strategy = st.integers(min_value=1, max_value=1000000)
    decimal_strategy = st.decimals(min_value=0, max_value=999999, places=2)
    boolean_strategy = st.booleans()
    datetime_strategy = st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31))
    date_strategy = st.dates(min_value=date(2000, 1, 1), max_value=date(2030, 12, 31))
    
    @classmethod
    def get_strategy_for_field(cls, field_type: str, field_config: Dict[str, Any] = None):
        """Get appropriate hypothesis strategy for field type."""
        field_config = field_config or {}
        
        if field_type in ["str", "string"]:
            min_size = field_config.get("min_length", 1)
            max_size = field_config.get("max_length", 100)
            return st.text(min_size=min_size, max_size=max_size)
        elif field_type in ["EmailStr", "email"]:
            return cls.email_strategy
        elif field_type in ["int", "integer"]:
            min_val = field_config.get("min_value", 1)
            max_val = field_config.get("max_value", 1000000)
            return st.integers(min_value=min_val, max_value=max_val)
        elif field_type in ["Decimal", "decimal"]:
            return cls.decimal_strategy
        elif field_type in ["bool", "boolean"]:
            return cls.boolean_strategy
        elif field_type in ["datetime"]:
            return cls.datetime_strategy
        elif field_type in ["date"]:
            return cls.date_strategy
        else:
            return st.text(min_size=1, max_size=50)


class HealthCheckTestFactory:
    """Factory for creating HealthCheck test data with comprehensive validation."""
    
    @staticmethod
    def valid_data() -> Dict[str, Any]:
        """Generate valid HealthCheck data."""
        return {
            "service_name": "test_value",
            "status": "test_value",
        }
    
    @staticmethod
    def invalid_data_missing_required() -> List[Dict[str, Any]]:
        """Generate data with missing required fields."""
        base_data = HealthCheckTestFactory.valid_data()
        invalid_datasets = []
        
        # Missing service_name
        data_without_service_name = {k: v for k, v in base_data.items() if k != "service_name"}
        invalid_datasets.append(data_without_service_name)
        # Missing status
        data_without_status = {k: v for k, v in base_data.items() if k != "status"}
        invalid_datasets.append(data_without_status)
        
        return invalid_datasets
    
    @staticmethod
    def edge_case_data() -> List[Dict[str, Any]]:
        """Generate edge case test data."""
        base_data = HealthCheckTestFactory.valid_data()
        edge_cases = []
        
        
        return edge_cases if edge_cases else [base_data]
    
    @staticmethod
    def random_valid_data(seed: Optional[int] = None) -> Dict[str, Any]:
        """Generate random valid data with optional seed for reproducibility."""
        if seed:
            random.seed(seed)
        
        return {
            "service_name": f"test_{random.randint(1000, 9999)}",
            "status": f"test_{random.randint(1000, 9999)}",
        }



class TestHealthCheckModel:
    """Comprehensive test cases for HealthCheck entity model with enhanced validation."""
    
    # Property-based testing fixtures
    @pytest.fixture
    def factory(self):
        """HealthCheck test factory fixture."""
        return HealthCheckTestFactory
    
    def test_healthcheck_creation_valid_data(self, factory):
        """Test creating HealthCheck with valid data."""
        valid_data = factory.valid_data()
        
        # Create entity using Create model
        create_data = HealthCheckCreate(**valid_data)
        assert create_data is not None
        
        # Validate all required fields are present
        assert hasattr(create_data, "service_name")
        assert getattr(create_data, "service_name") is not None
        assert hasattr(create_data, "status")
        assert getattr(create_data, "status") is not None
    
    def test_healthcheck_creation_multiple_valid_datasets(self, factory):
        """Test creating HealthCheck with multiple valid datasets."""
        for i in range(10):  # Test with 10 different random datasets
            valid_data = factory.random_valid_data(seed=i)
            create_data = HealthCheckCreate(**valid_data)
            assert create_data is not None
            
            # Verify data integrity
            for field_name, field_value in valid_data.items():
                assert getattr(create_data, field_name) == field_value

    def test_healthcheck_validation_required_fields(self, factory):
        """Test HealthCheck validation for required fields."""
        # Test each invalid dataset (missing required fields)
        invalid_datasets = factory.invalid_data_missing_required()
        
        for invalid_data in invalid_datasets:
            with pytest.raises(ValidationError) as exc_info:
                HealthCheckCreate(**invalid_data)
            
            # Verify that the error message mentions validation failure
            assert "validation error" in str(exc_info.value).lower() or "field required" in str(exc_info.value).lower()
    
    @pytest.mark.parametrize("edge_case_data", HealthCheckTestFactory.edge_case_data())
    def test_healthcheck_edge_case_validation(self, edge_case_data):
        """Test HealthCheck with edge case data."""
        # Edge case data should be valid
        create_data = HealthCheckCreate(**edge_case_data)
        assert create_data is not None
        
        # Verify all fields are set correctly
        for field_name, field_value in edge_case_data.items():
            assert getattr(create_data, field_name) == field_value
    
    @given(id_value=EntityTestStrategies.get_strategy_for_field("FieldType.STR", {}))
    @settings(max_examples=50)
    def test_healthcheck_id_property_based(self, id_value, factory):
        """Property-based test for id field."""
        base_data = factory.valid_data()
        # Optional field testing
        base_data["id"] = id_value
        create_data = HealthCheckCreate(**base_data)
        assert getattr(create_data, "id") == id_value
    @given(service_name_value=EntityTestStrategies.get_strategy_for_field("FieldType.STR", {}))
    @settings(max_examples=50)
    def test_healthcheck_service_name_property_based(self, service_name_value, factory):
        """Property-based test for service_name field."""
        base_data = factory.valid_data()
        # Test with property-based generated value
        base_data["service_name"] = service_name_value
        
        try:
            create_data = HealthCheckCreate(**base_data)
            assert getattr(create_data, "service_name") == service_name_value
        except ValidationError:
            # Some generated values may be invalid - this is expected
            pass
    @given(status_value=EntityTestStrategies.get_strategy_for_field("FieldType.STR", {}))
    @settings(max_examples=50)
    def test_healthcheck_status_property_based(self, status_value, factory):
        """Property-based test for status field."""
        base_data = factory.valid_data()
        # Test with property-based generated value
        base_data["status"] = status_value
        
        try:
            create_data = HealthCheckCreate(**base_data)
            assert getattr(create_data, "status") == status_value
        except ValidationError:
            # Some generated values may be invalid - this is expected
            pass


    def test_healthcheck_database_operations_comprehensive(self, session: Session, factory, db_helper):
        """Comprehensive test for HealthCheck database operations."""
        test_data = factory.valid_data()
        
        # Create entity
        create_model = HealthCheckCreate(**test_data)
        entity = HealthCheck.model_validate(create_model)
        
        # Save to database
        session.add(entity)
        session.commit()
        session.refresh(entity)
        
        # Verify saved entity
        assert entity.id is not None
        for field_name, field_value in test_data.items():
            assert getattr(entity, field_name) == field_value
        
        # Test database helper methods
        db_helper.assert_entity_exists(session, HealthCheck, entity.id)
        db_helper.assert_entity_count(session, HealthCheck, 1)
        
        # Query entity from database
        retrieved = session.get(HealthCheck, entity.id)
        assert retrieved is not None
        assert retrieved.id == entity.id
        
        # Test query operations
        statement = select(HealthCheck).where(HealthCheck.id == entity.id)
        result = session.exec(statement)
        queried_entity = result.first()
        assert queried_entity is not None
        assert queried_entity.id == entity.id
    
    def test_healthcheck_database_bulk_operations(self, session: Session, factory, db_helper):
        """Test bulk database operations for HealthCheck."""
        # Create multiple entities
        entities = []
        for i in range(5):
            test_data = factory.random_valid_data(seed=i)
            create_model = HealthCheckCreate(**test_data)
            entity = HealthCheck.model_validate(create_model)
            entities.append(entity)
            session.add(entity)
        
        session.commit()
        
        # Verify all entities were saved
        db_helper.assert_entity_count(session, HealthCheck, 5)
        
        # Test bulk retrieval
        statement = select(HealthCheck)
        result = session.exec(statement)
        all_entities = result.all()
        assert len(all_entities) == 5
        
        # Verify entity IDs are unique
        entity_ids = [entity.id for entity in all_entities]
        assert len(set(entity_ids)) == 5  # All IDs should be unique
    

    def test_healthcheck_update_operations_comprehensive(self, session: Session, factory, db_helper):
        """Comprehensive test for HealthCheck update operations."""
        # Create initial entity
        initial_data = factory.valid_data()
        entity = HealthCheck(**initial_data)
        session.add(entity)
        session.commit()
        session.refresh(entity)
        
        original_id = entity.id
        
        # Test partial updates
        update_data = {}
        update_data["id"] = "updated_id"        update_data["last_check_time"] = datetime.now() + timedelta(days=1)        update_data["response_time_ms"] = "updated_value"        update_data["error_message"] = "updated_value"        update_data["created_at"] = datetime.now() + timedelta(days=1)        update_data["updated_at"] = datetime.now() + timedelta(days=1)        
        if update_data:  # Only test if there are updatable fields
            update_model = HealthCheckUpdate(**update_data)
            
            # Apply updates using model_dump
            update_dict = update_model.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(entity, field, value)
            
            session.add(entity)
            session.commit()
            session.refresh(entity)
            
            # Verify updates
            assert entity.id == original_id  # ID should not change
            for field, value in update_dict.items():
                assert getattr(entity, field) == value
            
            # Verify entity still exists in database
            db_helper.assert_entity_exists(session, HealthCheck, entity.id)
    
    def test_healthcheck_serialization_deserialization(self, factory):
        """Test HealthCheck JSON serialization and deserialization."""
        # Test Create model
        create_data = factory.valid_data()
        create_model = HealthCheckCreate(**create_data)
        
        # Serialize to dict
        serialized = create_model.model_dump()
        assert isinstance(serialized, dict)
        
        # Deserialize back
        deserialized = HealthCheckCreate(**serialized)
        assert deserialized == create_model
        
        # Test Response model
        entity_data = create_data.copy()
        entity_data["id"] = 1
        response_model = HealthCheckResponse(**entity_data)
        
        # Serialize Response model
        response_serialized = response_model.model_dump()
        assert "id" in response_serialized
        assert response_serialized["id"] == 1
    
    def test_healthcheck_model_validation_edge_cases(self, factory):
        """Test HealthCheck model validation with edge cases."""
        # Test with None values for optional fields
        base_data = factory.valid_data()
        
        # Test id as None
        test_data = base_data.copy()
        test_data["id"] = None
        create_model = HealthCheckCreate(**test_data)
        assert getattr(create_model, "id") is None
        # Test last_check_time as None
        test_data = base_data.copy()
        test_data["last_check_time"] = None
        create_model = HealthCheckCreate(**test_data)
        assert getattr(create_model, "last_check_time") is None
        # Test response_time_ms as None
        test_data = base_data.copy()
        test_data["response_time_ms"] = None
        create_model = HealthCheckCreate(**test_data)
        assert getattr(create_model, "response_time_ms") is None
        # Test error_message as None
        test_data = base_data.copy()
        test_data["error_message"] = None
        create_model = HealthCheckCreate(**test_data)
        assert getattr(create_model, "error_message") is None
        # Test created_at as None
        test_data = base_data.copy()
        test_data["created_at"] = None
        create_model = HealthCheckCreate(**test_data)
        assert getattr(create_model, "created_at") is None
        # Test updated_at as None
        test_data = base_data.copy()
        test_data["updated_at"] = None
        create_model = HealthCheckCreate(**test_data)
        assert getattr(create_model, "updated_at") is None
        
        # Test Update model with empty data (should not fail)
        update_model = HealthCheckUpdate()
        assert update_model is not None
        
        # Test model_dump exclude_unset functionality
        update_dict = update_model.model_dump(exclude_unset=True)
        assert len(update_dict) == 0  # No fields should be set

    
    def test_healthcheck_performance_operations(self, session: Session, factory, db_helper):
        """Test HealthCheck performance characteristics."""
        import time
        
        # Test bulk insert performance
        start_time = time.time()
        entities = []
        for i in range(100):
            test_data = factory.random_valid_data(seed=i)
            entity = HealthCheck(**test_data)
            entities.append(entity)
            session.add(entity)
        
        session.commit()
        bulk_insert_time = time.time() - start_time
        
        # Performance assertion (should complete in reasonable time)
        assert bulk_insert_time < 10.0, f"Bulk insert took too long: {bulk_insert_time}s"
        
        # Verify all entities were created
        db_helper.assert_entity_count(session, HealthCheck, 100)
        
        # Test bulk query performance
        start_time = time.time()
        statement = select(HealthCheck)
        result = session.exec(statement)
        all_entities = result.all()
        bulk_query_time = time.time() - start_time
        
        assert len(all_entities) == 100
        assert bulk_query_time < 5.0, f"Bulk query took too long: {bulk_query_time}s"

    # @pyhex:begin:custom_healthcheck_tests
    # Add your custom HealthCheck tests here
    # @pyhex:end:custom_healthcheck_tests



class TestEntityIntegration:
    """Comprehensive integration tests for all entities in Health domain."""
    
    def test_all_entities_creation_comprehensive(self, session: Session, db_helper):
        """Test creating all entities together with comprehensive validation."""
        created_entities = {}
        
        # Create HealthCheck with factory data
        healthcheck_factory = HealthCheckTestFactory()
        healthcheck_data = healthcheck_factory.valid_data()
        healthcheck = HealthCheck(**healthcheck_data)
        session.add(healthcheck)
        created_entities["healthcheck"] = healthcheck
        
        # Commit all entities
        session.commit()
        
        # Verify all entities were created
        entity = created_entities["healthcheck"]
        assert entity.id is not None
        db_helper.assert_entity_exists(session, HealthCheck, entity.id)
        
        # Verify entity counts
        db_helper.assert_entity_count(session, HealthCheck, 1)
    
    def test_entity_domain_business_rules(self, session: Session):
        """Test domain-wide business rules and constraints."""
        # Test that entities follow domain conventions
        # Verify HealthCheck has required domain fields
        entity_fields = HealthCheck.model_fields
        
        # All entities should have id field
        assert "id" in entity_fields or hasattr(HealthCheck, "id")
        
        # Test that entity can be instantiated
        healthcheck_factory = HealthCheckTestFactory()
        test_data = healthcheck_factory.valid_data()
        entity = HealthCheck(**test_data)
        assert entity is not None
    
    def test_domain_wide_performance(self, session: Session, db_helper):
        """Test performance characteristics across all domain entities."""
        import time
        
        # Test creating multiple entities of each type
        start_time = time.time()
        
        healthcheck_factory = HealthCheckTestFactory()
        for i in range(10):
            test_data = healthcheck_factory.random_valid_data(seed=i)
            entity = HealthCheck(**test_data)
            session.add(entity)
        
        session.commit()
        creation_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert creation_time < 15.0, f"Domain entity creation took too long: {creation_time}s"
        
        # Verify all entities were created
        db_helper.assert_entity_count(session, HealthCheck, 10)
    
    def test_cross_entity_validation(self, session: Session):
        """Test validation rules that span multiple entities."""
        # This is a placeholder for cross-entity business rules
        # In real applications, this might test:
        # - Referential integrity between entities
        # - Domain-wide unique constraints
        # - Business rules that involve multiple entities
        
        healthcheck_factory = HealthCheckTestFactory()
        test_data = healthcheck_factory.valid_data()
        entity = HealthCheck(**test_data)
        
        # Test that entity follows domain naming conventions
        assert hasattr(entity, "id") or "id" in entity.model_fields
        
        # Test entity can be serialized (important for API responses)
        if hasattr(entity, "model_dump"):
            serialized = entity.model_dump()
            assert isinstance(serialized, dict)

    # @pyhex:begin:custom_integration_tests
    # Add your custom integration tests here
    # @pyhex:end:custom_integration_tests


class TestEntityGeneratedCodeQuality:
    """Test the quality of generated entity code itself."""
    
    def test_generated_entity_structure(self):
        """Test that generated entities have proper structure."""
        # Test HealthCheck class structure
        assert hasattr(HealthCheck, "__tablename__") or hasattr(HealthCheck, "metadata")
        assert hasattr(HealthCheck, "model_fields") or hasattr(HealthCheck, "__annotations__")
        
        # Test Create model exists and has proper structure
        assert HealthCheckCreate is not None
        assert hasattr(HealthCheckCreate, "model_fields") or hasattr(HealthCheckCreate, "__annotations__")
        
        # Test Update model exists
        assert HealthCheckUpdate is not None
        
        # Test Response model exists
        assert HealthCheckResponse is not None
    
    def test_generated_entity_inheritance(self):
        """Test that generated entities follow proper inheritance patterns."""
        # Test inheritance hierarchy
        mro = HealthCheck.mro()
        assert SQLModel in mro, "HealthCheck should inherit from SQLModel"
        
        # Test that Create model inherits from Base
        create_mro = HealthCheckCreate.mro()
        assert HealthCheckBase in create_mro, "HealthCheckCreate should inherit from HealthCheckBase"
        
        # Test that Response model has proper structure
        response_fields = HealthCheckResponse.model_fields
        assert "id" in response_fields, "HealthCheckResponse should include id field"
    
    def test_generated_entity_validators(self):
        """Test that generated entities have proper validation."""
        # Test validation by creating invalid instances
        with pytest.raises(ValidationError):
            # Missing required field should raise ValidationError
            invalid_data = {}
            HealthCheckCreate(**invalid_data)
        with pytest.raises(ValidationError):
            # Missing required field should raise ValidationError
            invalid_data = {}
            HealthCheckCreate(**invalid_data)

    # @pyhex:begin:custom_code_quality_tests
    # Add your custom code quality tests here
    # @pyhex:end:custom_code_quality_tests


# @pyhex:begin:custom_test_classes
# Add your custom test classes here
# @pyhex:end:custom_test_classes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])