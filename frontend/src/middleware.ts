import type { MiddlewareHandler } from 'astro';
import { getLogger } from './utils/logger';

export const onRequest: MiddlewareHandler = async (context, next) => {
  // Add logger to locals
  context.locals.logger = getLogger('frontend');
  
  // Log request
  context.locals.logger.info('Request received', {
    method: context.request.method,
    url: context.request.url,
    headers: Object.fromEntries(context.request.headers.entries())
  });

  try {
    const response = await next();
    
    // Log response
    context.locals.logger.info('Response sent', {
      status: response.status,
      statusText: response.statusText
    });
    
    return response;
  } catch (error) {
    // Log error
    context.locals.logger.error('Request failed', {
      error: error instanceof Error ? error.message : 'Unknown error'
    });
    throw error;
  }
}; 