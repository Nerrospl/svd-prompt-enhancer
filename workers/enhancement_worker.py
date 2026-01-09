"""
Enhancement Worker - Asynchronous worker for prompt enhancement with retry logic

Implements QThread-based worker for enhancing prompts using Ollama API.
Features exponential backoff retry mechanism and comprehensive error handling.

Author: Phase 1 Implementation - R1.2 (Retry System)
Date: 2026-01-09
Version: 1.0
"""

import json
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from threading import Event

try:
    from PyQt5.QtCore import QThread, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Fallback for testing without PyQt5
    class QThread:
        pass
    class pyqtSignal:
        def __init__(self, *args):
            self.args = args
        def emit(self, *args):
            pass
        def connect(self, func):
            pass

import requests

# Import Phase 1 infrastructure
from config.constants import (
    OLLAMA_HOST,
    OLLAMA_API_ENDPOINT,
    DEFAULT_ENHANCEMENT_MODEL,
    ENHANCEMENT_TIMEOUT,
    RETRY_ENABLED,
    RETRY_MAX_ATTEMPTS,
    RETRY_INITIAL_DELAY,
    RETRY_BACKOFF_MULTIPLIER,
    RETRY_MAX_DELAY,
    get_retry_delay,
)
from core import SafeJSONHandler, ParseResult


# Configure logging
logger = logging.getLogger(__name__)


class EnhancementStatus(Enum):
    """Status codes for enhancement operation"""
    IDLE = "idle"
    PREPARING = "preparing"
    SENDING = "sending"
    PROCESSING = "processing"
    PARSING = "parsing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class EnhancementResult:
    """Result of enhancement operation"""
    success: bool
    prompt_en: Optional[str] = None
    prompt_pl: Optional[str] = None
    strategy_used: Optional[str] = None
    attempts: int = 0
    total_time: float = 0.0
    error_message: Optional[str] = None
    raw_response: Optional[str] = None


class EnhancementWorker(QThread if PYQT_AVAILABLE else object):
    """
    Worker thread for prompt enhancement with retry mechanism.
    
    Features:
    - Exponential backoff retry (2s, 4s, 8s, 16s, max 30s)
    - SafeJSONHandler integration for robust parsing
    - Comprehensive logging at each stage
    - Cancellation support
    
    Problem: Ollama sometimes times out or returns malformed responses
    Solution: Retry with exponential backoff + SafeJSON parsing
    """
    
    # PyQt signals (emitted to update UI)
    status_changed = pyqtSignal(str) if PYQT_AVAILABLE else lambda x: None
    progress_updated = pyqtSignal(str, int) if PYQT_AVAILABLE else lambda x, y: None
    result_ready = pyqtSignal(dict) if PYQT_AVAILABLE else lambda x: None
    error_occurred = pyqtSignal(str) if PYQT_AVAILABLE else lambda x: None
    
    def __init__(self, debug: bool = False):
        """
        Initialize EnhancementWorker
        
        Args:
            debug: Enable debug logging
        """
        if PYQT_AVAILABLE:
            super().__init__()
        
        self.debug = debug
        self.cancelled = Event()
        self.json_handler = SafeJSONHandler(debug=debug)
        
        logger.info("EnhancementWorker initialized")
    
    def run(self):
        """
        Main worker loop (called by QThread.start())
        Override this to add custom enhancement logic
        """
        logger.info("EnhancementWorker started")
    
    def enhance_direct(
        self,
        prompt: str,
        model: Optional[str] = None,
        creativity: float = 0.7,
        length: int = 350,
        details: str = "Wysoki",
        style: str = "Kinematograficzny"
    ) -> EnhancementResult:
        """
        Enhance prompt directly with retry logic (R1.2)
        
        Args:
            prompt: Input prompt to enhance
            model: Model to use (default from constants)
            creativity: Temperature (0-1)
            length: Target length in words
            details: Detail level (Niski/Średni/Wysoki)
            style: Style (Kinematograficzny/Artystyczny/Techniczny)
        
        Returns:
            EnhancementResult with enhanced prompts or error
        """
        start_time = time.time()
        model = model or DEFAULT_ENHANCEMENT_MODEL
        
        logger.info(f"Starting enhancement: prompt_len={len(prompt)}, model={model}")
        self._emit_status("PREPARING")
        
        # Build enhancement prompt
        system_prompt = self._build_system_prompt(details, style)
        enhancement_prompt = self._build_enhancement_prompt(
            prompt, creativity, length, details, style
        )
        
        logger.debug(f"System prompt length: {len(system_prompt)}")
        logger.debug(f"Enhancement prompt length: {len(enhancement_prompt)}")
        
        # Retry loop with exponential backoff (R1.2)
        last_error = None
        
        for attempt in range(RETRY_MAX_ATTEMPTS):
            if self.cancelled.is_set():
                logger.warning("Enhancement cancelled by user")
                return EnhancementResult(
                    success=False,
                    error_message="Cancelled by user",
                    attempts=attempt + 1,
                    total_time=time.time() - start_time
                )
            
            try:
                logger.info(f"Attempt {attempt + 1}/{RETRY_MAX_ATTEMPTS}")
                self._emit_progress(f"Attempt {attempt + 1}", attempt)
                self._emit_status("SENDING")
                
                # Call Ollama API
                response = self._call_ollama_api(
                    model=model,
                    prompt=enhancement_prompt,
                    system=system_prompt
                )
                
                logger.debug(f"Response received: {len(response)} chars")
                self._emit_status("PARSING")
                
                # Parse with SafeJSONHandler (R1.1)
                parse_result = self.json_handler.parse(response)
                
                if parse_result.success:
                    logger.info("✅ Enhancement SUCCESS")
                    self._emit_status("SUCCESS")
                    
                    return EnhancementResult(
                        success=True,
                        prompt_en=parse_result.data.get('prompt_en'),
                        prompt_pl=parse_result.data.get('prompt_pl'),
                        strategy_used=parse_result.strategy_used.name,
                        attempts=attempt + 1,
                        total_time=time.time() - start_time
                    )
                else:
                    logger.warning(f"Parse failed: {parse_result.error_message}")
                    last_error = f"Parse error: {parse_result.error_message}"
                    
                    # If we have fallback data and required keys, use it
                    if (parse_result.data and 
                        'prompt_en' in parse_result.data and 
                        'prompt_pl' in parse_result.data):
                        logger.warning("Using fallback data")
                        return EnhancementResult(
                            success=True,
                            prompt_en=parse_result.data.get('prompt_en'),
                            prompt_pl=parse_result.data.get('prompt_pl'),
                            strategy_used=parse_result.strategy_used.name,
                            attempts=attempt + 1,
                            total_time=time.time() - start_time
                        )
            
            except requests.Timeout:
                last_error = "Ollama timeout (exceeded 120s)"
                logger.warning(f"Timeout on attempt {attempt + 1}")
                
            except requests.ConnectionError:
                last_error = "Cannot connect to Ollama (localhost:11434)"
                logger.warning(f"Connection error on attempt {attempt + 1}")
                
            except json.JSONDecodeError as e:
                last_error = f"Invalid JSON from Ollama: {str(e)[:100]}"
                logger.warning(f"JSON error on attempt {attempt + 1}: {last_error}")
                
            except Exception as e:
                last_error = str(e)[:200]
                logger.error(f"Unexpected error on attempt {attempt + 1}: {last_error}")
            
            # Retry logic with exponential backoff (R1.2)
            if attempt < RETRY_MAX_ATTEMPTS - 1:
                delay = get_retry_delay(attempt)
                logger.warning(f"Retrying in {delay}s... (attempt {attempt + 1}/{RETRY_MAX_ATTEMPTS})")
                self._emit_progress(f"Retrying in {delay:.0f}s", attempt + 1)
                self._emit_status(f"RETRYING_{attempt + 1}")
                
                # Sleep with cancellation check
                for _ in range(int(delay * 10)):
                    if self.cancelled.is_set():
                        logger.warning("Enhancement cancelled during retry delay")
                        return EnhancementResult(
                            success=False,
                            error_message="Cancelled by user",
                            attempts=attempt + 1,
                            total_time=time.time() - start_time
                        )
                    time.sleep(0.1)
            else:
                logger.error("All retry attempts exhausted")
        
        # All attempts failed
        logger.error(f"❌ Enhancement FAILED after {RETRY_MAX_ATTEMPTS} attempts")
        self._emit_status("FAILED")
        self._emit_error(last_error)
        
        return EnhancementResult(
            success=False,
            error_message=last_error or "Unknown error",
            attempts=RETRY_MAX_ATTEMPTS,
            total_time=time.time() - start_time
        )
    
    def _call_ollama_api(
        self,
        model: str,
        prompt: str,
        system: str = ""
    ) -> str:
        """
        Call Ollama API with proper error handling
        
        Args:
            model: Model name
            prompt: Prompt text
            system: System prompt
        
        Returns:
            Response text from Ollama
        
        Raises:
            requests.Timeout: If request times out
            requests.ConnectionError: If cannot connect to Ollama
            Exception: Other errors
        """
        url = f"{OLLAMA_API_ENDPOINT}/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,  # Non-streaming for simplicity
            "temperature": 0.7,
        }
        
        logger.debug(f"Calling Ollama: {url}")
        logger.debug(f"Model: {model}, Prompt len: {len(prompt)}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=ENHANCEMENT_TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"Ollama response status: {response.status_code}")
            
            return response_data.get('response', '')
        
        except requests.Timeout:
            logger.error(f"Ollama timeout after {ENHANCEMENT_TIMEOUT}s")
            raise
        except requests.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama at {OLLAMA_HOST}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise
    
    def _build_system_prompt(self, details: str, style: str) -> str:
        """Build system prompt based on detail level and style"""
        
        system_prompts = {
            "Niski": "You are a helpful assistant that enhances prompts briefly.",
            "Średni": "You are an expert at enhancing prompts with visual details and artistic elements.",
            "Wysoki": "You are a master prompt engineer specializing in creating detailed, vivid descriptions for image generation. Include specific colors, lighting, composition, and emotional tone.",
        }
        
        style_additions = {
            "Kinematograficzny": "Focus on cinematic framing, lighting setup, camera angles, and composition.",
            "Artystyczny": "Focus on artistic style, color palette, artistic techniques, and visual aesthetics.",
            "Techniczny": "Focus on technical details like resolution, bit depth, specific rendering techniques.",
        }
        
        base = system_prompts.get(details, system_prompts["Wysoki"])
        addition = style_additions.get(style, style_additions["Kinematograficzny"])
        
        return f"{base} {addition}"
    
    def _build_enhancement_prompt(
        self,
        prompt: str,
        creativity: float,
        length: int,
        details: str,
        style: str
    ) -> str:
        """Build enhancement prompt with user specifications"""
        
        return f"""Enhance this prompt for an image generation AI:

Original prompt: "{prompt}"

Requirements:
- Generate BOTH an English version (prompt_en) and Polish version (prompt_pl)
- Target length: around {length} words
- Detail level: {details}
- Style focus: {style}
- Creativity level: {creativity:.1f} (0=conservative, 1=creative)

IMPORTANT: You MUST respond with ONLY valid JSON in this exact format, no other text:
{{
    "prompt_en": "enhanced English prompt here...",
    "prompt_pl": "enhanced Polish prompt here...",
    "word_count": number
}}

Do not include any text before or after the JSON. Only JSON."""
    
    def _emit_status(self, status: str):
        """Emit status changed signal"""
        if PYQT_AVAILABLE:
            self.status_changed.emit(status)
        logger.debug(f"Status: {status}")
    
    def _emit_progress(self, message: str, value: int):
        """Emit progress updated signal"""
        if PYQT_AVAILABLE:
            self.progress_updated.emit(message, value)
        logger.debug(f"Progress: {message} ({value}%)")
    
    def _emit_error(self, error: str):
        """Emit error occurred signal"""
        if PYQT_AVAILABLE:
            self.error_occurred.emit(error)
        logger.error(f"Error: {error}")
    
    def cancel(self):
        """Cancel current enhancement operation"""
        logger.warning("Enhancement cancellation requested")
        self.cancelled.set()


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestEnhancementWorker:
    """Unit tests for EnhancementWorker"""
    
    @staticmethod
    def test_worker_initialization():
        """Test 1: Worker initializes correctly"""
        worker = EnhancementWorker(debug=True)
        
        assert worker is not None
        assert worker.json_handler is not None
        assert RETRY_ENABLED is True
        assert RETRY_MAX_ATTEMPTS == 3
        
        print("✅ Test 1 PASSED: Worker initialization")
        return True
    
    @staticmethod
    def test_system_prompt_building():
        """Test 2: System prompts are built correctly"""
        worker = EnhancementWorker(debug=True)
        
        # Test Wysoki detail
        prompt = worker._build_system_prompt("Wysoki", "Kinematograficzny")
        assert "master prompt engineer" in prompt
        assert "cinematic" in prompt
        
        # Test Niski detail
        prompt = worker._build_system_prompt("Niski", "Artystyczny")
        assert "briefly" in prompt
        assert "artistic" in prompt
        
        print("✅ Test 2 PASSED: System prompt building")
        return True
    
    @staticmethod
    def test_enhancement_prompt_building():
        """Test 3: Enhancement prompts are properly formatted"""
        worker = EnhancementWorker(debug=True)
        
        prompt = worker._build_enhancement_prompt(
            prompt="beautiful woman",
            creativity=0.7,
            length=350,
            details="Wysoki",
            style="Kinematograficzny"
        )
        
        assert "prompt_en" in prompt
        assert "prompt_pl" in prompt
        assert "350" in prompt
        assert "JSON" in prompt
        assert "beautiful woman" in prompt
        
        print("✅ Test 3 PASSED: Enhancement prompt building")
        return True
    
    @staticmethod
    def test_retry_delay_calculation():
        """Test 4: Retry delays are calculated correctly"""
        
        # Test exponential backoff
        assert get_retry_delay(0) == 2.0
        assert get_retry_delay(1) == 4.0
        assert get_retry_delay(2) == 8.0
        assert get_retry_delay(3) == 16.0
        
        # Test capping at max delay
        assert get_retry_delay(10) == 30.0  # Capped
        
        print("✅ Test 4 PASSED: Retry delay calculation")
        return True
    
    @staticmethod
    def test_enhancement_result_dataclass():
        """Test 5: EnhancementResult dataclass works"""
        
        result = EnhancementResult(
            success=True,
            prompt_en="test",
            prompt_pl="test",
            attempts=1,
            total_time=1.5
        )
        
        assert result.success is True
        assert result.prompt_en == "test"
        assert result.attempts == 1
        assert result.total_time == 1.5
        
        # Test failed result
        failed = EnhancementResult(
            success=False,
            error_message="Test error"
        )
        
        assert failed.success is False
        assert failed.error_message == "Test error"
        
        print("✅ Test 5 PASSED: EnhancementResult dataclass")
        return True
    
    @staticmethod
    def run_all_tests():
        """Run all unit tests"""
        print("\n" + "="*70)
        print("RUNNING UNIT TESTS FOR EnhancementWorker")
        print("="*70)
        
        try:
            TestEnhancementWorker.test_worker_initialization()
            TestEnhancementWorker.test_system_prompt_building()
            TestEnhancementWorker.test_enhancement_prompt_building()
            TestEnhancementWorker.test_retry_delay_calculation()
            TestEnhancementWorker.test_enhancement_result_dataclass()
            
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
    success = TestEnhancementWorker.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)
