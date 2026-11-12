#!/bin/bash
# Run 5 heuristic-mock and 5 oracle-mock A1 runs, sequentially, in fresh copies.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
SRC="$ROOT/Reward-Shaping-LLM"

for tag in h1 h2 h3 h4 h5; do
  dst="$ROOT/run/mock_$tag"
  rm -rf "$dst"
  mkdir -p "$dst"
  rsync -a \
    --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
    --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
    "$SRC/" "$dst/repo/"
  MOCK_PORT=8765 "$ROOT/env/run_mock_a1.sh" "$dst/repo" > "$dst/run.log" 2>&1
  echo "finished $tag $(date -Is)"
done

for tag in o1 o2 o3 o4 o5; do
  dst="$ROOT/run/mock_$tag"
  rm -rf "$dst"
  mkdir -p "$dst"
  rsync -a \
    --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
    --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
    "$SRC/" "$dst/repo/"
  MOCK_PORT=8766 "$ROOT/env/run_mock_a1.sh" "$dst/repo" > "$dst/run.log" 2>&1
  echo "finished $tag $(date -Is)"
done

echo "SUITE DONE $(date -Is)"
