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