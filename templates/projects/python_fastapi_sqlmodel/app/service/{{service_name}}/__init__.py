"""{{ service.name }} package - Domain-agnostic service module.

This package provides {{ service.name }} as a domain-agnostic service
that can be used across multiple domains and use cases.

Exports:
- {{ service.name }}: Main service implementation
- {{ service.name }}Protocol: Service interface/protocol
{%- if service.scope.value == 'singleton' %}
- get_{{ service.package }}_instance: Singleton factory function
{%- endif %}
"""

from .service import {{ service.name }}{% if service.scope.value == 'singleton' %}, get_{{ service.package }}_instance{% endif %}
from .protocols import {{ service.name }}Protocol

__all__ = [
    "{{ service.name }}",
    "{{ service.name }}Protocol",
{%- if service.scope.value == 'singleton' %}
    "get_{{ service.package }}_instance",
{%- endif %}
]