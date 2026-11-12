#!/bin/bash
# One budget-config seeded run. TAG unique. Original paper repo untouched.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TAG="$1"
SEED="$2"
EPISODES="$3"
EPOCHES="$4"
EPS_DECAY="$5"
DST="$ROOT/run/$TAG"
SRC="$ROOT/Reward-Shaping-LLM"
DATA="$SRC/ydata-labeled-time-series-anomalies-v1_0/A1Benchmark"

rm -rf "$DST"; mkdir -p "$DST"
rsync -a \
  --exclude '.git' --exclude '__pycache__' --exclude 'exp' \
  --exclude 'SMD' --exclude 'KPI_data' --exclude 'Figure' --exclude '.idea' \
  "$SRC/" "$DST/repo/"
"$ROOT/.venv38/bin/python" "$ROOT/env/instrument_checkpoint.py" "$DST/repo/myasp-A1.py"
"$ROOT/.venv38/bin/python" "$ROOT/env/instrument_training_budget.py" "$DST/repo/myasp-A1.py"
if [ -n "${RSL_VAE_COEF:-}" ]; then
  "$ROOT/.venv38/bin/python" "$ROOT/env/instrument_vae_coef.py" "$DST/repo/myasp-A1.py"
fi

find "$DATA" -maxdepth 1 -name '*.csv' -print0 | sort -z | xargs -0 sha256sum \
  > "$DST/data_manifest.sha256"

export RSL_SEED="$SEED"
export RSL_RAW_WINDOWS=1
export RSL_TEST=0
export PYTHONHASHSEED=0
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export RSL_SEED_LOG="$DST/seed_log.json"
export RSL_NUM_EPISODES="$EPISODES"
export RSL_NUM_EPOCHES="$EPOCHES"
export RSL_EPS_DECAY="$EPS_DECAY"

"$ROOT/.venv38/bin/python" - "$TAG" "$SEED" "$DST" "$ROOT" "$SRC" "$EPISODES" "$EPOCHES" "$EPS_DECAY" <<'PY'
import datetime, importlib.metadata as md, json, os, subprocess, sys
import requests
tag, seed, dst, root, src, ep, epochs, decay = sys.argv[1:9]
def ver(n):
    try: return md.version(n)
    except Exception: return None
def head(p):
    try: return subprocess.check_output(["git","-C",p,"rev-parse","HEAD"],text=True).strip()
    except Exception as e: return f"error: {e}"
try: proxy = requests.get("http://127.0.0.1:8772/health", timeout=5).json()
except Exception as e: proxy = {"error": str(e)}
meta = {
 "tag": tag, "seed": int(seed),
 "start_time_utc": datetime.datetime.utcnow().isoformat()+"Z",
 "host": os.uname().nodename,
 "paper_git_head": head(src), "parent_git_head": head(root),
 "budget": {"episodes": int(ep), "epoches": int(epochs), "eps_decay": int(decay)},
 "env": {k: os.environ.get(k) for k in ["RSL_SEED","RSL_RAW_WINDOWS","RSL_NUM_EPISODES","RSL_NUM_EPOCHES","RSL_EPS_DECAY","PYTHONHASHSEED","OMP_NUM_THREADS","OPENAI_BASE_URL","LLM_CHOICE"]},
 "proxy_health": proxy,
 "versions": {n: ver(n) for n in ["numpy","pandas","scipy","scikit-learn","tensorflow-cpu","torch","transformers","accelerate","openai"]},
}
json.dump(meta, open(os.path.join(dst,"meta.json"),"w"), indent=2, sort_keys=True)
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
import datetime, json, os, sys
dst, code = sys.argv[1], int(sys.argv[2])
p=os.path.join(dst,"meta.json"); d=json.load(open(p)); d["end_time_utc"]=datetime.datetime.utcnow().isoformat()+"Z"; d["exit_code"]=code
json.dump(d, open(p,"w"), indent=2, sort_keys=True)
PY
echo "$TAG done code=$RUN_CODE at $(date -Is)"
