#!/bin/bash
set -e

VENV_DIR=".venv"

# Create virtual environment if not exists
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

pip3 install --upgrade pip
pip3 install --no-cache-dir  -r requirements.txt
pip3 install --no-cache-dir -r tools/api-fuzzer/requirements.txt
pip3 install --no-cache-dir -r tools/header-injector/word_fuzzer/requirements.txt
pip3 install --no-cache-dir -r tools/jwt-manipulator/jwt_inspection/requirements.txt
pip3 install --no-cache-dir -r tools/pyapi-validator/requirements.txt
pip3 install --no-cache-dir -r tools/spec-analyzer/requirements.txt
