"""
A2A Registry Semantic Search - Data Models

Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Any
from datetime import datetime


class Skill(BaseModel):
    """Agent skill definition."""
    name: str
    description: Optional[str] = None
    input_schema: Optional[dict] = Field(default=None, alias="inputSchema")
    output_schema: Optional[dict] = Field(default=None, alias="outputSchema")


class Capabilities(BaseModel):
    """Agent capabilities."""
    streaming: bool = False
    push_notifications: bool = Field(default=False, alias="pushNotifications")


class AgentCard(BaseModel):
    """A2A Agent Card following the protocol specification."""
    name: str
    description: Optional[str] = None
    endpoint: str
    protocol_version: str = Field(default="0.3", alias="protocolVersion")
    capabilities: Optional[Capabilities] = None
    skills: List[Skill] = []

    class Config:
        populate_by_name = True


class RegistryEntry(BaseModel):
    """Agent registry entry from database."""
    id: str
    agent_id: str
    agent_card: AgentCard
    owner: str
    tags: List[str] = []
    verified: bool = False
    registered_at: datetime
    last_updated: datetime
    last_heartbeat: Optional[datetime] = None
    metadata: dict = {}


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search."""
    query: str = Field(..., description="Natural language query to search for agents")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    min_score: float = Field(default=0.5, ge=0, le=1, description="Minimum similarity score")
    filters: Optional[dict] = Field(default=None, description="Additional filters (tags, verified)")


class SemanticSearchResult(BaseModel):
    """Single search result with similarity score."""
    agent_id: str
    agent_card: AgentCard
    tags: List[str]
    verified: bool
    similarity_score: float = Field(..., ge=0, le=1)
    matched_on: str = Field(..., description="What field matched (name, description, skills)")


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search."""
    query: str
    results: List[SemanticSearchResult]
    total: int
    processing_time_ms: float


class IndexAgentRequest(BaseModel):
    """Request to index a single agent for semantic search."""
    agent_id: str
    agent_card: AgentCard
    tags: List[str] = []


class IndexAllResponse(BaseModel):
    """Response after indexing all agents."""
    indexed_count: int
    failed_count: int
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str = "a2a-semantic-search"
    version: str = "0.1.0"
    embedding_model: str
    database_connected: bool
    redis_connected: bool
