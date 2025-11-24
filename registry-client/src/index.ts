import axios, { AxiosInstance, AxiosError } from 'axios';
import {
    AgentCard,
    RegistrationRequest,
    RegistryEntry,
    ListAgentsParams,
    ListAgentsResponse,
    HeartbeatResponse,
    RegistryClientConfig,
} from './types';

export class RegistryClient {
    private client: AxiosInstance;
    private baseUrl: string;

    constructor(config: RegistryClientConfig) {
        this.baseUrl = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash

        this.client = axios.create({
            baseURL: `${this.baseUrl}/api/v1`,
            timeout: config.timeout || 10000,
            headers: {
                'Content-Type': 'application/json',
                ...(config.apiKey && { 'Authorization': `Bearer ${config.apiKey}` }),
            },
        });
    }

    /**
     * Register a new agent in the registry
     */
    async registerAgent(request: RegistrationRequest): Promise<RegistryEntry> {
        try {
            const response = await this.client.post<RegistryEntry>('/agents', request);
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Get an agent by ID
     */
    async getAgent(agentId: string): Promise<RegistryEntry> {
        try {
            const response = await this.client.get<RegistryEntry>(`/agents/${agentId}`);
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Update an existing agent
     */
    async updateAgent(agentId: string, request: RegistrationRequest): Promise<RegistryEntry> {
        try {
            const response = await this.client.put<RegistryEntry>(`/agents/${agentId}`, request);
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Delete an agent from the registry
     */
    async deleteAgent(agentId: string): Promise<void> {
        try {
            await this.client.delete(`/agents/${agentId}`);
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * List/search agents with optional filters
     */
    async listAgents(params?: ListAgentsParams): Promise<ListAgentsResponse> {
        try {
            const response = await this.client.get<ListAgentsResponse>('/agents', { params });
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Search agents by skill name
     */
    async searchBySkill(skillName: string): Promise<RegistryEntry[]> {
        const response = await this.listAgents({ skill: skillName });
        return response.agents;
    }

    /**
     * Search agents by tags
     */
    async searchByTags(tags: string[]): Promise<RegistryEntry[]> {
        const response = await this.listAgents({ tags });
        return response.agents;
    }

    /**
     * Send a heartbeat for an agent
     */
    async heartbeat(agentId: string): Promise<HeartbeatResponse> {
        try {
            const response = await this.client.post<HeartbeatResponse>(`/agents/${agentId}/heartbeat`);
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Check registry health
     */
    async healthCheck(): Promise<{ status: string; timestamp: string }> {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Handle axios errors and convert to meaningful error messages
     */
    private handleError(error: unknown): Error {
        if (axios.isAxiosError(error)) {
            const axiosError = error as AxiosError<{ error: { message: string } }>;

            if (axiosError.response) {
                // Server responded with error
                const message = axiosError.response.data?.error?.message || axiosError.message;
                const statusCode = axiosError.response.status;
                return new Error(`Registry Error (${statusCode}): ${message}`);
            } else if (axiosError.request) {
                // Request made but no response
                return new Error('Registry Error: No response from server');
            }
        }

        return error instanceof Error ? error : new Error('Unknown error occurred');
    }
}

// Export types
export * from './types';
