# Quick Setup & Deployment Guide

## 🚀 5-Minute Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/jenish2917/a2a-registry
cd a2a-registry/registry-server

# Start services
docker-compose up -d

# Verify
curl http://localhost:3000/health
```

**Registry is now running on `http://localhost:3000`!**

---

## 📦 Installation Options

### Option 1: Docker (Production)

**Requirements:**
- Docker 20+
- Docker Compose 2+

**Steps:**
```bash
cd registry-server
docker-compose up -d
```

**What it starts:**
- Registry server on port 3000
- PostgreSQL on port 5432
- Redis on port 6379

### Option 2: Local Development

**Requirements:**
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

**Steps:**
```bash
# 1. Install dependencies
cd registry-server
npm install

# 2. Set up PostgreSQL
createdb a2a_registry
psql a2a_registry < schema.sql

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Start services
npm run dev
```

---

## 🔧 Client Library Usage

### Installation

```bash
npm install @a2a/registry-client
```

### Basic Usage

```typescript
import { RegistryClient } from '@a2a/registry-client';

const client = new RegistryClient({
  baseUrl: 'http://localhost:3000'
});

// Register agent
const agent = await client.registerAgent({
  agentCard: {
    name: 'my-agent',
    endpoint: 'https://my-agent.example.com',
    protocolVersion: '0.3',
    skills: [{ name: 'translate' }]
  },
  tags: ['translation']
});

// Discover agents
const agents = await client.searchBySkill('translate');
console.log(`Found ${agents.length} translators`);
```

---

## 🧪 Testing

```bash
# Server tests (TODO: implement)
cd registry-server
npm test

# Client tests
cd registry-client
npm test
```

---

## 📚 Examples

### Register Agent (cURL)

```bash
curl -X POST http://localhost:3000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agentCard": {
      "name": "translator",
      "endpoint": "https://translator.example.com",
      "protocolVersion": "0.3",
      "skills": [{"name": "translate"}]
    },
    "tags": ["translation", "nlp"]
  }'
```

### Search Agents (cURL)

```bash
# By skill
curl http://localhost:3000/api/v1/agents?skill=translate

# By tags
curl http://localhost:3000/api/v1/agents?tags=nlp

# List all
curl http://localhost:3000/api/v1/agents
```

### Complete Workflow (TypeScript)

See [registry-client/examples/basic-usage.ts](registry-client/examples/basic-usage.ts)

---

## 🔐 Configuration

### Environment Variables

Create `.env` file in `registry-server/`:

```env
# Server
PORT=3000
NODE_ENV=production

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=a2a_registry
DB_USER=postgres
DB_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security (optional)
JWT_SECRET=your_secret_key
API_KEY_ENABLED=false

# Logging
LOG_LEVEL=info
```

---

## 🐳 Docker Configuration

### Ports

- **3000** - Registry API
- **5432** - PostgreSQL
- **6379** - Redis

### Volumes

Data is persisted in Docker volumes:
- `postgres_data` - Database
- `redis_data` - Cache

### Custom Configuration

Edit `docker-compose.yml` to customize:
```yaml
services:
  registry:
    environment:
      - PORT=3000
      - LOG_LEVEL=debug
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-24T11:24:07.000Z",
  "version": "0.1.0",
  "uptime": 3600
}
```

### Logs

```bash
# Docker logs
docker-compose logs -f registry

# Local development
tail -f logs/combined.log
```

---

## 🛠 Troubleshooting

### Port Already in Use

```bash
# Change port in docker-compose.yml or .env
PORT=3001
```

### Database Connection Failed

```bash
# Verify PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres
```

### Redis Connection Failed

```bash
# Verify Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

---

## 🚦 Production Deployment

### Security Checklist

- [ ] Change default passwords
- [ ] Enable API key authentication
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable HTTPS/TLS
- [ ] Regular backups
- [ ] Monitor logs

### Kubernetes (Advanced)

```bash
# Coming soon: Kubernetes manifests
kubectl apply -f k8s/
```

---

## 📖 More Documentation

- [API Reference](docs/api-reference.md)
- [Architecture](docs/architecture.md) _(TODO)_
- [Client Library](registry-client/README.md)
- [Contributing](CONTRIBUTING.md)

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/jenish2917/a2a-registry/issues)
- **Discussions:** [A2A Community](https://github.com/a2aproject/A2A/discussions/741)
- **Email:** jenishbarvaliya2012@gmail.com

---

**Quick Links:**
- [Main README](README.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)
