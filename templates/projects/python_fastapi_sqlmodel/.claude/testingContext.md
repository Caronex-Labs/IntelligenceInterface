# Testing Context & BDD Integration

## Testing Philosophy

### Quality-First Approach
The Python FastAPI SQLModel template system follows comprehensive testing strategies to ensure:
- **Template Reliability**: Generated code works consistently
- **Code Quality**: Generated applications meet production standards
- **Regression Prevention**: Changes don't break existing functionality
- **Developer Confidence**: Template system can be trusted for real projects

### Multi-Layer Testing Strategy

#### Template System Testing
- **Unit Tests**: Individual components of code generation tool
- **Integration Tests**: Complete domain generation workflows
- **End-to-End Tests**: Generated applications function correctly
- **Performance Tests**: Generation speed and output quality

#### Generated Code Testing
- **Template Validation**: Generated code follows architectural patterns
- **Functional Testing**: Generated APIs work as expected
- **Database Testing**: Generated models and migrations work correctly
- **Integration Testing**: All generated components work together

## BDD Integration Framework

### Template System BDD Scenarios

#### Code Generation Features
```gherkin
Feature: Domain Code Generation
  As a developer using the template system
  I want to generate complete domain implementations from YAML
  So that I can rapidly create production-ready backends

Scenario: Generate Simple Domain
  Given I have a YAML configuration for a "User" domain
  When I run the code generation tool
  Then it should create all hexagonal architecture layers
  And the generated FastAPI application should run successfully
  And all generated tests should pass

Scenario: Generate Domain with Relationships
  Given I have a YAML configuration with "User" and "Post" domains
  And the configuration defines a one-to-many relationship
  When I run the code generation tool
  Then it should create both domains with proper relationships
  And the generated SQLModel schemas should have correct foreign keys
  And the generated API endpoints should support related entity operations

Scenario: Preserve Custom Code During Regeneration
  Given I have generated a "User" domain
  And I have added custom business logic in preservation blocks
  When I regenerate the domain with updated configuration
  Then my custom business logic should be preserved
  And the updated configuration changes should be applied
  And all tests should still pass
```

#### Template Quality Features
```gherkin
Feature: Generated Code Quality
  As a developer using generated code
  I want the output to follow best practices
  So that I can deploy to production with confidence

Scenario: Generated Code Follows Architecture Patterns
  Given I generate any domain using the template system
  When I analyze the generated code structure
  Then it should follow hexagonal architecture principles
  And each layer should have clear separation of concerns
  And dependencies should point inward toward the domain

Scenario: Generated Tests Provide Adequate Coverage
  Given I generate a domain with the template system
  When I run the generated test suite
  Then it should test all generated functionality
  And coverage should be above 90%
  And tests should follow BDD patterns with clear scenarios

Scenario: Generated API Documentation is Complete
  Given I generate a domain and start the FastAPI application
  When I access the auto-generated API documentation
  Then it should document all endpoints
  And request/response schemas should be complete
  And examples should be provided for all operations
```

### Generated Application BDD Scenarios

#### Standard CRUD Operations
```gherkin
Feature: Generated CRUD API
  As an API consumer
  I want to perform standard operations on domain entities
  So that I can build applications using the backend

Scenario: Create Entity Successfully
  Given the generated API is running
  When I POST valid entity data to the creation endpoint
  Then I should receive a 201 Created response
  And the response should include the created entity with ID
  And the entity should be persisted in the database

Scenario: Retrieve Entity by ID
  Given an entity exists in the database
  When I GET the entity by its ID
  Then I should receive a 200 OK response
  And the response should contain the complete entity data

Scenario: Update Entity Successfully
  Given an entity exists in the database
  When I PUT updated data to the entity endpoint
  Then I should receive a 200 OK response
  And the entity should be updated in the database
  And the response should reflect the changes

Scenario: Delete Entity Successfully
  Given an entity exists in the database
  When I DELETE the entity by its ID
  Then I should receive a 204 No Content response
  And the entity should be removed from the database

Scenario: Handle Entity Not Found
  Given no entity exists with a specific ID
  When I try to retrieve, update, or delete that entity
  Then I should receive a 404 Not Found response
  And the error message should be clear and helpful
```

#### Relationship Management
```gherkin
Feature: Generated Relationship Handling
  As an API consumer
  I want to work with related entities
  So that I can model complex business domains

Scenario: Create Entity with Related Data
  Given I have a domain with relationships configured
  When I POST entity data that includes related entity references
  Then the entity should be created with proper relationships
  And I should be able to retrieve the entity with related data

Scenario: Query Related Entities
  Given entities with relationships exist in the database
  When I GET an entity that has related entities
  Then the response should include related entity data
  And I should be able to navigate relationships through the API

Scenario: Update Relationships
  Given entities with relationships exist
  When I update the relationship references in an entity
  Then the relationships should be updated correctly
  And related entities should maintain referential integrity
```

## Testing Implementation Patterns

### Template System Test Structure
```
tests/
├── unit/                           # Unit tests for generation tool
│   ├── test_config_processing.py   # YAML configuration parsing
│   ├── test_template_engine.py     # Jinja2 template processing
│   ├── test_code_preservation.py   # Custom code preservation
│   └── test_file_generation.py     # File generation logic
├── integration/                    # Integration tests
│   ├── test_domain_generation.py   # Complete domain generation
│   ├── test_relationship_handling.py # Relationship generation
│   └── test_regeneration.py        # Code preservation during regeneration
├── e2e/                            # End-to-end tests
│   ├── test_simple_domain.py       # Generate and test simple domain
│   ├── test_complex_domain.py      # Generate and test complex domain
│   └── test_riskbook_generation.py # Generate Riskbook-like domain
├── fixtures/                       # Test data and configurations
│   ├── yaml_configs/               # Sample YAML configurations
│   ├── expected_outputs/           # Expected generated code
│   └── custom_code_samples/        # Sample custom code for preservation
└── performance/                    # Performance tests
    ├── test_generation_speed.py    # Code generation performance
    └── test_generated_app_performance.py # Generated app performance
```

### Generated Application Test Pattern
```python
# Standard test pattern for generated applications
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.main import app
from src.database import get_session

class TestGeneratedEntityAPI:
    """BDD-style tests for generated entity API"""
    
    @pytest.fixture
    async def client(self, test_session: AsyncSession):
        """Test client with database session override"""
        def get_test_session():
            return test_session
        
        app.dependency_overrides[get_session] = get_test_session
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
        app.dependency_overrides.clear()
    
    async def test_create_entity_successfully(self, client: AsyncClient):
        """
        Scenario: Create Entity Successfully
          Given the generated API is running
          When I POST valid entity data to the creation endpoint
          Then I should receive a 201 Created response
          And the response should include the created entity with ID
        """
        # Given - test setup implicit
        entity_data = {
            "name": "Test Entity",
            "description": "Test Description"
        }
        
        # When
        response = await client.post("/entities/", json=entity_data)
        
        # Then
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == entity_data["name"]
        assert response_data["description"] == entity_data["description"]
        assert "id" in response_data
        assert response_data["id"] is not None
    
    async def test_retrieve_entity_by_id(self, client: AsyncClient, sample_entity):
        """
        Scenario: Retrieve Entity by ID
          Given an entity exists in the database
          When I GET the entity by its ID
          Then I should receive a 200 OK response
          And the response should contain the complete entity data
        """
        # Given - sample_entity fixture provides existing entity
        entity_id = sample_entity.id
        
        # When
        response = await client.get(f"/entities/{entity_id}")
        
        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == entity_id
        assert response_data["name"] == sample_entity.name
```

### Code Preservation Testing
```python
class TestCodePreservation:
    """Tests for custom code preservation during regeneration"""
    
    def test_preserve_custom_methods(self, temp_dir):
        """
        Scenario: Preserve Custom Code During Regeneration
          Given I have generated code with custom business logic
          When I regenerate with updated configuration
          Then my custom business logic should be preserved
        """
        # Given - generate initial code with custom additions
        initial_config = load_yaml_config("user_domain.yaml")
        generator = DomainGenerator(output_dir=temp_dir)
        generator.generate(initial_config)
        
        # Add custom code in preservation blocks
        entity_file = temp_dir / "src/domain/user/entity.py"
        add_custom_code(entity_file, """
        # @pyhex:begin(custom_methods)
        def custom_business_logic(self):
            return "Custom implementation"
        # @pyhex:end(custom_methods)
        """)
        
        # When - regenerate with updated config
        updated_config = modify_config(initial_config, add_field="email")
        generator.generate(updated_config)
        
        # Then - custom code preserved and new config applied
        regenerated_content = entity_file.read_text()
        assert "custom_business_logic" in regenerated_content
        assert "email" in regenerated_content  # New field added
```

## Quality Assurance Patterns

### Test-Driven Template Development
1. **Write BDD Scenarios First**: Define expected behavior before implementation
2. **Create Failing Tests**: Implement tests that fail with current code
3. **Implement Template**: Develop template to make tests pass
4. **Refactor and Improve**: Clean up while maintaining test coverage

### Continuous Integration Testing
```yaml
# Example CI pipeline for template system
name: Template System CI

on: [push, pull_request]

jobs:
  test-template-system:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .[dev,generation]
      
      - name: Run template system tests
        run: |
          pytest tests/unit tests/integration -v
      
      - name: Test domain generation
        run: |
          python -m cmd.generate --config tests/fixtures/yaml_configs/user_domain.yaml --output /tmp/generated
          cd /tmp/generated && python -m pytest tests/ -v
      
      - name: Test generated application
        run: |
          cd /tmp/generated
          uvicorn src.main:app &
          sleep 5
          pytest tests/e2e/ -v
```

### Performance Testing Integration
```python
class TestGenerationPerformance:
    """Performance tests for template generation"""
    
    def test_simple_domain_generation_speed(self):
        """Generation should complete within reasonable time"""
        config = load_yaml_config("simple_domain.yaml")
        
        start_time = time.time()
        generator.generate(config)
        generation_time = time.time() - start_time
        
        assert generation_time < 5.0  # Should complete in under 5 seconds
    
    def test_complex_domain_generation_speed(self):
        """Complex domains should still generate efficiently"""
        config = load_yaml_config("complex_domain_with_relationships.yaml")
        
        start_time = time.time()
        generator.generate(config)
        generation_time = time.time() - start_time
        
        assert generation_time < 30.0  # Complex domain under 30 seconds
```

## Integration with Development Workflow

### Pre-Commit Testing
- **Template System Tests**: Run unit and integration tests
- **Code Quality**: Linting and type checking
- **Generated Code Validation**: Quick generation test

### Development Testing
- **Rapid Feedback**: Fast unit tests during development
- **Integration Validation**: Test complete generation workflows
- **Manual Testing**: Generate test domains and validate manually

### Release Testing
- **Full Test Suite**: All tests including performance
- **Real-World Generation**: Generate complex domains like Riskbook
- **Documentation Testing**: Ensure generated documentation is accurate

### Testing Tools Integration

#### pytest Configuration
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "unit: Unit tests for template system components",
    "integration: Integration tests for complete workflows", 
    "e2e: End-to-end tests for generated applications",
    "performance: Performance tests for generation speed",
    "slow: Tests that take longer to run",
]
asyncio_mode = "auto"
```

#### Coverage Requirements
- **Template System**: Minimum 95% code coverage
- **Generated Code**: Ensure generated tests provide adequate coverage
- **Critical Paths**: 100% coverage for core generation logic

#### Test Data Management
- **Fixture Organization**: Clear separation of test configurations
- **Data Generation**: Factories for creating test data
- **Cleanup**: Proper test isolation and cleanup procedures