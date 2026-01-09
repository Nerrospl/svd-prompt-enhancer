#!/bin/bash
# setup.sh – Szybka instalacja SVD Prompt Enhancer Pro
# Usage: bash setup.sh

set -e  # Exit on error

echo "🚀 SVD Prompt Enhancer Pro v5.0 – Setup"
echo "=========================================="
echo ""

# Sprawdzenie Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie znaleziony!"
    echo "Zainstaluj: sudo apt install python3 python3-venv python3-dev"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION"

# Sprawdzenie Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama nie znaleziona!"
    echo "Zainstaluj: curl -fsSL https://ollama.com/install.sh | sh"
    echo "Następnie: sudo systemctl start ollama"
    exit 1
fi

OLLAMA_VERSION=$(ollama --version)
echo "✅ Ollama zainstalowana ($OLLAMA_VERSION)"

# Sprawdzenie statusu Ollama
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama nie odpowiada!"
    echo "Uruchom: sudo systemctl start ollama"
    exit 1
fi
echo "✅ Ollama działa (127.0.0.1:11434)"

# Stwórz venv
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Tworzę virtual environment..."
    python3 -m venv venv
    echo "✅ venv created"
fi

# Aktywuj venv
source venv/bin/activate
echo "✅ venv activated"

# Zainstaluj dependencje
echo ""
echo "📥 Instaluję dependencje..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencje zainstalowane"

# Stwórz strukturę katalogów
echo ""
echo "📁 Tworzę strukturę katalogów..."
mkdir -p config core workers ui/{tabs,dialogs,widgets} utils tests
for dir in config core workers ui utils tests; do
    touch "$dir/__init__.py"
done
echo "✅ Katalogi created"

echo ""
echo "=========================================="
echo "✅ Setup zakończony!"
echo ""
echo "🎯 Następne kroki:"
echo "  1. source venv/bin/activate       # Aktywuj venv"
echo "  2. python3 main.py                # Uruchom aplikację"
echo ""
echo "📚 Dokumentacja:"
echo "  README.md                         # Instrukcja użycia"
echo "  config/constants.py               # Konfiguracja (Q4/Q5/Q6 opcje!)"
echo ""
