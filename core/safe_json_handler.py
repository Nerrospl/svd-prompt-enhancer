"""
SafeJSONHandler - Safely extract and parse JSON from LLM responses
Handles malformed JSON with 3 fallback strategies

Author: Phase 1 Implementation
Date: 2026-01-09
Version: 1.0
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# Configure logging
logger = logging.getLogger(__name__)


class JSONExtractionStrategy(Enum):
    """Strategies for JSON extraction in order of preference"""
    DIRECT_PARSE = 1
    REGEX_EXTRACTION = 2
    PARTIAL_PARSE = 3
    FALLBACK = 4


@dataclass
class ParseResult:
    """Result of JSON parsing attempt"""
    success: bool
    data: Optional[Dict[str, Any]]
    strategy_used: JSONExtractionStrategy
    error_message: Optional[str] = None
    raw_response: Optional[str] = None


class SafeJSONHandler:
    """
    Safely extract and parse JSON from LLM responses with multiple fallback strategies.
    
    Problem: Ollama sometimes returns malformed JSON, causing crashes.
    Solution: Try 3 strategies before giving up.
    
    Strategy 1: Direct json.loads() - Fast, works 90% of time
    Strategy 2: Regex extraction - Finds {...} pattern, handles text before/after JSON
    Strategy 3: Partial parsing - Extracts valid parts, reconstructs JSON
    Strategy 4: Fallback - Returns error dict with user message
    """
    
    # Required keys in valid response
    REQUIRED_KEYS = {'prompt_en', 'prompt_pl'}
    
    # JSON pattern for regex extraction
    JSON_PATTERN = re.compile(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', re.DOTALL)
    
    # Patterns to find key-value pairs
    KEY_VALUE_PATTERN = re.compile(r'"(\w+)"\s*:\s*"([^"]*)"', re.DOTALL)
    
    def __init__(self, debug: bool = False):
        """
        Initialize SafeJSONHandler
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self.strategy_stats = {
            'direct': 0,
            'regex': 0,
            'partial': 0,
            'fallback': 0,
            'total_attempts': 0
        }
        logger.info("SafeJSONHandler initialized (debug=%s)", debug)
    
    def parse(self, response: str, context: Optional[str] = None) -> ParseResult:
        """
        Parse JSON response with fallback strategies
        
        Args:
            response: Raw response from LLM
            context: Optional context for error messages
        
        Returns:
            ParseResult object with data and metadata
        """
        self.strategy_stats['total_attempts'] += 1
        
        if not response or not isinstance(response, str):
            logger.error("Invalid response: not a string or empty")
            return self._fallback_result(
                response,
                f"Invalid response type: {type(response)}"
            )
        
        logger.debug(f"Response length: {len(response)} chars, first 100: {response[:100]}")
        
        # Strategy 1: Direct parse
        result = self._strategy_direct_parse(response)
        if result.success:
            logger.info("✅ Strategy 1 (direct parse) SUCCESS")
            self.strategy_stats['direct'] += 1
            return result
        
        # Strategy 2: Regex extraction
        result = self._strategy_regex_extraction(response)
        if result.success:
            logger.info("✅ Strategy 2 (regex extraction) SUCCESS")
            self.strategy_stats['regex'] += 1
            return result
        
        # Strategy 3: Partial parsing
        result = self._strategy_partial_parse(response)
        if result.success:
            logger.info("✅ Strategy 3 (partial parse) SUCCESS")
            self.strategy_stats['partial'] += 1
            return result
        
        # Strategy 4: Fallback
        logger.warning("All strategies failed, using fallback")
        self.strategy_stats['fallback'] += 1
        return self._fallback_result(response, "All parsing strategies failed")
    
    def _strategy_direct_parse(self, response: str) -> ParseResult:
        """
        Strategy 1: Try direct json.loads()
        Works 90% of time when JSON is valid
        """
        logger.debug("Strategy 1: Attempting direct json.loads()")
        
        try:
            data = json.loads(response)
            
            # Validate required keys
            if self._validate_json(data):
                logger.debug("Strategy 1: Validation passed")
                return ParseResult(
                    success=True,
                    data=data,
                    strategy_used=JSONExtractionStrategy.DIRECT_PARSE,
                    raw_response=response
                )
            else:
                logger.debug("Strategy 1: Missing required keys")
                return ParseResult(
                    success=False,
                    data=None,
                    strategy_used=JSONExtractionStrategy.DIRECT_PARSE,
                    error_message="Missing required keys",
                    raw_response=response
                )
        except json.JSONDecodeError as e:
            logger.debug(f"Strategy 1 failed: {str(e)[:100]}")
            return ParseResult(
                success=False,
                data=None,
                strategy_used=JSONExtractionStrategy.DIRECT_PARSE,
                error_message=str(e),
                raw_response=response
            )
    
    def _strategy_regex_extraction(self, response: str) -> ParseResult:
        """
        Strategy 2: Find {...} pattern and extract JSON
        Handles cases where text appears before/after JSON
        """
        logger.debug("Strategy 2: Attempting regex extraction")
        
        try:
            matches = self.JSON_PATTERN.findall(response)
            
            if not matches:
                logger.debug("Strategy 2: No JSON pattern found")
                return ParseResult(
                    success=False,
                    data=None,
                    strategy_used=JSONExtractionStrategy.REGEX_EXTRACTION,
                    error_message="No JSON pattern found",
                    raw_response=response
                )
            
            # Try each match
            for idx, match in enumerate(matches):
                logger.debug(f"Strategy 2: Trying match {idx+1}/{len(matches)}")
                
                try:
                    data = json.loads(match)
                    
                    if self._validate_json(data):
                        logger.debug(f"Strategy 2: Match {idx+1} validation passed")
                        return ParseResult(
                            success=True,
                            data=data,
                            strategy_used=JSONExtractionStrategy.REGEX_EXTRACTION,
                            raw_response=response
                        )
                except json.JSONDecodeError:
                    logger.debug(f"Strategy 2: Match {idx+1} failed parsing")
                    continue
            
            logger.debug("Strategy 2: All matches failed validation")
            return ParseResult(
                success=False,
                data=None,
                strategy_used=JSONExtractionStrategy.REGEX_EXTRACTION,
                error_message="No valid JSON found in matches",
                raw_response=response
            )
        
        except Exception as e:
            logger.debug(f"Strategy 2 exception: {str(e)[:100]}")
            return ParseResult(
                success=False,
                data=None,
                strategy_used=JSONExtractionStrategy.REGEX_EXTRACTION,
                error_message=str(e),
                raw_response=response
            )
    
    def _strategy_partial_parse(self, response: str) -> ParseResult:
        """
        Strategy 3: Extract key-value pairs and reconstruct JSON
        Works when JSON structure is mostly broken but contains required fields
        """
        logger.debug("Strategy 3: Attempting partial parse")
        
        try:
            matches = self.KEY_VALUE_PATTERN.findall(response)
            
            if not matches:
                logger.debug("Strategy 3: No key-value pairs found")
                return ParseResult(
                    success=False,
                    data=None,
                    strategy_used=JSONExtractionStrategy.PARTIAL_PARSE,
                    error_message="No key-value pairs found",
                    raw_response=response
                )
            
            # Build dict from matches
            reconstructed = {}
            for key, value in matches:
                reconstructed[key] = value
                logger.debug(f"Strategy 3: Extracted {key}='{value[:30]}...'")
            
            # Validate
            if self._validate_json(reconstructed):
                logger.debug("Strategy 3: Reconstructed dict validation passed")
                return ParseResult(
                    success=True,
                    data=reconstructed,
                    strategy_used=JSONExtractionStrategy.PARTIAL_PARSE,
                    raw_response=response
                )
            else:
                logger.debug("Strategy 3: Missing required keys in reconstructed dict")
                return ParseResult(
                    success=False,
                    data=None,
                    strategy_used=JSONExtractionStrategy.PARTIAL_PARSE,
                    error_message="Missing required keys",
                    raw_response=response
                )
        
        except Exception as e:
            logger.debug(f"Strategy 3 exception: {str(e)[:100]}")
            return ParseResult(
                success=False,
                data=None,
                strategy_used=JSONExtractionStrategy.PARTIAL_PARSE,
                error_message=str(e),
                raw_response=response
            )
    
    def _validate_json(self, data: Any) -> bool:
        """
        Validate that parsed JSON contains required keys
        
        Args:
            data: Parsed data to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            logger.debug(f"Validation: Not a dict, type={type(data)}")
            return False
        
        missing_keys = self.REQUIRED_KEYS - set(data.keys())
        
        if missing_keys:
            logger.debug(f"Validation: Missing keys: {missing_keys}")
            return False
        
        # Check that values are strings and non-empty
        for key in self.REQUIRED_KEYS:
            value = data.get(key)
            if not isinstance(value, str) or len(value.strip()) == 0:
                logger.debug(f"Validation: Key '{key}' is empty or not string")
                return False
        
        logger.debug("Validation: PASSED")
        return True
    
    def _fallback_result(self, response: str, error: str) -> ParseResult:
        """
        Strategy 4: Return fallback result when all else fails
        
        Args:
            response: Original response
            error: Error message
        
        Returns:
            ParseResult with error dict
        """
        fallback_data = {
            "prompt_en": "Error parsing response. Please try again.",
            "prompt_pl": "Błąd parsowania odpowiedzi. Spróbuj ponownie.",
            "error": error,
            "raw_response_length": len(response)
        }
        
        logger.warning(f"Fallback: {error}")
        
        return ParseResult(
            success=False,
            data=fallback_data,
            strategy_used=JSONExtractionStrategy.FALLBACK,
            error_message=error,
            raw_response=response
        )
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about parsing attempts
        
        Returns:
            Dict with strategy usage counts
        """
        return self.strategy_stats.copy()
    
    def reset_stats(self):
        """Reset strategy statistics"""
        for key in self.strategy_stats:
            self.strategy_stats[key] = 0
        logger.info("Statistics reset")


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestSafeJSONHandler:
    """Unit tests for SafeJSONHandler"""
    
    @staticmethod
    def test_valid_json():
        """Test 1: Valid JSON should parse directly"""
        handler = SafeJSONHandler(debug=True)
        
        valid_json = '{"prompt_en": "a beautiful woman", "prompt_pl": "piękna kobieta"}'
        result = handler.parse(valid_json)
        
        assert result.success, "Valid JSON should parse successfully"
        assert result.strategy_used == JSONExtractionStrategy.DIRECT_PARSE
        assert result.data['prompt_en'] == "a beautiful woman"
        print("✅ Test 1 PASSED: Valid JSON")
        return True
    
    @staticmethod
    def test_json_with_surrounding_text():
        """Test 2: JSON with text before/after should use regex extraction"""
        handler = SafeJSONHandler(debug=True)
        
        response = 'Here is the result:\n{"prompt_en": "a woman", "prompt_pl": "kobieta"}\n\nDone!'
        result = handler.parse(response)
        
        assert result.success, "JSON with surrounding text should parse with regex"
        assert result.strategy_used == JSONExtractionStrategy.REGEX_EXTRACTION
        assert result.data['prompt_en'] == "a woman"
        print("✅ Test 2 PASSED: JSON with surrounding text")
        return True
    
    @staticmethod
    def test_malformed_json():
        """Test 3: Malformed JSON should fallback gracefully"""
        handler = SafeJSONHandler(debug=True)
        
        malformed = '{"prompt_en": "a woman without closing quote, "prompt_pl": "kobieta"}'
        result = handler.parse(malformed)
        
        # Should not crash, should return fallback
        assert 'prompt_en' in result.data
        assert 'prompt_pl' in result.data
        print("✅ Test 3 PASSED: Malformed JSON fallback")
        return True
    
    @staticmethod
    def run_all_tests():
        """Run all unit tests"""
        print("\n" + "="*70)
        print("RUNNING UNIT TESTS FOR SafeJSONHandler")
        print("="*70)
        
        try:
            TestSafeJSONHandler.test_valid_json()
            TestSafeJSONHandler.test_json_with_surrounding_text()
            TestSafeJSONHandler.test_malformed_json()
            
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED")
            print("="*70 + "\n")
            return True
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {str(e)}\n")
            return False
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {str(e)}\n")
            return False


# ============================================================================
# MAIN - Run tests if executed directly
# ============================================================================

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
    )
    
    # Run tests
    success = TestSafeJSONHandler.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)
