# Services Layer - Domain-Agnostic Business Logic

The Services layer provides reusable, domain-agnostic business logic that can be used across multiple domains and use cases in the application.

## Architecture Overview

Services follow these key principles:

- **Domain-Agnostic**: Services work across all domains, not tied to specific business entities
- **Single Responsibility**: Each service focuses on one specific area of functionality
- **Protocol-Based**: Clean interfaces enable dependency injection and testing
- **Individual Directories**: Each service has its own complete directory structure
- **Template-Generated**: Scaffolding generated from configuration, custom logic preserved

## Service Directory Structure

Each service follows this standardized structure:

```
app/service/
├── EmailService/              # Email sending service
│   ├── service.py             # Service implementation
│   ├── protocols.py           # Service interface/protocol
│   ├── test_service.py        # Comprehensive test suite
│   ├── service.yaml           # Service configuration
│   └── __init__.py            # Package exports
├── FileStorageService/        # File management service
├── NotificationService/       # Push notifications service
└── README.md                  # This documentation
```

## Generating Services

### Using the CLI Tool

```bash
# Generate a new service from configuration
fastapi-sqlmodel-generator generate-service EmailService --config=email_service.yaml

# Generate service with method definitions
fastapi-sqlmodel-generator generate-service FileStorageService \
  --methods="upload_file,download_file,delete_file" \
  --output=./app/service/
```

### Using MCP (Model Context Protocol)

```python
# Generate service through MCP interface
service_config = {
    "service": {
        "name": "EmailService",
        "description": "Domain-agnostic email sending service",
        "methods": [
            {
                "name": "send_email",
                "parameters": [
                    {"name": "to_email", "type": "EmailStr", "required": True},
                    {"name": "subject", "type": "str", "required": True},
                    {"name": "body", "type": "str", "required": True}
                ],
                "return_type": "bool",
                "description": "Send email to recipient"
            }
        ],
        "scope": "scoped"
    }
}

result = generate_service_from_config(
    service_config=json.dumps(service_config),
    output_dir="./app/service/"
)
```

## Service Configuration

Services are configured using YAML files that define the service interface:

```yaml
# service.yaml
service:
  name: "EmailService"
  description: "Domain-agnostic email sending service"
  scope: "scoped"  # singleton, scoped, transient
  
  dependencies:
    - "LoggingService"
    - "ConfigurationService"
  
  methods:
    - name: "send_email"
      description: "Send email to recipient"
      async_method: true
      return_type: "bool"
      parameters:
        - name: "to_email"
          type: "EmailStr"
          required: true
        - name: "subject"
          type: "str"
          required: true
        - name: "body"
          type: "str"
          required: true
```

## Implementation Patterns

### Service Implementation

```python
# service.py
class EmailService(EmailServiceProtocol):
    def __init__(self, config_service: ConfigurationServiceProtocol):
        self._config = config_service
    
    async def send_email(
        self, 
        to_email: EmailStr, 
        subject: str, 
        body: str
    ) -> bool:
        # @pyhex:preserve_start:send_email_implementation
        try:
            # Custom implementation here
            smtp_config = await self._config.get_smtp_settings()
            # Send email logic...
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
        # @pyhex:preserve_end:send_email_implementation
```

### Protocol Interface

```python
# protocols.py
class EmailServiceProtocol(Protocol):
    async def send_email(
        self, 
        to_email: EmailStr, 
        subject: str, 
        body: str
    ) -> bool:
        """Send email to recipient."""
        ...
```

### Usage in Use Cases

```python
# In use case implementations
class UserRegistrationUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        email_service: EmailServiceProtocol,  # Service dependency
        notification_service: NotificationServiceProtocol
    ):
        self._user_repo = user_repo
        self._email_service = email_service
        self._notification_service = notification_service
    
    async def register_user(self, registration_data: UserRegistrationRequest):
        # Create user entity
        user = await self._user_repo.create(registration_data.to_entity())
        
        # Use services for cross-cutting concerns
        await self._email_service.send_welcome_email(user.email)
        await self._notification_service.send_push_notification(
            user.id, "Welcome to our platform!"
        )
        
        return user
```

## Dependency Injection Scopes

Services support three dependency injection scopes:

### Singleton
- Single instance shared across the application
- Use for stateless services with expensive initialization
- Example: Configuration services, logging services

```python
@lru_cache(maxsize=1)
def get_email_service_instance() -> EmailService:
    return EmailService(config_service=get_config_service())
```

### Scoped
- New instance per request/transaction scope
- Use for services that maintain request-specific state
- Example: User context services, request tracking services

### Transient
- New instance every time service is requested
- Use for lightweight, stateless operations
- Example: Calculation services, formatting services

## Testing Patterns

### Unit Testing

```python
class TestEmailService:
    @pytest.fixture
    def service(self) -> EmailService:
        mock_config = Mock(spec=ConfigurationServiceProtocol)
        return EmailService(config_service=mock_config)
    
    @pytest.mark.asyncio
    async def test_send_email_success(self, service: EmailService):
        result = await service.send_email(
            to_email="test@example.com",
            subject="Test",
            body="Test message"
        )
        assert result is True
```

### Integration Testing

```python
class TestEmailServiceIntegration:
    @pytest.mark.asyncio
    async def test_email_service_with_real_config(self):
        config_service = RealConfigurationService()
        email_service = EmailService(config_service=config_service)
        
        result = await email_service.send_email(
            to_email="integration@test.com",
            subject="Integration Test",
            body="Testing email service integration"
        )
        
        assert result is True
```

## Best Practices

### Service Design
1. **Single Responsibility**: Each service should have one clear purpose
2. **Stateless**: Prefer stateless services for better scalability
3. **Error Handling**: Implement comprehensive error handling and logging
4. **Type Safety**: Use proper type hints and protocol definitions
5. **Documentation**: Provide clear docstrings for all public methods

### Dependencies
1. **Protocol-Based**: Always depend on protocols, not concrete implementations
2. **Minimal Dependencies**: Keep service dependencies to a minimum
3. **Circular Dependencies**: Avoid circular dependencies between services
4. **Constructor Injection**: Use constructor injection for all dependencies

### Implementation
1. **Preservation Markers**: Use @pyhex markers to protect custom code
2. **Async by Default**: Use async/await for I/O operations
3. **Logging**: Log important operations and errors
4. **Configuration**: Externalize configuration through dependency injection

### Testing
1. **Protocol Compliance**: Test that implementations follow protocols
2. **Mock Dependencies**: Use mock dependencies for unit testing
3. **Integration Tests**: Test service interactions with real dependencies
4. **Error Scenarios**: Test error handling and edge cases

## Common Service Types

### Communication Services
- EmailService: Send emails and notifications
- SMSService: Send text messages
- PushNotificationService: Send push notifications
- SlackService: Integrate with Slack API

### Storage Services
- FileStorageService: File upload/download/management
- ImageProcessingService: Image resizing and optimization
- CacheService: Caching operations
- DocumentGenerationService: PDF/report generation

### External Integration Services
- PaymentService: Payment processing integration
- GeocodingService: Address and location services
- AuditLogService: System audit and tracking
- MetricsService: Application metrics collection

### Utility Services
- ValidationService: Complex validation logic
- EncryptionService: Data encryption/decryption
- HashingService: Password hashing and verification
- TokenService: JWT token generation and validation

## Migration from Domain-Specific Logic

When extracting logic from domain-specific implementations to services:

1. **Identify Reusable Logic**: Look for logic used across multiple domains
2. **Extract Interface**: Define a clear protocol for the service
3. **Create Service**: Generate service scaffolding using templates
4. **Implement Logic**: Move reusable logic to service implementation
5. **Update Dependencies**: Inject service into use cases that need it
6. **Test Thoroughly**: Ensure all consumers work with the new service

This approach ensures clean separation of concerns while maintaining the benefits of hexagonal architecture and dependency injection.