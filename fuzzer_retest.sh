#!/bin/zsh

python3 tools/api-fuzzer/APIFuzzer.py \
  --src_file data/openapi_mdr_v3.json \
  --retest_dir reports/2025-04-30_16-15-23/Passed/401 \
  --status_code 401 \
  --alternate_url https://mdr.api.secure-dev.services/ \
  --log debug \
  -r ./reports