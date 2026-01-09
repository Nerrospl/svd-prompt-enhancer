"""
═══════════════════════════════════════════════════════════════════════════════
PLIK 1: core/prompt_enhancer.py (KOMPLETNY - ZASTĄP CAŁY PLIK)
WERSJA: 2.1 – Z MULTI-STAGE VALIDATION I POLSKIM ROZWIJANIEM

Data: 2026-01-08
Status: ✅ GOTOWY DO WKLEJENIA
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
        Wzbogacaj prompt z multi-stage validacją
        
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
        
        # ETAP 1: Ekspansja promptu (rozwijanie szczegółów)
        expanded_prompt = self._expand_prompt(prompt, language, detail_level)
        if not expanded_prompt:
            logger.error("Prompt expansion failed")
            return False, {"error": "Prompt expansion failed"}
        
        logger.info(f"STAGE 1 DONE: Prompt expanded")
        
        # ETAP 2: Wzbogacanie z kontekstem obrazu
        image_context = ""
        if image_analysis:
            image_context = self._format_image_context(image_analysis)
        
        system_prompt = self._build_system_prompt_advanced(
            image_context,
            language,
            word_count,
            detail_level,
            style
        )
        
        user_prompt = self._build_user_prompt_with_expansion(
            prompt,
            expanded_prompt,
            language
        )
        
        try:
            logger.info("STAGE 2: Generating enhanced prompt via Ollama...")
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
            data = extract_json_from_response(raw_response)
            
            if not data or "error" in data:
                logger.error(f"Invalid response: {data}")
                return False, {"error": "Invalid JSON response"}
            
            logger.info("STAGE 3: Validating enhanced prompt...")
            
            # ETAP 3: Walidacja jakości
            is_valid, validation_msg = self._validate_enhancement(
                data,
                word_count,
                language,
                detail_level
            )
            
            if not is_valid:
                logger.warning(f"Validation warning: {validation_msg}")
                data["validation_warning"] = validation_msg
            
            logger.info(f"STAGE 4: Quality check passed - {validation_msg}")
            
            # Dodaj metadane
            data["enhanced"] = True
            data["model"] = self.model_name
            data["creativity"] = creativity
            data["word_count"] = word_count
            data["detail_level"] = detail_level
            data["style"] = style
            data["original_prompt"] = prompt
            data["expanded_prompt"] = expanded_prompt
            
            if image_analysis:
                data["image_data"] = image_analysis
            
            logger.info("Enhancement COMPLETED SUCCESSFULLY")
            return True, data
        
        except requests.exceptions.Timeout:
            msg = f"Timeout ({self.timeout}s)"
            logger.error(msg)
            return False, {"error": msg}
        except Exception as e:
            msg = f"Exception: {str(e)}"
            logger.error(msg, exc_info=True)
            return False, {"error": msg}
    
    def _expand_prompt(
        self,
        prompt: str,
        language: str = "pl",
        detail_level: str = "medium"
    ) -> Optional[str]:
        """
        ETAP 1: Ekspanduj polski prompt na podstawową wersję rozszerzoną
        Celem jest zrozumienie i rozwinięcie głównych elementów
        """
        
        detail_map = {
            "low": "Zidentyfikuj 2-3 główne elementy.",
            "medium": "Zidentyfikuj 4-5 głównych elementów wizualnych.",
            "high": "Zidentyfikuj 6-8 elementów wizualnych i ich relacje."
        }
        detail_text = detail_map.get(detail_level, detail_map["medium"])
        
        if language == "pl":
            system = f"""Jesteś asystentem do rozwijania polskich promptów.
Twoim zadaniem jest przeanalizować polski prompt i zwrócić listę kluczowych 
elementów wizualnych, które będą pomocne w wzbogacaniu opisu.

{detail_text}

Zwróć JSON z polem "elements" zawierającym listę zidentyfikowanych elementów."""
        else:
            system = f"""You are an assistant for expanding prompts.
Analyze the prompt and identify key visual elements.

{detail_text}

Return JSON with "elements" field containing identified elements."""
        
        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{system}\n\nPrompt: {prompt}",
                    "temperature": 0.5,
                    "stream": False,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                raw = response.json().get("response", "")
                data = extract_json_from_response(raw)
                
                if data and "elements" in data:
                    elements = data.get("elements", [])
                    if isinstance(elements, list):
                        expanded = " + ".join(elements)
                        logger.info(f"Expanded to: {expanded}")
                        return expanded
        except Exception as e:
            logger.warning(f"Expansion failed: {e}")
        
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
        - Zawartość (czy zawiera detale)
        - Spójność z original promptem
        """
        
        en_prompt = result.get("prompt_en", "")
        pl_prompt = result.get("prompt_pl", "")
        
        # Policz słowa bardziej dokładnie
        en_words = len(en_prompt.split())
        pl_words = len(pl_prompt.split())
        
        logger.info(f"Word count - EN: {en_words}, PL: {pl_words}, Target: {target_words}")
        
        # Walidacja 1: Minimalna ilość słów
        min_words = max(50, target_words // 2)
        if en_words < min_words:
            return False, f"Too short: {en_words} words (min: {min_words})"
        
        # Walidacja 2: Czy zawiera detale
        detail_keywords = [
            "light", "texture", "color", "shadow", "atmosphere", "detail",
            "golden", "cinematic", "composition", "lighting", "mood",
            "świat", "oświetlenie", "tekstura", "kolor", "atmosfera",
            "szczegół", "nastrój", "złoty", "kinematograficzny"
        ]
        
        has_details = any(kw in en_prompt.lower() or kw in pl_prompt.lower() 
                         for kw in detail_keywords)
        
        if not has_details and detail_level == "high":
            return False, "Missing visual details for HIGH detail level"
        
        # Walidacja 3: Czy nie jest puste/błędne
        if len(en_prompt.strip()) < 20 or len(pl_prompt.strip()) < 20:
            return False, "Result too short or empty"
        
        # Walidacja 4: Podstawowe sprawdzenie spójności
        if "error" in en_prompt.lower() or "error" in pl_prompt.lower():
            return False, "Error found in response"
        
        return True, f"Valid ({en_words} EN words, {pl_words} PL words)"
    
    def _build_system_prompt_advanced(
        self,
        image_context: str = "",
        language: str = "pl",
        word_count: int = 200,
        detail_level: str = "medium",
        style: str = "cinematic"
    ) -> str:
        """System prompt z kontrolą szczegółowości i stylu"""
        
        detail_map = {
            "low": (
                "Bądź zwięzły. Opisz tylko kluczowe elementy bez zbędnych detali. "
                "Skupiaj się na głównych komponentach sceny."
            ),
            "medium": (
                "Opisz elementy wizualne ze szczegółami. Dodaj informacje o "
                "oświetleniu, kolorach i podstawowej atmosferze."
            ),
            "high": (
                "Dodaj BARDZO DUŻO szczegółów: tekstury, kolory, oświetlenie, "
                "atmosfera, efekty, głębia ostrości, temperaturę barwną, "
                "rodzaje światła, cienie, odbicia, kontrast, nasycenie, "
                "material powierzchni, jakość powietrza, mgłę, cząsteczki, "
                "refleksy, specjalne efekty. Bądź bardzo szczegółowy i opisowy."
            )
        }
        detail_text = detail_map.get(detail_level, detail_map["medium"])
        
        style_map = {
            "cinematic": (
                "Użyj kinematograficznego języka (cinematography, lighting design, "
                "lens choice, composition, depth of field, color grading, "
                "mise-en-scène, visual storytelling)"
            ),
            "artistic": (
                "Skoncentruj się na aspektach artystycznych (art style, "
                "composition, aesthetic, artistic movement, color palette, "
                "brushwork, visual harmony, artistic techniques)"
            ),
            "technical": (
                "Opisz techniczne parametry (resolution, bit depth, frame rate, "
                "codec, color space, dynamic range, exposure settings, "
                "white balance, ISO, aperture equivalents)"
            )
        }
        style_text = style_map.get(style, style_map["cinematic"])
        
        if language == "pl":
            base = f"""Jesteś ekspertem w tworzeniu BARDZO SZCZEGÓŁOWYCH, ROZBUDOWANYCH 
i BOGATYCH w detale promptów dla narzędzi generacji obrazów i wideo.

NAJWAŻNIEJSZE WYTYCZNE:
1. ROZWIJAJ I ROZSZERZAJ input - nie tylko go tłumacz
2. Dodaj KONKRETNE detale (nie uogólniaj)
3. {detail_text}
4. {style_text}
5. Docelowa długość: ~{word_count} słów (WAŻNE: licz słowa dokładnie)
6. Zachowaj oryginalną intencję
7. Polski prompt rozwijaj na szczegóły, nie go przepisuj
8. Dla wersji EN: naturalny angielski bez zbędnych tłumaczeń

STRUKTURA ODPOWIEDZI (JSON):
{{
    "prompt_en": "Bardzo szczegółowy angielski opis z bogatymi detalami...",
    "prompt_pl": "Bardzo szczegółowy polski opis z bogatymi detalami..."
}}

KRYTYCZNE: Oba prompty muszą być ROZBUDOWANE i SZCZEGÓŁOWE, nie krótkie!"""
        else:
            base = f"""You are an expert in creating EXTREMELY DETAILED, COMPREHENSIVE, 
and RICH prompts for image and video generation tools.

KEY GUIDELINES:
1. EXPAND and ELABORATE on the input - don't just translate
2. Add CONCRETE details (not generalizations)
3. {detail_text}
4. {style_text}
5. Target length: ~{word_count} words (IMPORTANT: count words accurately)
6. Preserve original intent
7. Create natural, detailed descriptions
8. Both EN and PL versions must be COMPREHENSIVE

RESPONSE STRUCTURE (JSON):
{{
    "prompt_en": "Extremely detailed English description with rich details...",
    "prompt_pl": "Extremely detailed Polish description with rich details..."
}}

CRITICAL: Both prompts must be ELABORATE and DETAILED, not short!"""
        
        if image_context:
            base += f"\n\nIMAGE CONTEXT TO INCORPORATE:\n{image_context}"
        
        return base
    
    def _build_user_prompt_with_expansion(
        self,
        original: str,
        expanded: Optional[str],
        language: str = "pl"
    ) -> str:
        """User prompt z informacją o rozszerzeniu"""
        
        if language == "pl":
            user = f"""Bazowy prompt: "{original}"

Zidentyfikowane elementy do rozwinięcia: {expanded if expanded else "wszystkie aspekty"}

Zadanie: Wzbogać powyższy prompt w SZCZEGÓŁY, DETALE i OPISY wizualne.
Pamiętaj:
1. ZAWSZE zwróć ROZBUDOWANY opis (200+ słów)
2. KONKRETNE detale (kolory, materiały, oświetlenie, tekstury)
3. TYLKO JSON format
4. Oba pola (prompt_en i prompt_pl) MUSZĄ być szczegółowe"""
        else:
            user = f"""Base prompt: "{original}"

Identified elements to expand: {expanded if expanded else "all aspects"}

Task: Enrich the above prompt with DETAILS, SPECIFICS and VISUAL DESCRIPTIONS.
Remember:
1. ALWAYS return a COMPREHENSIVE description (200+ words)
2. CONCRETE details (colors, materials, lighting, textures)
3. JSON format ONLY
4. Both fields (prompt_en and prompt_pl) MUST be detailed"""
        
        return user
    
    def _format_image_context(self, image_analysis: Dict) -> str:
        """Formatuj analizę obrazu"""
        
        parts = []
        
        if image_analysis.get("width") and image_analysis.get("height"):
            w, h = image_analysis["width"], image_analysis["height"]
            parts.append(f"Resolution: {w}x{h}")
        
        if image_analysis.get("detected"):
            detected = ", ".join(image_analysis["detected"])
            parts.append(f"Elements: {detected}")
        
        if image_analysis.get("color_temp"):
            parts.append(f"Color: {image_analysis['color_temp']}")
        
        if image_analysis.get("brightness"):
            parts.append(f"Brightness: {image_analysis['brightness']}")
        
        return " | ".join(parts) if parts else ""
    
    def set_model(self, model_name: str) -> None:
        """Zmień model"""
        self.model_name = model_name
        logger.info(f"Model changed to: {model_name}")
