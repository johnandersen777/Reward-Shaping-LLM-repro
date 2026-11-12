#!/bin/bash
# Reload a saved seed checkpoint and run validation only.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
SEED="$1"
MODEL="$ROOT/models/llama_seed_$SEED"
DST="$ROOT/run/validate_seed_$SEED"
SRC="$ROOT/Reward-Shaping-LLM"
[ -d "$MODEL/checkpoints" ] || { echo "missing checkpoint for seed $SEED"; exit 1; }

rm -rf "$DST"
mkdir -p "$DST"
rsync -a \
  --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
  --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
  "$SRC/" "$DST/repo/"
"$ROOT/.venv38/bin/python" "$ROOT/env/instrument_checkpoint.py" "$DST/repo/myasp-A1.py"

EXP="$DST/repo/exp/A1_LP200_AL1000_d0.96"
mkdir -p "$EXP/checkpoints"
cp -a "$MODEL/checkpoints/." "$EXP/checkpoints/"

export RSL_SEED="$SEED"
export RSL_RAW_WINDOWS=1
export RSL_TEST=1
export PYTHONHASHSEED=0
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
"$ROOT/env/run_real_a1_remote.sh" "$DST/repo" > "$DST/run.log" 2>&1
PERF="$(find "$DST/repo/exp" -name '*performance.txt' -print -quit 2>/dev/null || true)"
[ -n "$PERF" ] && cp "$PERF" "$DST/performance.txt"
echo "validation seed $SEED done"
