#!/usr/bin/env python3
"""
SVD Prompt Enhancer Pro v5.0
Main entry point

Usage:
    python3 main.py
"""

import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import setup_logging
from config.constants import LOG_DIR
from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication


def main():
    """Application entry point"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("🚀 SVD Prompt Enhancer Pro v5.0")
    logger.info("Pop!_OS | RTX 2060 6GB | Local Ollama")
    logger.info("=" * 60)
    logger.info(f"📁 Config: {PROJECT_ROOT / 'config'}")
    logger.info(f"📁 Logs: {LOG_DIR / 'app.log'}")
    
    # Create PyQt5 app
    app = QApplication(sys.argv)
    
    # Create main window
    try:
        window = MainWindow()
        window.show()
        logger.info("✅ UI loaded successfully")
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"❌ Failed to start UI: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
