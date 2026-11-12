#!/bin/bash
# Copy one seed's checkpoint + logs into models/ and commit/push.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
SEED="$1"
SRC="$ROOT/run/llama_seed_$SEED"
DST="$ROOT/models/llama_seed_$SEED"
[ -d "$SRC" ] || exit 0
CKPT_DIR="$(find "$SRC/repo/exp" -type d -name checkpoints -print -quit 2>/dev/null || true)"
[ -n "$CKPT_DIR" ] || exit 0
rm -rf "$DST"
mkdir -p "$DST"
cp -a "$CKPT_DIR/." "$DST/checkpoints/"
for f in meta.json seed_log.json performance.txt llm_potentials.csv run.log; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$DST/$f"
done
cd "$ROOT"
git add "models/llama_seed_$SEED"
if git diff --cached --quiet; then
  echo "no checkpoint changes for seed $SEED"
  exit 0
fi
F1_LINE="$(grep -h 'Average F1' "$DST/run.log" 2>/dev/null | tail -1 || true)"
git commit -m "checkpoint: seed $SEED ${F1_LINE}

Co-Authored-By: Claude Code <noreply@anthropic.com>"
git push origin repro-setup
