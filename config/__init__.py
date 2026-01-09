"""
Core module for SVD Prompt Enhancer Pro v5.0

Contains business logic for prompt enhancement and JSON handling.

Modules:
    - safe_json_handler: Safely parse JSON with fallback strategies
    - prompt_enhancer: Enhance prompts using LLM
    - validation: Validate enhanced prompts
"""

from .safe_json_handler import (
    SafeJSONHandler,
    ParseResult,
    JSONExtractionStrategy,
    TestSafeJSONHandler
)

__all__ = [
    'SafeJSONHandler',
    'ParseResult',
    'JSONExtractionStrategy',
    'TestSafeJSONHandler'
]

__version__ = '1.0.0'
__author__ = 'SVD Prompt Enhancer Team'
