"""
A2A Registry Semantic Search - Embedding Service

Handles text embedding generation using sentence-transformers.
"""

import logging
from typing import List, Optional
from functools import lru_cache

from sentence_transformers import SentenceTransformer
import numpy as np

from config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformer model to use.
                       Defaults to settings.embedding_model.
        """
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self._model: Optional[SentenceTransformer] = None
        logger.info(f"Initializing EmbeddingService with model: {self.model_name}")

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model on first access."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self._model.get_sentence_embedding_dimension()}")
        return self._model

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as numpy array.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            2D numpy array of shape (len(texts), embedding_dim).
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings

    def embed_agent(self, agent_card: dict, tags: List[str] = None) -> np.ndarray:
        """
        Generate a combined embedding for an agent.

        Creates embeddings from:
        - Agent name
        - Agent description
        - Skill names and descriptions
        - Tags

        These are combined into a single representative embedding.

        Args:
            agent_card: Agent card dictionary.
            tags: List of tags associated with the agent.

        Returns:
            Combined embedding vector.
        """
        # Collect all text components
        text_parts = []

        # Add name and description
        if name := agent_card.get("name"):
            text_parts.append(f"Agent: {name}")

        if description := agent_card.get("description"):
            text_parts.append(f"Description: {description}")

        # Add skills
        skills = agent_card.get("skills", [])
        for skill in skills:
            skill_text = f"Skill: {skill.get('name', '')}"
            if skill_desc := skill.get("description"):
                skill_text += f" - {skill_desc}"
            text_parts.append(skill_text)

        # Add tags
        if tags:
            text_parts.append(f"Tags: {', '.join(tags)}")

        # Combine and embed
        combined_text = " | ".join(text_parts) if text_parts else agent_card.get("name", "unknown")

        logger.debug(f"Embedding agent text: {combined_text[:100]}...")

        return self.embed_text(combined_text)

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector.
            embedding2: Second embedding vector.

        Returns:
            Cosine similarity score between 0 and 1.
        """
        # Normalize
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)

        # Ensure in valid range
        return float(max(0.0, min(1.0, similarity)))


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()
