/**
 * A2A Registry - Semantic Search Controller
 *
 * Proxies semantic search requests to the Python semantic search microservice.
 */

import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { ApiError } from '../middleware/errorHandler';

// Semantic search service URL
const SEMANTIC_SEARCH_URL = process.env.SEMANTIC_SEARCH_URL || 'http://localhost:3001';

/**
 * Helper function to make requests to the semantic search service
 */
async function fetchFromSemanticService(
    endpoint: string,
    method: string = 'GET',
    body?: any
): Promise<any> {
    const url = `${SEMANTIC_SEARCH_URL}${endpoint}`;

    const options: RequestInit = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(
            response.status,
            `Semantic search service error: ${errorText}`
        );
    }

    return response.json();
}

/**
 * Semantic search for agents
 * POST /api/v1/agents/semantic/search
 */
export const semanticSearch = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { query, top_k = 10, min_score = 0.5, filters } = req.body;

        if (!query) {
            throw new ApiError(400, 'Query is required for semantic search');
        }

        logger.info(`Semantic search: "${query}" (top_k=${top_k})`);

        const result = await fetchFromSemanticService(
            '/api/v1/semantic/search',
            'POST',
            { query, top_k, min_score, filters }
        );

        res.json(result);
    } catch (error) {
        logger.error('Semantic search failed:', error);
        next(error);
    }
};

/**
 * Index a single agent for semantic search
 * POST /api/v1/agents/semantic/index
 */
export const indexAgent = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { agent_id, agent_card, tags = [] } = req.body;

        if (!agent_id || !agent_card) {
            throw new ApiError(400, 'agent_id and agent_card are required');
        }

        logger.info(`Indexing agent: ${agent_id}`);

        const result = await fetchFromSemanticService(
            '/api/v1/semantic/index',
            'POST',
            { agent_id, agent_card, tags }
        );

        res.json(result);
    } catch (error) {
        logger.error('Agent indexing failed:', error);
        next(error);
    }
};

/**
 * Index all agents for semantic search
 * POST /api/v1/agents/semantic/index-all
 */
export const indexAllAgents = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        logger.info('Indexing all agents for semantic search');

        const result = await fetchFromSemanticService(
            '/api/v1/semantic/index-all',
            'POST'
        );

        res.json(result);
    } catch (error) {
        logger.error('Bulk agent indexing failed:', error);
        next(error);
    }
};
