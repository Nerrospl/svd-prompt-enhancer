"""
SVD Prompt Enhancer Pro v5.1 - Core Package

Core functionality for prompt enhancement:
- SafeJSONHandler: Robust JSON parsing with 4 fallback strategies
- ParseResult: Result dataclass for JSON parsing outcomes
- ParseStrategy: Enum of parsing strategies used

This module provides the foundation for safe, resilient JSON parsing
that never crashes the application even with malformed API responses.

Author: SVD Prompt Enhancer Team
Date: 2026-01-09
Version: 5.1.0
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, List
import json
import re

logger = logging.getLogger(__name__)
logger.debug("Initializing core package...")


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class ParseStrategy(Enum):
    """Enum of JSON parsing strategies"""
    DIRECT = "direct"  # Strategy 1: Direct JSON parsing
    REGEX = "regex"  # Strategy 2: Regex-based extraction
    SPLIT = "split"  # Strategy 3: String splitting
    PARTIAL = "partial"  # Strategy 4: Partial/fallback parsing


@dataclass
class ParseResult:
    """Result of JSON parsing operation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    strategy_used: Optional[ParseStrategy] = None
    error_message: Optional[str] = None
    raw_text: Optional[str] = None
    attempts: int = 1
    total_time: float = 0.0


# ============================================================================
# SAFE JSON HANDLER
# ============================================================================

class SafeJSONHandler:
    """
    Robust JSON parser with 4 fallback strategies.
    
    Never crashes on invalid JSON. Tries 4 strategies in sequence:
    1. Direct JSON parsing (json.loads)
    2. Regex-based text extraction
    3. String splitting/parsing
    4. Partial/fallback parsing
    
    Always returns ParseResult with success status and strategy used.
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize SafeJSONHandler
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
    
    def parse(self, text: str) -> ParseResult:
        """
        Parse JSON text using up to 4 fallback strategies
        
        Args:
            text: Raw text to parse
        
        Returns:
            ParseResult with success status and parsed data
        """
        if not text or not isinstance(text, str):
            return ParseResult(
                success=False,
                error_message="Invalid input: text must be non-empty string"
            )
        
        # Strategy 1: Direct JSON parsing
        result = self._strategy_direct(text)
        if result.success:
            return result
        
        # Strategy 2: Regex-based extraction
        result = self._strategy_regex(text)
        if result.success:
            return result
        
        # Strategy 3: String splitting
        result = self._strategy_split(text)
        if result.success:
            return result
        
        # Strategy 4: Partial/fallback parsing
        result = self._strategy_partial(text)
        return result
    
    def _strategy_direct(self, text: str) -> ParseResult:
        """Strategy 1: Direct JSON parsing"""
        try:
            data = json.loads(text)
            if self.debug:
                logger.debug(f"Strategy DIRECT successful")
            return ParseResult(
                success=True,
                data=data,
                strategy_used=ParseStrategy.DIRECT,
                raw_text=text
            )
        except json.JSONDecodeError as e:
            if self.debug:
                logger.debug(f"Strategy DIRECT failed: {e}")
            return ParseResult(success=False, error_message=str(e))
    
    def _strategy_regex(self, text: str) -> ParseResult:
        """Strategy 2: Regex-based text extraction"""
        try:
            # Try to find JSON object pattern
            json_pattern = r'\{[\s\S]*\}'
            match = re.search(json_pattern, text)
            
            if not match:
                return ParseResult(success=False, error_message="No JSON-like pattern found")
            
            json_str = match.group(0)
            data = json.loads(json_str)
            
            if self.debug:
                logger.debug(f"Strategy REGEX successful")
            
            return ParseResult(
                success=True,
                data=data,
                strategy_used=ParseStrategy.REGEX,
                raw_text=text
            )
        except Exception as e:
            if self.debug:
                logger.debug(f"Strategy REGEX failed: {e}")
            return ParseResult(success=False, error_message=str(e))
    
    def _strategy_split(self, text: str) -> ParseResult:
        """Strategy 3: String splitting"""
        try:
            # Try to extract key-value pairs manually
            data = {}
            
            # Look for patterns like "key": "value" or "key": number
            pattern = r'"([^"]+)"\s*:\s*"?([^",}]+)"?'
            matches = re.findall(pattern, text)
            
            if not matches:
                return ParseResult(success=False, error_message="No key-value pairs found")
            
            for key, value in matches:
                # Try to convert to appropriate type
                if value.lower() in ['true', 'false']:
                    data[key] = value.lower() == 'true'
                elif value.replace('.', '').replace('-', '').isdigit():
                    try:
                        data[key] = float(value) if '.' in value else int(value)
                    except ValueError:
                        data[key] = value
                else:
                    data[key] = value
            
            if self.debug:
                logger.debug(f"Strategy SPLIT successful")
            
            return ParseResult(
                success=True,
                data=data,
                strategy_used=ParseStrategy.SPLIT,
                raw_text=text
            )
        except Exception as e:
            if self.debug:
                logger.debug(f"Strategy SPLIT failed: {e}")
            return ParseResult(success=False, error_message=str(e))
    
    def _strategy_partial(self, text: str) -> ParseResult:
        """Strategy 4: Partial/fallback parsing"""
        try:
            # Last resort: return whatever we can extract
            data = {
                "raw_response": text[:500],  # First 500 chars
                "length": len(text),
                "contains_json": "{" in text and "}" in text
            }
            
            if self.debug:
                logger.debug(f"Strategy PARTIAL successful (fallback)")
            
            return ParseResult(
                success=True,
                data=data,
                strategy_used=ParseStrategy.PARTIAL,
                raw_text=text
            )
        except Exception as e:
            if self.debug:
                logger.debug(f"Strategy PARTIAL failed: {e}")
            return ParseResult(
                success=False,
                error_message=f"All parsing strategies failed: {e}"
            )


# ============================================================================
# MODULE EXPORTS
# ============================================================================

logger.debug("Core package initialized successfully")

__version__ = "5.1.0"

__all__ = [
    'SafeJSONHandler',
    'ParseResult',
    'ParseStrategy',
]
