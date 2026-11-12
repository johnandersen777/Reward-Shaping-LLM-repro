#!/bin/bash
# Start PrismML llama-server with Ternary-Bonsai MTP Q8_0.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
MODEL="$HOME/models/Ternary-Bonsai-2-9B-gguf/Ternary-Bonsai-2-9B-PQ2_0-MTP-Q8_0.gguf"
export LD_LIBRARY_PATH="$ROOT/llama-cuda12libs/nvidia/cuda_runtime/lib:$ROOT/llama-cuda12libs/nvidia/cublas/lib:${LD_LIBRARY_PATH:-}"
BIN="${BIN:-$HOME/llama.cpp-prism/llama-prism-b10776-d00e252/llama-server}"
if [ ! -x "$BIN" ]; then
  BIN="$(find "$HOME/llama.cpp-prism" -type f -name llama-server | head -1)"
fi
EXTRA=()
if [ -n "${CACHE_REUSE:-}" ]; then
  EXTRA+=(--cache-reuse "$CACHE_REUSE")
fi
exec "$BIN" \
  -m "$MODEL" \
  -ngl 99 -fa on \
  --spec-type draft-mtp --spec-draft-n-max 2 --spec-draft-n-min 0 --spec-draft-p-min 0 \
  -c 2048 -t 8 \
  --host 127.0.0.1 --port "${PORT:-8770}" \
  --no-webui \
  --temp 0.0 --top-k 1 --top-p 1.0 "${EXTRA[@]}"
