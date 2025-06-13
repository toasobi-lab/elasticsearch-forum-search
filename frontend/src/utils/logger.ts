export interface Logger {
  info: (message: string, data?: Record<string, unknown>) => void;
  debug: (message: string, data?: Record<string, unknown>) => void;
  error: (message: string, data?: Record<string, unknown>) => void;
}

class ConsoleLogger implements Logger {
  private context: string;

  constructor(context: string) {
    this.context = context;
  }

  private formatMessage(level: string, message: string, data?: Record<string, unknown>): string {
    const timestamp = new Date().toISOString();
    const dataStr = data ? ` ${JSON.stringify(data)}` : '';
    return `[${timestamp}] [${level}] [${this.context}] ${message}${dataStr}`;
  }

  info(message: string, data?: Record<string, unknown>): void {
    console.log(this.formatMessage('INFO', message, data));
  }

  debug(message: string, data?: Record<string, unknown>): void {
    console.debug(this.formatMessage('DEBUG', message, data));
  }

  error(message: string, data?: Record<string, unknown>): void {
    console.error(this.formatMessage('ERROR', message, data));
  }
}

export function getLogger(context: string): Logger {
  return new ConsoleLogger(context);
} 