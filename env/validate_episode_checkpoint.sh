#!/bin/bash
# Validate one per-episode checkpoint. Restore-only, no training.
# Usage: validate_episode_checkpoint.sh <tag> <episode>
# Reads models/<tag>/episodes/epNNNN/, writes row to models/<tag>/episode_f1.csv.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TAG="$1"
EP4="$(printf '%04d' "$2")"
MODEL="$ROOT/models/$TAG"
CKPT="$MODEL/episodes/ep$EP4"
CSV="$MODEL/episode_f1.csv"
[ -d "$CKPT" ] || { echo "missing checkpoint $CKPT"; exit 1; }
[ -f "$CKPT/model.index" ] || { echo "missing model.index in $CKPT"; exit 1; }

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

DST="$ROOT/run/validate_${TAG}_ep$EP4"
SRC="$ROOT/Reward-Shaping-LLM"
rm -rf "$DST"; mkdir -p "$DST"
rsync -a \
  --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
  --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
  "$SRC/" "$DST/repo/"
"$ROOT/.venv38/bin/python" "$ROOT/env/instrument_checkpoint.py" "$DST/repo/myasp-A1.py"

EXP="$DST/repo/exp/A1_LP200_AL1000_d0.96"
mkdir -p "$EXP/checkpoints"
cp -a "$CKPT/." "$EXP/checkpoints/"
# Saved state file holds an absolute path from the machine that trained.
# Rewrite relative so the copy restores itself.
printf 'model_checkpoint_path: "model"\nall_model_checkpoint_paths: "model"\n' > "$EXP/checkpoints/checkpoint"

export RSL_SEED="$SEED"
export RSL_RAW_WINDOWS=1
export RSL_TEST=1
export PYTHONHASHSEED=0
export OMP_NUM_THREADS="${RSL_VALIDATE_THREADS:-2}"
export TF_INTRA_OP_PARALLELISM_THREADS="$OMP_NUM_THREADS"
export TF_INTER_OP_PARALLELISM_THREADS="$OMP_NUM_THREADS"
# Training may use CPU; keep validation low priority.
nice -n "${RSL_VALIDATE_NICE:-19}" "$ROOT/env/run_real_a1_remote.sh" "$DST/repo" > "$DST/run.log" 2>&1
PERF="$(find "$DST/repo/exp" -name '*performance.txt' -print -quit 2>/dev/null || true)"
[ -n "$PERF" ] && cp "$PERF" "$DST/performance.txt"
[ -f "$DST/performance.txt" ] || { echo "validation $TAG ep$EP4 produced no performance.txt"; exit 1; }

ROW="$("$ROOT/.venv38/bin/python" - "$DST/performance.txt" "$EP4" <<'PY'
import datetime, re, sys
path, ep = sys.argv[1], sys.argv[2]
p, r, f = [], [], []
for line in open(path):
    m = re.search(r"Precision:([0-9.eE+-]+), Recall:([0-9.eE+-]+), F1-score:([0-9.eE+-]+)", line)
    if m:
        p.append(float(m.group(1))); r.append(float(m.group(2))); f.append(float(m.group(3)))
if not f:
    raise SystemExit("no episodes parsed from " + path)
mean = lambda xs: sum(xs) / len(xs)
ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
print("ep%s,%.6f,%.6f,%.6f,%.6f,%s" % (ep, mean(f), max(f), mean(p), mean(r), ts))
PY
)"

if [ ! -f "$CSV" ]; then
  echo "episode,mean_f1,max_f1,mean_precision,mean_recall,timestamp" > "$CSV"
fi
export ROW CSV
flock "$CSV.lock" bash -c 'printf "%s\n" "$ROW" >> "$CSV"'
echo "validation $TAG ep$EP4: $ROW"
