"""
PLIK 3: workers/image_analysis_worker.py
QThread do analizy obrazu

INSTRUKCJA:
1. Utwórz nowy plik: /mnt/dane/svd-prompt-enhancer/workers/image_analysis_worker.py
2. Skopiuj CAŁĄ zawartość poniżej
3. Zapisz plik
"""

import logging
from PyQt5.QtCore import QThread, pyqtSignal
from core.image_processor import ImageAnalyzer, DeepAttributeAnalyzer

logger = logging.getLogger(__name__)


class ImageAnalysisWorker(QThread):
    """Worker do analizy obrazu w osobnym wątku"""
    
    started = pyqtSignal()
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, dict)
    error = pyqtSignal(str)
    
    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path
    
    def run(self):
        """Główna logika wątku"""
        
        try:
            logger.info(f"Image analysis worker started: {self.image_path}")
            self.started.emit()
            
            self.progress.emit("📊 Analiza techniczna obrazu...")
            tech_data = ImageAnalyzer.analyze_image(self.image_path)
            
            if tech_data.get("error"):
                self.error.emit(tech_data["error"])
                self.finished.emit(False, tech_data)
                return
            
            self.progress.emit("🔍 Rozpoznawanie atrybutów...")
            deep_data = DeepAttributeAnalyzer.analyze(self.image_path)
            
            result = {
                **tech_data,
                **deep_data,
            }
            
            self.progress.emit("✅ Analiza zakończona")
            logger.info("Image analysis succeeded")
            self.finished.emit(True, result)
        
        except Exception as e:
            msg = f"Worker exception: {str(e)}"
            logger.error(msg, exc_info=True)
            self.error.emit(msg)
            self.finished.emit(False, {"error": msg})
