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