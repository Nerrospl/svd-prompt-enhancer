"""
utils/regex_utils.py
Regex utilities dla wyciągania JSON
"""

import re
import json
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def extract_json_from_response(response: str) -> Dict:
    """
    Wyciągnij JSON z outputu modelu LLM
    
    Próbuje różne strategie w kolejności:
    1. Dokładny JSON (prompt_en + prompt_pl)
    2. Słabszy regex
    3. Fallback raw response
    """
    
    patterns = [
        # Dokładny JSON
        r'\{[^{}]*"prompt_en"[^{}]*"prompt_pl"[^{}]*\}',
        r'\{[^{}]*"prompt_pl"[^{}]*"prompt_en"[^{}]*\}',
        # Słabszy
        r'\{.*?"prompt_en".*?"prompt_pl".*?\}',
        r'\{.*?"prompt_pl".*?"prompt_en".*?\}',
        # Desperacja
        r'\{.*\}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if "prompt_en" in data and "prompt_pl" in data:
                    logger.debug(f"✅ JSON extracted with pattern: {pattern[:30]}...")
                    return data
            except json.JSONDecodeError:
                continue
    
    # Fallback
    logger.warning("⚠️ Using fallback raw response")
    return {
        "prompt_en": response[:500],
        "prompt_pl": response[:500],
        "_status": "fallback_raw_response"
    }