# A2A Agent Registry

**Production-ready reference implementation of an Agent Registry for the Agent2Agent (A2A) Protocol**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)](https://www.typescriptlang.org/)

## Overview

The A2A Agent Registry enables agent discovery and registration in the Agent2Agent ecosystem. It provides a centralized service for agents to:

- **Register** their capabilities and endpoints
- **Discover** other agents by skills, tags, or capabilities
- **Monitor** agent health and availability
- **Manage** agent lifecycle

This implementation addresses the community's most-requested feature ([Discussion #741](https://github.com/a2aproject/A2A/discussions/741)) with a production-ready, Docker-deployable solution.

## Features

✅ **RESTful API** - Complete CRUD operations for agent registration  
✅ **Advanced Search** - Filter by tags, skills, verification status  
✅ **High Performance** - PostgreSQL + Redis caching, sub-100ms queries  
✅ **Production-Ready** - Docker deployment, comprehensive logging, error handling  
✅ **Type-Safe** - Full TypeScript implementation  
✅ **Client SDK** - TypeScript/JavaScript library for easy integration  
✅ **Well-Documented** - Complete API docs, examples, guides  

## Quick Start

### Using Docker (Recommended)

```bash
git clone https://github.com/jenish2917/a2a-registry
cd a2a-registry/registry-server
docker-compose up -d
```

The registry will be available at `http://localhost:3000`.

### Using the Client Library

```bash
npm install @a2a/registry-client
```

```typescript
import { RegistryClient } from '@a2a/registry-client';

const client = new RegistryClient({ baseUrl: 'http://localhost:3000' });

// Register an agent
const agent = await client.registerAgent({
  agentCard: {
    name: 'translation-agent',
    endpoint: 'https://my-agent.example.com',
    protocolVersion: '0.3',
    skills: [{ name: 'translate' }],
  },
  tags: ['translation', 'nlp'],
});

// Discover agents
const translators = await client.searchBySkill('translate');
```

## Architecture

```
┌─────────────────┐
│  Client Apps    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐      ┌──────────┐
│ Registry Server │◄────►│  Redis   │
│   (Express.js)  │      │  Cache   │
└────────┬────────┘      └──────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (JSONB)       │
└─────────────────┘
```

### Technology Stack

- **Backend:** TypeScript + Express.js
- **Database:** PostgreSQL with JSONB indexing
- **Cache:** Redis for high-performance lookups
- **Deployment:** Docker + Docker Compose
- **Client:** TypeScript/JavaScript SDK

## Project Structure

```
a2a-registry/
├── registry-server/          # Core registry service
│   ├── src/
│   │   ├── controllers/      # Business logic
│   │   ├── routes/           # API routes
│   │   ├── middleware/       # Validation, errors
│   │   ├── config/           # DB, Redis config
│   │   └── utils/            # Helpers
│   ├── schema.sql            # Database schema
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── registry-client/          # TypeScript/JS client
│   ├── src/
│   │   ├── index.ts          # RegistryClient
│   │   └── types.ts          # Type definitions
│   └── README.md
├── examples/                 # Usage examples
│   ├── sample-agent.json
│   └── demo.sh
└── docs/                     # Documentation
    ├── api-reference.md
    ├── deployment.md
    └── architecture.md
```

## API Endpoints

### Core Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents` | Register a new agent |
| GET | `/api/v1/agents/:id` | Get agent by ID |
| PUT | `/api/v1/agents/:id` | Update agent |
| DELETE | `/api/v1/agents/:id` | Delete agent |
| GET | `/api/v1/agents` | List/search agents |
| POST | `/api/v1/agents/:id/heartbeat` | Send heartbeat |
| GET | `/health` | Health check |

### Search & Discovery

```bash
# Search by skill
GET /api/v1/agents?skill=translate

# Filter by tags
GET /api/v1/agents?tags=nlp,translation

# Filter by verification
GET /api/v1/agents?verified=true

# Pagination
GET /api/v1/agents?limit=20&offset=40
```

## Examples

### Register an Agent

```bash
curl -X POST http://localhost:3000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agentCard": {
      "name": "my-agent",
      "description": "My awesome agent",
      "endpoint": "https://my-agent.example.com",
      "protocolVersion": "0.3",
      "capabilities": {
        "streaming": true,
        "pushNotifications": false
      },
      "skills": [
        { "name": "task1", "description": "Does task 1" }
      ]
    },
    "tags": ["category1", "type-a"],
    "metadata": {
      "version": "1.0.0",
      "region": "us-east-1"
    }
  }'
```

### Discover Agents

```bash
# Find all agents with a specific skill
curl http://localhost:3000/api/v1/agents?skill=translate

# Find agents by tag
curl http://localhost:3000/api/v1/agents?tags=nlp

# List all agents
curl http://localhost:3000/api/v1/agents
```

## Documentation

- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[Architecture](docs/architecture.md)** - System design and decisions
- **[Client Library](registry-client/README.md)** - TypeScript/JS SDK docs

## Development

### Prerequisites

- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16+ (if running locally)
- Redis 7+ (if running locally)

### Setup

```bash
# Clone repository
git clone https://github.com/jenish2917/a2a-registry
cd a2a-registry

# Server setup
cd registry-server
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev

# Client setup
cd ../registry-client
npm install
npm run build
```

### Testing

```bash
# Server tests
cd registry-server
npm test
npm run test:integration

# Client tests
cd registry-client
npm test
```

## Deployment

### Docker (Production)

```bash
cd registry-server
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

See [docs/deployment.md](docs/deployment.md) for Kubernetes manifests.

## Contributing

We welcome contributions! Please see:

- [A2A Contributing Guide](https://github.com/a2aproject/A2A/blob/main/CONTRIBUTING.md)
- [Open Issues](https://github.com/jenish2917/a2a-registry/issues)
- [Discussion #741](https://github.com/a2aproject/A2A/discussions/741)

## Roadmap

- [x] **Phase 1:** Core Registry Server
- [x] **Phase 2:** TypeScript/JavaScript Client
- [ ] **Phase 3:** Python Client
- [ ] **Phase 4:** Enhanced Security (OAuth2, API Keys)
- [ ] **Phase 5:** Federation Support
- [ ] **Phase 6:** Hosted Registry Service

## License

Apache 2.0 - See [LICENSE](LICENSE) for details

## Acknowledgments

- Built for the [A2A Protocol](https://a2a-protocol.org)
- Inspired by community discussions #741, #234, #924
- Part of the Linux Foundation's A2A project

## Support

- **Issues:** [GitHub Issues](https://github.com/jenish2917/a2a-registry/issues)
- **Discussions:** [A2A Discussions](https://github.com/a2aproject/A2A/discussions)
- **Documentation:** [docs/](docs/)

---

**Status:** ✅ Production Ready | **Version:** 0.1.0 | **Maintained by:** [jenish2917](https://github.com/jenish2917)
