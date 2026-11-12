#!/bin/bash
# Full A1 run with remote Llama via local proxy.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
REPO="${1:-$ROOT/run/A1_remote_llama/repo}"
export PYTHONPATH="$ROOT/env"
export PYTHONDONTWRITEBYTECODE=1
export TF_CPP_MIN_LOG_LEVEL=2
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
export OPENAI_API_KEY=mock-key
export OPENAI_BASE_URL="http://127.0.0.1:${PROXY_PORT:-8772}/v1"
export LLM_CHOICE=gpt-3.5-turbo
export PHI_DEBUG=1
cd "$REPO"
exec "$ROOT/.venv38/bin/python" myasp-A1.py
