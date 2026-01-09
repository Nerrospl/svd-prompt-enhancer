"""
Constants and configuration for SVD Prompt Enhancer Pro v5.0

Author: Phase 1 Implementation
Date: 2026-01-09
Version: 1.0

This module contains all application constants, configuration values,
and default settings used throughout the application.
"""

import os
from enum import Enum
from pathlib import Path


# ============================================================================
# APPLICATION INFO
# ============================================================================

APP_NAME = "SVD Prompt Enhancer Pro"
APP_VERSION = "5.1.0"  # Updated to 5.1 (Phase 1)
APP_AUTHOR = "Nerrospl"
APP_DESCRIPTION = "Enhance prompts for Stable Diffusion and other image generators"

# Build and environment
PHASE = "Phase 1 - Stabilization"
RELEASE_DATE = "2026-01-16"
PYTHON_MIN_VERSION = "3.8"

# ============================================================================
# XDG COMPLIANCE - Data directories
# ============================================================================

# Linux standard directories
_XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
_XDG_DATA_HOME = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
_XDG_CACHE_HOME = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))

# Application-specific directories
CONFIG_DIR = Path(_XDG_CONFIG_HOME) / 'svd_enhancer'
DATA_DIR = Path(_XDG_DATA_HOME) / 'svd_enhancer'
CACHE_DIR = Path(_XDG_CACHE_HOME) / 'svd_enhancer'
LOGS_DIR = DATA_DIR / 'logs'

# Ensure directories exist
for directory in [CONFIG_DIR, DATA_DIR, CACHE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Files
LOG_FILE = LOGS_DIR / 'app.log'
SETTINGS_FILE = CONFIG_DIR / 'settings.json'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 3

# Log file rotation settings
LOG_ROTATION_ENABLED = True
LOG_ROTATION_SIZE = 5 * 1024 * 1024  # 5 MB

# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================

# Ollama server connection
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_API_ENDPOINT = f"{OLLAMA_HOST}/api"
OLLAMA_HEALTH_CHECK = f"{OLLAMA_HOST}/api/tags"

# Default models
DEFAULT_ENHANCEMENT_MODEL = 'dolphin-llama3:latest'
DEFAULT_VISION_MODEL = 'llava:latest'
DEFAULT_TRANSLATION_MODEL = 'mistral:latest'

# Available models
ENHANCEMENT_MODELS = [
    'dolphin-llama3:latest',
    'dolphin:latest',
    'mistral:latest',
    'neural-chat:latest',
    'qwen:latest',
]

VISION_MODELS = [
    'llava:latest',
    'llava-llama2:latest',
    'moondream:latest',
]

TRANSLATION_MODELS = [
    'mistral:latest',
    'neural-chat:latest',
]

# ============================================================================
# TIMEOUTS (PHASE 1 - STABILIZATION)
# ============================================================================

# Connection timeouts
OLLAMA_CONNECT_TIMEOUT = 5  # seconds
OLLAMA_READ_TIMEOUT = 10  # seconds

# Operation timeouts
OLLAMA_HEALTH_CHECK_TIMEOUT = 3  # seconds
MODEL_LOAD_TIMEOUT = 30  # seconds
ENHANCEMENT_TIMEOUT = 120  # seconds (Phase 1: was 60, increased for reliability)
VISION_ANALYSIS_TIMEOUT = 60  # seconds
TRANSLATION_TIMEOUT = 30  # seconds

# Request timeout (total)
REQUEST_TIMEOUT = 180  # seconds (3 minutes)

# ============================================================================
# RETRY CONFIGURATION (NEW - PHASE 1 R1.2)
# ============================================================================

# Retry behavior for failed requests
RETRY_ENABLED = True  # R1.2: Enable retry system
RETRY_MAX_ATTEMPTS = 3  # Maximum number of retry attempts
RETRY_INITIAL_DELAY = 2  # seconds (initial backoff)
RETRY_MAX_DELAY = 30  # seconds (maximum backoff)
RETRY_BACKOFF_MULTIPLIER = 2  # exponential backoff: 2, 4, 8, 16...

# Retry conditions (which errors should trigger retry)
RETRY_ON_TIMEOUT = True
RETRY_ON_CONNECTION_ERROR = True
RETRY_ON_SERVER_ERROR = True
RETRY_ON_JSON_ERROR = True  # Will use SafeJSONHandler instead

# Logging retries
RETRY_LOG_ATTEMPTS = True
RETRY_LOG_LEVEL = 'WARNING'  # Log retries at WARNING level

# ============================================================================
# JSON PARSING (NEW - PHASE 1 R1.1)
# ============================================================================

# SafeJSONHandler configuration
SAFE_JSON_ENABLED = True  # R1.1: Enable fallback JSON parsing
JSON_VALIDATION_ENABLED = True
JSON_REQUIRED_KEYS = {'prompt_en', 'prompt_pl'}
JSON_MIN_LENGTH = 20  # Minimum characters for valid response
JSON_MAX_LENGTH = 5000  # Maximum characters for response

# JSON parsing strategies
JSON_STRATEGY_DIRECT = True  # Try direct parse
JSON_STRATEGY_REGEX = True  # Try regex extraction
JSON_STRATEGY_PARTIAL = True  # Try partial parse
JSON_STRATEGY_FALLBACK = True  # Always fallback if all fail

# ============================================================================
# PROMPT ENHANCEMENT CONFIGURATION
# ============================================================================

# Prompt length constraints
PROMPT_MIN_LENGTH = 5  # Minimum input prompt length
PROMPT_MAX_LENGTH = 1000  # Maximum input prompt length (Phase 1: validation added)
ENHANCED_PROMPT_MIN_LENGTH = 50  # Minimum enhanced prompt
ENHANCED_PROMPT_MAX_LENGTH = 2000  # Maximum enhanced prompt

# Prompt enhancement settings (sliders)
CREATIVITY_MIN = 0.0
CREATIVITY_MAX = 1.0
CREATIVITY_DEFAULT = 0.7
CREATIVITY_STEP = 0.05

LENGTH_MIN = 50  # words
LENGTH_MAX = 500  # words
LENGTH_DEFAULT = 350
LENGTH_STEP = 10

# Detail levels
DETAIL_LEVELS = ['Niski', 'Średni', 'Wysoki']
DETAIL_DEFAULT = 'Wysoki'

# Style options
STYLES = ['Kinematograficzny', 'Artystyczny', 'Techniczny']
STYLE_DEFAULT = 'Kinematograficzny'

# ============================================================================
# UI CONFIGURATION
# ============================================================================

# Window settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

# UI Themes
DEFAULT_THEME = 'light'
SUPPORTED_THEMES = ['light', 'dark']

# Fonts
FONT_FAMILY = 'Segoe UI, Courier New'
FONT_SIZE_SMALL = 9
FONT_SIZE_DEFAULT = 10
FONT_SIZE_LARGE = 12

# Colors (will be updated by theme)
PRIMARY_COLOR = '#2196F3'
SECONDARY_COLOR = '#FFC107'
ERROR_COLOR = '#F44336'
SUCCESS_COLOR = '#4CAF50'
WARNING_COLOR = '#FF9800'

# ============================================================================
# LANGUAGE SETTINGS
# ============================================================================

DEFAULT_LANGUAGE = 'pl'  # Polish
SUPPORTED_LANGUAGES = {
    'pl': 'Polski',
    'en': 'English'
}

# UI translations (can be expanded to i18n system)
LANGUAGE_PROMPTS = {
    'pl': {
        'title': 'SVD Prompt Enhancer Pro',
        'direct_enhance': 'Wzbogacz promptów',
        'image_enhance': 'Wzbogacz z obrazem',
        'placeholder_prompt': 'Wpisz prompt (np. piękna kobieta na plaży)...',
    },
    'en': {
        'title': 'SVD Prompt Enhancer Pro',
        'direct_enhance': 'Direct Enhancement',
        'image_enhance': 'Image Enhancement',
        'placeholder_prompt': 'Enter prompt (e.g. beautiful woman on beach)...',
    }
}

# ============================================================================
# IMAGE PROCESSING CONFIGURATION
# ============================================================================

# Image constraints
IMAGE_MAX_SIZE = 20 * 1024 * 1024  # 20 MB
IMAGE_SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
IMAGE_MAX_DIMENSION = 4096  # pixels

# Image analysis timeouts
IMAGE_PIL_ANALYSIS_TIMEOUT = 2  # seconds (fast PIL analysis)
IMAGE_LLAVA_ANALYSIS_TIMEOUT = 60  # seconds (LLaVA vision model)

# ============================================================================
# PERFORMANCE & RESOURCES
# ============================================================================

# Memory settings
CACHE_ENABLED = True
CACHE_MAX_ENTRIES = 100
CACHE_MAX_SIZE = 50 * 1024 * 1024  # 50 MB

# Worker threads
WORKER_THREAD_POOL_SIZE = 4
WORKER_TIMEOUT = 300  # seconds (5 minutes)

# Rate limiting
RATE_LIMIT_ENABLED = False
RATE_LIMIT_PER_MINUTE = 60

# ============================================================================
# VALIDATION CONFIGURATION (NEW - PHASE 1 R1.3)
# ============================================================================

# Input validation
VALIDATE_PROMPT_LENGTH = True
VALIDATE_SPECIAL_CHARACTERS = True
VALIDATE_LANGUAGE = True

# Output validation
VALIDATE_RESPONSE_KEYS = True
VALIDATE_RESPONSE_LENGTH = True
VALIDATE_RESPONSE_QUALITY = True

# ============================================================================
# CANCEL/INTERRUPT CONFIGURATION (NEW - PHASE 1 R1.3)
# ============================================================================

# Cancel button settings
CANCEL_BUTTON_ENABLED = True  # R1.3: Enable cancel mechanism
CANCEL_DEBOUNCE_MS = 200  # Debounce cancel clicks
CANCELLATION_GRACE_PERIOD = 2  # seconds (time to cleanup)

# Progress reporting
PROGRESS_UPDATE_INTERVAL = 500  # milliseconds
PROGRESS_REPORT_ENABLED = True

# ============================================================================
# NOTIFICATION SETTINGS
# ============================================================================

# Status messages
STATUS_UPDATE_INTERVAL = 1000  # milliseconds
NOTIFICATION_DURATION = 3000  # milliseconds (3 seconds)

# Sound notifications
SOUND_ENABLED = False
SOUND_ON_COMPLETION = True
SOUND_ON_ERROR = True

# ============================================================================
# API RESPONSE VALIDATION
# ============================================================================

# Response validation rules
MIN_RESPONSE_LENGTH = 50
MAX_RESPONSE_LENGTH = 5000
REQUIRED_RESPONSE_FIELDS = ['prompt_en', 'prompt_pl']

# ============================================================================
# DEBUGGING & DEVELOPMENT
# ============================================================================

# Debug mode
DEBUG_MODE = False
DEBUG_LOG_LEVEL = 'DEBUG'
DEBUG_SHOW_NETWORK_CALLS = True
DEBUG_SHOW_TIMINGS = True

# Development settings
DEV_MODE = False  # Bypass certain validations
DEV_USE_MOCK_OLLAMA = False  # Use mock responses instead of real API
DEV_LOG_FULL_RESPONSES = False  # Log full API responses

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_retry_delay(attempt: int) -> float:
    """
    Calculate retry delay with exponential backoff
    
    Args:
        attempt: Attempt number (0-indexed)
    
    Returns:
        Delay in seconds
    """
    delay = RETRY_INITIAL_DELAY * (RETRY_BACKOFF_MULTIPLIER ** attempt)
    return min(delay, RETRY_MAX_DELAY)


def is_valid_model(model_name: str, model_type: str = 'enhancement') -> bool:
    """
    Check if model is in supported list
    
    Args:
        model_name: Model name to check
        model_type: 'enhancement', 'vision', or 'translation'
    
    Returns:
        True if model is supported
    """
    if model_type == 'enhancement':
        return model_name in ENHANCEMENT_MODELS
    elif model_type == 'vision':
        return model_name in VISION_MODELS
    elif model_type == 'translation':
        return model_name in TRANSLATION_MODELS
    return False


def get_timeout_for_operation(operation: str) -> int:
    """
    Get timeout for specific operation
    
    Args:
        operation: Operation name (enhancement, vision, etc.)
    
    Returns:
        Timeout in seconds
    """
    timeouts = {
        'enhancement': ENHANCEMENT_TIMEOUT,
        'vision': VISION_ANALYSIS_TIMEOUT,
        'translation': TRANSLATION_TIMEOUT,
        'health_check': OLLAMA_HEALTH_CHECK_TIMEOUT,
        'model_load': MODEL_LOAD_TIMEOUT,
    }
    return timeouts.get(operation, REQUEST_TIMEOUT)


# ============================================================================
# VERSION HISTORY
# ============================================================================

VERSION_HISTORY = {
    '5.0.0': 'Initial release',
    '5.1.0': 'Phase 1 - Stabilization (R1.1, R1.2, R1.3)',
}

# ============================================================================
# EXPORT FOR IMPORTS
# ============================================================================

__all__ = [
    # App info
    'APP_NAME', 'APP_VERSION', 'APP_AUTHOR', 'APP_DESCRIPTION',
    'PHASE', 'RELEASE_DATE',
    
    # Directories
    'CONFIG_DIR', 'DATA_DIR', 'CACHE_DIR', 'LOGS_DIR', 'LOG_FILE',
    
    # Logging
    'LOG_LEVEL', 'LOG_FORMAT', 'LOG_FILE',
    
    # Ollama
    'OLLAMA_HOST', 'OLLAMA_API_ENDPOINT', 'DEFAULT_ENHANCEMENT_MODEL',
    
    # Timeouts
    'OLLAMA_CONNECT_TIMEOUT', 'ENHANCEMENT_TIMEOUT', 'VISION_ANALYSIS_TIMEOUT',
    
    # Retry (Phase 1)
    'RETRY_ENABLED', 'RETRY_MAX_ATTEMPTS', 'RETRY_INITIAL_DELAY',
    
    # JSON (Phase 1)
    'SAFE_JSON_ENABLED', 'JSON_REQUIRED_KEYS',
    
    # Validation (Phase 1)
    'VALIDATE_PROMPT_LENGTH', 'PROMPT_MAX_LENGTH',
    
    # UI
    'WINDOW_WIDTH', 'WINDOW_HEIGHT', 'DEFAULT_LANGUAGE',
    
    # Helpers
    'get_retry_delay', 'is_valid_model', 'get_timeout_for_operation',
]
