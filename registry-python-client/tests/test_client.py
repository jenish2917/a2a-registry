"""
Tests for A2A Registry Client

All tests use mocking to avoid requiring a running server.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from a2a_registry import (
    RegistryClient,
    AgentCard,
    Skill,
    RegistryEntry,
    SemanticSearchResult,
    AgentNotFoundError,
    AgentAlreadyExistsError,
    ValidationError,
)
from a2a_registry.models import SemanticSearchResponse, ListAgentsResponse, HeartbeatResponse


# ============== Fixtures ==============

@pytest.fixture
def client():
    """Create a test client."""
    return RegistryClient(base_url="http://localhost:3000")


@pytest.fixture
def sample_agent_card():
    """Create a sample agent card."""
    return AgentCard(
        name="test-agent",
        endpoint="https://test-agent.example.com",
        description="A test agent for unit tests",
        skills=[
            Skill(name="translate", description="Translate text"),
            Skill(name="summarize", description="Summarize text"),
        ]
    )


@pytest.fixture
def sample_registry_entry():
    """Create a sample registry entry response."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "agent_id": "test-agent",
        "agent_card": {
            "name": "test-agent",
            "endpoint": "https://test-agent.example.com",
            "protocolVersion": "0.3",
            "skills": [{"name": "translate"}]
        },
        "owner": "anonymous",
        "tags": ["nlp", "translation"],
        "verified": False,
        "registered_at": "2024-12-24T10:00:00Z",
        "last_updated": "2024-12-24T10:00:00Z",
        "last_heartbeat": None,
        "metadata": {}
    }


@pytest.fixture
def sample_semantic_response():
    """Create a sample semantic search response."""
    return {
        "query": "translate text",
        "results": [
            {
                "agent_id": "translator-agent",
                "agent_card": {
                    "name": "translator-agent",
                    "endpoint": "https://translator.example.com",
                    "protocolVersion": "0.3",
                    "skills": [{"name": "translate"}]
                },
                "tags": ["nlp"],
                "verified": True,
                "similarity_score": 0.95,
                "matched_on": "skills"
            }
        ],
        "total": 1,
        "processing_time_ms": 45.2
    }


def create_mock_response(status_code: int, data: dict, is_success: bool = True):
    """Helper to create mock HTTP response."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.is_success = is_success
    mock_response.json.return_value = data
    mock_response.text = json.dumps(data)
    return mock_response


# ============== AgentCard Tests ==============

class TestAgentCard:
    def test_create_agent_card(self, sample_agent_card):
        """Test creating an agent card."""
        assert sample_agent_card.name == "test-agent"
        assert sample_agent_card.endpoint == "https://test-agent.example.com"
        assert len(sample_agent_card.skills) == 2

    def test_to_api_dict(self, sample_agent_card):
        """Test converting agent card to API dict."""
        api_dict = sample_agent_card.to_api_dict()

        assert api_dict["name"] == "test-agent"
        assert api_dict["endpoint"] == "https://test-agent.example.com"
        assert api_dict["protocolVersion"] == "0.3"
        assert "description" in api_dict
        assert len(api_dict["skills"]) == 2

    def test_agent_card_minimal(self):
        """Test creating minimal agent card."""
        card = AgentCard(name="minimal", endpoint="https://example.com")
        assert card.name == "minimal"
        assert card.skills == []
        assert card.protocol_version == "0.3"


# ============== Client Tests ==============

class TestRegistryClient:
    def test_client_initialization(self):
        """Test client initialization."""
        client = RegistryClient(
            base_url="http://localhost:3000",
            timeout=60.0,
            api_key="test-key"
        )
        assert client.base_url == "http://localhost:3000"
        assert client.timeout == 60.0
        assert client.api_key == "test-key"

    def test_client_strips_trailing_slash(self):
        """Test that client strips trailing slash from base URL."""
        client = RegistryClient(base_url="http://localhost:3000/")
        assert client.base_url == "http://localhost:3000"

    def test_get_agent_method_exists(self, client):
        """Test that get_agent method exists."""
        assert hasattr(client, "get_agent")
        assert callable(client.get_agent)

    def test_semantic_search_method_exists(self, client):
        """Test that semantic_search method exists."""
        assert hasattr(client, "semantic_search")
        assert callable(client.semantic_search)


# ============== Exception Tests ==============

class TestExceptions:
    def test_agent_not_found_error(self):
        """Test AgentNotFoundError."""
        error = AgentNotFoundError("test-agent")
        assert "test-agent" in str(error)
        assert error.status_code == 404
        assert error.agent_id == "test-agent"

    def test_agent_already_exists_error(self):
        """Test AgentAlreadyExistsError."""
        error = AgentAlreadyExistsError("test-agent")
        assert "test-agent" in str(error)
        assert error.status_code == 409

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid field", {"field": "name"})
        assert error.status_code == 400
        assert error.details == {"field": "name"}


# ============== Mocked API Tests ==============

class TestMockedAPIOperations:
    """Tests with mocked HTTP responses - no server required."""

    def test_register_agent_success(self, sample_agent_card, sample_registry_entry):
        """Test registering an agent with mocked response."""
        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_client_instance.post.return_value = create_mock_response(
                201, sample_registry_entry
            )

            client = RegistryClient()
            entry = client.register_agent(
                agent_card=sample_agent_card,
                tags=["nlp", "translation"]
            )

            assert entry.agent_id == "test-agent"
            assert entry.owner == "anonymous"
            assert "nlp" in entry.tags

    def test_get_agent_success(self, sample_registry_entry):
        """Test getting an agent with mocked response."""
        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_client_instance.get.return_value = create_mock_response(
                200, sample_registry_entry
            )

            client = RegistryClient()
            entry = client.get_agent("test-agent")

            assert entry.agent_id == "test-agent"
            assert entry.agent_card.name == "test-agent"

    def test_get_agent_not_found(self):
        """Test getting a non-existent agent."""
        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_client_instance.get.return_value = create_mock_response(
                404, {"message": "Agent not found", "agent_id": "unknown"}, is_success=False
            )

            client = RegistryClient()
            with pytest.raises(AgentNotFoundError):
                client.get_agent("unknown-agent")

    def test_semantic_search_success(self, sample_semantic_response):
        """Test semantic search with mocked response."""
        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_client_instance.post.return_value = create_mock_response(
                200, sample_semantic_response
            )

            client = RegistryClient()
            results = client.semantic_search("translate text", top_k=5)

            assert len(results) == 1
            assert results[0].agent_id == "translator-agent"
            assert results[0].similarity_score == 0.95
            assert results[0].matched_on == "skills"

    def test_list_agents_success(self, sample_registry_entry):
        """Test listing agents with mocked response."""
        list_response = {
            "agents": [sample_registry_entry],
            "total": 1,
            "limit": 50,
            "offset": 0
        }

        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_client_instance.get.return_value = create_mock_response(
                200, list_response
            )

            client = RegistryClient()
            response = client.list_agents(limit=50, offset=0)

            assert response.total == 1
            assert len(response.agents) == 1
            assert response.agents[0].agent_id == "test-agent"

    def test_delete_agent_success(self):
        """Test deleting an agent with mocked response."""
        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.is_success = True
            mock_client_instance.delete.return_value = mock_response

            client = RegistryClient()
            # Should not raise
            client.delete_agent("test-agent")

    def test_heartbeat_success(self):
        """Test heartbeat with mocked response."""
        heartbeat_response = {
            "agent_id": "test-agent",
            "last_heartbeat": "2024-12-24T10:00:00Z"
        }

        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_client_instance.post.return_value = create_mock_response(
                200, heartbeat_response
            )

            client = RegistryClient()
            response = client.heartbeat("test-agent")

            assert response.agent_id == "test-agent"

    def test_health_check_success(self):
        """Test health check with mocked response."""
        health_response = {
            "status": "healthy",
            "database": True,
            "redis": True
        }

        with patch("httpx.Client") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value.__enter__ = Mock(return_value=mock_client_instance)
            MockClient.return_value.__exit__ = Mock(return_value=False)

            mock_client_instance.get.return_value = create_mock_response(
                200, health_response
            )

            client = RegistryClient()
            response = client.health_check()

            assert response["status"] == "healthy"
