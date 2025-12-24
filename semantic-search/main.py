"""
A2A Registry Semantic Search - Main Application

FastAPI application providing semantic search capabilities for agent discovery.
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from config import get_settings, Settings
from models import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResult,
    IndexAgentRequest,
    IndexAllResponse,
    HealthResponse,
    AgentCard
)
from embeddings import get_embedding_service, EmbeddingService
from database import get_database_service, close_database_service, DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Redis client
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        try:
            _redis_client = redis.from_url(settings.redis_url)
            await _redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            _redis_client = None
    return _redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("Starting A2A Semantic Search Service...")

    # Pre-load embedding model
    embedding_service = get_embedding_service()
    _ = embedding_service.model  # Force load

    # Connect database
    try:
        await get_database_service()
        logger.info("Database connected")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")

    # Connect Redis
    await get_redis()

    logger.info("A2A Semantic Search Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down A2A Semantic Search Service...")
    await close_database_service()

    if _redis_client:
        await _redis_client.close()

    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="A2A Registry Semantic Search",
    description="Semantic search capabilities for A2A Agent Registry using NLP embeddings",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== API Routes ==============

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check service health and dependencies."""
    settings = get_settings()
    embedding_service = get_embedding_service()

    # Check database
    db_connected = False
    try:
        db = await get_database_service()
        db_connected = await db.is_connected()
    except Exception:
        pass

    # Check Redis
    redis_connected = False
    try:
        redis_client = await get_redis()
        if redis_client:
            await redis_client.ping()
            redis_connected = True
    except Exception:
        pass

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        embedding_model=settings.embedding_model,
        database_connected=db_connected,
        redis_connected=redis_connected
    )


@app.post("/api/v1/semantic/search", response_model=SemanticSearchResponse, tags=["Search"])
async def semantic_search(request: SemanticSearchRequest):
    """
    Search for agents using natural language queries.

    The search uses sentence-transformer embeddings to find semantically
    similar agents based on their names, descriptions, skills, and tags.
    """
    start_time = time.time()

    try:
        # Get services
        embedding_service = get_embedding_service()
        db = await get_database_service()

        # Generate query embedding
        query_embedding = embedding_service.embed_text(request.query)

        # Extract filters
        tags_filter = None
        verified_only = False
        if request.filters:
            tags_filter = request.filters.get("tags")
            verified_only = request.filters.get("verified", False)

        # Search database
        raw_results = await db.search_similar(
            query_embedding=query_embedding,
            top_k=request.top_k,
            min_score=request.min_score,
            tags_filter=tags_filter,
            verified_only=verified_only
        )

        # Format results
        results = []
        for agent_data, similarity in raw_results:
            # Parse agent card
            agent_card_data = agent_data["agent_card"]

            # Determine what matched
            query_lower = request.query.lower()
            matched_on = "description"
            if query_lower in agent_card_data.get("name", "").lower():
                matched_on = "name"
            elif any(query_lower in s.get("name", "").lower() for s in agent_card_data.get("skills", [])):
                matched_on = "skills"
            elif any(query_lower in tag.lower() for tag in agent_data.get("tags", [])):
                matched_on = "tags"

            results.append(SemanticSearchResult(
                agent_id=agent_data["agent_id"],
                agent_card=AgentCard(**agent_card_data),
                tags=agent_data["tags"],
                verified=agent_data["verified"],
                similarity_score=round(similarity, 4),
                matched_on=matched_on
            ))

        processing_time = (time.time() - start_time) * 1000

        return SemanticSearchResponse(
            query=request.query,
            results=results,
            total=len(results),
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/api/v1/semantic/index", tags=["Indexing"])
async def index_agent(request: IndexAgentRequest):
    """
    Index a single agent for semantic search.

    This creates or updates the vector embedding for the specified agent.
    """
    try:
        embedding_service = get_embedding_service()
        db = await get_database_service()

        # Generate embedding
        agent_card_dict = request.agent_card.model_dump()
        embedding = embedding_service.embed_agent(agent_card_dict, request.tags)

        # Create text content for reference
        text_parts = [f"Agent: {request.agent_card.name}"]
        if request.agent_card.description:
            text_parts.append(request.agent_card.description)
        for skill in request.agent_card.skills:
            text_parts.append(f"Skill: {skill.name}")
        if request.tags:
            text_parts.append(f"Tags: {', '.join(request.tags)}")
        text_content = " | ".join(text_parts)

        # Store embedding
        await db.store_embedding(request.agent_id, embedding, text_content)

        return {
            "status": "indexed",
            "agent_id": request.agent_id,
            "embedding_dimension": len(embedding)
        }

    except Exception as e:
        logger.error(f"Indexing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.post("/api/v1/semantic/index-all", response_model=IndexAllResponse, tags=["Indexing"])
async def index_all_agents():
    """
    Index all agents in the registry for semantic search.

    This should be called initially to populate the vector index,
    and periodically to sync with new agents.
    """
    start_time = time.time()

    try:
        embedding_service = get_embedding_service()
        db = await get_database_service()

        # Get all agents
        agents = await db.get_all_agents()

        indexed_count = 0
        failed_count = 0

        for agent in agents:
            try:
                # Generate embedding
                embedding = embedding_service.embed_agent(
                    agent["agent_card"],
                    agent["tags"]
                )

                # Create text content
                text_parts = [f"Agent: {agent['agent_card'].get('name', '')}"]
                if desc := agent["agent_card"].get("description"):
                    text_parts.append(desc)
                for skill in agent["agent_card"].get("skills", []):
                    text_parts.append(f"Skill: {skill.get('name', '')}")
                if agent["tags"]:
                    text_parts.append(f"Tags: {', '.join(agent['tags'])}")
                text_content = " | ".join(text_parts)

                # Store
                await db.store_embedding(agent["agent_id"], embedding, text_content)
                indexed_count += 1

            except Exception as e:
                logger.error(f"Failed to index agent {agent['agent_id']}: {e}")
                failed_count += 1

        processing_time = (time.time() - start_time) * 1000

        return IndexAllResponse(
            indexed_count=indexed_count,
            failed_count=failed_count,
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bulk indexing failed: {str(e)}")


@app.get("/api/v1/semantic/stats", tags=["System"])
async def get_stats():
    """Get semantic search statistics."""
    try:
        embedding_service = get_embedding_service()
        db = await get_database_service()

        # Get agent count
        agents = await db.get_all_agents()

        return {
            "model": embedding_service.model_name,
            "embedding_dimension": embedding_service.dimension,
            "total_agents": len(agents),
            "status": "ready"
        }

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Run ==============

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
