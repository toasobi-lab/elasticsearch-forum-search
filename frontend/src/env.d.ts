/// <reference types="astro/client" />

import type { Logger } from './utils/logger';

declare namespace App {
  interface Locals {
    logger: Logger;
  }
} 