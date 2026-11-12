#!/bin/bash
# Run the real local-Llama A1 pipeline in the pristine Windows-order copy.
# Usage: run_real_a1.sh [/path/to/repo-copy]
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
REPO="${1:-$ROOT/run/A1_winorder/repo}"
PY="$ROOT/.venv38/bin/python"
export PYTHONPATH="$ROOT/env"
export PYTHONDONTWRITEBYTECODE=1
export RSL_PRELOAD_TORCH=1
export TF_CPP_MIN_LOG_LEVEL=2
export OPENAI_API_KEY=unused
export LLM_CHOICE=llama-3
export PHI_DEBUG=1
cd "$REPO"
exec "$PY" myasp-A1.py
