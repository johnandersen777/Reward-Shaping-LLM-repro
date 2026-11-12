"""Benchmark Bonsai llama-server on 20 fixed llm_shaping prompts.

Usage: bench_bonsai.py OUTPUT.json [BASE_URL]
Records wall time and llama-server timings for each prompt.
"""

import json
import os
import statistics
import sys
import time

import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import MinMaxScaler

os.environ["LLM_CHOICE"] = "gpt-3.5-turbo"
os.environ.setdefault("OPENAI_API_KEY", "unused")
import llm_shaping

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
DATA = os.path.join(ROOT, "Reward-Shaping-LLM", "ydata-labeled-time-series-anomalies-v1_0", "A1Benchmark")
OUT = sys.argv[1]
BASE = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8770"

prompts = []
for i in range(1, 21):
    path = os.path.join(DATA, f"real_{i}.csv")
    df = pd.read_csv(path, usecols=[1, 2], header=0, names=["value", "anomaly"]).astype(np.float32)
    df["value"] = MinMaxScaler().fit_transform(df[["value"]])
    vals = df["value"].values
    if len(vals) < 125:
        continue
    w = vals[100:125]
    z = llm_shaping._normalize_for_prompt(w)
    txt = ", ".join(f"{v:.2f}" for v in z)
    prompts.append(llm_shaping._build_prompt(txt))

records = []
for idx, prompt in enumerate(prompts):
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 32,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    t0 = time.time()
    resp = requests.post(BASE + "/v1/chat/completions", json=payload, timeout=600)
    wall_ms = (time.time() - t0) * 1000.0
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"].get("content") or ""
    timings = data.get("timings", {})
    usage = data.get("usage", {})
    records.append(
        {
            "i": idx,
            "wall_ms": round(wall_ms, 2),
            "content": content,
            "prompt_n": timings.get("prompt_n"),
            "prompt_ms": timings.get("prompt_ms"),
            "predicted_n": timings.get("predicted_n"),
            "predicted_ms": timings.get("predicted_ms"),
            "cached_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
        }
    )

with open(OUT, "w") as fh:
    json.dump(records, fh, indent=2)

walls = [r["wall_ms"] for r in records]
prompt_ms = [r["prompt_ms"] for r in records if r["prompt_ms"] is not None]
pred_ms = [r["predicted_ms"] for r in records if r["predicted_ms"] is not None]
print("n", len(records))
print("wall_ms mean", round(statistics.mean(walls), 1), "median", round(statistics.median(walls), 1))
print("prompt_ms mean", round(statistics.mean(prompt_ms), 1) if prompt_ms else None)
print("predicted_ms mean", round(statistics.mean(pred_ms), 1) if pred_ms else None)
print("cached_tokens", [r["cached_tokens"] for r in records])
print("contents", [r["content"] for r in records])
