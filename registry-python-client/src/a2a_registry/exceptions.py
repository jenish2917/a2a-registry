"""
A2A Registry Client - Exceptions

Custom exception classes for error handling.
"""


class RegistryError(Exception):
    """Base exception for registry errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AgentNotFoundError(RegistryError):
    """Raised when an agent is not found."""

    def __init__(self, agent_id: str):
        super().__init__(
            f"Agent not found: {agent_id}",
            status_code=404
        )
        self.agent_id = agent_id


class AgentAlreadyExistsError(RegistryError):
    """Raised when trying to register an agent that already exists."""

    def __init__(self, agent_id: str):
        super().__init__(
            f"Agent already exists: {agent_id}",
            status_code=409
        )
        self.agent_id = agent_id


class ValidationError(RegistryError):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, status_code=400)
        self.details = details or {}


class ConnectionError(RegistryError):
    """Raised when connection to the registry fails."""

    def __init__(self, message: str = "Failed to connect to registry"):
        super().__init__(message, status_code=None)


class SemanticSearchError(RegistryError):
    """Raised when semantic search fails."""

    def __init__(self, message: str):
        super().__init__(f"Semantic search failed: {message}", status_code=500)
