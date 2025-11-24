# A2A Registry Client Library

TypeScript/JavaScript client library for interacting with the A2A Agent Registry.

## Installation

```bash
npm install @a2a/registry-client
```

## Quick Start

```typescript
import { RegistryClient } from '@a2a/registry-client';

// Create client
const client = new RegistryClient({
  baseUrl: 'http://localhost:3000',
});

// Register an agent
const agent = await client.registerAgent({
  agentCard: {
    name: 'my-agent',
    endpoint: 'https://my-agent.example.com',
    protocolVersion: '0.3',
    skills: [{ name: 'translate' }],
  },
  tags: ['translation', 'nlp'],
});

// Discover agents by skill
const translators = await client.searchBySkill('translate');

// Send heartbeat
await client.heartbeat(agent.agentId);
```

## Features

- ✅ **Type-Safe** - Full TypeScript support with comprehensive type definitions
- ✅ **Promise-Based** - Modern async/await API
- ✅ **Error Handling** - Meaningful error messages
- ✅ **Comprehensive** - All registry API endpoints covered
- ✅ **Easy to Use** - Intuitive method names and parameters

## API Reference

### Constructor

```typescript
const client = new RegistryClient({
  baseUrl: string;      // Registry server URL
  timeout?: number;     // Request timeout (default: 10000ms)
  apiKey?: string;      // Optional API key for authentication
});
```

### Methods

#### `registerAgent(request: RegistrationRequest): Promise<RegistryEntry>`

Register a new agent.

```typescript
const agent = await client.registerAgent({
  agentCard: {
    name: 'translation-agent',
    description: 'Multilingual translator',
    endpoint: 'https://translation-agent.example.com',
    protocolVersion: '0.3',
    capabilities: { streaming: true },
    skills: [{ name: 'translate' }],
  },
  tags: ['translation', 'nlp'],
  metadata: { version: '1.0.0' },
});
```

#### `getAgent(agentId: string): Promise<RegistryEntry>`

Get an agent by ID.

```typescript
const agent = await client.getAgent('translation-agent');
```

#### `updateAgent(agentId: string, request: RegistrationRequest): Promise<RegistryEntry>`

Update an existing agent.

```typescript
const updated = await client.updateAgent('translation-agent', {
  agentCard: { ...updatedCard },
  tags: ['translation', 'nlp', 'enhanced'],
});
```

#### `deleteAgent(agentId: string): Promise<void>`

Delete an agent from the registry.

```typescript
await client.deleteAgent('translation-agent');
```

#### `listAgents(params?: ListAgentsParams): Promise<ListAgentsResponse>`

List/search agents with optional filters.

```typescript
const response = await client.listAgents({
  tags: ['translation'],
  skill: 'translate',
  verified: true,
  limit: 20,
  offset: 0,
});

console.log(response.agents);    // Array of agents
console.log(response.total);     // Total count
```

#### `searchBySkill(skillName: string): Promise<RegistryEntry[]>`

Search agents by skill name.

```typescript
const translators = await client.searchBySkill('translate');
```

#### `searchByTags(tags: string[]): Promise<RegistryEntry[]>`

Search agents by tags.

```typescript
const nlpAgents = await client.searchByTags(['nlp', 'ai']);
```

#### `heartbeat(agentId: string): Promise<HeartbeatResponse>`

Send a heartbeat to mark agent as active.

```typescript
const response = await client.heartbeat('translation-agent');
console.log(response.lastHeartbeat);
```

#### `healthCheck(): Promise<{ status: string; timestamp: string }>`

Check registry health.

```typescript
const health = await client.healthCheck();
console.log(health.status); // "healthy"
```

## Types

### AgentCard

```typescript
interface AgentCard {
  name: string;
  description?: string;
  endpoint: string;
  protocolVersion: string;
  capabilities?: {
    streaming?: boolean;
    pushNotifications?: boolean;
  };
  skills?: Skill[];
  securitySchemes?: Record<string, any>;
  security?: any[];
}
```

### RegistryEntry

```typescript
interface RegistryEntry {
  id: string;
  agentId: string;
  agentCard: AgentCard;
  owner: string;
  tags: string[];
  verified: boolean;
  registeredAt: Date;
  lastUpdated: Date;
  lastHeartbeat?: Date;
  metadata: Record<string, any>;
}
```

## Example: Complete Workflow

```typescript
import { RegistryClient } from '@a2a/registry-client';

const client = new RegistryClient({
  baseUrl: 'http://localhost:3000',
});

// 1. Register agent
const agent = await client.registerAgent({
  agentCard: {
    name: 'my-agent',
    endpoint: 'https://my-agent.example.com',
    protocolVersion: '0.3',
    skills: [{ name: 'task1' }, { name: 'task2' }],
  },
  tags: ['category1'],
});

// 2. Discover agents with specific skill
const agents = await client.searchBySkill('task1');
console.log(`Found ${agents.length} agents`);

// 3. Send periodic heartbeats
setInterval(async () => {
  await client.heartbeat(agent.agentId);
}, 60000); // Every minute

// 4. Update when capabilities change
await client.updateAgent(agent.agentId, {
  agentCard: {
    ...agent.agentCard,
    skills: [...agent.agentCard.skills, { name: 'task3' }],
  },
  tags: agent.tags,
});

// 5. Cleanup on shutdown
process.on('SIGINT', async () => {
  await client.deleteAgent(agent.agentId);
  process.exit();
});
```

## Error Handling

```typescript
try {
  await client.registerAgent(request);
} catch (error) {
  if (error.message.includes('409')) {
    console.error('Agent already exists');
  } else if (error.message.includes('404')) {
    console.error('Agent not found');
  } else {
    console.error('Registry error:', error.message);
  }
}
```

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Run example
npm run example
```

## License

Apache 2.0
