"""
Test Generation Module for SQLModel Domain Validation

This module generates comprehensive automated tests for domain configurations
to verify that generated SQLModel entities, repositories, use cases, and 
interfaces work correctly at runtime.
"""

import textwrap
from pathlib import Path
from typing import Dict

from cli.generate.config.models import DomainConfig, EntityField


class TestGenerator:
    """Generates automated tests for domain configurations."""
    
    def __init__(self, domain_config: DomainConfig, output_dir: Path):
        self.domain_config = domain_config
        self.output_dir = Path(output_dir)
        self.domain_name = domain_config.domain.name
        self.entities = domain_config.entities.entities
        
    def generate_all_validation_tests(self) -> Dict[str, str]:
        """Generate all validation test files."""
        test_files = {}
        
        # Generate entity validation tests
        test_files["entity_tests"] = self._generate_entity_validation_tests()
        
        # Generate SQLAlchemy integration tests  
        test_files["sqlalchemy_tests"] = self._generate_sqlalchemy_integration_tests()
        
        # Generate repository tests
        test_files["repository_tests"] = self._generate_repository_tests()
        
        # Generate use case tests
        test_files["usecase_tests"] = self._generate_usecase_tests()
        
        # Generate interface tests
        test_files["interface_tests"] = self._generate_interface_tests()
        
        # Generate field constraint tests
        test_files["constraint_tests"] = self._generate_field_constraint_tests()
        
        # Generate property-based tests
        test_files["property_tests"] = self._generate_property_based_tests()
        
        return test_files
    
    def _generate_entity_validation_tests(self) -> str:
        """Generate tests for entity creation and validation."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            test_methods = []
            
            # Test basic entity creation
            test_methods.append(self._generate_basic_creation_test(entity))
            
            # Test field validation
            test_methods.append(self._generate_field_validation_test(entity))
            
            # Test SQLModel configuration
            test_methods.append(self._generate_sqlmodel_config_test(entity))
            
            # Test Pydantic v2 compatibility
            test_methods.append(self._generate_pydantic_v2_test(entity))
            
            tests.append(f"""
class Test{entity_name}Entity:
    \"\"\"Test {entity_name} entity creation and validation.\"\"\"
    
{textwrap.indent(chr(10).join(test_methods), '    ')}
""")
        
        return f"""
import pytest
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session

from app.domain.{self.domain_name}.entities import {', '.join(e.name for e in self.entities)}


{chr(10).join(tests)}
"""
    
    def _generate_basic_creation_test(self, entity) -> str:
        """Generate basic entity creation test."""
        entity_name = entity.name
        sample_data = self._generate_sample_data(entity)
        
        return f"""
def test_{entity_name.lower()}_creation_with_valid_data(self):
    \"\"\"Test {entity_name} creation with valid data.\"\"\"
    entity = {entity_name}(
{textwrap.indent(sample_data, '        ')}
    )
    
    assert entity is not None
    assert isinstance(entity, {entity_name})
    {self._generate_field_assertions(entity)}
"""
    
    def _generate_field_validation_test(self, entity) -> str:
        """Generate field validation tests."""
        entity_name = entity.name
        validation_tests = []
        
        for field in entity.fields:
            if field.required:
                validation_tests.append(f"""
    # Test required field: {field.name}
    with pytest.raises((ValueError, TypeError)):
        {entity_name}(**{{k: v for k, v in sample_data.items() if k != '{field.name}'}})
""")
            
            if field.sqlmodel_field and "min_length" in field.sqlmodel_field:
                validation_tests.append(f"""
    # Test min_length constraint: {field.name}
    with pytest.raises(ValueError):
        data = sample_data.copy()
        data['{field.name}'] = ""
        {entity_name}(**data)
""")
            
            if field.sqlmodel_field and "max_length" in field.sqlmodel_field:
                validation_tests.append(f"""
    # Test max_length constraint: {field.name}
    with pytest.raises(ValueError):
        data = sample_data.copy()
        data['{field.name}'] = "x" * 1000
        {entity_name}(**data)
""")
        
        sample_data_var = self._generate_sample_data_dict(entity)
        
        return f"""
def test_{entity_name.lower()}_field_validation(self):
    \"\"\"Test {entity_name} field validation constraints.\"\"\"
    sample_data = {sample_data_var}
    
{textwrap.indent(chr(10).join(validation_tests), '    ')}
"""
    
    def _generate_sqlmodel_config_test(self, entity) -> str:
        """Generate SQLModel configuration tests."""
        entity_name = entity.name
        config_tests = []
        
        # Test primary key configuration
        primary_key_fields = [f for f in entity.fields if f.sqlmodel_field and "primary_key=True" in f.sqlmodel_field]
        if primary_key_fields:
            config_tests.append(f"""
    # Test primary key configuration
    assert hasattr({entity_name}, '__table__')
    primary_keys = [col.name for col in {entity_name}.__table__.primary_key.columns]
    expected_pks = {[f.name for f in primary_key_fields]}
    assert set(primary_keys) == set(expected_pks), f"Expected primary keys {{expected_pks}}, got {{primary_keys}}"
""")
        
        # Test unique constraints
        unique_fields = [f for f in entity.fields if f.sqlmodel_field and "unique=True" in f.sqlmodel_field]
        if unique_fields:
            config_tests.append(f"""
    # Test unique constraints
    table = {entity_name}.__table__
    unique_columns = []
    for constraint in table.constraints:
        if hasattr(constraint, 'columns'):
            unique_columns.extend([col.name for col in constraint.columns])
    expected_unique = {[f.name for f in unique_fields]}
    for field in expected_unique:
        assert field in unique_columns, f"Field {{field}} should have unique constraint"
""")
        
        # Test indexes
        index_fields = [f for f in entity.fields if f.sqlmodel_field and "index=True" in f.sqlmodel_field]
        if index_fields:
            config_tests.append(f"""
    # Test index configuration
    table = {entity_name}.__table__
    indexed_columns = [idx.columns.keys()[0] for idx in table.indexes if len(idx.columns) == 1]
    expected_indexes = {[f.name for f in index_fields]}
    for field in expected_indexes:
        assert field in indexed_columns, f"Field {{field}} should have index"
""")
        
        return f"""
def test_{entity_name.lower()}_sqlmodel_configuration(self):
    \"\"\"Test {entity_name} SQLModel table configuration.\"\"\"
{textwrap.indent(chr(10).join(config_tests), '    ')}
"""
    
    def _generate_pydantic_v2_test(self, entity) -> str:
        """Generate Pydantic v2 compatibility tests."""
        entity_name = entity.name
        
        return f"""
def test_{entity_name.lower()}_pydantic_v2_compatibility(self):
    \"\"\"Test {entity_name} Pydantic v2 compatibility.\"\"\"
    # Test model_config exists (not deprecated Config class)
    assert hasattr({entity_name}, 'model_config'), "Should use model_config not Config class"
    
    # Test model can be created and validated
    sample_data = {self._generate_sample_data_dict(entity)}
    entity = {entity_name}(**sample_data)
    
    # Test model_dump works (Pydantic v2 method)
    data_dict = entity.model_dump()
    assert isinstance(data_dict, dict)
    
    # Test model_validate works (Pydantic v2 method)
    validated_entity = {entity_name}.model_validate(data_dict)
    assert isinstance(validated_entity, {entity_name})
"""
    
    def _generate_sqlalchemy_integration_tests(self) -> str:
        """Generate SQLAlchemy integration tests."""
        entity_names = [e.name for e in self.entities]
        
        return f"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, select

from app.domain.{self.domain_name}.entities import {', '.join(entity_names)}


class TestSQLAlchemyIntegration:
    \"\"\"Test SQLAlchemy integration for {self.domain_name} domain.\"\"\"
    
    @pytest.fixture
    def engine(self):
        \"\"\"Create test database engine.\"\"\"
        engine = create_engine("sqlite:///:memory:", echo=True)
        SQLModel.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def session(self, engine):
        \"\"\"Create test database session.\"\"\"
        with Session(engine) as session:
            yield session
    
{self._generate_crud_tests()}
    
{self._generate_constraint_enforcement_tests()}
    
{self._generate_relationship_tests()}
"""
    
    def _generate_crud_tests(self) -> str:
        """Generate CRUD operation tests."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            sample_data = self._generate_sample_data_dict(entity)
            
            tests.append(f"""
    def test_{entity_name.lower()}_crud_operations(self, session):
        \"\"\"Test CRUD operations for {entity_name}.\"\"\"
        # Create
        sample_data = {sample_data}
        entity = {entity_name}(**sample_data)
        session.add(entity)
        session.commit()
        session.refresh(entity)
        
        assert entity.id is not None
        
        # Read
        found_entity = session.get({entity_name}, entity.id)
        assert found_entity is not None
        assert found_entity.id == entity.id
        
        # Update
        {self._generate_update_test_code(entity)}
        session.commit()
        session.refresh(found_entity)
        
        # Delete
        session.delete(found_entity)
        session.commit()
        
        deleted_entity = session.get({entity_name}, entity.id)
        assert deleted_entity is None
""")
        
        return chr(10).join(tests)
    
    def _generate_constraint_enforcement_tests(self) -> str:
        """Generate constraint enforcement tests."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            constraint_tests = []
            
            # Test unique constraints
            unique_fields = [f for f in entity.fields if f.sqlmodel_field and "unique=True" in f.sqlmodel_field]
            if unique_fields:
                for field in unique_fields:
                    sample_data = self._generate_sample_data_dict(entity)
                    constraint_tests.append(f"""
        # Test unique constraint on {field.name}
        entity1 = {entity_name}(**{sample_data})
        session.add(entity1)
        session.commit()
        
        # Try to create duplicate
        entity2 = {entity_name}(**{sample_data})
        session.add(entity2)
        
        with pytest.raises(Exception):  # SQLAlchemy will raise integrity error
            session.commit()
        session.rollback()
""")
            
            # Test required field constraints
            required_fields = [f for f in entity.fields if f.required and f.name != "id"]
            if required_fields:
                for field in required_fields:
                    constraint_tests.append(f"""
        # Test required field constraint: {field.name}
        data = {self._generate_sample_data_dict(entity)}
        data['{field.name}'] = None
        
        with pytest.raises((ValueError, TypeError)):
            {entity_name}(**data)
""")
            
            if constraint_tests:
                tests.append(f"""
    def test_{entity_name.lower()}_constraint_enforcement(self, session):
        \"\"\"Test constraint enforcement for {entity_name}.\"\"\"
{textwrap.indent(chr(10).join(constraint_tests), '        ')}
""")
        
        return chr(10).join(tests)
    
    def _generate_relationship_tests(self) -> str:
        """Generate relationship tests."""
        # This would be more complex for actual relationships
        # For now, generate placeholder test
        return """
    def test_entity_relationships(self, session):
        \"\"\"Test entity relationships (if any).\"\"\"
        # TODO: Add relationship tests when foreign keys are detected
        pass
"""
    
    def _generate_repository_tests(self) -> str:
        """Generate repository layer tests."""
        return f"""
import pytest
from unittest.mock import Mock, AsyncMock
from sqlmodel import Session

from app.repository.{self.domain_name}.protocols import {self.domain_name}RepositoryProtocol
from app.repository.{self.domain_name}.repository import {self.domain_name}Repository
from app.domain.{self.domain_name}.entities import {', '.join(e.name for e in self.entities)}


class Test{self.domain_name}Repository:
    \"\"\"Test {self.domain_name} repository implementation.\"\"\"
    
    @pytest.fixture
    def mock_session(self):
        \"\"\"Create mock database session.\"\"\"
        return Mock(spec=Session)
    
    @pytest.fixture
    def repository(self, mock_session):
        \"\"\"Create repository instance.\"\"\"
        return {self.domain_name}Repository(session=mock_session)
    
{self._generate_repository_method_tests()}
"""
    
    def _generate_repository_method_tests(self) -> str:
        """Generate repository method tests."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            sample_data = self._generate_sample_data_dict(entity)
            
            tests.append(f"""
    async def test_create_{entity_name.lower()}(self, repository, mock_session):
        \"\"\"Test {entity_name} creation in repository.\"\"\"
        sample_data = {sample_data}
        entity = {entity_name}(**sample_data)
        
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        result = await repository.create(entity)
        
        mock_session.add.assert_called_once_with(entity)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(entity)
        assert result == entity
    
    async def test_get_{entity_name.lower()}_by_id(self, repository, mock_session):
        \"\"\"Test {entity_name} retrieval by ID.\"\"\"
        entity_id = 1
        expected_entity = {entity_name}(id=entity_id, **{sample_data})
        
        mock_session.get = AsyncMock(return_value=expected_entity)
        
        result = await repository.get_by_id(entity_id)
        
        mock_session.get.assert_called_once_with({entity_name}, entity_id)
        assert result == expected_entity
    
    async def test_list_{entity_name.lower()}s(self, repository, mock_session):
        \"\"\"Test {entity_name} listing.\"\"\"
        entities = [
            {entity_name}(id=1, **{sample_data}),
            {entity_name}(id=2, **{sample_data})
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = entities
        mock_session.exec = AsyncMock(return_value=mock_result)
        
        result = await repository.list()
        
        assert len(result) == 2
        assert all(isinstance(e, {entity_name}) for e in result)
""")
        
        return chr(10).join(tests)
    
    def _generate_usecase_tests(self) -> str:
        """Generate use case layer tests."""
        return f"""
import pytest
from unittest.mock import Mock, AsyncMock

from app.usecase.{self.domain_name}.usecase import {self.domain_name}UseCase
from app.usecase.{self.domain_name}.schemas import {', '.join(f'Create{e.name}Request, {e.name}Response' for e in self.entities)}
from app.domain.{self.domain_name}.entities import {', '.join(e.name for e in self.entities)}


class Test{self.domain_name}UseCase:
    \"\"\"Test {self.domain_name} use case implementation.\"\"\"
    
    @pytest.fixture
    def mock_repository(self):
        \"\"\"Create mock repository.\"\"\"
        return Mock()
    
    @pytest.fixture
    def usecase(self, mock_repository):
        \"\"\"Create use case instance.\"\"\"
        return {self.domain_name}UseCase(repository=mock_repository)
    
{self._generate_usecase_method_tests()}
"""
    
    def _generate_usecase_method_tests(self) -> str:
        """Generate use case method tests."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            sample_data = self._generate_sample_data_dict(entity)
            
            tests.append(f"""
    async def test_create_{entity_name.lower()}(self, usecase, mock_repository):
        \"\"\"Test {entity_name} creation use case.\"\"\"
        request_data = {sample_data}
        request = Create{entity_name}Request(**request_data)
        
        created_entity = {entity_name}(id=1, **request_data)
        mock_repository.create = AsyncMock(return_value=created_entity)
        
        result = await usecase.create_{entity_name.lower()}(request)
        
        assert isinstance(result, {entity_name}Response)
        mock_repository.create.assert_called_once()
""")
        
        return chr(10).join(tests)
    
    def _generate_interface_tests(self) -> str:
        """Generate interface layer tests."""
        return f"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock

from app.interface.{self.domain_name}.router import router
from app.main import app


class Test{self.domain_name}Interface:
    \"\"\"Test {self.domain_name} interface layer.\"\"\"
    
    @pytest.fixture
    def client(self):
        \"\"\"Create test client.\"\"\"
        return TestClient(app)
    
{self._generate_endpoint_tests()}
"""
    
    def _generate_endpoint_tests(self) -> str:
        """Generate API endpoint tests."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            sample_data = self._generate_sample_data_dict(entity, for_json=True)
            
            tests.append(f"""
    def test_create_{entity_name.lower()}_endpoint(self, client):
        \"\"\"Test {entity_name} creation endpoint.\"\"\"
        data = {sample_data}
        
        response = client.post("/{self.domain_name.lower()}/", json=data)
        
        assert response.status_code in [200, 201]
        result = response.json()
        assert "id" in result
    
    def test_get_{entity_name.lower()}_endpoint(self, client):
        \"\"\"Test {entity_name} retrieval endpoint.\"\"\"
        # First create an entity
        data = {sample_data}
        create_response = client.post("/{self.domain_name.lower()}/", json=data)
        created_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/{self.domain_name.lower()}/{{created_id}}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == created_id
""")
        
        return chr(10).join(tests)
    
    def _generate_field_constraint_tests(self) -> str:
        """Generate property-based tests for field constraints."""
        return f"""
import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import text, integers, booleans

from app.domain.{self.domain_name}.entities import {', '.join(e.name for e in self.entities)}


class TestFieldConstraints:
    \"\"\"Test field constraints using property-based testing.\"\"\"
    
{self._generate_hypothesis_tests()}
"""
    
    def _generate_hypothesis_tests(self) -> str:
        """Generate Hypothesis property-based tests."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            
            # Generate property-based tests for string constraints
            string_fields = [f for f in entity.fields if f.type == "str" and f.sqlmodel_field]
            for field in string_fields:
                if "min_length" in field.sqlmodel_field or "max_length" in field.sqlmodel_field:
                    tests.append(f"""
    @given(text(min_size=1, max_size=100))
    def test_{entity_name.lower()}_{field.name}_valid_strings(self, value):
        \"\"\"Test {entity_name}.{field.name} accepts valid strings.\"\"\"
        data = {self._generate_minimal_data_dict(entity)}
        data['{field.name}'] = value
        
        try:
            entity = {entity_name}(**data)
            assert getattr(entity, '{field.name}') == value
        except ValueError:
            # Some strings might still be invalid due to other constraints
            pass
""")
            
            # Generate property-based tests for integer constraints  
            integer_fields = [f for f in entity.fields if f.type == "int" and f.name != "id"]
            for field in integer_fields:
                tests.append(f"""
    @given(integers(min_value=0, max_value=1000000))
    def test_{entity_name.lower()}_{field.name}_valid_integers(self, value):
        \"\"\"Test {entity_name}.{field.name} accepts valid integers.\"\"\"
        data = {self._generate_minimal_data_dict(entity)}
        data['{field.name}'] = value
        
        entity = {entity_name}(**data)
        assert getattr(entity, '{field.name}') == value
""")
        
        return chr(10).join(tests)
    
    def _generate_property_based_tests(self) -> str:
        """Generate property-based tests."""
        return f"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime

from app.domain.{self.domain_name}.entities import {', '.join(e.name for e in self.entities)}


class TestPropertyBased:
    \"\"\"Property-based tests for {self.domain_name} domain.\"\"\"
    
{self._generate_invariant_tests()}
"""
    
    def _generate_invariant_tests(self) -> str:
        """Generate invariant tests."""
        tests = []
        
        for entity in self.entities:
            entity_name = entity.name
            
            tests.append(f"""
    @given(st.text(min_size=1), st.text(min_size=1))
    def test_{entity_name.lower()}_invariants(self, name_value, description_value):
        \"\"\"Test {entity_name} invariants hold.\"\"\"
        assume(len(name_value.strip()) > 0)
        assume(len(description_value.strip()) > 0)
        
        data = {self._generate_minimal_data_dict(entity)}
        
        # Update with hypothesis values
        string_fields = [f for f in {entity.fields} if f.type == "str" and f.required]
        if string_fields:
            data[string_fields[0].name] = name_value.strip()
            if len(string_fields) > 1:
                data[string_fields[1].name] = description_value.strip()
        
        entity = {entity_name}(**data)
        
        # Test invariants
        assert entity is not None
        assert hasattr(entity, 'id')
        
        # Test serialization roundtrip
        data_dict = entity.model_dump()
        recreated = {entity_name}.model_validate(data_dict)
        assert recreated == entity
""")
        
        return chr(10).join(tests)
    
    # Helper methods
    def _generate_sample_data(self, entity) -> str:
        """Generate sample data string for entity."""
        data_lines = []
        
        for field in entity.fields:
            if field.name == "id":
                continue  # Skip ID field in creation
                
            value = self._generate_field_value(field)
            data_lines.append(f'{field.name}={value}')
        
        return ',\n'.join(data_lines)
    
    def _generate_sample_data_dict(self, entity, for_json: bool = False) -> str:
        """Generate sample data as dictionary."""
        data = {}
        
        for field in entity.fields:
            if field.name == "id":
                continue  # Skip ID field in creation
                
            value = self._generate_field_value(field, for_dict=True, for_json=for_json)
            data[field.name] = value
        
        return str(data)
    
    def _generate_minimal_data_dict(self, entity) -> str:
        """Generate minimal valid data dictionary."""
        data = {}
        
        for field in entity.fields:
            if field.name == "id":
                continue
                
            if field.required:
                value = self._generate_field_value(field, for_dict=True, minimal=True)
                data[field.name] = value
        
        return str(data)
    
    def _generate_field_value(self, field: EntityField, for_dict: bool = False, for_json: bool = False, minimal: bool = False):
        """Generate appropriate value for field."""
        if field.type == "str":
            if minimal:
                return '"test"' if not for_dict else "test"
            return f'"test_{field.name}"' if not for_dict else f"test_{field.name}"
        elif field.type == "int":
            return "1" if not for_dict else 1
        elif field.type == "float":
            return "1.0" if not for_dict else 1.0
        elif field.type == "bool":
            return "True" if not for_dict else True
        elif field.type == "datetime":
            if for_json:
                return "2023-01-01T00:00:00" if not for_dict else "2023-01-01T00:00:00"
            return "datetime.utcnow()" if not for_dict else "datetime.utcnow()"
        elif field.type == "Optional[str]":
            return '"optional_value"' if not for_dict else "optional_value"
        elif field.type == "Optional[int]":
            return "1" if not for_dict else 1
        elif field.type == "Optional[datetime]":
            if for_json:
                return "2023-01-01T00:00:00" if not for_dict else "2023-01-01T00:00:00"
            return "datetime.utcnow()" if not for_dict else "datetime.utcnow()"
        else:
            return f'"default_{field.name}"' if not for_dict else f"default_{field.name}"
    
    def _generate_field_assertions(self, entity) -> str:
        """Generate field assertion statements."""
        assertions = []
        
        for field in entity.fields:
            if field.name == "id":
                continue
                
            if field.type in ["str", "int", "float", "bool"]:
                assertions.append(f"assert entity.{field.name} is not None")
            elif field.type.startswith("Optional"):
                assertions.append(f"# {field.name} is optional")
        
        return '\n    '.join(assertions)
    
    def _generate_update_test_code(self, entity) -> str:
        """Generate update test code."""
        # Find first string field to update
        string_fields = [f for f in entity.fields if f.type == "str" and f.name != "id"]
        if string_fields:
            field = string_fields[0]
            return f'found_entity.{field.name} = "updated_value"'
        
        # Fall back to first field that's not ID
        other_fields = [f for f in entity.fields if f.name != "id"]
        if other_fields:
            field = other_fields[0]
            new_value = self._generate_field_value(field, for_dict=True)
            return f'found_entity.{field.name} = {new_value}'
        
        return "# No updateable fields found"


def generate_validation_tests(domain_config: DomainConfig, output_dir: Path) -> Dict[str, str]:
    """Generate comprehensive validation tests for domain configuration."""
    generator = TestGenerator(domain_config, output_dir)
    return generator.generate_all_validation_tests()