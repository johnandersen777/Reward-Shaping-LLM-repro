#!/bin/bash
# Real A1 run with Instruct weights under the hardcoded Llama-3.2-3B path.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
REPO="${1:-$ROOT/run/A1_winorder/repo}"
export HOME="$ROOT/env/instructhome"
export PYTHONPATH="$ROOT/env"
export PYTHONDONTWRITEBYTECODE=1
export RSL_PRELOAD_TORCH=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TF_CPP_MIN_LOG_LEVEL=2
export OPENAI_API_KEY=unused
export LLM_CHOICE=llama-3
export PHI_DEBUG=1
cd "$REPO"
exec "$ROOT/.venv38/bin/python" myasp-A1.py
