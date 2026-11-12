#!/bin/bash
# Commit one per-episode checkpoint and its F1 row.
# Usage: commit_episode_checkpoint.sh <tag> <episode>
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TAG="$1"
EP4="$(printf '%04d' "$2")"
REL="models/$TAG"
CSV="$ROOT/$REL/episode_f1.csv"
F1="$(awk -F, -v e="ep$EP4" '$1==e{print $2}' "$CSV" 2>/dev/null | tail -1)"
MSG="checkpoint: $TAG ep$EP4 mean F1 ${F1:-unknown} (per-episode)"
export ROOT REL EP4 MSG
flock /tmp/rsl_git.lock bash -c '
  set -e
  cd "$ROOT"
  paths="$REL/episodes/ep$EP4 $REL/episode_f1.csv"
  [ -f "$REL/meta.json" ] && paths="$paths $REL/meta.json"
  git add $paths
  if git diff --cached --quiet; then echo "nothing to commit for ep$EP4"; exit 0; fi
  git commit -m "$MSG" -m "Co-Authored-By: Claude Code <noreply@anthropic.com>"
  git push origin HEAD
'
