#!/bin/bash
# One fresh mock A1 run against a given mock server port.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TAG="$1"
PORT="$2"
DST="$ROOT/run/mock_$TAG"
SRC="$ROOT/Reward-Shaping-LLM"
rm -rf "$DST"
mkdir -p "$DST"
rsync -a \
  --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
  --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
  "$SRC/" "$DST/repo/"
MOCK_PORT="$PORT" "$ROOT/env/run_mock_a1.sh" "$DST/repo" > "$DST/run.log" 2>&1
echo "finished $TAG at $(date -Is)"
