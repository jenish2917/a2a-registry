import { Pool, PoolConfig } from 'pg';
import { logger } from '../utils/logger';

const poolConfig: PoolConfig = {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'a2a_registry',
    user: process.env.DB_USER || 'registry_user',
    password: process.env.DB_PASSWORD,
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
};

export const pool = new Pool(poolConfig);

pool.on('connect', () => {
    logger.info('Database connection established');
});

pool.on('error', (err: Error) => {
    logger.error('Unexpected database error', err);
});

export const query = (text: string, params?: any[]) => pool.query(text, params);
