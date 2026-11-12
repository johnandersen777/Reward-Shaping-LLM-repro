#!/bin/bash
# Commit one budget run's checkpoint and logs. Serialized with flock.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TAG="$1"
SRC="$ROOT/run/$TAG"
DST="$ROOT/models/$TAG"
[ -d "$SRC" ] || exit 0
CKPT_DIR="$(find "$SRC/repo/exp" -type d -name checkpoints -print -quit 2>/dev/null || true)"
[ -n "$CKPT_DIR" ] || exit 0
rm -rf "$DST"; mkdir -p "$DST"
cp -a "$CKPT_DIR/." "$DST/checkpoints/"
for f in meta.json seed_log.json performance.txt llm_potentials.csv run.log; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$DST/$f"
done
cd "$ROOT"
exec 9>/tmp/rsl_git.lock
flock 9
git add "models/$TAG"
if git diff --cached --quiet; then
  echo "no checkpoint changes for $TAG"; exit 0
fi
F1_LINE="$(grep -h 'Average F1' "$DST/run.log" 2>/dev/null | tail -1 || true)"
git commit -m "checkpoint: $TAG ${F1_LINE}

Co-Authored-By: Claude Code <noreply@anthropic.com>"
git push origin repro-setup
