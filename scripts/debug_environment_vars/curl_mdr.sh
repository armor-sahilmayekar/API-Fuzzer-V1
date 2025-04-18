#!/usr/bin/env bash
echo "This script is a simple curl script to test your environment!"
echo "The environment file will need to have some requirec key=value pairs"
echo "Required Key TOKEN"
echo "Required Key MDR_API_HOST"
echo "Required Key ACCOUNT_ID"
echo "Optional Key LOG_LEVEL"
echo "Optional Key USER"
echo "Optional Key PASS"



source .env
MDR_API_HOST="https://mdr.api.secure-dev.services"

[ -z "$TOKEN" ] && echo "ERROR! TOKEN is not set" || echo "TOKEN is set"
[ -z "$ACCOUNT_ID" ] && echo "ERROR! ACCOUNT_ID is not set" || echo "ACCOUNT_ID is set"
[ -z "$MDR_API_HOST" ] && echo "ERROR! MDR_API_HOST is not set" || echo "MDR_API_HOST is set"

echo 'curl "${MDR_API_HOST}/metrics/incidents" '
echo "   -H "accept: application/json, text/plain, */*" "
echo "   -H 'accept-language: en-US,en;q=0.9' "
echo "   -H authorization: Bearer ${TOKEN} "
echo "   -H 'if-none-match: W/"1b0cd-mBw7Z/VQAsFNfEzG1bLwgN7+CR0"' "
echo "   -H internal: true "
echo "   -H origin: https://mdr.nexus.armor.com "
echo "   -H priority: u=1, i "
echo "   -H referer: https://mdr.nexus.armor.com/ "
echo "   -H x-account-context: ${ACCOUNT_ID}"

curl "${MDR_API_HOST}/metrics/incidents" \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H "authorization: Bearer ${TOKEN}" \
  -H 'if-none-match: W/"1b0cd-mBw7Z/VQAsFNfEzG1bLwgN7+CR0"' \
  -H 'internal: true' \
  -H 'origin: https://mdr.nexus.armor.com' \
  -H 'priority: u=1, i' \
  -H 'referer: https://mdr.nexus.armor.com/' \
  -H "x-account-context: ${ACCOUNT_ID}"
