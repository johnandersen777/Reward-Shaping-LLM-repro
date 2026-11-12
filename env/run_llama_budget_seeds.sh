#!/bin/bash
# Predeclared training-budget grid. 3 configs x 3 seeds, 3 workers.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
CONFIGS=(
  "budget_b5_e100_d500 5 100 500"
  "budget_c10_e100_d1000 10 100 1000"
  "budget_d10_e200_d1000 10 200 1000"
)
SEEDS=(200 201 202)
TASKS=()
for cfg in "${CONFIGS[@]}"; do
  read -r name ep epochs decay <<< "$cfg"
  for seed in "${SEEDS[@]}"; do
    tag="${name}_s${seed}"
    TASKS+=("$tag $seed $ep $epochs $decay")
  done
done
printf '%s\n' "${TASKS[@]}" | xargs -P 3 -n 5 bash -c '
  ROOT="$0"
  tag="$1"; seed="$2"; ep="$3"; epochs="$4"; decay="$5"
  "$ROOT/env/run_llama_budget_seed.sh" "$tag" "$seed" "$ep" "$epochs" "$decay" || echo "$tag failed"
  "$ROOT/env/commit_budget_artifact.sh" "$tag" || echo "$tag commit failed"
' "$ROOT"
echo "BUDGET SUITE DONE $(date -Is)"
