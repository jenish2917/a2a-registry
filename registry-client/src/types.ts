/**
 * A2A Agent Card as per protocol specification
 */
export interface AgentCard {
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
    [key: string]: any; // Allow additional properties
}

export interface Skill {
    name: string;
    description?: string;
    parameters?: Record<string, any>;
}

export interface RegistrationRequest {
    agentCard: AgentCard;
    tags?: string[];
    metadata?: Record<string, any>;
}

export interface RegistryEntry {
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

export interface ListAgentsParams {
    tags?: string | string[];
    skill?: string;
    verified?: boolean;
    limit?: number;
    offset?: number;
}

export interface ListAgentsResponse {
    agents: RegistryEntry[];
    total: number;
    limit: number;
    offset: number;
}

export interface HeartbeatResponse {
    agentId: string;
    lastHeartbeat: Date;
}

export interface RegistryClientConfig {
    baseUrl: string;
    timeout?: number;
    apiKey?: string;
}
