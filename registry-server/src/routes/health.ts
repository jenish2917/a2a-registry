import { Router } from 'express';
import { query } from '../config/database';

const router = Router();

router.get('/', async (req, res) => {
    try {
        const result = await query('SELECT NOW()');
        res.json({
            status: 'healthy',
            database: 'connected',
            timestamp: result.rows[0].now,
        });
    } catch (error) {
        res.status(503).json({
            status: 'unhealthy',
            database: 'disconnected',
            error: (error as Error).message,
        });
    }
});

export default router;
