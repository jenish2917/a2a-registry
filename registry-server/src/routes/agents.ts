import { Router } from 'express';
import * as agentController from '../controllers/agentController';
import * as semanticController from '../controllers/semanticController';
import { validateAgentRegistration } from '../middleware/validation';

const router = Router();

// Register a new agent
router.post('/', validateAgentRegistration, agentController.registerAgent);

// Get agent by ID
router.get('/:agentId', agentController.getAgent);

// Update agent
router.put('/:agentId', validateAgentRegistration, agentController.updateAgent);

// Delete agent
router.delete('/:agentId', agentController.deleteAgent);

// List/search agents
router.get('/', agentController.listAgents);

// Heartbeat endpoint
router.post('/:agentId/heartbeat', agentController.heartbeat);

// ============== Semantic Search Routes ==============

// Semantic search for agents
router.post('/semantic/search', semanticController.semanticSearch);

// Index a single agent for semantic search
router.post('/semantic/index', semanticController.indexAgent);

// Index all agents for semantic search
router.post('/semantic/index-all', semanticController.indexAllAgents);

export default router;
