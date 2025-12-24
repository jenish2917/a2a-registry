# A2A Registry Semantic Search Service

Python-based microservice providing semantic search capabilities for the A2A Agent Registry.

## Features

- 🔍 **Semantic Search** - Find agents by natural language queries
- 🧠 **Vector Embeddings** - Uses sentence-transformers for text embeddings
- ⚡ **FastAPI** - High-performance async API
- 🐘 **pgvector** - PostgreSQL vector similarity search

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn main:app --port 3001 --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/semantic/search` | Search agents by natural language |
| POST | `/api/v1/semantic/index` | Index agent embeddings |
| GET | `/health` | Health check |

## Integration

The semantic search service connects to the same PostgreSQL database as the main registry server while adding vector search capabilities.

## Architecture

```
Registry Server (port 3000)  ──► PostgreSQL ◄── Semantic Search (port 3001)
      (TypeScript/Express)         (+ pgvector)      (Python/FastAPI)
```
