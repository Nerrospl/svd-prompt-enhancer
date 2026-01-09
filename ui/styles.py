"""
ui/styles.py
PyQt5 stylesheets (dark mode)
"""

DARK_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    QTabWidget::pane {
        border: 1px solid #3d3d3d;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #ffffff;
        padding: 8px 20px;
        border: 1px solid #3d3d3d;
    }
    
    QTabBar::tab:selected {
        background-color: #3d3d3d;
        border: 1px solid #64B5F6;
    }
    
    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #1976D2;
    }
    
    QPushButton:pressed {
        background-color: #1565C0;
    }
    
    QTextEdit, QPlainTextEdit, QLineEdit {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        padding: 6px;
    }
    
    QLabel {
        color: #ffffff;
    }
    
    QComboBox {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        padding: 6px;
    }
    
    QProgressBar {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        height: 20px;
    }
    
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 3px;
    }
"""


def setup_styles(app):
    """Zastosuj stylesheet do aplikacji"""
    app.setStyleSheet(DARK_STYLESHEET)