#!/bin/bash
# Reload a saved checkpoint and run validation only.
# Usage: validate_llama_checkpoint.sh <tag>
# Legacy: numeric seed -> llama_seed_<N>
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
ARG="$1"
if [ -d "$ROOT/models/$ARG" ]; then
  TAG="$ARG"
elif [ -d "$ROOT/models/llama_seed_$ARG" ]; then
  TAG="llama_seed_$ARG"
else
  echo "missing models/$ARG or models/llama_seed_$ARG"; exit 1
fi
MODEL="$ROOT/models/$TAG"
[ -d "$MODEL/checkpoints" ] || { echo "missing checkpoint for $TAG"; exit 1; }

SEED="$("$ROOT/.venv38/bin/python" - "$MODEL/meta.json" "$TAG" <<'PY'
import json, re, sys
meta_path, tag = sys.argv[1], sys.argv[2]
try:
    print(int(json.load(open(meta_path))["seed"]))
except Exception:
    m = re.search(r"_s(\d+)$", tag)
    if not m:
        raise SystemExit("cannot determine seed for " + tag)
    print(int(m.group(1)))
PY
)"

DST="$ROOT/run/validate_$TAG"
SRC="$ROOT/Reward-Shaping-LLM"
rm -rf "$DST"; mkdir -p "$DST"
rsync -a \
  --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
  --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
  "$SRC/" "$DST/repo/"
"$ROOT/.venv38/bin/python" "$ROOT/env/instrument_checkpoint.py" "$DST/repo/myasp-A1.py"

EXP="$DST/repo/exp/A1_LP200_AL1000_d0.96"
mkdir -p "$EXP/checkpoints"
cp -a "$MODEL/checkpoints/." "$EXP/checkpoints/"
# Saved state file holds an absolute path from the machine that trained.
# Rewrite relative so the copy restores itself.
printf 'model_checkpoint_path: "model"\nall_model_checkpoint_paths: "model"\n' > "$EXP/checkpoints/checkpoint"

export RSL_SEED="$SEED"
export RSL_RAW_WINDOWS=1
export RSL_TEST=1
export PYTHONHASHSEED=0
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
"$ROOT/env/run_real_a1_remote.sh" "$DST/repo" > "$DST/run.log" 2>&1
PERF="$(find "$DST/repo/exp" -name '*performance.txt' -print -quit 2>/dev/null || true)"
[ -n "$PERF" ] && cp "$PERF" "$DST/performance.txt"
echo "validation $TAG done"
