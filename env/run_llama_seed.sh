#!/bin/bash
# One seeded A1 run with remote Llama Instruct, raw-window shim.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
SEED="$1"
DST="$ROOT/run/llama_seed_$SEED"
SRC="$ROOT/Reward-Shaping-LLM"
rm -rf "$DST"
mkdir -p "$DST"
rsync -a \
  --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
  --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
  "$SRC/" "$DST/repo/"
export RSL_SEED="$SEED"
export RSL_RAW_WINDOWS=1
export PYTHONHASHSEED=0
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
"$ROOT/env/run_real_a1_remote.sh" "$DST/repo" > "$DST/run.log" 2>&1
echo "seed $SEED done at $(date -Is)"
