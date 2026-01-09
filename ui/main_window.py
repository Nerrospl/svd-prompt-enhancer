"""
EDYCJA main_window.py
KOD DO WKLEJENIA

INSTRUKCJA EDYCJI:
1. Otwórz plik: /mnt/dane/svd-prompt-enhancer/ui/main_window.py
2. USUŃ zawartość CAŁEJ metody init_ui() (linie ~18-37)
3. WKLEJ kod poniżej na jej miejsce
4. Zapisz plik
5. Uruchom: python3 main.py

WSZYSTKO - od "def init_ui" aż do konca metody "event.accept()"
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PEŁNY NOWY PLIK main_window.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
ui/main_window.py
Główne okno aplikacji PyQt5

WERSJA: FAZA 2 - Z WZBOGACANIEM PROMPTÓW
"""

import logging
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Główne okno aplikacji"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 SVD Prompt Enhancer Pro v5.0")
        self.setGeometry(100, 100, 1400, 900)
        
        self.init_ui()
    
    def init_ui(self):
        """Zabuduj UI"""
        
        from ui.tabs.enhance_tab import EnhanceTab
        
        # Centralna zakładka
        tabs = QTabWidget()
        
        # TAB 1: Wzbogacanie (PEŁNY INTERFEJS - FAZA 2)
        self.enhance_tab = EnhanceTab()
        tabs.addTab(self.enhance_tab, "✨ Wzbogacanie")
        
        # TAB 2-5: Placeholder na przyszłość
        tabs.addTab(QWidget(), "🤖 Ollama")
        tabs.addTab(QWidget(), "📚 Historia")
        tabs.addTab(QWidget(), "⚙️ Ustawienia")
        tabs.addTab(QWidget(), "ℹ️ O programie")
        
        self.setCentralWidget(tabs)
    
    def closeEvent(self, event):
        """Przed zamknięciem"""
        logger.info("Zamykanie aplikacji...")
        event.accept()