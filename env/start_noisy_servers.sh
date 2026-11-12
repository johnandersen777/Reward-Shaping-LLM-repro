#!/bin/bash
# Start graded noisy-oracle servers. Rates: 0, 0.1, 0.25, 0.5, 1.0.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
cd "$ROOT/mock_llm"
PY="$ROOT/.venv38/bin/python"
start_one() {
  local port="$1" rate="$2" tag="$3"
  env MOCK_MODE=noisy_oracle \
    ORACLE_FLIP_RATE="$rate" \
    ORACLE_NOISE_SEED=0 \
    MOCK_LLM_LOG="$ROOT/mock_llm/noisy_${tag}.jsonl" \
    "$PY" -m uvicorn server:app --host 127.0.0.1 --port "$port" --log-level warning
}
start_one 8781 0.0  n000 &
start_one 8782 0.1  n010 &
start_one 8783 0.25 n025 &
start_one 8784 0.5  n050 &
start_one 8785 1.0  n100 &
wait
