#!/bin/bash

# Exit script on any error
set -e

echo "======================================"
echo "🚀 Starting APIFuzzer environment setup"
echo "======================================"

# Move to project root (2 levels up from this script's location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "[*] Changed working directory to project root: $PROJECT_ROOT"

# Define paths from project root
VENV_DIR="$PROJECT_ROOT/tools/api-fuzzer/.venv"
REQUIREMENTS_FILE="$PROJECT_ROOT/tools/api-fuzzer/requirements.txt"
APP_DIR="$PROJECT_ROOT/tools/api-fuzzer"
MODULES_DIR="$PROJECT_ROOT/modules"
APP_ENTRY="$APP_DIR/APIFuzzer.py"

echo "[*] Virtual environment directory: $VENV_DIR"
echo "[*] Requirements file: $REQUIREMENTS_FILE"
echo "[*] Application directory: $APP_DIR"
echo "[*] Modules directory: $MODULES_DIR"
echo "[*] Application entry point: $APP_ENTRY"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "[*] Creating virtual environment at $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
else
  echo "[*] Virtual environment already exists at $VENV_DIR"
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "[*] Python in use: $(which python)"
echo "[*] Pip in use: $(which pip)"

# Upgrade pip
echo "[*] Upgrading pip..."
pip install --upgrade pip

# Upgrade pip and setuptools
echo "[*] Upgrading pip and setuptools..."
pip install --upgrade pip setuptools

# Install requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "[*] Installing dependencies from $REQUIREMENTS_FILE..."
  pip install -r "$REQUIREMENTS_FILE"
else
  echo "[!] requirements.txt not found at $REQUIREMENTS_FILE"
  exit 1
fi

# Export paths
export PYTHONPATH="$PYTHONPATH:$APP_DIR:$MODULES_DIR"
export PATH="$PATH:$APP_DIR"

echo "[*] PYTHONPATH set to: $PYTHONPATH"
echo "[*] PATH set to: $PATH"

echo "======================================"
echo "✅ Environment setup complete"
echo "▶️ Launching APIFuzzer..."
echo "======================================"

# Load environment variables from .env if it exists
ENV_FILE="$APP_DIR/.env"
if [ -f "$ENV_FILE" ]; then
  echo "[*] Loading environment variables from $ENV_FILE"
  set -o allexport
  source "$ENV_FILE"
  set +o allexport
else
  echo "[!] .env file not found at $ENV_FILE — skipping"
fi

# Run the APIFuzzer
python tools/api-fuzzer/APIFuzzer.py --src_file data/openapi/openapi_mdr_v3.json -u https://mdr.api.secure-dev.services/ --log debug
