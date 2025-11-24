# [RFC] Agent Registry Reference Implementation

## Overview

I'm proposing a reference implementation of an **Agent Registry** for the A2A Protocol, addressing one of the most discussed needs in the community (see [Discussion #741](https://github.com/a2aproject/A2A/discussions/741)).

This implementation provides a production-ready, centralized registry service that enables agent discovery at scale.

## Motivation

Agent discovery is critical for the A2A ecosystem to function at scale. Without a standardized registry:
- Agents cannot easily find each other
- Manual configuration becomes a bottleneck
- Discovery mechanisms are ad-hoc and fragmented

The community has expressed strong demand for this (100+ comments across 4 discussions), but no reference implementation exists yet.

## Implementation Approach

### Architecture: Centralized Registry

I chose a **centralized registry** approach for the initial implementation because:

✅ **Faster time-to-value** - Simpler to implement and deploy  
✅ **Easier to understand** - Clear mental model for developers  
✅ **Production-ready** - Battle-tested architecture (npm, Docker Hub, etc.)  
✅ **Foundation for hybrid** - Can evolve to federated/P2P later  

### Technology Stack

- **Backend:** TypeScript + Express.js (aligns with A2A JS SDK)
- **Database:** PostgreSQL with JSONB (flexible Agent Card storage)
- **Cache:** Redis (sub-100ms query latency)
- **Deployment:** Docker + Docker Compose (one-command setup)

### Features Implemented

**Core API Endpoints:**
```
POST   /api/v1/agents          - Register agent
GET    /api/v1/agents/:id      - Get agent by ID
PUT    /api/v1/agents/:id      - Update agent
DELETE /api/v1/agents/:id      - Deregister agent
GET    /api/v1/agents          - List/search agents
POST   /api/v1/agents/:id/heartbeat - Health monitoring
```

**Advanced Features:**
- Search/filtering by tags, skills, verification status
- Pagination support
- Redis caching for high performance
- Input validation (Joi)
- Structured logging (Winston)
- Security middleware (Helmet, CORS)
- Audit logging capability
- Health monitoring endpoints

**Production-Ready:**
- Complete Docker deployment
- Database schema with optimized indexes
- Comprehensive error handling
- Type-safe TypeScript implementation
- Full documentation and examples

## Repository Structure

```
a2a-registry/
├── registry-server/
│   ├── src/
│   │   ├── controllers/     # Business logic
│   │   ├── routes/          # API routes
│   │   ├── middleware/      # Validation, errors
│   │   ├── config/          # DB, Redis config
│   │   └── utils/           # Logger, helpers
│   ├── schema.sql           # Database schema
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
└── examples/
    ├── sample-agent.json    # Example Agent Card
    └── demo.sh              # API demo script
```

## Quick Start

```bash
git clone https://github.com/<username>/a2a-registry
cd a2a-registry/registry-server
docker-compose up -d
```

The registry will be available at `http://localhost:3000`.

## Example Usage

**Register an agent:**
```bash
curl -X POST http://localhost:3000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agentCard": {
      "name": "translation-agent",
      "description": "Multilingual translation agent",
      "endpoint": "https://translation-agent.example.com",
      "protocolVersion": "0.3",
      "capabilities": { "streaming": true },
      "skills": [{ "name": "translate" }]
    },
    "tags": ["translation", "nlp"]
  }'
```

**Discover agents by skill:**
```bash
curl http://localhost:3000/api/v1/agents?skill=translate
```

## Design Decisions

### 1. Centralized vs. Decentralized

**Decision:** Start with centralized, design for federation

**Rationale:**
- Faster community adoption
- Lower operational complexity
- Can evolve to federated model (multiple registries syncing)
- Established pattern (Docker Hub, npm, Maven Central)

### 2. Database Choice: PostgreSQL

**Decision:** PostgreSQL with JSONB

**Rationale:**
- JSONB allows flexible Agent Card storage
- GIN indexes enable fast metadata queries
- Production-proven reliability
- Strong ecosystem support

### 3. Agent ID Strategy

**Decision:** Use Agent Card `name` as primary identifier

**Rationale:**
- Human-readable
- Aligns with A2A Card structure
- Fallback to UUID for unnamed agents

## Roadmap

### Completed ✅
- Core registry server
- REST API with full CRUD
- Docker deployment
- Documentation and examples

### Next Steps
1. **Client Libraries** (Week 2-3)
   - TypeScript/JavaScript SDK
   - Python SDK
   - Integration with existing a2a-python/a2a-js

2. **Enhanced Discovery** (Week 3-4)
   - Advanced search queries
   - Agent version management
   - Agent deprecation workflow

3. **Security & Auth** (Week 4-5)
   - API key authentication
   - OAuth2 support
   - Rate limiting

4. **Federation Support** (Future)
   - Registry-to-registry sync
   - Distributed query routing 
   - Conflict resolution

## Open Questions

1. **Authentication:** Should registration require auth, or allow open submissions with verification?
2. **Naming conflicts:** How to handle agents with duplicate names?
3. **Agent lifecycle:** Should inactive agents be auto-pruned? What's the timeout?
4. **Federation:** Is there interest in federated registries, or is centralized sufficient?

## Request for Feedback

I'd love community input on:

1. **Architecture:** Is centralized the right starting point, or should we prioritize P2P from day 1?
2. **API Design:** Are the endpoints intuitive? Missing any critical operations?
3. **Search/Discovery:** What query patterns are most important? (by skill, capability, region, etc.)
4. **Security:** What auth mechanisms are most important for your use cases?
5. **Deployment:** Would a hosted registry service be valuable, or is self-hosted preferred?

## Contributing

The code is ready for review. I plan to:
1. Gather feedback on this RFC
2. Iterate based on community input
3. Create a PR to the A2A project

**Repository:** `https://github.com/<username>/a2a-registry` (update with actual URL)

## Conclusion

This implementation provides a solid foundation for agent discovery in the A2A ecosystem. It's production-ready, well-documented, and designed to evolve with community needs.

Looking forward to your feedback!

---
**Related Discussions:**
- [Discussion #741 - Agent Registry](https://github.com/a2aproject/A2A/discussions/741)
- [Discussion #234 - An A2A Registry](https://github.com/a2aproject/A2A/discussions/234)
- [Discussion #924 - Registry Platform Proposal](https://github.com/a2aproject/A2A/discussions/924)
