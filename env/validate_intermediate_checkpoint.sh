#!/bin/bash
# Wait for a run's first intermediate checkpoint (paper code saves at
# i_episode % 50 == 49), snapshot it under its own tag, validate, commit.
# Usage: validate_intermediate_checkpoint.sh <run-tag> <snapshot-tag>
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TAG="$1"
SNAP="$2"
RUN="$ROOT/run/$TAG"
MODEL="$ROOT/models/$SNAP"
LOG="$RUN/intermediate_validate.log"
mkdir -p "$RUN"
echo "waiting for $TAG checkpoint $(date -Is)" >> "$LOG"
until ls "$RUN"/repo/exp/*/checkpoints/model.index >/dev/null 2>&1; do sleep 30; done
CKPT_DIR="$(dirname "$(ls "$RUN"/repo/exp/*/checkpoints/model.index | head -1)")"
mkdir -p "$MODEL/checkpoints"
cp -a "$CKPT_DIR/model.data-00000-of-00001" "$CKPT_DIR/model.index" "$MODEL/checkpoints/"
printf 'model_checkpoint_path: "model"\nall_model_checkpoint_paths: "model"\n' > "$MODEL/checkpoints/checkpoint"
cp "$RUN/meta.json" "$MODEL/meta.json"
echo "copied checkpoint from $CKPT_DIR $(date -Is)" >> "$LOG"
"$ROOT/env/validate_llama_checkpoint.sh" "$SNAP" >> "$LOG" 2>&1
cp "$ROOT/run/validate_$SNAP/performance.txt" "$MODEL/validation_performance.txt"
cp "$ROOT/run/validate_$SNAP/run.log" "$MODEL/validation_run.log"
F1="$(grep -h 'Average F1' "$MODEL/validation_run.log" | tail -1)"
export ROOT SNAP F1
flock /tmp/rsl_git.lock bash -c '
  set -e
  cd "$ROOT"
  git add "models/$SNAP"
  if git diff --cached --quiet; then echo "nothing to commit for $SNAP"; exit 0; fi
  git commit -m "checkpoint: $SNAP ${F1:-unknown F1} (intermediate)" -m "Co-Authored-By: Claude Code <noreply@anthropic.com>"
  git push origin repro-setup
' >> "$LOG" 2>&1
echo "intermediate validation done: $F1 $(date -Is)" >> "$LOG"
