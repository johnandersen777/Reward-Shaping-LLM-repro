#!/bin/bash
# Canary against Bonsai via the OpenAI-compatible proxy.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
export PYTHONPATH="$ROOT/run/A1_winorder/repo:$ROOT/env"
export PYTHONDONTWRITEBYTECODE=1
export OPENAI_API_KEY=mock-key
export OPENAI_BASE_URL="http://127.0.0.1:${PROXY_PORT:-8771}/v1"
export LLM_CHOICE=gpt-3.5-turbo
export PHI_DEBUG=1
exec "$ROOT/.venv38/bin/python" "$ROOT/env/check_llm.py"
