"""
A2A Registry Client - Main Client Class

Provides synchronous and asynchronous methods for interacting with the A2A Agent Registry.
"""

from typing import Any, Optional
import httpx

from a2a_registry.models import (
    AgentCard,
    RegistryEntry,
    SemanticSearchResult,
    SemanticSearchResponse,
    ListAgentsResponse,
    HeartbeatResponse,
)
from a2a_registry.exceptions import (
    RegistryError,
    AgentNotFoundError,
    AgentAlreadyExistsError,
    ValidationError,
    ConnectionError,
    SemanticSearchError,
)


class RegistryClient:
    """
    Python client for the A2A Agent Registry.

    Provides methods for registering, discovering, and managing agents
    in the A2A ecosystem.

    Example:
        >>> client = RegistryClient("http://localhost:3000")
        >>> agent = client.register_agent(
        ...     agent_card=AgentCard(
        ...         name="my-agent",
        ...         endpoint="https://example.com",
        ...         skills=[Skill(name="translate")]
        ...     ),
        ...     tags=["nlp"]
        ... )
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        timeout: float = 30.0,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the registry client.

        Args:
            base_url: Base URL of the A2A Registry server.
            timeout: Request timeout in seconds.
            api_key: Optional API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key

        # Build headers
        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    def _get_client(self) -> httpx.Client:
        """Create a new HTTP client."""
        return httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._headers,
        )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}

        if response.status_code == 404:
            raise AgentNotFoundError(data.get("agent_id", "unknown"))
        elif response.status_code == 409:
            raise AgentAlreadyExistsError(data.get("agent_id", "unknown"))
        elif response.status_code == 400:
            raise ValidationError(data.get("message", "Validation failed"), data)
        elif response.status_code >= 500:
            raise RegistryError(
                data.get("message", "Server error"),
                status_code=response.status_code
            )
        elif not response.is_success:
            raise RegistryError(
                data.get("message", f"Request failed with status {response.status_code}"),
                status_code=response.status_code
            )

        return data

    # ============== Agent CRUD Operations ==============

    def register_agent(
        self,
        agent_card: AgentCard | dict[str, Any],
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RegistryEntry:
        """
        Register a new agent in the registry.

        Args:
            agent_card: Agent card with name, endpoint, skills, etc.
            tags: Optional list of tags for categorization.
            metadata: Optional metadata dictionary.

        Returns:
            RegistryEntry with the registered agent details.

        Raises:
            AgentAlreadyExistsError: If agent with same ID exists.
            ValidationError: If agent card is invalid.
        """
        # Convert AgentCard to dict if needed
        if isinstance(agent_card, AgentCard):
            card_data = agent_card.to_api_dict()
        else:
            card_data = agent_card

        payload = {
            "agentCard": card_data,
            "tags": tags or [],
            "metadata": metadata or {},
        }

        try:
            with self._get_client() as client:
                response = client.post("/api/v1/agents", json=payload)
                data = self._handle_response(response)
                return RegistryEntry(**data)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")

    def get_agent(self, agent_id: str) -> RegistryEntry:
        """
        Get an agent by ID.

        Args:
            agent_id: Unique identifier of the agent.

        Returns:
            RegistryEntry with agent details.

        Raises:
            AgentNotFoundError: If agent doesn't exist.
        """
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/agents/{agent_id}")
                data = self._handle_response(response)
                return RegistryEntry(**data)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")

    def update_agent(
        self,
        agent_id: str,
        agent_card: AgentCard | dict[str, Any],
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RegistryEntry:
        """
        Update an existing agent.

        Args:
            agent_id: ID of the agent to update.
            agent_card: Updated agent card.
            tags: Updated tags.
            metadata: Updated metadata.

        Returns:
            Updated RegistryEntry.

        Raises:
            AgentNotFoundError: If agent doesn't exist.
        """
        if isinstance(agent_card, AgentCard):
            card_data = agent_card.to_api_dict()
        else:
            card_data = agent_card

        payload = {
            "agentCard": card_data,
            "tags": tags or [],
            "metadata": metadata or {},
        }

        try:
            with self._get_client() as client:
                response = client.put(f"/api/v1/agents/{agent_id}", json=payload)
                data = self._handle_response(response)
                return RegistryEntry(**data)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")

    def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent from the registry.

        Args:
            agent_id: ID of the agent to delete.

        Raises:
            AgentNotFoundError: If agent doesn't exist.
        """
        try:
            with self._get_client() as client:
                response = client.delete(f"/api/v1/agents/{agent_id}")
                if response.status_code == 404:
                    raise AgentNotFoundError(agent_id)
                elif not response.is_success:
                    self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")

    # ============== Search Operations ==============

    def list_agents(
        self,
        limit: int = 50,
        offset: int = 0,
        tags: list[str] | None = None,
        skill: str | None = None,
        verified: bool | None = None,
    ) -> ListAgentsResponse:
        """
        List agents with optional filters.

        Args:
            limit: Maximum number of results.
            offset: Pagination offset.
            tags: Filter by tags.
            skill: Filter by skill name.
            verified: Filter by verification status.

        Returns:
            ListAgentsResponse with agents and pagination info.
        """
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if tags:
            params["tags"] = tags
        if skill:
            params["skill"] = skill
        if verified is not None:
            params["verified"] = str(verified).lower()

        try:
            with self._get_client() as client:
                response = client.get("/api/v1/agents", params=params)
                data = self._handle_response(response)
                return ListAgentsResponse(**data)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")

    def search_by_skill(self, skill: str) -> list[RegistryEntry]:
        """
        Search agents by skill name.

        Args:
            skill: Name of the skill to search for.

        Returns:
            List of agents with the specified skill.
        """
        result = self.list_agents(skill=skill)
        return result.agents

    def search_by_tags(self, tags: list[str]) -> list[RegistryEntry]:
        """
        Search agents by tags.

        Args:
            tags: List of tags to search for.

        Returns:
            List of agents with any of the specified tags.
        """
        result = self.list_agents(tags=tags)
        return result.agents

    # ============== Semantic Search ==============

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.5,
        tags: list[str] | None = None,
        verified_only: bool = False,
    ) -> list[SemanticSearchResult]:
        """
        Search for agents using natural language.

        Uses NLP embeddings to find semantically similar agents based on
        their names, descriptions, skills, and tags.

        Args:
            query: Natural language search query.
            top_k: Maximum number of results to return.
            min_score: Minimum similarity score (0-1).
            tags: Optional tag filter.
            verified_only: Only return verified agents.

        Returns:
            List of SemanticSearchResult with similarity scores.

        Raises:
            SemanticSearchError: If search fails.
        """
        payload: dict[str, Any] = {
            "query": query,
            "top_k": top_k,
            "min_score": min_score,
        }

        filters: dict[str, Any] = {}
        if tags:
            filters["tags"] = tags
        if verified_only:
            filters["verified"] = True
        if filters:
            payload["filters"] = filters

        try:
            with self._get_client() as client:
                response = client.post("/api/v1/agents/semantic/search", json=payload)
                data = self._handle_response(response)

                response_obj = SemanticSearchResponse(**data)
                return response_obj.results
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")
        except RegistryError:
            raise
        except Exception as e:
            raise SemanticSearchError(str(e))

    # ============== Health & Monitoring ==============

    def heartbeat(self, agent_id: str) -> HeartbeatResponse:
        """
        Send heartbeat for an agent.

        Args:
            agent_id: ID of the agent sending heartbeat.

        Returns:
            HeartbeatResponse with timestamp.

        Raises:
            AgentNotFoundError: If agent doesn't exist.
        """
        try:
            with self._get_client() as client:
                response = client.post(f"/api/v1/agents/{agent_id}/heartbeat")
                data = self._handle_response(response)
                return HeartbeatResponse(**data)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")

    def health_check(self) -> dict[str, Any]:
        """
        Check if the registry is healthy.

        Returns:
            Health status dictionary.
        """
        try:
            with self._get_client() as client:
                response = client.get("/health")
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to registry: {e}")

    # ============== Context Manager ==============

    def __enter__(self) -> "RegistryClient":
        return self

    def __exit__(self, *args: Any) -> None:
        pass
