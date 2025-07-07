"""Service layer - Domain-agnostic business logic services.

This package contains domain-agnostic services that provide reusable
business logic across multiple domains and use cases in the application.

Service Architecture:
- Each service has its own directory with complete scaffolding
- Protocol-based interfaces for dependency injection and testing
- @pyhex preservation markers for custom implementation
- Configurable dependency injection scopes (singleton, scoped, transient)

Service Directory Structure:
```
service/
├── EmailService/          # Email sending service
│   ├── service.py         # Service implementation
│   ├── protocols.py       # Service interface
│   ├── test_service.py    # Comprehensive tests
│   ├── service.yaml       # Service configuration
│   └── __init__.py        # Package exports
├── FileStorageService/    # File management service
└── ...                    # Other domain-agnostic services
```

Usage in Use Cases:
```python
from app.service.EmailService import EmailServiceProtocol

class UserRegistrationUseCase:
    def __init__(self, email_service: EmailServiceProtocol):
        self.email_service = email_service
    
    async def register_user(self, user_data):
        # Use the email service
        await self.email_service.send_welcome_email(user_data.email)
```

Benefits:
- Domain-agnostic: Services work across all domains
- Testable: Protocol-based dependency injection
- Reusable: Single implementation, multiple consumers
- Maintainable: Clear separation of concerns
- Scalable: Individual service directories and configurations
"""

# Services are imported dynamically based on generated directories
# Each service provides its own __init__.py with proper exports

__all__ = []