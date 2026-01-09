#!/usr/bin/env python3
"""
SVD Prompt Enhancer Pro v5.1
Config Module - Constants and Configuration Management

Centralizes all application constants for:
- Retry logic (exponential backoff)
- Ollama API configuration
- Input validation
- UI settings
- Application metadata

Author: SVD Prompt Enhancer Team
Date: 2026-01-09
Version: 5.1.0
"""

import logging
from enum import Enum
from dataclasses import dataclass

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# RETRY LOGIC CONSTANTS (R1.2 - Exponential Backoff)
# ============================================================================

RETRY_ENABLED = True
"""Enable/disable retry logic for API calls"""

RETRY_MAX_ATTEMPTS = 3
"""Maximum number of retry attempts (including initial attempt)"""

RETRY_INITIAL_DELAY = 2
"""Initial delay in seconds before first retry"""

RETRY_BACKOFF_MULTIPLIER = 2
"""Exponential backoff multiplier (delay = initial_delay * (multiplier ^ attempt))"""

RETRY_MAX_DELAY = 30
"""Maximum delay between retries in seconds (cap)"""


def get_retry_delay(attempt: int) -> float:
    """
    Calculate retry delay using exponential backoff formula
    
    Formula: delay = min(initial_delay * (multiplier ^ attempt), max_delay)
    
    Examples:
        attempt 0: 2 * (2^0) = 2s
        attempt 1: 2 * (2^1) = 4s
        attempt 2: 2 * (2^2) = 8s
        attempt 3: 2 * (2^3) = 16s
        attempt 4+: capped at 30s
    
    Args:
        attempt: Attempt number (0-indexed)
    
    Returns:
        Delay in seconds (float)
    """
    delay = RETRY_INITIAL_DELAY * (RETRY_BACKOFF_MULTIPLIER ** attempt)
    return min(delay, RETRY_MAX_DELAY)


# ============================================================================
# OLLAMA API CONFIGURATION
# ============================================================================

OLLAMA_HOST = "http://localhost:11434"
"""Ollama API host URL"""

OLLAMA_API_ENDPOINT = f"{OLLAMA_HOST}/api/generate"
"""Full Ollama API endpoint for prompt generation"""

DEFAULT_ENHANCEMENT_MODEL = "mistral"
"""Default model to use for prompt enhancement"""

ENHANCEMENT_TIMEOUT = 60
"""Timeout in seconds for Ollama API calls"""


# ============================================================================
# INPUT VALIDATION CONSTANTS
# ============================================================================

VALIDATE_PROMPT_LENGTH = True
"""Enable/disable prompt length validation"""

PROMPT_MIN_LENGTH = 5
"""Minimum prompt length in characters"""

PROMPT_MAX_LENGTH = 2000
"""Maximum prompt length in characters"""


# ============================================================================
# UI CONFIGURATION
# ============================================================================

CANCEL_BUTTON_ENABLED = True
"""Enable/disable cancel button in UI"""

APP_VERSION = "5.1.0"
"""Application version"""

APP_NAME = "SVD Prompt Enhancer Pro"
"""Application name"""


# ============================================================================
# ENHANCEMENT PARAMETERS (Safe Defaults)
# ============================================================================

DEFAULT_CREATIVITY = 0.7
"""Default creativity level (0.0-1.0) for prompt enhancement"""

DEFAULT_DETAIL_LEVEL = "Wysoki"
"""Default detail level (Niski, Średni, Wysoki)"""

DEFAULT_STYLE = "Kinematograficzny"
"""Default style (Kinematograficzny, Artystyczny, Techniczny)"""

DEFAULT_LENGTH = 350
"""Default enhanced prompt length in words"""


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = logging.INFO
"""Default logging level"""

LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
"""Log format string"""

LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
"""Log date format"""


# ============================================================================
# WORKER/THREAD CONFIGURATION
# ============================================================================

WORKER_TIMEOUT = 120
"""Worker thread timeout in seconds"""

WORKER_POLL_INTERVAL = 0.1
"""Worker polling interval in seconds"""


# ============================================================================
# SAFETY LIMITS
# ============================================================================

MAX_CONCURRENT_WORKERS = 1
"""Maximum number of concurrent enhancement workers"""

REQUEST_QUEUE_SIZE = 10
"""Maximum size of request queue"""


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

logger.debug(f"Constants module loaded (APP_VERSION={APP_VERSION})")

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
