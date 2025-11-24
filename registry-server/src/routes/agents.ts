import { Router } from 'express';
import * as agentController from '../controllers/agentController';
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

export default router;
