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