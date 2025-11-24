import { Request, Response, NextFunction } from 'express';
import { uuidv4 } from '../utils/uuid';
import { query } from '../config/database';
import { redisClient } from '../config/redis';
import { logger } from '../utils/logger';
import { ApiError } from '../middleware/errorHandler';

interface RegistryEntry {
    id: string;
    agent_id: string;
    agent_card: any;
    owner: string;
    tags: string[];
    verified: boolean;
    registered_at: Date;
    last_updated: Date;
    last_heartbeat: Date | null;
    metadata: any;
}

export const registerAgent = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { agentCard, tags = [], metadata = {} } = req.body;
        const agentId = agentCard.name || uuidv4();
        const owner = (req as any).user?.id || 'anonymous'; // TODO: Implement auth

        // Check if agent already exists
        const existing = await query(
            'SELECT id FROM registry_entries WHERE agent_id = $1',
            [agentId]
        );

        if (existing.rows.length > 0) {
            throw new ApiError(409, 'Agent with this ID already exists');
        }

        // Insert into database
        const result = await query(
            `INSERT INTO registry_entries 
       (agent_id, agent_card, owner, tags, metadata) 
       VALUES ($1, $2, $3, $4, $5) 
       RETURNING *`,
            [agentId, JSON.stringify(agentCard), owner, tags, JSON.stringify(metadata)]
        );

        const entry = result.rows[0];

        // Cache in Redis
        await redisClient.setEx(
            `agent:${agentId}`,
            3600,
            JSON.stringify(entry)
        );

        logger.info(`Agent registered: ${agentId}`);

        res.status(201).json({
            id: entry.id,
            agentId: entry.agent_id,
            agentCard: entry.agent_card,
            registeredAt: entry.registered_at,
        });
    } catch (error) {
        next(error);
    }
};

export const getAgent = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { agentId } = req.params;

        // Try cache first
        const cached = await redisClient.get(`agent:${agentId}`);
        if (cached) {
            return res.json(JSON.parse(cached));
        }

        // Query database
        const result = await query(
            'SELECT * FROM registry_entries WHERE agent_id = $1',
            [agentId]
        );

        if (result.rows.length === 0) {
            throw new ApiError(404, 'Agent not found');
        }

        const entry = result.rows[0];

        // Update cache
        await redisClient.setEx(
            `agent:${agentId}`,
            3600,
            JSON.stringify(entry)
        );

        res.json(entry);
    } catch (error) {
        next(error);
    }
};

export const updateAgent = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { agentId } = req.params;
        const { agentCard, tags, metadata } = req.body;

        const result = await query(
            `UPDATE registry_entries 
       SET agent_card = $1, tags = $2, metadata = $3
       WHERE agent_id = $4
       RETURNING *`,
            [
                JSON.stringify(agentCard),
                tags,
                JSON.stringify(metadata),
                agentId,
            ]
        );

        if (result.rows.length === 0) {
            throw new ApiError(404, 'Agent not found');
        }

        const entry = result.rows[0];

        // Update cache
        await redisClient.setEx(
            `agent:${agentId}`,
            3600,
            JSON.stringify(entry)
        );

        // Invalidate list cache
        await redisClient.del('agents:list');

        logger.info(`Agent updated: ${agentId}`);

        res.json(entry);
    } catch (error) {
        next(error);
    }
};

export const deleteAgent = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { agentId } = req.params;

        const result = await query(
            'DELETE FROM registry_entries WHERE agent_id = $1 RETURNING id',
            [agentId]
        );

        if (result.rows.length === 0) {
            throw new ApiError(404, 'Agent not found');
        }

        // Remove from cache
        await redisClient.del(`agent:${agentId}`);
        await redisClient.del('agents:list');

        logger.info(`Agent deleted: ${agentId}`);

        res.status(204).send();
    } catch (error) {
        next(error);
    }
};

export const listAgents = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const {
            tags,
            skill,
            verified,
            limit = 50,
            offset = 0,
        } = req.query;

        let queryText = 'SELECT * FROM registry_entries WHERE 1=1';
        const queryParams: any[] = [];
        let paramIndex = 1;

        // Build dynamic query based on filters
        if (tags) {
            queryText += ` AND tags && $${paramIndex}`;
            queryParams.push(Array.isArray(tags) ? tags : [tags]);
            paramIndex++;
        }

        if (skill) {
            queryText += ` AND agent_card @> $${paramIndex}::jsonb`;
            queryParams.push(JSON.stringify({ skills: [{ name: skill }] }));
            paramIndex++;
        }

        if (verified !== undefined) {
            queryText += ` AND verified = $${paramIndex}`;
            queryParams.push(verified === 'true');
            paramIndex++;
        }

        queryText += ` ORDER BY last_updated DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
        queryParams.push(parseInt(limit as string), parseInt(offset as string));

        const result = await query(queryText, queryParams);

        res.json({
            agents: result.rows,
            total: result.rows.length,
            limit: parseInt(limit as string),
            offset: parseInt(offset as string),
        });
    } catch (error) {
        next(error);
    }
};

export const heartbeat = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { agentId } = req.params;

        const result = await query(
            `UPDATE registry_entries 
       SET last_heartbeat = CURRENT_TIMESTAMP 
       WHERE agent_id = $1 
       RETURNING last_heartbeat`,
            [agentId]
        );

        if (result.rows.length === 0) {
            throw new ApiError(404, 'Agent not found');
        }

        res.json({
            agentId,
            lastHeartbeat: result.rows[0].last_heartbeat,
        });
    } catch (error) {
        next(error);
    }
};
