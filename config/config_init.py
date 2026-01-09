"""
Config module for SVD Prompt Enhancer Pro v5.0

Contains application-wide constants and configuration.

Modules:
    - constants: Application constants and configuration values
"""

from .constants import (
    # App info
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    APP_DESCRIPTION,
    PHASE,
    RELEASE_DATE,
    
    # Directories
    CONFIG_DIR,
    DATA_DIR,
    CACHE_DIR,
    LOGS_DIR,
    LOG_FILE,
    
    # Logging
    LOG_LEVEL,
    LOG_FORMAT,
    
    # Ollama
    OLLAMA_HOST,
    OLLAMA_API_ENDPOINT,
    DEFAULT_ENHANCEMENT_MODEL,
    DEFAULT_VISION_MODEL,
    
    # Timeouts
    OLLAMA_CONNECT_TIMEOUT,
    ENHANCEMENT_TIMEOUT,
    VISION_ANALYSIS_TIMEOUT,
    REQUEST_TIMEOUT,
    
    # Retry (Phase 1)
    RETRY_ENABLED,
    RETRY_MAX_ATTEMPTS,
    RETRY_INITIAL_DELAY,
    RETRY_BACKOFF_MULTIPLIER,
    RETRY_MAX_DELAY,
    
    # JSON (Phase 1)
    SAFE_JSON_ENABLED,
    JSON_REQUIRED_KEYS,
    JSON_MIN_LENGTH,
    JSON_MAX_LENGTH,
    
    # Validation (Phase 1)
    VALIDATE_PROMPT_LENGTH,
    PROMPT_MAX_LENGTH,
    
    # UI
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    
    # Helpers
    get_retry_delay,
    is_valid_model,
    get_timeout_for_operation,
)

__all__ = [
    'APP_NAME', 'APP_VERSION', 'APP_AUTHOR', 'APP_DESCRIPTION',
    'PHASE', 'RELEASE_DATE',
    'CONFIG_DIR', 'DATA_DIR', 'CACHE_DIR', 'LOGS_DIR', 'LOG_FILE',
    'LOG_LEVEL', 'LOG_FORMAT',
    'OLLAMA_HOST', 'OLLAMA_API_ENDPOINT', 'DEFAULT_ENHANCEMENT_MODEL',
    'DEFAULT_VISION_MODEL',
    'OLLAMA_CONNECT_TIMEOUT', 'ENHANCEMENT_TIMEOUT', 'VISION_ANALYSIS_TIMEOUT',
    'REQUEST_TIMEOUT',
    'RETRY_ENABLED', 'RETRY_MAX_ATTEMPTS', 'RETRY_INITIAL_DELAY',
    'RETRY_BACKOFF_MULTIPLIER', 'RETRY_MAX_DELAY',
    'SAFE_JSON_ENABLED', 'JSON_REQUIRED_KEYS', 'JSON_MIN_LENGTH',
    'JSON_MAX_LENGTH',
    'VALIDATE_PROMPT_LENGTH', 'PROMPT_MAX_LENGTH',
    'WINDOW_WIDTH', 'WINDOW_HEIGHT', 'DEFAULT_LANGUAGE',
    'SUPPORTED_LANGUAGES',
    'get_retry_delay', 'is_valid_model', 'get_timeout_for_operation',
]

__version__ = '1.0.0'
__author__ = 'SVD Prompt Enhancer Team'
