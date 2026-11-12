#!/bin/bash
# One seeded A1 run with remote Llama Instruct, raw-window shim.
# Logs seed, RNG state, versions, proxy config, data manifest, all artifacts.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
SEED="$1"
DST="$ROOT/run/llama_seed_$SEED"
SRC="$ROOT/Reward-Shaping-LLM"
DATA="$SRC/ydata-labeled-time-series-anomalies-v1_0/A1Benchmark"

rm -rf "$DST"
mkdir -p "$DST"
rsync -a \
  --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
  --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
  "$SRC/" "$DST/repo/"

"$ROOT/.venv38/bin/python" "$ROOT/env/instrument_checkpoint.py" "$DST/repo/myasp-A1.py"

find "$DATA" -maxdepth 1 -name '*.csv' -print0 | sort -z | xargs -0 sha256sum \
  > "$DST/data_manifest.sha256"

export RSL_SEED="$SEED"
export RSL_RAW_WINDOWS=1
export RSL_TEST=0
export PYTHONHASHSEED=0
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
export RSL_SEED_LOG="$DST/seed_log.json"

"$ROOT/.venv38/bin/python" - "$SEED" "$DST" "$ROOT" "$SRC" <<'PY'
import datetime
import importlib.metadata as md
import json
import os
import subprocess
import sys

import requests

seed, dst, root, src = sys.argv[1:5]


def version(name):
    try:
        return md.version(name)
    except Exception:
        return None


def git_head(path):
    try:
        return subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip()
    except Exception as exc:
        return f"error: {exc}"


try:
    proxy = requests.get("http://127.0.0.1:8772/health", timeout=5).json()
except Exception as exc:
    proxy = {"error": str(exc)}

meta = {
    "seed": int(seed),
    "start_time_utc": datetime.datetime.utcnow().isoformat() + "Z",
    "host": os.uname().nodename,
    "cwd": os.getcwd(),
    "paper_git_head": git_head(src),
    "parent_git_head": git_head(root),
    "env": {
        "RSL_SEED": os.environ.get("RSL_SEED"),
        "RSL_RAW_WINDOWS": os.environ.get("RSL_RAW_WINDOWS"),
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
        "OPENAI_BASE_URL": os.environ.get("OPENAI_BASE_URL"),
        "LLM_CHOICE": os.environ.get("LLM_CHOICE"),
    },
    "proxy_health": proxy,
    "versions": {
        name: version(name)
        for name in [
            "numpy", "pandas", "scipy", "scikit-learn", "tensorflow-cpu",
            "torch", "transformers", "accelerate", "openai", "fastapi", "uvicorn",
        ]
    },
}
with open(os.path.join(dst, "meta.json"), "w") as fh:
    json.dump(meta, fh, indent=2, sort_keys=True)
PY

set +e
"$ROOT/env/run_real_a1_remote.sh" "$DST/repo" > "$DST/run.log" 2>&1
RUN_CODE=$?
set -e

PERF="$(find "$DST/repo/exp" -name '*performance.txt' -print -quit 2>/dev/null || true)"
[ -n "$PERF" ] && cp "$PERF" "$DST/performance.txt"
PHI="$(find "$DST/repo/exp" -name 'llm_potentials.csv' -print -quit 2>/dev/null || true)"
[ -n "$PHI" ] && cp "$PHI" "$DST/llm_potentials.csv"

"$ROOT/.venv38/bin/python" - "$DST" "$RUN_CODE" <<'PY'
import datetime
import json
import os
import sys

dst, code = sys.argv[1], int(sys.argv[2])
path = os.path.join(dst, "meta.json")
meta = json.load(open(path))
meta["end_time_utc"] = datetime.datetime.utcnow().isoformat() + "Z"
meta["exit_code"] = code
json.dump(meta, open(path, "w"), indent=2, sort_keys=True)
PY

echo "seed $SEED done code=$RUN_CODE at $(date -Is)"
