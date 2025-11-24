# A2A Agent Registry

Reference implementation of an Agent Registry for the Agent2Agent (A2A) Protocol.

## Features

- ✅ RESTful API for agent registration and discovery
- ✅ PostgreSQL backend with JSONB support
- ✅ Redis caching for fast lookups
- ✅ Advanced search and filtering
- ✅ Health monitoring and heartbeat tracking
- ✅ Docker deployment ready
- ✅ TypeScript for type safety

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for development without Docker)

### Run with Docker

```bash
cd registry-server
docker-compose up -d
```

The registry will be available at `http://localhost:3000`.

### Run Locally

```bash
cd registry-server
npm install
cp .env.example .env
# Update .env with your database credentials
npm run dev
```

## API Endpoints

### Health Check

```http
GET /health
```

### Register Agent

```http
POST /api/v1/agents
Content-Type: application/json

{
  "agentCard": {
    "name": "my-agent",
    "description": "Description of my agent",
    "endpoint": "https://my-agent.example.com",
    "protocolVersion": "0.3",
    "capabilities": {
      "streaming": true,
      "pushNotifications": false
    },
    "skills": [
      {
        "name": "translation",
        "description": "Translate text between languages"
      }
    ]
  },
  "tags": ["translation", "nlp"],
  "metadata": {}
}
```

### Get Agent

```http
GET /api/v1/agents/:agentId
```

### Update Agent

```http
PUT /api/v1/agents/:agentId
Content-Type: application/json

{
  "agentCard": { ... },
  "tags": [],
  "metadata": {}
}
```

### Delete Agent

```http
DELETE /api/v1/agents/:agentId
```

### List/Search Agents

```http
GET /api/v1/agents?tags=translation&skill=translation&verified=true&limit=20&offset=0
```

### Heartbeat

```http
POST /api/v1/agents/:agentId/heartbeat
```

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build
npm run build

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Lint
npm run lint

# Format
npm run format
```

## Database Schema

The registry uses PostgreSQL with the following main tables:

- `registry_entries`: Agent registrations and metadata
- `users`: User authentication (future)
- `audit_logs`: Audit trail of registry operations

See `schema.sql` for the complete schema.

## Configuration

Environment variables (see `.env.example`):

- `NODE_ENV`: Environment (development/production)
- `PORT`: Server port (default: 3000)
- `DB_*`: PostgreSQL connection settings
- `REDIS_*`: Redis connection settings
- `JWT_SECRET`: Secret for JWT tokens

## Architecture

```
├── src/
│   ├── index.ts              # Application entry point
│   ├── config/               # Configuration (database, redis)
│   ├── controllers/          # Request handlers
│   ├── middleware/           # Express middleware
│   ├── routes/               # API routes
│   └── utils/                # Utility functions
├── schema.sql                # Database schema
├── Dockerfile                # Docker image
└── docker-compose.yml        # Docker Compose setup
```

## Contributing

This is a reference implementation for the A2A project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Apache 2.0
