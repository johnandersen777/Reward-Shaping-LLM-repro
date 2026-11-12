#!/bin/bash
# 5 rates x 5 runs. Two workers in parallel.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TASKS=()
for spec in "n000:8781" "n010:8782" "n025:8783" "n050:8784" "n100:8785"; do
  tag="${spec%%:*}"
  port="${spec##*:}"
  for i in 1 2 3 4 5; do
    TASKS+=("${tag}_${i} ${port}")
  done
done
printf '%s\n' "${TASKS[@]}" | xargs -P 2 -n 2 bash -c '"$0/env/run_mock_one.sh" "$1" "$2"' "$ROOT"
echo "NOISY SUITE DONE $(date -Is)"
