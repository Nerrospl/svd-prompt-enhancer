"""
═══════════════════════════════════════════════════════════════════════════════
PLIK 3: workers/enhancement_worker.py (KOMPLETNY - ZASTĄP CAŁY PLIK)
WERSJA: 2.1 – Z PEŁNYMI PARAMETRAMI

Data: 2026-01-08
Status: ✅ GOTOWY DO WKLEJENIA
═══════════════════════════════════════════════════════════════════════════════

INSTRUKCJA:
1. Otwórz: /mnt/dane/svd-prompt-enhancer/workers/enhancement_worker.py
2. Zaznacz wszystko: Ctrl+A
3. Usuń: Delete
4. Wklej CAŁY kod poniżej
5. Zapisz: Ctrl+O, Enter, Ctrl+X
6. Weryfikacja: python3 -m py_compile workers/enhancement_worker.py

═══════════════════════════════════════════════════════════════════════════════
"""

import logging
from PyQt5.QtCore import QThread, pyqtSignal
from core.prompt_enhancer import PromptEnhancer
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class EnhancementWorker(QThread):
    """Worker do wzbogacania w osobnym wątku"""
    
    started = pyqtSignal()
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, dict)
    error = pyqtSignal(str)
    
    def __init__(
        self,
        prompt: str,
        language: str = "pl",
        creativity: float = 0.7,
        image_analysis: Optional[Dict] = None,
        model_name: str = None,
        word_count: int = 200,
        detail_level: str = "medium",
        style: str = "cinematic"
    ):
        super().__init__()
        
        self.prompt = prompt
        self.language = language
        self.creativity = creativity
        self.image_analysis = image_analysis
        self.model_name = model_name
        self.word_count = word_count
        self.detail_level = detail_level
        self.style = style
    
    def run(self):
        """Główna logika wątku"""
        
        try:
            logger.info("Enhancement worker started")
            self.started.emit()
            
            self.progress.emit("🔧 Inicjalizacja modelu...")
            enhancer = PromptEnhancer(model_name=self.model_name)
            
            self.progress.emit("⚙️ ETAP 1: Ekspansja promptu...")
            self.progress.emit("📊 ETAP 2: Generacja wzbogacenia...")
            self.progress.emit("✔️ ETAP 3: Walidacja jakości...")
            
            success, result = enhancer.enhance_direct(
                prompt=self.prompt,
                language=self.language,
                creativity=self.creativity,
                image_analysis=self.image_analysis,
                word_count=self.word_count,
                detail_level=self.detail_level,
                style=self.style
            )
            
            if success:
                self.progress.emit("✅ Gotowe!")
                logger.info("Enhancement succeeded")
                self.finished.emit(True, result)
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Enhancement failed: {error_msg}")
                self.error.emit(error_msg)
                self.finished.emit(False, result)
        
        except Exception as e:
            msg = f"Worker exception: {str(e)}"
            logger.error(msg, exc_info=True)
            self.error.emit(msg)
            self.finished.emit(False, {"error": msg})
