"""
A2A Registry Semantic Search Configuration

Manages environment variables and settings for the semantic search service.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://a2a_user:a2a_password@localhost:5432/a2a_registry"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Server
    host: str = "0.0.0.0"
    port: int = 3001
    debug: bool = True

    # Main registry
    registry_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
