# SVD Prompt Enhancer Pro v5.0

🎬 **Zaawansowana lokalnie aplikacja do wzbogacania promptów dla SVD/SDXL** 

Napisana w **PyQt5** z obsługą **Ollama** na karcie graficznej (RTX 2060 6GB+)

## ✨ Główne cechy

- ✅ **Analiza obrazów** – LLaVA analizuje obrazy lokalnie
- ✅ **Wzbogacanie promptów** – Dolphin-LLaVA/Mistral generuje szczegółowe prompty (PL + EN)
- ✅ **Bez cenzury** – Modele bez filtrów (Dolphin 3.0)
- ✅ **Zarządzanie Ollama** – Pobieranie, usuwanie, zwolnianie modelów z UI
- ✅ **Historia** – SQLite baza danych wszystkich promptów
- ✅ **Wielojęzyczność** – Polski + Angielski
- ✅ **Konfiguracja sprzętu** – Opcja wyboru Q4/Q5/Q6 modeli
- ✅ **XDG Standard** – Konfiguracja w `~/.config/`, dane w `~/.local/share/`

## 📋 Wymagania

- **Pop!_OS 22.04+** (lub inny Linux)
- **Python 3.10+**
- **Ollama** zainstalowana i uruchomiona
- **GPU:** RTX 2060 6GB+ (CUDA 11.8+) lub CPU mode

## 🚀 Szybki start

### 1. Zainstaluj Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama
sudo systemctl enable ollama
```

### 2. Pobierz modele

```bash
# Model do analizy obrazów (WYMAGANY)
ollama pull llava:latest

# Model do wzbogacania promptu (rekomendowany bez cenzury)
ollama pull dolphin-llama3:latest

# Fallback (jeśli RTX 2060 nie starczy)
ollama pull mistral:latest
```

### 3. Zainstaluj aplikację

```bash
# Clone repo
git clone <repo_url>
cd svd-prompt-enhancer

# Wirtualne środowisko
python3 -m venv venv
source venv/bin/activate

# Zależności
pip install -r requirements.txt

# Uruchom
python3 main.py
```

## 📊 Specyfikacja dla Twojego sprzętu

| Komponent | Specyfikacja |
|-----------|-------------|
| **GPU** | RTX 2060 6GB GDDR6 |
| **RAM** | 37GB (dostępna) |
| **OS** | Pop!_OS (Linux) |
| **CUDA** | 11.8+ |

### Rekomendowane modele

| Model | VRAM (Q4) | Zastosowanie | Status |
|-------|-----------|-------------|--------|
| `llava:latest` | 5.5GB | Analiza obrazów | ✅ WYMAGANY |
| `dolphin-llama3:latest` | 5.2GB | Wzbogacanie (bez cenzury) | ✅ GŁÓWNY |
| `mistral:latest` | 4.5GB | Fallback wzbogacania | ✅ REZERWA |

**Timeout'i:**
- Analiza obrazu: 600s (10 min)
- Wzbogacanie promptu: 300s (5 min)
- Tłumaczenia: 180s (3 min)

## 🎯 Użycie

1. **Wczytaj obraz** – kliknij "Wybierz obraz"
2. **Wpisz prompt** – opisz co chcesz wygenerować (PL lub EN)
3. **Analizuj** – system przeanalizuje obraz (LLaVA)
4. **Wzbogać** – model wzbogaci Twój prompt (Dolphin/Mistral)
5. **Tłumacz** – opcjonalnie przełącz między PL/EN
6. **Zapisz** – dodaj do historii lub skopiuj

## 🔧 Zarządzanie modelami

W zakładce **"🤖 Ollama"** możesz:
- Sprawdzić status Ollama
- Zobaczyć zainstalowane modele
- Pobrać nowe modele (Q4, Q5, Q6 – dostosuj do sprzętu)
- Zwolnić modele z VRAM (unload)
- Usunąć modele z dysku
- Zrestartować serwer

### Opcje kwantyzacji:

| Kwantyzacja | VRAM (7B) | Jakość | Szybkość |
|------------|-----------|--------|----------|
| **Q4** | 4-5GB | Dobra | Szybka ✅ |
| **Q5** | 6-7GB | Lepsza | Średnia |
| **Q6** | 8-10GB | Najlepsza | Wolna |

**Dla RTX 2060 6GB rekomendujemy Q4.**

## 📁 Struktura projektu

```
svd-prompt-enhancer/
├── main.py                          # Entry point
├── requirements.txt
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── constants.py                 # Konfiguracja, modele, ścieżki
│   └── logging_config.py
│
├── core/
│   ├── __init__.py
│   ├── ollama_manager.py            # HTTP API do Ollama
│   ├── image_processor.py           # PIL + NumPy analiza
│   ├── prompt_enhancer.py           # Logika wzbogacania
│   ├── translator.py                # Tłumaczenia EN ↔ PL
│   └── storage.py                   # SQLite + FileLogger
│
├── workers/
│   ├── __init__.py
│   ├── image_analysis_worker.py     # QThread do analizy
│   ├── enhancement_worker.py        # QThread do wzbogacania
│   └── translation_worker.py        # QThread do tłumaczeń
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── styles.py
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── enhance_tab.py           # TAB 1: Główny (analiza + wzbogacanie)
│   │   ├── ollama_control_tab.py    # TAB 2: Zarządzanie modelami
│   │   ├── history_tab.py           # TAB 3: Historia SQLite
│   │   ├── settings_tab.py          # TAB 4: Ustawienia
│   │   └── info_tab.py              # TAB 5: O programie
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── model_download_dialog.py
│   │   └── prompt_editor_dialog.py
│   └── widgets/
│       └── __init__.py
│
└── utils/
    ├── __init__.py
    ├── json_utils.py                # SafeJSONEncoder
    ├── regex_utils.py               # JSON extraction
    ├── path_utils.py                # XDG paths
    └── language_utils.py            # i18n: Translator
```

## 🐛 Troubleshooting

### Ollama nie odpowiada
```bash
# Sprawdzanie statusu
curl http://127.0.0.1:11434/api/tags

# Restart
sudo systemctl restart ollama

# Logi
journalctl -u ollama -f
```

### RTX 2060 jest wolna
- Zmniejsz rozmiar promptu
- Zwiększ timeout w ustawieniach
- Wybierz Q4 (zamiast Q5/Q6)
- Zwolnij inne procesy z VRAM

### Model zwisł
Kliknij "Unload Model" w karcie Ollama – zwalnia VRAM bez usuwania

## 📝 Logs

Logi aplikacji zapisywane do:
```
~/.local/share/svd_enhancer/logs/app.log
```

Zamiast systemd:
```
journalctl -u ollama -f  # Logi Ollama
```

## 📚 Dokumentacja

- **config/constants.py** – wszystkie stałe i konfiguracja
- **core/ollama_manager.py** – API do Ollama
- **workers/** – QThread workers (asynchroniczne przetwarzanie)
- **ui/** – PyQt5 interfejs

## 🤝 Wsparcie

Jeśli coś nie działa:
1. Sprawdź logi: `tail -f ~/.local/share/svd_enhancer/logs/app.log`
2. Upewnij się że Ollama działa: `ollama list`
3. Sprawdź VRAM: `nvidia-smi`
4. Zrestartuj aplikację

## 📄 Licencja

MIT License – możesz używać, modyfikować, rozpowszechniać

## 🎯 Plany na przyszłość

- [ ] Batch processing (wiele obrazów naraz)
- [ ] Export do Markdown/JSON
- [ ] Integracja z generatorami (API call)
- [ ] Profiles szybkie (presets dla różnych celów)
- [ ] WebUI (FastAPI)

---

**Wersja:** 5.0 | **Data:** 2026-01-06 | **Platform:** Linux/Pop!_OS
