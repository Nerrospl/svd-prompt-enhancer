#!/usr/bin/env python3
"""
SVD Prompt Enhancer Pro v5.1 - Main Entry Point

Launches the PyQt5 GUI application for prompt enhancement.

Features:
- Polish prompt input
- AI-powered enhancement with retry logic
- Safe JSON parsing (4 strategies)
- Responsive UI with async workers
- Real-time progress feedback

Usage:
    python3 main.py

Requirements:
    - PyQt5
    - requests
    - Ollama running on http://localhost:11434

Author: SVD Prompt Enhancer Team
Version: 5.1.0
Date: 2026-01-09
"""

import sys
import logging
from pathlib import Path

# ============================================================================
# SETUP PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# SETUP LOGGING
# ============================================================================

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


logger = setup_logging()
logger.info("=" * 70)
logger.info("SVD Prompt Enhancer Pro v5.1 - Startup")
logger.info("=" * 70)


# ============================================================================
# IMPORTS
# ============================================================================

try:
    logger.info("Importing configuration...")
    from config import (
        APP_VERSION,
        APP_NAME,
        RETRY_MAX_ATTEMPTS,
        DEFAULT_CREATIVITY,
        DEFAULT_DETAIL_LEVEL,
        DEFAULT_STYLE,
        DEFAULT_LENGTH,
    )
    logger.info(f"✅ Configuration loaded")
except ImportError as e:
    logger.error(f"❌ Failed to import config: {e}")
    logger.error("Make sure config/constants.py exists")
    sys.exit(1)

try:
    logger.info("Importing core modules...")
    from core import SafeJSONHandler, ParseResult
    logger.info("✅ Core modules loaded")
except ImportError as e:
    logger.error(f"❌ Failed to import core: {e}")
    logger.error("Make sure core/__init__.py exists and exports SafeJSONHandler")
    sys.exit(1)

try:
    logger.info("Importing workers...")
    from workers import EnhancementWorker, EnhancementResult
    logger.info("✅ Workers loaded")
except ImportError as e:
    logger.error(f"❌ Failed to import workers: {e}")
    logger.error("Make sure workers/__init__.py exists and exports EnhancementWorker")
    sys.exit(1)

try:
    logger.info("Importing PyQt5...")
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QVBoxLayout,
        QHBoxLayout,
        QWidget,
        QLabel,
        QLineEdit,
        QPushButton,
        QTextEdit,
        QComboBox,
        QSpinBox,
        QProgressBar,
        QMessageBox,
    )
    from PyQt5.QtCore import pyqtSlot, Qt
    logger.info("✅ PyQt5 loaded")
except ImportError as e:
    logger.error(f"❌ Failed to import PyQt5: {e}")
    logger.error("Install: pip install PyQt5 requests")
    sys.exit(1)


# ============================================================================
# MAIN WINDOW
# ============================================================================

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        logger.info("Initializing MainWindow...")
        
        # Setup window
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ====================================================================
        # TITLE SECTION
        # ====================================================================
        
        title_label = QLabel(f"{APP_NAME} v{APP_VERSION}")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # ====================================================================
        # INPUT SECTION
        # ====================================================================
        
        input_section_label = QLabel("📝 Prompt to Enhance (Polish):")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("e.g., 'piękna kobieta na plaży o zachodzie słońca'")
        self.input_field.setMinimumHeight(50)
        
        main_layout.addWidget(input_section_label)
        main_layout.addWidget(self.input_field)
        
        # ====================================================================
        # SETTINGS SECTION
        # ====================================================================
        
        settings_label = QLabel("⚙️ Enhancement Settings:")
        main_layout.addWidget(settings_label)
        
        settings_layout = QHBoxLayout()
        
        # Detail level
        detail_label = QLabel("Detail Level:")
        self.detail_combo = QComboBox()
        self.detail_combo.addItems(["Niski", "Średni", "Wysoki"])
        self.detail_combo.setCurrentText(DEFAULT_DETAIL_LEVEL)
        settings_layout.addWidget(detail_label)
        settings_layout.addWidget(self.detail_combo)
        
        settings_layout.addSpacing(20)
        
        # Style
        style_label = QLabel("Style:")
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Kinematograficzny", "Artystyczny", "Techniczny"])
        self.style_combo.setCurrentText(DEFAULT_STYLE)
        settings_layout.addWidget(style_label)
        settings_layout.addWidget(self.style_combo)
        
        settings_layout.addSpacing(20)
        
        # Length
        length_label = QLabel("Length (words):")
        self.length_spin = QSpinBox()
        self.length_spin.setMinimum(50)
        self.length_spin.setMaximum(1000)
        self.length_spin.setValue(DEFAULT_LENGTH)
        settings_layout.addWidget(length_label)
        settings_layout.addWidget(self.length_spin)
        
        settings_layout.addStretch()
        main_layout.addLayout(settings_layout)
        
        # ====================================================================
        # ACTION BUTTONS
        # ====================================================================
        
        buttons_layout = QHBoxLayout()
        
        self.enhance_button = QPushButton("🚀 Enhance Prompt")
        self.enhance_button.setMinimumHeight(40)
        self.enhance_button.clicked.connect(self.on_enhance_clicked)
        self.enhance_button.setStyleSheet("""
            QPushButton {
                background-color: #2186a6;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1a6a8a;
            }
        """)
        
        self.cancel_button = QPushButton("⏹️ Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        
        buttons_layout.addWidget(self.enhance_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        
        # ====================================================================
        # STATUS AND PROGRESS
        # ====================================================================
        
        self.status_label = QLabel("📊 Status: Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress_bar)
        
        # ====================================================================
        # RESULTS SECTION
        # ====================================================================
        
        results_label = QLabel("✨ Enhanced Prompts:")
        results_label_font = results_label.font()
        results_label_font.setBold(True)
        results_label.setFont(results_label_font)
        main_layout.addWidget(results_label)
        
        # English prompt
        en_label = QLabel("🌐 English:")
        self.en_field = QTextEdit()
        self.en_field.setReadOnly(True)
        self.en_field.setMinimumHeight(120)
        self.en_field.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: #f5f5f5;
            }
        """)
        
        main_layout.addWidget(en_label)
        main_layout.addWidget(self.en_field)
        
        # Polish prompt
        pl_label = QLabel("🇵🇱 Polish:")
        self.pl_field = QTextEdit()
        self.pl_field.setReadOnly(True)
        self.pl_field.setMinimumHeight(120)
        self.pl_field.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: #f5f5f5;
            }
        """)
        
        main_layout.addWidget(pl_label)
        main_layout.addWidget(self.pl_field)
        
        # Apply layout
        central_widget.setLayout(main_layout)
        
        # Initialize worker
        self.worker = None
        
        logger.info("✅ MainWindow initialized")
    
    @pyqtSlot()
    def on_enhance_clicked(self):
        """Handle enhance button click"""
        prompt = self.input_field.text().strip()
        
        if not prompt:
            QMessageBox.warning(self, "Input Error", "Please enter a prompt in Polish")
            return
        
        if len(prompt) < 5:
            QMessageBox.warning(self, "Input Error", "Prompt is too short (min 5 characters)")
            return
        
        if len(prompt) > 2000:
            QMessageBox.warning(self, "Input Error", "Prompt is too long (max 2000 characters)")
            return
        
        logger.info(f"🚀 Starting enhancement: {prompt[:50]}...")
        
        # Disable input during processing
        self.enhance_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.input_field.setEnabled(False)
        
        # Clear results
        self.en_field.clear()
        self.pl_field.clear()
        self.progress_bar.setValue(0)
        
        # Create worker
        self.worker = EnhancementWorker(debug=False)
        self.worker.status_changed.connect(self.on_status_changed)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.error_occurred.connect(self.on_error_occurred)
        
        # Run enhancement (blocking, simple version)
        result = self.worker.enhance_direct(
            prompt=prompt,
            creativity=DEFAULT_CREATIVITY,
            length=self.length_spin.value(),
            details=self.detail_combo.currentText(),
            style=self.style_combo.currentText()
        )
        
        # Display results
        if result.success:
            self.en_field.setText(result.prompt_en or "(No English prompt)")
            self.pl_field.setText(result.prompt_pl or "(No Polish prompt)")
            
            status_msg = f"✅ Success! Attempt {result.attempts}, Strategy: {result.strategy_used}"
            self.status_label.setText(f"📊 Status: {status_msg}")
            logger.info(status_msg)
        else:
            error_msg = result.error_message or "Unknown error"
            self.status_label.setText(f"❌ Status: {error_msg}")
            logger.error(f"❌ Enhancement failed: {error_msg}")
            
            QMessageBox.critical(
                self,
                "Enhancement Failed",
                f"Failed to enhance prompt:\n\n{error_msg}"
            )
        
        # Reset button states
        self.enhance_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.input_field.setEnabled(True)
        self.progress_bar.setValue(100)
    
    @pyqtSlot()
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        if self.worker:
            logger.warning("⏹️ Cancelling enhancement...")
            self.worker.cancel()
            self.status_label.setText("📊 Status: Cancelled by user")
            
            self.enhance_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.input_field.setEnabled(True)
    
    @pyqtSlot(str)
    def on_status_changed(self, status: str):
        """Handle status change signal"""
        self.status_label.setText(f"📊 Status: {status}")
        logger.debug(f"Status: {status}")
    
    @pyqtSlot(str, int)
    def on_progress_updated(self, message: str, value: int):
        """Handle progress update signal"""
        self.progress_bar.setValue(min(100, value * 20))
        logger.debug(f"Progress: {message} ({value})")
    
    @pyqtSlot(str)
    def on_error_occurred(self, error: str):
        """Handle error signal"""
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error}")
        logger.error(f"Error: {error}")


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main application entry point"""
    logger.info("Creating QApplication...")
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    logger.info("Creating MainWindow...")
    window = MainWindow()
    
    logger.info("Showing window...")
    window.show()
    
    logger.info("Entering event loop...")
    sys.exit(app.exec_())


# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        print(f"\n❌ Application crashed!")
        print(f"Error: {e}")
        print("\nCheck the logs above for details.")
        sys.exit(1)
