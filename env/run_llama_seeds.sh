#!/bin/bash
# Fixed seed list. All runs kept. No filtering.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
N="${1:-10}"
for seed in $(seq 0 $((N - 1))); do
  echo "starting seed $seed"
  "$ROOT/env/run_llama_seed.sh" "$seed"
done
echo "LLAMA SEED SUITE DONE $(date -Is)"
