"""
SVD Prompt Enhancer Pro v5.1 - Workers Package

Async worker threads for prompt enhancement:
- EnhancementWorker: QThread-based worker for async prompt enhancement
- EnhancementResult: Result dataclass from enhancement operation

Workers run in separate threads to keep UI responsive.
Communicate via Qt signals.

Author: SVD Prompt Enhancer Team
Date: 2026-01-09
Version: 5.1.0
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

from PyQt5.QtCore import QThread, pyqtSignal
import requests

from config import (
    RETRY_ENABLED,
    RETRY_MAX_ATTEMPTS,
    OLLAMA_HOST,
    DEFAULT_ENHANCEMENT_MODEL,
    ENHANCEMENT_TIMEOUT,
    get_retry_delay,
)
from core import SafeJSONHandler, ParseStrategy

logger = logging.getLogger(__name__)
logger.debug("Initializing workers package...")


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class EnhancementStatus(Enum):
    """Status of enhancement operation"""
    IDLE = "idle"
    CONNECTING = "connecting"
    PROCESSING = "processing"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class EnhancementResult:
    """Result of prompt enhancement operation"""
    success: bool
    prompt_en: Optional[str] = None
    prompt_pl: Optional[str] = None
    strategy_used: Optional[str] = None
    error_message: Optional[str] = None
    attempts: int = 1
    total_time: float = 0.0
    raw_response: Optional[str] = None


# ============================================================================
# ENHANCEMENT WORKER
# ============================================================================

class EnhancementWorker(QThread):
    """
    QThread-based worker for async prompt enhancement.
    
    Signals:
        status_changed: str - Status changed
        progress_updated: (str, int) - Progress message and value
        result_ready: EnhancementResult - Enhancement completed
        error_occurred: str - Error occurred
    
    Features:
        - Exponential backoff retry logic
        - Safe JSON parsing (4 strategies)
        - Timeout handling
        - Thread-safe operation
        - Cancel support
    """
    
    # Qt Signals
    status_changed = pyqtSignal(str)
    progress_updated = pyqtSignal(str, int)
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, debug: bool = False):
        """
        Initialize EnhancementWorker
        
        Args:
            debug: Enable debug logging
        """
        super().__init__()
        self.debug = debug
        self.cancelled = False
        self.current_result = None
        self.json_handler = SafeJSONHandler(debug=debug)
        logger.debug("EnhancementWorker initialized")
    
    def run(self):
        """QThread run method - executed when thread starts"""
        pass  # Implemented in enhance_direct()
    
    def cancel(self):
        """Cancel current operation"""
        self.cancelled = True
        logger.warning("Enhancement cancelled by user")
    
    def enhance_direct(
        self,
        prompt: str,
        creativity: float = 0.7,
        length: int = 350,
        details: str = "Wysoki",
        style: str = "Kinematograficzny"
    ) -> EnhancementResult:
        """
        Enhance prompt directly (blocking call)
        
        Args:
            prompt: Polish prompt to enhance
            creativity: Creativity level (0.0-1.0)
            length: Target length in words
            details: Detail level (Niski, Średni, Wysoki)
            style: Style (Kinematograficzny, Artystyczny, Techniczny)
        
        Returns:
            EnhancementResult with success status and enhanced prompts
        """
        start_time = time.time()
        
        if not prompt or not isinstance(prompt, str):
            return EnhancementResult(
                success=False,
                error_message="Invalid prompt: must be non-empty string"
            )
        
        # Build enhancement request
        enhancement_prompt = self._build_enhancement_prompt(
            prompt, creativity, length, details, style
        )
        
        # Attempt enhancement with retry logic
        for attempt in range(RETRY_MAX_ATTEMPTS):
            if self.cancelled:
                total_time = time.time() - start_time
                return EnhancementResult(
                    success=False,
                    error_message="Cancelled by user",
                    attempts=attempt + 1,
                    total_time=total_time
                )
            
            self.status_changed.emit(f"Attempt {attempt + 1}/{RETRY_MAX_ATTEMPTS}")
            self.progress_updated.emit(f"Attempt {attempt + 1}", attempt)
            
            try:
                result = self._call_ollama_api(enhancement_prompt)
                
                if result.success:
                    total_time = time.time() - start_time
                    result.attempts = attempt + 1
                    result.total_time = total_time
                    
                    self.status_changed.emit("✅ Enhancement successful")
                    logger.info(f"✅ Enhancement successful (attempt {attempt + 1})")
                    
                    return result
                
            except Exception as e:
                logger.debug(f"Attempt {attempt + 1} failed: {e}")
            
            # Wait before retry (except for last attempt)
            if attempt < RETRY_MAX_ATTEMPTS - 1:
                delay = get_retry_delay(attempt)
                self.status_changed.emit(f"Retrying in {delay:.0f}s...")
                
                # Sleep in small intervals to allow cancellation
                for _ in range(int(delay * 10)):
                    if self.cancelled:
                        total_time = time.time() - start_time
                        return EnhancementResult(
                            success=False,
                            error_message="Cancelled during retry delay",
                            attempts=attempt + 1,
                            total_time=total_time
                        )
                    time.sleep(0.1)
        
        total_time = time.time() - start_time
        return EnhancementResult(
            success=False,
            error_message=f"All {RETRY_MAX_ATTEMPTS} attempts failed",
            attempts=RETRY_MAX_ATTEMPTS,
            total_time=total_time
        )
    
    def _build_enhancement_prompt(
        self,
        prompt: str,
        creativity: float,
        length: int,
        details: str,
        style: str
    ) -> str:
        """Build the enhancement prompt for Ollama"""
        creativity_word = {
            0.0: "conservative",
            0.3: "standard",
            0.5: "creative",
            0.7: "very creative",
            1.0: "extremely creative"
        }.get(round(creativity * 2) / 2, "creative")
        
        return f"""Enhance this Polish prompt for AI image generation. 
        
Original prompt: "{prompt}"

Requirements:
- Generate BOTH Polish and English enhanced versions
- Detail level: {details}
- Style: {style}
- Target length: ~{length} words
- Creativity: {creativity_word}
- Be specific, vivid, and imaginative
- Include technical details for AI models

Format your response as JSON:
{{
    "prompt_en": "Your enhanced English prompt here",
    "prompt_pl": "Your enhanced Polish prompt here"
}}

Only respond with valid JSON, no other text."""
    
    def _call_ollama_api(self, prompt: str) -> EnhancementResult:
        """
        Call Ollama API and parse response
        
        Args:
            prompt: Enhancement prompt
        
        Returns:
            EnhancementResult with success status
        """
        try:
            # Prepare request
            headers = {"Content-Type": "application/json"}
            data = {
                "model": DEFAULT_ENHANCEMENT_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
            }
            
            # Make request
            response = requests.post(
                OLLAMA_HOST + "/api/generate",
                json=data,
                timeout=ENHANCEMENT_TIMEOUT,
                headers=headers
            )
            
            if response.status_code != 200:
                return EnhancementResult(
                    success=False,
                    error_message=f"API returned {response.status_code}: {response.text[:100]}"
                )
            
            # Parse response
            response_text = response.text
            parse_result = self.json_handler.parse(response_text)
            
            if not parse_result.success:
                return EnhancementResult(
                    success=False,
                    error_message=f"Failed to parse response: {parse_result.error_message}",
                    raw_response=response_text
                )
            
            # Extract prompts from parsed data
            parsed_data = parse_result.data or {}
            prompt_en = parsed_data.get("prompt_en") or ""
            prompt_pl = parsed_data.get("prompt_pl") or ""
            
            if not prompt_en and not prompt_pl:
                return EnhancementResult(
                    success=False,
                    error_message="API response missing prompt_en or prompt_pl",
                    raw_response=response_text
                )
            
            return EnhancementResult(
                success=True,
                prompt_en=prompt_en,
                prompt_pl=prompt_pl,
                strategy_used=parse_result.strategy_used.value if parse_result.strategy_used else "unknown",
                raw_response=response_text
            )
        
        except requests.Timeout:
            return EnhancementResult(
                success=False,
                error_message=f"API timeout (>{ENHANCEMENT_TIMEOUT}s)"
            )
        except requests.ConnectionError:
            return EnhancementResult(
                success=False,
                error_message=f"Cannot connect to Ollama at {OLLAMA_HOST}. Is it running?"
            )
        except Exception as e:
            return EnhancementResult(
                success=False,
                error_message=f"API call failed: {str(e)}"
            )


# ============================================================================
# MODULE EXPORTS
# ============================================================================

logger.debug("Workers package initialized successfully")

__version__ = "5.1.0"

__all__ = [
    'EnhancementWorker',
    'EnhancementResult',
    'EnhancementStatus',
]
