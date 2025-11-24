import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import { ApiError } from './errorHandler';

const agentCardSchema = Joi.object({
    name: Joi.string().required(),
    description: Joi.string(),
    endpoint: Joi.string().uri().required(),
    protocolVersion: Joi.string().pattern(/^\d+\.\d+$/).required(),
    capabilities: Joi.object({
        streaming: Joi.boolean(),
        pushNotifications: Joi.boolean(),
    }),
    skills: Joi.array().items(Joi.object({
        name: Joi.string().required(),
        description: Joi.string(),
    })),
    securitySchemes: Joi.object(),
    security: Joi.array(),
}).unknown(true);

const registrationSchema = Joi.object({
    agentCard: agentCardSchema.required(),
    tags: Joi.array().items(Joi.string()).max(10),
    metadata: Joi.object(),
});

export const validateAgentRegistration = (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    const { error } = registrationSchema.validate(req.body, { abortEarly: false });

    if (error) {
        const message = error.details.map((detail: any) => detail.message).join(', ');
        throw new ApiError(400, `Validation error: ${message}`);
    }

    next();
};
