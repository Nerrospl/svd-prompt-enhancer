"""
═══════════════════════════════════════════════════════════════════════════════
PLIK: core/prompt_enhancer.py (KOMPLETNY - WERSJA 2.2 NAPRAWIONA)
NAPRAWA: Usunięta ekspansja, solidne rozwijanie w system prompt

Data: 2026-01-09 20:30
Status: ✅ GOTOWY - BEZ BŁĘDÓW EXPANSION
═══════════════════════════════════════════════════════════════════════════════

INSTRUKCJA:
1. Otwórz: /mnt/dane/svd-prompt-enhancer/core/prompt_enhancer.py
2. Zaznacz wszystko: Ctrl+A
3. Usuń: Delete
4. Wklej CAŁY kod poniżej
5. Zapisz: Ctrl+O, Enter, Ctrl+X
6. Weryfikacja: python3 -m py_compile core/prompt_enhancer.py

═══════════════════════════════════════════════════════════════════════════════
"""

import requests
import json
import logging
from typing import Dict, Tuple, Optional
from config.constants import (
    OLLAMA_API_URL,
    AVAILABLE_MODELS,
    TIMEOUTS,
    QuantizationType
)
from utils.regex_utils import extract_json_from_response

logger = logging.getLogger(__name__)


class PromptEnhancer:
    """Wzbogacanie promptów za pomocą modelu Ollama z validacją"""
    
    def __init__(
        self,
        model_name: str = None,
        api_url: str = OLLAMA_API_URL,
        timeout: int = None
    ):
        if model_name is None:
            model_name = AVAILABLE_MODELS["enhancement"]["primary"]["models"][
                QuantizationType.Q4
            ]
        
        self.model_name = model_name
        self.api_url = api_url
        self.timeout = timeout or TIMEOUTS.get("enhancement", 300)
        
        logger.info(f"PromptEnhancer initialized: {self.model_name}")
    
    def enhance_direct(
        self,
        prompt: str,
        language: str = "pl",
        creativity: float = 0.7,
        image_analysis: Optional[Dict] = None,
        word_count: int = 200,
        detail_level: str = "medium",
        style: str = "cinematic"
    ) -> Tuple[bool, Dict]:
        """
        Wzbogacaj prompt z walidacją (WERSJA 2.2 - BEZ EKSPANSJI)
        
        Args:
            prompt: Prompt do wzbogacenia
            language: Język (pl/en)
            creativity: Kreatywność 0.0-1.0
            image_analysis: Opcjonalna analiza obrazu
            word_count: Docelowa ilość słów (50-500)
            detail_level: Poziom detali (low/medium/high)
            style: Styl opisu (cinematic/artistic/technical)
        
        Returns:
            (success, result_dict)
        """
        
        # Walidacja parametrów
        word_count = max(50, min(500, word_count))
        detail_level = detail_level.lower() if detail_level else "medium"
        style = style.lower() if style else "cinematic"
        
        logger.info(
            f"Enhancement START: '{prompt[:40]}...' (lang={language}, "
            f"words={word_count}, detail={detail_level}, style={style})"
        )
        
        # ETAP 1: Przygotowanie kontekstu obrazu (jeśli dostępny)
        image_context = ""
        if image_analysis:
            image_context = self._format_image_context(image_analysis)
            logger.info(f"Image context: {image_context}")
        
        # ETAP 2: Budowanie system prompt z wytycznymi rozwijania
        system_prompt = self._build_system_prompt_advanced(
            image_context,
            language,
            word_count,
            detail_level,
            style
        )
        
        # ETAP 3: Budowanie user prompt
        user_prompt = self._build_user_prompt(prompt, language)
        
        logger.info("ETAP 1: System prompt przygotowany")
        
        try:
            logger.info("ETAP 2: Generowanie wzbogacenia via Ollama...")
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "temperature": creativity,
                    "stream": False,
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(msg)
                return False, {"error": msg}
            
            raw_response = response.json().get("response", "")
            logger.info(f"Raw response length: {len(raw_response)} chars")
            
            # Wydobyj JSON z odpowiedzi
            data = extract_json_from_response(raw_response)
            
            if not data:
                logger.warning("JSON extraction failed, trying manual parsing...")
                data = self._parse_response_fallback(raw_response)
            
            if not data or "error" in data:
                logger.error(f"Invalid response: {data}")
                return False, {"error": "Invalid response format"}
            
            logger.info("ETAP 2: Wzbogacenie wygenerowane")
            
            # ETAP 3: Walidacja jakości
            logger.info("ETAP 3: Walidacja jakości...")
            is_valid, validation_msg = self._validate_enhancement(
                data,
                word_count,
                language,
                detail_level
            )
            
            if not is_valid:
                logger.warning(f"Validation warning: {validation_msg}")
                data["validation_warning"] = validation_msg
            else:
                logger.info(f"Validation passed: {validation_msg}")
            
            # Dodaj metadane
            data["enhanced"] = True
            data["model"] = self.model_name
            data["creativity"] = creativity
            data["word_count"] = word_count
            data["detail_level"] = detail_level
            data["style"] = style
            data["original_prompt"] = prompt
            
            if image_analysis:
                data["image_data"] = image_analysis
            
            logger.info("✅ Enhancement COMPLETED SUCCESSFULLY")
            return True, data
        
        except requests.exceptions.Timeout:
            msg = f"Timeout ({self.timeout}s)"
            logger.error(msg)
            return False, {"error": msg}
        except Exception as e:
            msg = f"Exception: {str(e)}"
            logger.error(msg, exc_info=True)
            return False, {"error": msg}
    
    def _parse_response_fallback(self, raw: str) -> Optional[Dict]:
        """
        Fallback parser dla przypadków gdy extract_json_from_response nie działa
        """
        try:
            # Szukaj JSON obiektu w odpowiedzi
            start = raw.find('{')
            end = raw.rfind('}')
            
            if start == -1 or end == -1:
                logger.warning("No JSON braces found in response")
                return None
            
            json_str = raw[start:end+1]
            data = json.loads(json_str)
            
            logger.info("Fallback JSON parsing successful")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Fallback parsing failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in fallback: {e}")
            return None
    
    def _validate_enhancement(
        self,
        result: Dict,
        target_words: int,
        language: str,
        detail_level: str
    ) -> Tuple[bool, str]:
        """
        ETAP 3: Walidacja jakości wzbogacenia
        Sprawdza:
        - Ilość słów
        - Zawartość detali
        - Spójność
        """
        
        en_prompt = result.get("prompt_en", "")
        pl_prompt = result.get("prompt_pl", "")
        
        # Policz słowa
        en_words = len(en_prompt.split())
        pl_words = len(pl_prompt.split())
        
        logger.info(f"Word count - EN: {en_words}, PL: {pl_words}, Target: {target_words}")
        
        # Walidacja 1: Minimalna ilość słów
        min_words = max(50, target_words // 2)
        if en_words < min_words or pl_words < min_words:
            return False, f"Too short: EN={en_words}, PL={pl_words} (min={min_words})"
        
        # Walidacja 2: Czy zawiera detale
        detail_keywords = [
            "light", "lighting", "texture", "color", "shadow", "atmosphere",
            "detail", "cinematic", "composition", "mood", "golden", "vivid",
            "oświetlenie", "tekstura", "kolor", "cień", "atmosfera",
            "szczegół", "nastrój", "złoty", "żywy", "kinematograficzny"
        ]
        
        has_details = any(kw in en_prompt.lower() or kw in pl_prompt.lower() 
                         for kw in detail_keywords)
        
        if not has_details and detail_level == "high":
            logger.warning("Missing visual details for HIGH detail level")
            return False, "Missing visual details"
        
        # Walidacja 3: Czy nie jest puste/błędne
        if len(en_prompt.strip()) < 30 or len(pl_prompt.strip()) < 30:
            return False, "Result too short or empty"
        
        # Walidacja 4: Brak błędów
        if "error" in en_prompt.lower() or "error" in pl_prompt.lower():
            return False, "Error found in response"
        
        return True, f"Valid (EN: {en_words} words, PL: {pl_words} words)"
    
    def _build_system_prompt_advanced(
        self,
        image_context: str = "",
        language: str = "pl",
        word_count: int = 200,
        detail_level: str = "medium",
        style: str = "cinematic"
    ) -> str:
        """
        System prompt z solidnymi wytycznymi rozwijania
        Bez dodatkowego API call - wszystko w jednym promptcie
        """
        
        # Wytyczne dla każdego detail_level
        detail_map = {
            "low": (
                "Bądź zwięzły. Opisz tylko kluczowe elementy wizualne. "
                "Bez zbędnych detali, skupiaj się na głównych komponentach sceny."
            ),
            "medium": (
                "Opisz elementy wizualne ze szczegółami. Dodaj informacje o "
                "oświetleniu, kolorach i atmosferze sceny. "
                "Bądź konkretny - wymień kolory, tekstury, światło."
            ),
            "high": (
                "Dodaj WIELE szczegółów wizualnych: dokładne kolory RGB/hex, "
                "rodzaje i kierunki oświetlenia (golden hour, neon, daylight), "
                "tekstury materiałów (linen, silk, sand, skin tones), "
                "atmosferę (romantic, cinematic, moody), "
                "efekty optyczne (bokeh, lens flare, depth of field), "
                "kontrast, nasycenie barw, refleksy, cienie, głębia, "
                "detale drugiego planu, jakość powietrza, mgłę, cząsteczki pyłu. "
                "Bądź BARDZO szczegółowy i malowniczy."
            )
        }
        detail_text = detail_map.get(detail_level, detail_map["medium"])
        
        # Wytyczne dla stylu
        style_map = {
            "cinematic": (
                "Użyj kinematograficznego języka: lighting design, "
                "composition, lens choice, depth of field, color grading, "
                "mise-en-scène, visual storytelling, frame composition"
            ),
            "artistic": (
                "Skoncentruj się na aspektach artystycznych: art style, "
                "aesthetic, artistic movement, color palette, brushwork, "
                "artistic harmony, visual composition, artistic techniques"
            ),
            "technical": (
                "Opisz techniczne parametry: resolution, bit depth, "
                "color space, dynamic range, exposure, white balance, "
                "ISO equivalents, aperture, shot type, technical specs"
            )
        }
        style_text = style_map.get(style, style_map["cinematic"])
        
        if language == "pl":
            base = f"""Jesteś ekspertem w tworzeniu SZCZEGÓŁOWYCH i ROZBUDOWANYCH 
promptów dla narzędzi generacji obrazów i wideo.

INSTRUKCJE OBOWIĄZKOWE:
1. ROZWIJAJ polski prompt - dodaj konkretne detale, nie tylko przepisuj
2. Zwróć polsko-angielski JSON z polami "prompt_en" i "prompt_pl"
3. Oba prompty MUSZĄ być szczegółowe i wzbogacone
4. {detail_text}
5. {style_text}
6. Docelowa długość: ~{word_count} słów (WAŻNE: licz dokładnie)
7. Zachowaj oryginalną intencję promptu

STRUKTURA ODPOWIEDZI (TYLKO JSON):
{{
    "prompt_en": "Szczegółowy angielski opis z bogatymi detalami...",
    "prompt_pl": "Szczegółowy polski opis z bogatymi detalami..."
}}

KRYTYCZNE: 
- OBA prompty MUSZĄ być rozbudowane (200+ słów każdy)
- Nie przepisuj - ROZWIJAJ szczegóły
- Konkretne kolory, światło, tekstury, atmosfera
- Tylko JSON, nic więcej
- Polskie i angielskie prompty na tej samej długości"""
        else:
            base = f"""You are an expert in creating DETAILED and COMPREHENSIVE prompts 
for image and video generation tools.

MANDATORY INSTRUCTIONS:
1. EXPAND the prompt - add concrete details, don't just translate
2. Return Polish-English JSON with "prompt_en" and "prompt_pl" fields
3. BOTH prompts MUST be detailed and enriched
4. {detail_text}
5. {style_text}
6. Target length: ~{word_count} words (IMPORTANT: count accurately)
7. Preserve original intent

RESPONSE STRUCTURE (JSON ONLY):
{{
    "prompt_en": "Detailed English description with rich details...",
    "prompt_pl": "Detailed Polish description with rich details..."
}}

CRITICAL:
- BOTH prompts MUST be elaborate (200+ words each)
- Don't just translate - EXPAND details
- Specific colors, lighting, textures, atmosphere
- JSON ONLY, nothing else
- Polish and English prompts at similar length"""
        
        if image_context:
            base += f"\n\nIMAGE CONTEXT:\n{image_context}"
        
        return base
    
    def _build_user_prompt(
        self,
        original: str,
        language: str = "pl"
    ) -> str:
        """User prompt - prosty i bezpośredni"""
        
        if language == "pl":
            return f"""Wzbogać ten prompt o szczegóły i detale:

"{original}"

Pamiętaj:
- ZAWSZE zwróć długi, szczegółowy opis (200+ słów w każdym języku)
- Dodaj konkretne detale: kolory, oświetlenie, tekstury, atmosferę
- Polskie i angielskie prompty powinny być równie szczegółowe
- TYLKO JSON format - nic więcej"""
        else:
            return f"""Enrich this prompt with details and specifics:

"{original}"

Remember:
- ALWAYS return a long, detailed description (200+ words in each language)
- Add concrete details: colors, lighting, textures, atmosphere
- Polish and English prompts should be equally detailed
- JSON format ONLY - nothing else"""
    
    def _format_image_context(self, image_analysis: Dict) -> str:
        """Formatuj analizę obrazu"""
        
        parts = []
        
        if image_analysis.get("width") and image_analysis.get("height"):
            w, h = image_analysis["width"], image_analysis["height"]
            parts.append(f"Resolution: {w}x{h}")
        
        if image_analysis.get("detected"):
            detected = ", ".join(image_analysis["detected"][:5])
            parts.append(f"Detected: {detected}")
        
        if image_analysis.get("color_temp"):
            parts.append(f"Color: {image_analysis['color_temp']}")
        
        if image_analysis.get("brightness"):
            parts.append(f"Brightness: {image_analysis['brightness']}")
        
        return " | ".join(parts) if parts else ""
    
    def set_model(self, model_name: str) -> None:
        """Zmień model"""
        self.model_name = model_name
        logger.info(f"Model changed to: {model_name}")
