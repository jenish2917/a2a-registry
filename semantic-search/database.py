"""
A2A Registry Semantic Search - Database Service

Handles PostgreSQL operations including pgvector for semantic search.
"""

import logging
from typing import List, Optional, Tuple
from contextlib import asynccontextmanager

import asyncpg
import numpy as np
from pgvector.asyncpg import register_vector

from config import get_settings
from models import RegistryEntry, SemanticSearchResult, AgentCard

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for PostgreSQL database operations with pgvector support."""

    def __init__(self):
        self.settings = get_settings()
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection pool."""
        logger.info("Connecting to database...")

        self._pool = await asyncpg.create_pool(
            self.settings.database_url,
            min_size=5,
            max_size=20,
            init=self._init_connection
        )

        # Ensure vector extension and table exist
        await self._setup_vector_table()

        logger.info("Database connected successfully")

    async def _init_connection(self, conn: asyncpg.Connection):
        """Initialize each connection with vector support."""
        await register_vector(conn)

    async def _setup_vector_table(self):
        """Create pgvector extension and embeddings table if not exist."""
        async with self._pool.acquire() as conn:
            # Create extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

            # Create embeddings table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_embeddings (
                    id SERIAL PRIMARY KEY,
                    agent_id VARCHAR(255) UNIQUE NOT NULL,
                    embedding vector(384),
                    text_content TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES registry_entries(agent_id) ON DELETE CASCADE
                )
            """)

            # Create index for similarity search
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_embeddings_vector
                ON agent_embeddings
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)

            logger.info("Vector table and indexes created/verified")

    async def disconnect(self):
        """Close database connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Database disconnected")

    async def store_embedding(
        self,
        agent_id: str,
        embedding: np.ndarray,
        text_content: str
    ):
        """
        Store or update an agent embedding.

        Args:
            agent_id: Unique agent identifier.
            embedding: Vector embedding.
            text_content: Original text used for embedding.
        """
        async with self._pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_embeddings (agent_id, embedding, text_content, updated_at)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                ON CONFLICT (agent_id)
                DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    text_content = EXCLUDED.text_content,
                    updated_at = CURRENT_TIMESTAMP
            """, agent_id, embedding.tolist(), text_content)

            logger.debug(f"Stored embedding for agent: {agent_id}")

    async def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        min_score: float = 0.5,
        tags_filter: Optional[List[str]] = None,
        verified_only: bool = False
    ) -> List[Tuple[dict, float]]:
        """
        Search for similar agents using vector similarity.

        Args:
            query_embedding: Query vector embedding.
            top_k: Number of results to return.
            min_score: Minimum cosine similarity score.
            tags_filter: Filter by tags (optional).
            verified_only: Only return verified agents.

        Returns:
            List of (agent_data, similarity_score) tuples.
        """
        async with self._pool.acquire() as conn:
            # Build query with filters
            base_query = """
                SELECT
                    r.agent_id,
                    r.agent_card,
                    r.tags,
                    r.verified,
                    e.text_content,
                    1 - (e.embedding <=> $1::vector) as similarity
                FROM agent_embeddings e
                JOIN registry_entries r ON e.agent_id = r.agent_id
                WHERE 1 - (e.embedding <=> $1::vector) >= $2
            """

            params = [query_embedding.tolist(), min_score]
            param_idx = 3

            if verified_only:
                base_query += f" AND r.verified = true"

            if tags_filter:
                base_query += f" AND r.tags && ${param_idx}::text[]"
                params.append(tags_filter)
                param_idx += 1

            base_query += f" ORDER BY similarity DESC LIMIT ${param_idx}"
            params.append(top_k)

            rows = await conn.fetch(base_query, *params)

            results = []
            for row in rows:
                import json
                agent_data = {
                    "agent_id": row["agent_id"],
                    "agent_card": json.loads(row["agent_card"]) if isinstance(row["agent_card"], str) else row["agent_card"],
                    "tags": row["tags"],
                    "verified": row["verified"],
                    "matched_text": row["text_content"]
                }
                results.append((agent_data, float(row["similarity"])))

            return results

    async def get_all_agents(self) -> List[dict]:
        """Get all agents for indexing."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT agent_id, agent_card, tags
                FROM registry_entries
                ORDER BY registered_at
            """)

            import json
            return [
                {
                    "agent_id": row["agent_id"],
                    "agent_card": json.loads(row["agent_card"]) if isinstance(row["agent_card"], str) else row["agent_card"],
                    "tags": row["tags"]
                }
                for row in rows
            ]

    async def is_connected(self) -> bool:
        """Check if database is connected."""
        if not self._pool:
            return False
        try:
            async with self._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                return True
        except Exception:
            return False


# Singleton instance
_db_service: Optional[DatabaseService] = None


async def get_database_service() -> DatabaseService:
    """Get the database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
        await _db_service.connect()
    return _db_service


async def close_database_service():
    """Close the database service."""
    global _db_service
    if _db_service:
        await _db_service.disconnect()
        _db_service = None
