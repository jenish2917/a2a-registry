import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export class ApiError extends Error {
    statusCode: number;
    isOperational: boolean;

    constructor(statusCode: number, message: string, isOperational = true) {
        super(message);
        this.statusCode = statusCode;
        this.isOperational = isOperational;
        Error.captureStackTrace(this, this.constructor);
    }
}

export const errorHandler = (
    err: Error | ApiError,
    req: Request,
    res: Response,
    next: NextFunction
) => {
    if (err instanceof ApiError) {
        logger.error(`API Error: ${err.message}`, {
            statusCode: err.statusCode,
            path: req.path,
            method: req.method,
        });

        return res.status(err.statusCode).json({
            error: {
                message: err.message,
                statusCode: err.statusCode,
            },
        });
    }

    // Unhandled errors
    logger.error('Unhandled Error:', err);
    return res.status(500).json({
        error: {
            message: 'Internal Server Error',
            statusCode: 500,
        },
    });
};
