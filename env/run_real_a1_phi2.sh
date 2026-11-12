#!/bin/bash
# Real A1 run with phi-2 via the research code's local HF path.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
REPO="${1:-$ROOT/run/A1_phi2/repo}"
export PYTHONPATH="$ROOT/env"
export PYTHONDONTWRITEBYTECODE=1
export RSL_PRELOAD_TORCH=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TF_CPP_MIN_LOG_LEVEL=2
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-12}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-12}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-12}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-12}"
export TOKENIZERS_PARALLELISM=false
export OPENAI_API_KEY=unused
export LLM_CHOICE=phi-2
export PHI_DEBUG=1
cd "$REPO"
exec "$ROOT/.venv38/bin/python" myasp-A1.py
