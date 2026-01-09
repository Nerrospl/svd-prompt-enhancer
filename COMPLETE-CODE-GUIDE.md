# 📦 SVD PROMPT ENHANCER PRO v5.0 – KOMPLETNY KOD
## Instrukcja: skopiuj kod z odpowiedniej sekcji do odpowiedniego pliku

**Struktura:** `config/constants.py`, `config/__init__.py`, itd.

---

## 🔧 INSTALACJA (PRZED KODEM)

```bash
# 1. Klonuj / pobierz projekt
mkdir svd-prompt-enhancer && cd svd-prompt-enhancer

# 2. Uruchom setup
bash setup.sh

# 3. Aktywuj venv
source venv/bin/activate

# 4. Skopiuj kod z poniższych sekcji do odpowiednich plików

# 5. Uruchom
python3 main.py
```

---

## 📄 PLIK: `config/__init__.py`

```python
"""Configuration module"""
```

---

## 📄 PLIK: `config/logging_config.py`

```python
"""
config/logging_config.py
Konfiguracja loggingu aplikacji
"""

import logging
from pathlib import Path
from config.constants import LOG_DIR, LOG_FORMAT, LOG_LEVEL


def setup_logging():
    """Setup logging do pliku i console"""
    
    log_file = LOG_DIR / "app.log"
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging configured – file: {log_file}")
```

---

## 📄 PLIK: `core/__init__.py`

```python
"""Core business logic module"""
```

---

## 📄 PLIK: `core/ollama_manager.py`

```python
"""
core/ollama_manager.py
Menedżer komunikacji z Ollama (HTTP REST API)
"""

import requests
import subprocess
import json
from typing import Dict, List, Optional, Callable, Tuple
import logging
from config.constants import OLLAMA_API_URL, TIMEOUTS

logger = logging.getLogger(__name__)


class OllamaManager:
    """Zarządza stanem, pobieraniem i usuwaniem modeli Ollama"""
    
    def __init__(self, api_url: str = OLLAMA_API_URL):
        self.api_url = api_url
        self.timeout_check = TIMEOUTS.get("ollama_check", 2)
    
    # ─────────────────────────────────────────────────────────────────────
    # STATUS I DIAGNOSTYKA
    # ─────────────────────────────────────────────────────────────────────
    
    def is_running(self) -> bool:
        """Czy Ollama daemon jest uruchomiona?"""
        try:
            resp = requests.get(
                f"{self.api_url}/api/tags",
                timeout=self.timeout_check
            )
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> List[Dict]:
        """Zwróć listę zainstalowanych modeli"""
        try:
            resp = requests.get(
                f"{self.api_url}/api/tags",
                timeout=self.timeout_check
            )
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return [
                    {
                        "name": m.get("name", "unknown"),
                        "size_bytes": m.get("size", 0),
                        "size_gb": round(m.get("size", 0) / (1024**3), 2),
                        "modified": m.get("modified_at", "?"),
                    }
                    for m in models
                ]
        except Exception as e:
            logger.error(f"Błąd listy modeli: {e}")
        return []
    
    # ─────────────────────────────────────────────────────────────────────
    # POBIERANIE MODELI
    # ─────────────────────────────────────────────────────────────────────
    
    def pull_model(
        self,
        model_name: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Tuple[bool, str]:
        """Pobierz model"""
        logger.info(f"Pobieranie modelu: {model_name}")
        
        try:
            proc = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in iter(proc.stdout.readline, ""):
                if not line.strip():
                    continue
                
                pct = self._extract_progress_pct(line)
                if progress_callback:
                    progress_callback(pct or 0, line.strip())
                
                logger.debug(line.strip())
            
            returncode = proc.wait()
            
            if returncode == 0:
                logger.info(f"✅ Pobrano: {model_name}")
                return True, f"Pobrano {model_name}"
            else:
                msg = f"Błąd pobierania (kod {returncode})"
                logger.error(msg)
                return False, msg
        
        except Exception as e:
            msg = f"Wyjątek: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def unload_model(self, model_name: str) -> Tuple[bool, str]:
        """Zwolnij model z VRAM"""
        try:
            logger.info(f"Zwalnianie {model_name} z VRAM...")
            requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": "",
                    "keep_alive": 0,
                },
                timeout=5
            )
            logger.info(f"✅ Zwolniono {model_name}")
            return True, f"Zwolniono {model_name}"
        except Exception as e:
            msg = f"Błąd zwolnienia: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def delete_model(self, model_name: str) -> Tuple[bool, str]:
        """Usuń model"""
        try:
            logger.info(f"Usuwanie {model_name}...")
            result = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Usunięto {model_name}")
                return True, f"Usunięto {model_name}"
            else:
                msg = f"Błąd: {result.stderr}"
                logger.error(msg)
                return False, msg
        except Exception as e:
            msg = f"Wyjątek: {str(e)}"
            logger.error(msg)
            return False, msg
    
    @staticmethod
    def _extract_progress_pct(line: str) -> Optional[int]:
        """Wyciągnij % z outputu ollama pull"""
        import re
        m = re.search(r'(\d+)%', line)
        return int(m.group(1)) if m else None
```

---

## 📄 PLIK: `core/image_processor.py`

```python
"""
core/image_processor.py
Analiza obrazów (PIL + NumPy)
"""

from PIL import Image
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analiza techniczna obrazów"""
    
    @staticmethod
    def analyze_image(image_path: str) -> dict:
        """Analiza szczegółowa obrazu"""
        try:
            img = Image.open(image_path)
            w, h = img.size
            format_img = img.format
            mode = img.mode
            
            if mode != 'RGB':
                img = img.convert('RGB')
            
            arr = np.array(img, dtype=np.uint8)
            
            r_mean = float(np.mean(arr[:,:,0]))
            g_mean = float(np.mean(arr[:,:,1]))
            b_mean = float(np.mean(arr[:,:,2]))
            luminance = 0.299*r_mean + 0.587*g_mean + 0.114*b_mean
            
            file_size = Path(image_path).stat().st_size / 1024
            
            return {
                "filename": Path(image_path).name,
                "format": format_img,
                "size_kb": round(file_size, 1),
                "width": w,
                "height": h,
                "megapixels": round(w*h / 1e6, 1),
                "r_avg": round(r_mean, 1),
                "g_avg": round(g_mean, 1),
                "b_avg": round(b_mean, 1),
                "luminance": round(luminance, 1),
                "aspect_ratio": round(w/h, 2),
            }
        except Exception as e:
            logger.error(f"Błąd analizy obrazu: {e}")
            return {"error": str(e)}


class DeepAttributeAnalyzer:
    """Heurystyczne rozpoznawanie atrybutów obrazu"""
    
    @staticmethod
    def analyze(image_path: str) -> dict:
        """Głębokie rozpoznawanie atrybutów"""
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            arr = np.array(img, dtype=np.uint8)
            
            detected = []
            
            # Detekcja osób
            has_person = DeepAttributeAnalyzer._detect_person(arr)
            if has_person:
                detected.append("osoba/osoby")
            
            # Kolory
            r_mean = float(np.mean(arr[:,:,0]))
            g_mean = float(np.mean(arr[:,:,1]))
            b_mean = float(np.mean(arr[:,:,2]))
            
            if r_mean > b_mean:
                detected.append("ciepłe tony")
            else:
                detected.append("chłodne tony")
            
            # Jasność
            brightness = 0.299*r_mean + 0.587*g_mean + 0.114*b_mean
            if brightness > 180:
                detected.append("jasne")
            elif brightness < 100:
                detected.append("ciemne")
            
            return {
                "detected": detected,
                "has_person": bool(has_person),
                "color_temp": "warm" if r_mean > b_mean else "cool",
                "brightness": "bright" if brightness > 180 else "dark" if brightness < 100 else "medium",
            }
        except Exception as e:
            logger.error(f"Błąd atrybutów: {e}")
            return {"detected": []}
    
    @staticmethod
    def _detect_person(arr: np.ndarray) -> bool:
        """Heurystyczna detekcja skóry"""
        try:
            r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
            
            skin_mask = (
                ((r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b)) |
                ((r > 150) & (g > 100) & (b > 60) & (r > g) & (r > b))
            )
            
            height, width = arr.shape[:2]
            skin_ratio = np.sum(skin_mask) / (height * width)
            
            return bool(skin_ratio > 0.10)
        except:
            return False
```

---

## 📄 PLIK: `utils/__init__.py`

```python
"""Utilities module"""
```

---

## 📄 PLIK: `utils/json_utils.py`

```python
"""
utils/json_utils.py
Bezpieczne obsługiwanie JSON (NumPy types)
"""

import json
import numpy as np
from pathlib import Path


class SafeJSONEncoder(json.JSONEncoder):
    """Encoder dla NumPy i innych specjalnych typów"""
    
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def safe_dumps(obj, **kwargs) -> str:
    """JSON.dumps ze zmiękczeniem typów NumPy"""
    return json.dumps(obj, cls=SafeJSONEncoder, ensure_ascii=False, **kwargs)


def safe_loads(s: str) -> dict:
    """Bezpieczne wczytanie JSON"""
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise ValueError(f"Błąd parsowania JSON: {e}")
```

---

## 📄 PLIK: `utils/regex_utils.py`

```python
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
```

---

## 📄 PLIK: `workers/__init__.py`

```python
"""Workers module (QThread workers)"""
```

---

## 📄 PLIK: `ui/__init__.py`

```python
"""UI module (PyQt5)"""
```

---

## 📄 PLIK: `ui/styles.py`

```python
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
```

---

## 📄 PLIK: `ui/main_window.py`

```python
"""
ui/main_window.py
Główne okno aplikacji PyQt5
"""

import logging
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
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
        
        # Centralna zakładka
        tabs = QTabWidget()
        
        # Placeholder dla przyszłych tabs
        placeholder = QWidget()
        placeholder_layout = QVBoxLayout()
        placeholder_layout.addWidget(
            QLabel("📦 Komponenty będą dodane w kolejnych fazach")
        )
        placeholder.setLayout(placeholder_layout)
        
        # Dodaj placeholder tabs
        tabs.addTab(placeholder, "✨ Wzbogacanie")
        tabs.addTab(QWidget(), "🤖 Ollama")
        tabs.addTab(QWidget(), "📚 Historia")
        tabs.addTab(QWidget(), "⚙️ Ustawienia")
        tabs.addTab(QWidget(), "ℹ️ O programie")
        
        self.setCentralWidget(tabs)
    
    def closeEvent(self, event):
        """Przed zamknięciem"""
        logger.info("Zamykanie aplikacji...")
        event.accept()


from PyQt5.QtWidgets import QLabel
```

---

## 🎯 PODSUMOWANIE STRUKTURY

Wszystkie pliki z kodami powyżej. Aby szybko je wdrożyć:

```bash
# 1. Stwórz strukturę
mkdir -p config core workers ui/{tabs,dialogs,widgets} utils tests
for dir in config core workers ui utils tests; do touch $dir/__init__.py; done

# 2. Skopiuj kod z sekcji do odpowiednich plików:
# config/constants.py      ← z dokumentu analiza-kompleksowa.md
# config/__init__.py       ← "PLIK: config/__init__.py" powyżej
# config/logging_config.py ← "PLIK: config/logging_config.py" powyżej
# ... itd

# 3. Uruchom
python3 main.py
```

---

**UWAGA:** Kompletny kod jest w osobnych dokumentach + sekcjach powyżej.
Kolejne pliki (workers, UI tabs) będą w kolejnych komunikatach.
