"""
SVD Prompt Enhancer Pro v5.1 - Config Package

Configuration management module containing:
- constants: All application constants (retry, API, validation, UI)

Import everything from config package:
    from config import RETRY_ENABLED, OLLAMA_HOST, etc.

Author: SVD Prompt Enhancer Team
Date: 2026-01-09
Version: 5.1.0
"""

import logging

logger = logging.getLogger(__name__)
logger.debug("Initializing config package...")

# Import all constants from the constants module
from .constants import (
    # Retry
    RETRY_ENABLED,
    RETRY_MAX_ATTEMPTS,
    RETRY_INITIAL_DELAY,
    RETRY_BACKOFF_MULTIPLIER,
    RETRY_MAX_DELAY,
    get_retry_delay,
    # Ollama
    OLLAMA_HOST,
    OLLAMA_API_ENDPOINT,
    DEFAULT_ENHANCEMENT_MODEL,
    ENHANCEMENT_TIMEOUT,
    # Validation
    VALIDATE_PROMPT_LENGTH,
    PROMPT_MIN_LENGTH,
    PROMPT_MAX_LENGTH,
    # UI
    CANCEL_BUTTON_ENABLED,
    APP_VERSION,
    APP_NAME,
    # Enhancement parameters
    DEFAULT_CREATIVITY,
    DEFAULT_DETAIL_LEVEL,
    DEFAULT_STYLE,
    DEFAULT_LENGTH,
    # Logging
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATEFORMAT,
    # Worker
    WORKER_TIMEOUT,
    WORKER_POLL_INTERVAL,
    # Safety
    MAX_CONCURRENT_WORKERS,
    REQUEST_QUEUE_SIZE,
)

logger.debug("Config package initialized successfully")

__version__ = "5.1.0"

__all__ = [
    # Retry
    'RETRY_ENABLED',
    'RETRY_MAX_ATTEMPTS',
    'RETRY_INITIAL_DELAY',
    'RETRY_BACKOFF_MULTIPLIER',
    'RETRY_MAX_DELAY',
    'get_retry_delay',
    # Ollama
    'OLLAMA_HOST',
    'OLLAMA_API_ENDPOINT',
    'DEFAULT_ENHANCEMENT_MODEL',
    'ENHANCEMENT_TIMEOUT',
    # Validation
    'VALIDATE_PROMPT_LENGTH',
    'PROMPT_MIN_LENGTH',
    'PROMPT_MAX_LENGTH',
    # UI
    'CANCEL_BUTTON_ENABLED',
    'APP_VERSION',
    'APP_NAME',
    # Enhancement
    'DEFAULT_CREATIVITY',
    'DEFAULT_DETAIL_LEVEL',
    'DEFAULT_STYLE',
    'DEFAULT_LENGTH',
    # Logging
    'LOG_LEVEL',
    'LOG_FORMAT',
    'LOG_DATEFORMAT',
    # Worker
    'WORKER_TIMEOUT',
    'WORKER_POLL_INTERVAL',
    # Safety
    'MAX_CONCURRENT_WORKERS',
    'REQUEST_QUEUE_SIZE',
]
