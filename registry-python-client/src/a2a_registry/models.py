"""
A2A Registry Client - Data Models

Pydantic models for API requests and responses.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class Skill(BaseModel):
    """Agent skill definition."""

    name: str
    description: Optional[str] = None
    input_schema: Optional[dict[str, Any]] = Field(default=None, alias="inputSchema")
    output_schema: Optional[dict[str, Any]] = Field(default=None, alias="outputSchema")

    class Config:
        populate_by_name = True


class Capabilities(BaseModel):
    """Agent capabilities."""

    streaming: bool = False
    push_notifications: bool = Field(default=False, alias="pushNotifications")

    class Config:
        populate_by_name = True


class AgentCard(BaseModel):
    """
    A2A Agent Card following the protocol specification.

    An AgentCard contains metadata about an agent including its name,
    endpoint, capabilities, and available skills.
    """

    name: str
    description: Optional[str] = None
    endpoint: str
    protocol_version: str = Field(default="0.3", alias="protocolVersion")
    capabilities: Optional[Capabilities] = None
    skills: list[Skill] = Field(default_factory=list)

    class Config:
        populate_by_name = True

    def to_api_dict(self) -> dict[str, Any]:
        """Convert to API-compatible dictionary with camelCase keys."""
        data: dict[str, Any] = {
            "name": self.name,
            "endpoint": self.endpoint,
            "protocolVersion": self.protocol_version,
        }
        if self.description:
            data["description"] = self.description
        if self.capabilities:
            data["capabilities"] = {
                "streaming": self.capabilities.streaming,
                "pushNotifications": self.capabilities.push_notifications,
            }
        if self.skills:
            data["skills"] = [
                {
                    "name": s.name,
                    **({"description": s.description} if s.description else {}),
                }
                for s in self.skills
            ]
        return data


class RegistryEntry(BaseModel):
    """Agent registry entry from database."""

    id: str
    agent_id: str
    agent_card: AgentCard
    owner: str
    tags: list[str] = Field(default_factory=list)
    verified: bool = False
    registered_at: datetime
    last_updated: datetime
    last_heartbeat: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticSearchResult(BaseModel):
    """Single search result with similarity score."""

    agent_id: str
    agent_card: AgentCard
    tags: list[str] = Field(default_factory=list)
    verified: bool = False
    similarity_score: float = Field(..., ge=0, le=1)
    matched_on: str = Field(..., description="What field matched (name, description, skills)")


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search."""

    query: str
    results: list[SemanticSearchResult]
    total: int
    processing_time_ms: float


class ListAgentsResponse(BaseModel):
    """Response model for listing agents."""

    agents: list[RegistryEntry]
    total: int
    limit: int
    offset: int


class HeartbeatResponse(BaseModel):
    """Response from heartbeat endpoint."""

    agent_id: str
    last_heartbeat: datetime
