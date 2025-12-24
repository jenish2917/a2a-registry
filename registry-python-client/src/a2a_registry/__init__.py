"""
A2A Registry Python Client

Python SDK for interacting with the A2A Agent Registry.
"""

from a2a_registry.client import RegistryClient
from a2a_registry.models import (
    AgentCard,
    Skill,
    Capabilities,
    RegistryEntry,
    SemanticSearchResult,
)
from a2a_registry.exceptions import (
    RegistryError,
    AgentNotFoundError,
    AgentAlreadyExistsError,
    ValidationError,
    ConnectionError,
)

__version__ = "0.1.0"
__all__ = [
    "RegistryClient",
    "AgentCard",
    "Skill",
    "Capabilities",
    "RegistryEntry",
    "SemanticSearchResult",
    "RegistryError",
    "AgentNotFoundError",
    "AgentAlreadyExistsError",
    "ValidationError",
    "ConnectionError",
]
