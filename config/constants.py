"""
config/constants.py
Centralna konfiguracja aplikacji

Zawiera:
- Modele Ollama (z opcjami Q4/Q5/Q6)
- Timeout'i
- Ścieżki (XDG standard)
- Języki (PL/EN)
- Domyślne ustawienia
"""

from pathlib import Path
import os
from enum import Enum
from typing import Dict, List

# ============================================================================
# ENUMERACJE
# ============================================================================

class QuantizationType(Enum):
    """Typy kwantyzacji modeli"""
    Q4 = "q4"      # 4-5GB VRAM – szybki, dobra jakość (REKOMENDOWANY RTX 2060)
    Q5 = "q5"      # 6-7GB VRAM – średni, lepsza jakość
    Q6 = "q6"      # 8-10GB VRAM – wolny, najlepsza jakość
    FP16 = "fp16"  # Full precision – bardzo powolny


class ModelPurpose(Enum):
    """Zastosowanie modelu"""
    ENHANCEMENT = "enhancement"  # Wzbogacanie promptu
    VISION = "vision"             # Analiza obrazów
    TRANSLATION = "translation"   # Tłumaczenia


# ============================================================================
# MODELE OLLAMA – Z OPCJAMI KWANTYZACJI
# ============================================================================

AVAILABLE_MODELS = {
    "enhancement": {
        "primary": {
            "name": "Dolphin 3.0 (8B) – BEZ CENZURY 🔓",
            "models": {
                QuantizationType.Q4: "dolphin-llama3:latest",  # 5.2GB
                QuantizationType.Q5: "dolphin-llama3:7b-q5",  # 6.5GB
                QuantizationType.Q6: "dolphin-llama3:7b-q6",  # 9GB
            },
            "description": "🌟 Najlepsza jakość + bez cenzury. Idealna do artystycznych promptów.",
            "requirements": {
                QuantizationType.Q4: {
                    "vram_gb": 5.2,
                    "suitable_for": ["RTX 2060", "RTX 3060", "RTX 4060"],
                    "speed": "🚀 Szybka (~40 tok/s)",
                },
                QuantizationType.Q5: {
                    "vram_gb": 6.5,
                    "suitable_for": ["RTX 2080", "RTX 3070", "RTX 4070"],
                    "speed": "⚡ Średnia (~30 tok/s)",
                },
                QuantizationType.Q6: {
                    "vram_gb": 9.0,
                    "suitable_for": ["RTX 3080", "RTX 4080", "RTX 4090"],
                    "speed": "🐢 Wolna (~20 tok/s)",
                },
            },
            "pros": [
                "✅ Brak cenzury – pełna kreatywność",
                "✅ Doskonała jakość tekstu",
                "✅ Zoptymalizowana dla opisów",
            ],
            "cons": [
                "❌ Wymaga 5+ GB VRAM (Q4)",
                "❌ Wolniejsza niż Mistral",
            ],
        },
        "alternatives": [
            {
                "name": "Mistral 7B",
                "models": {
                    QuantizationType.Q4: "mistral:latest",
                    QuantizationType.Q5: "mistral:7b-q5",
                    QuantizationType.Q6: "mistral:7b-q6",
                },
                "description": "⚡ Szybka, efektywna, dobra dla JSON. Lekka cenzura.",
                "vram_q4": 4.5,
                "speed": "🚀🚀 Bardzo szybka (~50 tok/s)",
                "best_for": "Gdy brakuje VRAM lub potrzebujesz szybkości",
            },
            {
                "name": "Nous-Hermes 2 Mixtral (MoE)",
                "models": {
                    QuantizationType.Q4: "nous-hermes2-mixtral:8x7b-q4",
                },
                "description": "🔥 Uncensored, świetna dla złożonych promptów. MoE = mniej VRAM niż się wydaje.",
                "vram_q4": 6.0,
                "speed": "⚡ Średnia (~30 tok/s)",
                "best_for": "Kreatywne, zaawansowane prompty bez cenzury",
            },
            {
                "name": "Qwen 2.5 7B",
                "models": {
                    QuantizationType.Q4: "qwen2.5:7b-q4",
                },
                "description": "🌐 Chiński LLM, świetny do opisów. Neutralna cenzura.",
                "vram_q4": 4.5,
                "speed": "🚀 Szybka (~45 tok/s)",
                "best_for": "Uniwersalne zastosowania, małe VRAM",
            },
        ],
    },
    
    "vision": {
        "primary": {
            "name": "LLaVA 1.6 (34B Vision) 👁️",
            "models": {
                QuantizationType.Q4: "llava:latest",
                QuantizationType.Q5: "llava:34b-q5",
                QuantizationType.Q6: "llava:34b-q6",
            },
            "description": "🌟 Najlepsza lokalnie analiza obrazów. WYMAGANA do działania!",
            "requirements": {
                QuantizationType.Q4: {
                    "vram_gb": 5.5,
                    "suitable_for": ["RTX 2060", "RTX 3060", "RTX 4060"],
                    "speed": "⚡ ~40s per image",
                },
                QuantizationType.Q5: {
                    "vram_gb": 7.0,
                    "suitable_for": ["RTX 2080", "RTX 3070"],
                    "speed": "🚀 ~25s per image",
                },
                QuantizationType.Q6: {
                    "vram_gb": 9.5,
                    "suitable_for": ["RTX 3080+"],
                    "speed": "🎯 ~15s per image",
                },
            },
            "pros": [
                "✅ Najlepsza jakość analizy",
                "✅ Rozumie kontekst wizualny",
                "✅ Doskonała dla artystycznych obrazów",
            ],
            "cons": [
                "❌ BRAK fallback – wymagana!",
                "❌ Wolniejsza (40s+ per image)",
                "❌ 5.5+ GB VRAM",
            ],
        },
        "alternatives": [
            {
                "name": "LLaVA Llama2 (11B)",
                "models": {
                    QuantizationType.Q4: "llava-llama2:latest",
                },
                "description": "Lżejsza alternatywa (4.5GB). Mniej dokładna niż LLaVA 34B.",
                "vram_q4": 4.5,
                "best_for": "Gdy 34B za duży, ale chcesz vision",
            },
            {
                "name": "Moondream (Tiny Vision)",
                "models": {
                    QuantizationType.Q4: "moondream:latest",
                },
                "description": "Bardzo lekka (2.5GB). Dla szybkiej, podstawowej analizy.",
                "vram_q4": 2.5,
                "best_for": "Nisko-zasobowe systemy (CPU-only)",
            },
        ],
    },
    
    "translation": {
        "primary": {
            "name": "Mistral 7B",
            "models": {
                QuantizationType.Q4: "mistral:latest",
            },
            "description": "Szybka, dokładna tłumaczenia EN ↔ PL",
            "vram_q4": 4.5,
            "speed": "🚀 50 tok/s",
        },
    },
}

# ============================================================================
# TIMEOUT'I (DOSTOSOWANE DLA RTX 2060)
# ============================================================================

TIMEOUTS = {
    "ollama_check": 2,              # Sprawdzenie statusu
    "image_analysis": 600,          # 10 min (LLaVA na RTX 2060)
    "enhancement": 300,             # 5 min (Mistral/Dolphin)
    "translation": 180,             # 3 min
    "model_download": 7200,         # 2 godziny (duże modele)
    "model_operation": 60,          # 1 min dla pull/rm/unload
}

# ============================================================================
# ŚCIEŻKI (XDG STANDARD DLA LINUXA)
# ============================================================================

def get_config_dir() -> Path:
    """Zwróć ~/.config/svd_enhancer/"""
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        cfg_dir = Path(xdg) / "svd_enhancer"
    else:
        cfg_dir = Path.home() / ".config" / "svd_enhancer"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


def get_data_dir() -> Path:
    """Zwróć ~/.local/share/svd_enhancer/"""
    xdg = os.getenv("XDG_DATA_HOME")
    if xdg:
        data_dir = Path(xdg) / "svd_enhancer"
    else:
        data_dir = Path.home() / ".local" / "share" / "svd_enhancer"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_cache_dir() -> Path:
    """Zwróć ~/.cache/svd_enhancer/"""
    xdg = os.getenv("XDG_CACHE_HOME")
    if xdg:
        cache_dir = Path(xdg) / "svd_enhancer"
    else:
        cache_dir = Path.home() / ".cache" / "svd_enhancer"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


# Finalne ścieżki
CONFIG_DIR = get_config_dir()
DATA_DIR = get_data_dir()
CACHE_DIR = get_cache_dir()

CONFIG_FILE = CONFIG_DIR / "settings.json"
LOG_DIR = DATA_DIR / "logs"
DB_FILE = DATA_DIR / "history.db"

# Stwórz logi folder
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# JĘZYKI
# ============================================================================

LANGUAGES = {
    "pl": {"name": "Polski", "flag": "🇵🇱"},
    "en": {"name": "English", "flag": "🇬🇧"},
}

DEFAULT_LANGUAGE = "pl"

# ============================================================================
# DOMYŚLNE USTAWIENIA (UI)
# ============================================================================

DEFAULT_WINDOW_GEOMETRY = {
    "width": 1400,
    "height": 900,
    "x": 100,
    "y": 100,
}

DEFAULT_PROMPT_SETTINGS = {
    "purpose": "video",               # video / image
    "creativity": 50,                 # 0-100
    "max_tokens": 250,
    "temperature": 0.7,
    "model_quantization": QuantizationType.Q4.value,
}

DEFAULT_UI_SETTINGS = {
    "language": DEFAULT_LANGUAGE,
    "theme": "dark",
    "auto_save": True,
    "notifications": True,
}

# ============================================================================
# KOLORY I STYLE
# ============================================================================

COLORS = {
    "light_mode": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f5f5f5",
        "text_primary": "#000000",
        "text_secondary": "#666666",
        "accent": "#2196F3",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
    },
    "dark_mode": {
        "bg_primary": "#1e1e1e",
        "bg_secondary": "#2d2d2d",
        "text_primary": "#ffffff",
        "text_secondary": "#999999",
        "accent": "#64B5F6",
        "success": "#66BB6A",
        "warning": "#FFA726",
        "error": "#EF5350",
    },
}

# ============================================================================
# LOGGING
# ============================================================================

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s – %(message)s"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================================================
# OLLAMA API
# ============================================================================

OLLAMA_API_URL = "http://127.0.0.1:11434"
OLLAMA_MODELS_ENDPOINT = f"{OLLAMA_API_URL}/api/tags"
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_API_URL}/api/generate"
OLLAMA_PULL_ENDPOINT = f"{OLLAMA_API_URL}/api/pull"

# ============================================================================
# APLIKACJA
# ============================================================================

APP_NAME = "SVD Prompt Enhancer Pro"
APP_VERSION = "5.0"
APP_AUTHOR = "SVD Development Team"
APP_DESCRIPTION = "AI Prompt Enhancement Tool – Local Ollama + PyQt5"
