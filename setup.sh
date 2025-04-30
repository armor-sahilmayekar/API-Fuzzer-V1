#!/usr/bin/env bash

pip3 install --upgrade pip
pip3 install --no-cache-dir  -r requirements.txt
pip3 install --no-cache-dir -r tools/api-fuzzer/requirements.txt
pip3 install --no-cache-dir -r tools/header-injector/word_fuzzer/requirements.txt
pip3 install --no-cache-dir -r tools/jwt-manipulator/jwt_inspection/requirements.txt
pip3 install --no-cache-dir -r tools/pyapi-validator/requirements.txt
pip3 install --no-cache-dir -r tools/spec-analyzer/requirements.txt
