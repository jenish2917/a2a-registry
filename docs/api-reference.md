# API Reference

Complete API documentation for the A2A Agent Registry.

## Base URL

```
http://localhost:3000/api/v1
```

## Authentication

Currently, authentication is optional. Future versions will support:
- API Keys
- OAuth 2.0
- JWT tokens

## Endpoints

### 1. Register Agent

Register a new agent in the registry.

**Endpoint:** `POST /agents`

**Request Body:**
```json
{
  "agentCard": {
    "name": "string (required)",
    "description": "string (optional)",
    "endpoint": "string (required, URL)",
    "protocolVersion": "string (required, e.g., '0.3')",
    "capabilities": {
      "streaming": "boolean (optional)",
      "pushNotifications": "boolean (optional)"
    },
    "skills": [
      {
        "name": "string (required)",
        "description": "string (optional)",
        "parameters": "object (optional)"
      }
    ],
    "securitySchemes": "object (optional)",
    "security": "array (optional)"
  },
  "tags": ["string"],
  "metadata": "object (optional)"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "agentId": "string",
  "agentCard": { ... },
  "registeredAt": "ISO8601 timestamp"
}
```

**Errors:**
- `400 Bad Request` - Invalid agent card
- `409 Conflict` - Agent already exists

---

### 2. Get Agent

Retrieve an agent by ID.

**Endpoint:** `GET /agents/:agentId`

**Parameters:**
- `agentId` (path) - Agent identifier

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "agentId": "string",
  "agentCard": { ... },
  "owner": "string",
  "tags": ["string"],
  "verified": "boolean",
  "registeredAt": "ISO8601 timestamp",
  "lastUpdated": "ISO8601 timestamp",
  "lastHeartbeat": "ISO8601 timestamp",
  "metadata": { ... }
}
```

**Errors:**
- `404 Not Found` - Agent does not exist

---

### 3. Update Agent

Update an existing agent.

**Endpoint:** `PUT /agents/:agentId`

**Parameters:**
- `agentId` (path) - Agent identifier

**Request Body:** Same as Register Agent

**Response:** `200 OK` - Updated agent object

**Errors:**
- `400 Bad Request` - Invalid data
- `404 Not Found` - Agent does not exist

---

### 4. Delete Agent

Remove an agent from the registry.

**Endpoint:** `DELETE /agents/:agentId`

**Parameters:**
- `agentId` (path) - Agent identifier

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - Agent does not exist

---

### 5. List/Search Agents

List and filter agents.

**Endpoint:** `GET /agents`

**Query Parameters:**
- `tags` (string|array) - Filter by tags
- `skill` (string) - Filter by skill name
- `verified` (boolean) - Filter by verification status
- `limit` (integer) - Results per page (default: 50, max: 100)
- `offset` (integer) - Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "agents": [ ... ],
  "total": "integer",
  "limit": "integer",
  "offset": "integer"
}
```

**Examples:**
```bash
# All agents
GET /api/v1/agents

# Filter by skill
GET /api/v1/agents?skill=translate

# Filter by tags
GET /api/v1/agents?tags=nlp&tags=translation

# Pagination
GET /api/v1/agents?limit=20&offset=40

# Verified only
GET /api/v1/agents?verified=true
```

---

### 6. Send Heartbeat

Update agent's last heartbeat timestamp.

**Endpoint:** `POST /agents/:agentId/heartbeat`

**Parameters:**
- `agentId` (path) - Agent identifier

**Response:** `200 OK`
```json
{
  "agentId": "string",
  "lastHeartbeat": "ISO8601 timestamp"
}
```

**Errors:**
- `404 Not Found` - Agent does not exist

---

### 7. Health Check

Check registry service health.

**Endpoint:** `GET /health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "ISO8601 timestamp",
  "version": "string",
  "uptime": "integer (seconds)"
}
```

## Data Models

### Agent Card

Based on A2A Protocol specification v0.3:

```typescript
interface AgentCard {
  name: string;                    // Unique identifier
  description?: string;             // Human-readable description
  endpoint: string;                 // Agent's HTTP/S endpoint
  protocolVersion: string;          // A2A protocol version
  capabilities?: {
    streaming?: boolean;
    pushNotifications?: boolean;
  };
  skills?: Skill[];
  securitySchemes?: Record<string, any>;
  security?: any[];
}

interface Skill {
  name: string;
  description?: string;
  parameters?: Record<string, any>;
}
```

### Registry Entry

Complete agent registration data:

```typescript
interface RegistryEntry {
  id: string;                       // Internal UUID
  agentId: string;                  // Agent's name from card
  agentCard: AgentCard;             // Full agent card
  owner: string;                    // Owner identifier
  tags: string[];                   // Categorization tags
  verified: boolean;                // Verification status
  registeredAt: Date;               // Registration timestamp
  lastUpdated: Date;                // Last modification
  lastHeartbeat: Date | null;       // Last heartbeat
  metadata: Record<string, any>;    // Additional metadata
}
```

## Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | VALIDATION_ERROR | Request validation failed |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 500 | INTERNAL_ERROR | Server error |

## Rate Limiting

Current limits (subject to change):
- 100 requests per minute per IP
- 1000 agents per owner

Headers returned:
- `X-RateLimit-Limit` - Request limit
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset timestamp

## Versioning

API versioning is done via URL path:
- Current: `/api/v1/`
- Future: `/api/v2/`

Deprecated versions will be supported for 6 months after new version release.

## Examples

See [examples/](../examples/) directory for complete working examples.
