#!/bin/bash
# Real A1 run with phi-2 via the research code's local HF path.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
REPO="${1:-$ROOT/run/A1_winorder/repo}"
export PYTHONPATH="$ROOT/env"
export PYTHONDONTWRITEBYTECODE=1
export RSL_PRELOAD_TORCH=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TF_CPP_MIN_LOG_LEVEL=2
export OPENAI_API_KEY=unused
export LLM_CHOICE=phi-2
export PHI_DEBUG=1
cd "$REPO"
exec "$ROOT/.venv38/bin/python" myasp-A1.py
