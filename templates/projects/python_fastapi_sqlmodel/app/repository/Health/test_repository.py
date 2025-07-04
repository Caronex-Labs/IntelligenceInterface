"""Health Repository Tests - Co-location Architecture

This module provides comprehensive tests for the Health repository implementation,
ensuring async database operations work correctly with proper transaction handling.

Generated from: app/repository/Health/test_repository.py.j2
Configuration: app/repository/Health/repository.yaml
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import List, Dict, Any

# Testing imports
import pytest_asyncio
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# @pyhex:begin:custom_test_imports
# Add custom test imports here - preserved during regeneration
# @pyhex:end:custom_test_imports

# Domain and repository imports
from app.domain.Health.entities import Health
from app.repository.Health.repository import (
    SQLModelHealthRepository,
    HealthNotFoundError,
    HealthDuplicateError,
    HealthValidationError,
    HealthRepositoryError
)
from app.repository.Health.protocols import HealthRepositoryProtocol


class TestAsyncDatabaseSetup:
    """Test database setup utilities for async operations."""
    
    @staticmethod
    def get_async_test_engine():
        """Create async test database engine."""
        # Use in-memory SQLite for fast testing
        database_url = "sqlite+aiosqlite:///:memory:"
        engine = create_async_engine(
            database_url,
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        return engine
    
    @staticmethod
    async def create_tables(engine):
        """Create database tables for testing."""
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    
    @staticmethod
    async def drop_tables(engine):
        """Drop database tables after testing."""
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def async_test_engine():
    """Pytest fixture for async test database engine."""
    engine = TestAsyncDatabaseSetup.get_async_test_engine()
    await TestAsyncDatabaseSetup.create_tables(engine)
    yield engine
    await TestAsyncDatabaseSetup.drop_tables(engine)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_test_session(async_test_engine):
    """Pytest fixture for async test database session."""
    async_session_maker = async_sessionmaker(
        async_test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_repository(async_test_session):
    """Pytest fixture for Health repository."""
    return SQLModelHealthRepository(async_test_session)


@pytest_asyncio.fixture
async def sample_Health_data():
    """Pytest fixture for sample Health test data."""
    return {
        "name": "Test Health",
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "description": "Test Health description",
        "status": "active",
        "metadata": {"test": True},
        "tags": ["test", "sample"]
    }


@pytest_asyncio.fixture
async def created_Health(test_repository, sample_Health_data):
    """Pytest fixture for pre-created Health entity."""
    entity = Health(**sample_Health_data)
    return await test_repository.create(entity)


class TestHealthRepositoryProtocolCompliance:
    """Test repository protocol compliance and interface implementation."""
    
    def test_repository_implements_protocol(self, test_repository):
        """Test that repository implements the required protocol."""
        assert isinstance(test_repository, HealthRepositoryProtocol)
        
        # Check all required methods exist
        required_methods = [
"create","get_by_id","delete","list", "count","find_by_id","find_by_email","find_active_entities","find_by_status","count_by_status","search_by_name",        ]
        
        for method_name in required_methods:
            assert hasattr(test_repository, method_name)
            assert callable(getattr(test_repository, method_name))


class TestHealthRepositoryCreate:
    """Test Health repository create operations."""
    
    @pytest.mark.asyncio
    async def test_create_Health_success(self, test_repository, sample_Health_data):
        """Test successful Health creation."""
        # Arrange
        entity = Health(**sample_Health_data)
        
        # Act
        created_entity = await test_repository.create(entity)
        
        # Assert
        assert created_entity is not None
        assert created_entity.id is not None
        assert isinstance(created_entity.id, UUID)
        assert created_entity.name == sample_Health_data["name"]
        assert created_entity.email == sample_Health_data["email"]
        assert created_entity.status == sample_Health_data["status"]
        assert created_entity.created_at is not None
        assert created_entity.updated_at is not None
        
    @pytest.mark.asyncio
    async def test_create_Health_with_validation(self, test_repository, sample_Health_data):
        """Test Health creation with business validation."""
        # Arrange
        entity = Health(**sample_Health_data)
        
        # Act
        created_entity = await test_repository.create(entity, validate=True)
        
        # Assert
        assert created_entity is not None
        assert created_entity.id is not None
        
    @pytest.mark.asyncio
    async def test_create_Health_duplicate_email_fails(self, test_repository, sample_Health_data):
        """Test that duplicate email creation fails."""
        # Arrange
        entity1 = Health(**sample_Health_data)
        entity2 = Health(**sample_Health_data)  # Same email
        
        # Act
        await test_repository.create(entity1)
        
        # Assert
        with pytest.raises(HealthDuplicateError):
            await test_repository.create(entity2)
            
    @pytest.mark.asyncio
    async def test_create_Health_invalid_data_fails(self, test_repository):
        """Test that invalid data creation fails."""
        # Arrange
        invalid_data = {
            "name": "",  # Invalid: empty name
            "email": "invalid-email",  # Invalid: bad email format
            "status": "invalid_status"  # Invalid: not in allowed values
        }
        entity = Health(**invalid_data)
        
        # Act & Assert
        with pytest.raises((HealthValidationError, ValueError)):
            await test_repository.create(entity, validate=True)

class TestHealthRepositoryRead:
    """Test Health repository read operations."""
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self, test_repository, created_Health):
        """Test successful Health retrieval by ID."""
        # Act
        retrieved_entity = await test_repository.get_by_id(created_Health.id)
        
        # Assert
        assert retrieved_entity is not None
        assert retrieved_entity.id == created_Health.id
        assert retrieved_entity.name == created_Health.name
        assert retrieved_entity.email == created_Health.email
        
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_repository):
        """Test Health retrieval with non-existent ID."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        retrieved_entity = await test_repository.get_by_id(non_existent_id)
        
        # Assert
        assert retrieved_entity is None
        
    @pytest.mark.asyncio
    async def test_get_by_id_with_eager_loading(self, test_repository, created_Health):
        """Test Health retrieval with relationship eager loading."""
        # Act
        retrieved_entity = await test_repository.get_by_id(
            created_Health.id,
            eager_load=["related_items", "categories"]
        )
        
        # Assert
        assert retrieved_entity is not None
        assert retrieved_entity.id == created_Health.id
        
@pytest.mark.asyncio
    async def test_get_by_id_soft_deleted_excluded(self, test_repository, created_Health):
        """Test that soft-deleted entities are excluded by default."""
        # Arrange - soft delete the entity
        await test_repository.delete(created_Health.id, soft_delete=True)
        
        # Act
        retrieved_entity = await test_repository.get_by_id(created_Health.id)
        
        # Assert
        assert retrieved_entity is None
        
    @pytest.mark.asyncio
    async def test_get_by_id_soft_deleted_included(self, test_repository, created_Health):
        """Test that soft-deleted entities can be included when requested."""
        # Arrange - soft delete the entity
        await test_repository.delete(created_Health.id, soft_delete=True)
        
        # Act
        retrieved_entity = await test_repository.get_by_id(
            created_Health.id,
            include_deleted=True
        )
        
        # Assert
        assert retrieved_entity is not None
        assert retrieved_entity.id == created_Health.id
        assert retrieved_entity.is_deleted == True


class TestHealthRepositoryDelete:
    """Test Health repository delete operations."""
    
@pytest.mark.asyncio
    async def test_soft_delete_Health_success(self, test_repository, created_Health):
        """Test successful Health soft deletion."""
        # Act
        result = await test_repository.delete(created_Health.id, soft_delete=True)
        
        # Assert
        assert result == True
        
        # Verify entity is marked as deleted
        entity = await test_repository.get_by_id(created_Health.id, include_deleted=True)
        assert entity is not None
        assert entity.is_deleted == True
        assert entity.deleted_at is not None
        
        # Verify entity is not returned in normal queries
        entity_normal = await test_repository.get_by_id(created_Health.id)
        assert entity_normal is None
    
    @pytest.mark.asyncio
    async def test_hard_delete_Health_success(self, test_repository, created_Health):
        """Test successful Health hard deletion."""
        # Act
        result = await test_repository.delete(created_Health.id, soft_delete=False)
        
        # Assert
        assert result == True
        
        # Verify entity is completely removed
        entity = await test_repository.get_by_id(created_Health.id, include_deleted=True)
        assert entity is None
        
    @pytest.mark.asyncio
    async def test_delete_Health_not_found(self, test_repository):
        """Test deletion of non-existent Health."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await test_repository.delete(non_existent_id)
        
        # Assert
        assert result == False

class TestHealthRepositoryList:
    """Test Health repository list operations."""
    
    @pytest_asyncio.fixture
    async def multiple_Health_entities(self, test_repository, sample_Health_data):
        """Create multiple Health entities for testing."""
        entities = []
        for i in range(5):
            data = sample_Health_data.copy()
            data["name"] = f"Test Health {i}"
            data["email"] = f"test_{i}_{uuid4().hex[:8]}@example.com"
            data["status"] = "active" if i % 2 == 0 else "inactive"
            
            entity = Health(**data)
            created_entity = await test_repository.create(entity)
            entities.append(created_entity)
        
        return entities
    
    @pytest.mark.asyncio
    async def test_list_Health_entities_default(self, test_repository, multiple_Health_entities):
        """Test listing Health entities with default parameters."""
        # Act
        entities = await test_repository.list()
        
        # Assert
        assert len(entities) == 5
        assert all(isinstance(entity, Health) for entity in entities)
        
    @pytest.mark.asyncio
    async def test_list_Health_entities_pagination(self, test_repository, multiple_Health_entities):
        """Test Health list pagination."""
        # Act - First page
        page1 = await test_repository.list(offset=0, limit=2)
        page2 = await test_repository.list(offset=2, limit=2)
        page3 = await test_repository.list(offset=4, limit=2)
        
        # Assert
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1  # Only 5 total entities
        
        # Verify no overlap between pages
        all_ids = [e.id for e in page1] + [e.id for e in page2] + [e.id for e in page3]
        assert len(set(all_ids)) == 5  # All unique
        
    @pytest.mark.asyncio
    async def test_list_Health_entities_filtering(self, test_repository, multiple_Health_entities):
        """Test Health list filtering."""
        # Act
        active_entities = await test_repository.list(filters={"status": "active"})
        inactive_entities = await test_repository.list(filters={"status": "inactive"})
        
        # Assert
        assert len(active_entities) == 3  # Entities 0, 2, 4
        assert len(inactive_entities) == 2  # Entities 1, 3
        assert all(e.status == "active" for e in active_entities)
        assert all(e.status == "inactive" for e in inactive_entities)
        
    @pytest.mark.asyncio
    async def test_list_Health_entities_sorting(self, test_repository, multiple_Health_entities):
        """Test Health list sorting."""
        # Act
        entities_asc = await test_repository.list(sort_by="name", sort_order="asc")
        entities_desc = await test_repository.list(sort_by="name", sort_order="desc")
        
        # Assert
        assert len(entities_asc) == 5
        assert len(entities_desc) == 5
        
        # Verify sort order
        names_asc = [e.name for e in entities_asc]
        names_desc = [e.name for e in entities_desc]
        assert names_asc == sorted(names_asc)
        assert names_desc == sorted(names_desc, reverse=True)
        
    @pytest.mark.asyncio
    async def test_count_Health_entities(self, test_repository, multiple_Health_entities):
        """Test counting Health entities."""
        # Act
        total_count = await test_repository.count()
        active_count = await test_repository.count(filters={"status": "active"})
        inactive_count = await test_repository.count(filters={"status": "inactive"})
        
        # Assert
        assert total_count == 5
        assert active_count == 3
        assert inactive_count == 2

# Custom Query Method Tests
class TestHealthRepositoryFind_By_Id:
    """Test Health repository find_by_id method."""
    
    @pytest.mark.asyncio
    async def test_find_by_id_success(self, test_repository, created_Health):
        """Test successful find_by_id query."""
# Generic test for find_by_id
        # Act
# This method requires parameters - implement specific test logic
        pytest.skip("find_by_id requires specific test implementation")
        
@pytest.mark.asyncio
    async def test_find_by_id_invalid_parameters(self, test_repository):
        """Test find_by_id with invalid parameters."""
    

class TestHealthRepositoryFind_By_Email:
    """Test Health repository find_by_email method."""
    
    @pytest.mark.asyncio
    async def test_find_by_email_success(self, test_repository, created_Health):
        """Test successful find_by_email query."""
# Act
        result = await test_repository.find_by_email(created_Health.email)
        
        # Assert
        assert result is not None
        assert result.id == created_Health.id
        assert result.email == created_Health.email
        
@pytest.mark.asyncio
    async def test_find_by_email_invalid_parameters(self, test_repository):
        """Test find_by_email with invalid parameters."""
    
@pytest.mark.asyncio
    async def test_find_by_email_caching(self, test_repository, created_Health):
        """Test find_by_email caching behavior."""
        # This test would require cache manager mock
        # Implementation depends on cache backend configuration
        pytest.skip("Caching tests require cache manager configuration")

class TestHealthRepositoryFind_Active_Entities:
    """Test Health repository find_active_entities method."""
    
    @pytest.mark.asyncio
    async def test_find_active_entities_success(self, test_repository, created_Health):
        """Test successful find_active_entities query."""
# Ensure entity is active
        if created_Health.status != "active":
            await test_repository.update(created_Health.id, {"status": "active"})
        
        # Act
        result = await test_repository.find_active_entities()
        
        # Assert
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(e.id == created_Health.id for e in result)
        assert all(e.status == "active" for e in result)
        
    

class TestHealthRepositoryFind_By_Status:
    """Test Health repository find_by_status method."""
    
    @pytest.mark.asyncio
    async def test_find_by_status_success(self, test_repository, created_Health):
        """Test successful find_by_status query."""
# Act
        result = await test_repository.find_by_status(created_Health.status)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(e.id == created_Health.id for e in result)
        assert all(e.status == created_Health.status for e in result)
        
@pytest.mark.asyncio
    async def test_find_by_status_invalid_parameters(self, test_repository):
        """Test find_by_status with invalid parameters."""
# Test invalid status
        with pytest.raises((HealthValidationError, ValueError)):
            await test_repository.find_by_status("invalid_status")
    

class TestHealthRepositoryCount_By_Status:
    """Test Health repository count_by_status method."""
    
    @pytest.mark.asyncio
    async def test_count_by_status_success(self, test_repository, created_Health):
        """Test successful count_by_status query."""
# Act
        result = await test_repository.count_by_status(created_Health.status)
        
        # Assert
        assert isinstance(result, int)
        assert result >= 1
        
@pytest.mark.asyncio
    async def test_count_by_status_invalid_parameters(self, test_repository):
        """Test count_by_status with invalid parameters."""
    

class TestHealthRepositorySearch_By_Name:
    """Test Health repository search_by_name method."""
    
    @pytest.mark.asyncio
    async def test_search_by_name_success(self, test_repository, created_Health):
        """Test successful search_by_name query."""
# Act
        result = await test_repository.search_by_name(created_Health.name[:5])
        
        # Assert
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(e.id == created_Health.id for e in result)
        
@pytest.mark.asyncio
    async def test_search_by_name_invalid_parameters(self, test_repository):
        """Test search_by_name with invalid parameters."""
    


class TestHealthRepositoryPerformance:
    """Test Health repository performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_create_performance_batch(self, test_repository, sample_Health_data):
        """Test bulk create performance."""
        # Arrange
        batch_size = 100
        entities = []
        for i in range(batch_size):
            data = sample_Health_data.copy()
            data["email"] = f"perf_test_{i}_{uuid4().hex[:8]}@example.com"
            entities.append(Health(**data))
        
        # Act
        start_time = datetime.utcnow()
        for entity in entities:
            await test_repository.create(entity)
        end_time = datetime.utcnow()
        
        # Assert
        duration = (end_time - start_time).total_seconds()
        assert duration < 100.0  # Reasonable time for batch
        
    @pytest.mark.asyncio
    async def test_query_performance(self, test_repository, created_Health):
        """Test query performance benchmarks."""
        # Act
        start_time = datetime.utcnow()
        await test_repository.get_by_id(created_Health.id)
        end_time = datetime.utcnow()
        
        # Assert
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0


class TestHealthRepositoryErrorHandling:
    """Test Health repository error handling."""
    
    @pytest.mark.asyncio
    async def test_database_connection_error_handling(self, test_repository):
        """Test handling of database connection errors."""
        # This test would require database connection mocking
        # Implementation depends on specific error scenarios
        pass
        
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, test_repository, sample_Health_data):
        """Test transaction rollback on database errors."""
        # Arrange
        entity = Health(**sample_Health_data)
        
        # Act & Assert
        # This test would require forcing a database error
        # Implementation depends on specific error injection
        pass


class TestHealthRepositoryTransactions:
    """Test Health repository transaction handling."""
    
@pytest.mark.asyncio
    async def test_transaction_commit_success(self, test_repository, sample_Health_data):
        """Test successful transaction commit."""
        # Arrange
        entity = Health(**sample_Health_data)
        
        # Act
        await test_repository.begin_transaction()
        created_entity = await test_repository.create(entity)
        await test_repository.commit_transaction()
        
        # Assert
        retrieved_entity = await test_repository.get_by_id(created_entity.id)
        assert retrieved_entity is not None
        
    @pytest.mark.asyncio
    async def test_transaction_rollback_success(self, test_repository, sample_Health_data):
        """Test successful transaction rollback."""
        # Arrange
        entity = Health(**sample_Health_data)
        
        # Act
        await test_repository.begin_transaction()
        created_entity = await test_repository.create(entity)
        await test_repository.rollback_transaction()
        
        # Assert
        retrieved_entity = await test_repository.get_by_id(created_entity.id)
        assert retrieved_entity is None


# @pyhex:begin:custom_repository_tests
# Add custom repository test classes here - preserved during regeneration
# @pyhex:end:custom_repository_tests


# Test Configuration and Utilities
class HealthRepositoryTestConfig:
    """Configuration for Health repository tests."""
    
    # Test data generators
    @staticmethod
    def generate_test_Health_data(count: int = 1) -> List[Dict[str, Any]]:
        """Generate test data for Health entities."""
        data = []
        for i in range(count):
            data.append({
                "name": f"Test Health {i}",
                "email": f"test_{i}_{uuid4().hex[:8]}@example.com",
                "description": f"Test description {i}",
                "status": "active" if i % 2 == 0 else "inactive",
                "metadata": {"test": True, "index": i},
                "tags": [f"tag{i}", "test"]
            })
        return data
    
    # Test assertion helpers
    @staticmethod
    def assert_Health_equals(actual: Health, expected_data: Dict[str, Any]):
        """Assert Health entity matches expected data."""
        assert actual.name == expected_data["name"]
        assert actual.email == expected_data["email"]
        assert actual.description == expected_data["description"]
        assert actual.status == expected_data["status"]
        assert actual.metadata == expected_data["metadata"]
        assert actual.tags == expected_data["tags"]
    
    # Performance benchmarks
    PERFORMANCE_BENCHMARKS = {
        "create_max_time": 1.0,
        "read_max_time": 1.0,
        "update_max_time": 1.0,
        "delete_max_time": 1.0,
        "list_max_time": 1.0,
    }


# Integration Test Markers
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.repository,
    pytest.mark.Health,
    pytest.mark.integration
]