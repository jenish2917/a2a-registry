# A2A Registry Python Client

Python SDK for interacting with the A2A Agent Registry.

## Installation

```bash
pip install a2a-registry-client
```

## Quick Start

```python
from a2a_registry import RegistryClient

# Initialize client
client = RegistryClient(base_url="http://localhost:3000")

# Register an agent
agent = client.register_agent(
    agent_card={
        "name": "translation-agent",
        "endpoint": "https://my-agent.example.com",
        "protocolVersion": "0.3",
        "skills": [{"name": "translate", "description": "Translate text"}]
    },
    tags=["nlp", "translation"]
)

# Semantic search for agents
results = client.semantic_search("translate text between languages", top_k=5)
for result in results:
    print(f"{result.agent_id}: {result.similarity_score}")

# Search by skill
translators = client.search_by_skill("translate")

# Search by tags
nlp_agents = client.search_by_tags(["nlp", "ml"])
```

## Features

- ✅ Full CRUD operations for agent registration
- ✅ Semantic search using natural language
- ✅ Tag-based and skill-based search
- ✅ Type hints with Pydantic models
- ✅ Async support with `httpx`
- ✅ Comprehensive error handling

## API Reference

### RegistryClient

```python
client = RegistryClient(
    base_url="http://localhost:3000",
    timeout=30.0,
    api_key=None  # Optional API key
)
```

### Methods

| Method | Description |
|--------|-------------|
| `register_agent(agent_card, tags, metadata)` | Register a new agent |
| `get_agent(agent_id)` | Get agent by ID |
| `update_agent(agent_id, agent_card, tags)` | Update an agent |
| `delete_agent(agent_id)` | Delete an agent |
| `list_agents(limit, offset, tags, verified)` | List agents with filters |
| `search_by_skill(skill)` | Search agents by skill name |
| `search_by_tags(tags)` | Search agents by tags |
| `semantic_search(query, top_k, min_score)` | Natural language search |
| `heartbeat(agent_id)` | Send heartbeat for agent |

## License

Apache 2.0
