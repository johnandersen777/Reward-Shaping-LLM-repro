"""Balanced calibration test for remote Llama Instruct judge.

Selects normal and anomalous windows across A1 series, asks for severity,
reports separation, high-score fraction, JSON parse failures.
"""

import json
import os
import statistics
import sys

import numpy as np
import pandas as pd
import requests
from scipy.stats import mannwhitneyu
from sklearn.preprocessing import MinMaxScaler

os.environ["LLM_CHOICE"] = "gpt-3.5-turbo"
os.environ.setdefault("OPENAI_API_KEY", "x")
import llm_shaping

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
DATA = os.path.join(ROOT, "Reward-Shaping-LLM", "ydata-labeled-time-series-anomalies-v1_0", "A1Benchmark")
BASE = os.environ.get("REMOTE_BASE_URL", "http://192.168.0.20:8001/v1")
MODEL = os.environ.get("REMOTE_MODEL", "llama-3.2-3b-instruct")
N = int(os.environ.get("N_PER_CLASS", "30"))

SYSTEMS = {
    "minimal": 'You are an anomaly severity judge. Return ONLY JSON {"severity": s} with s in [0.0,1.0]. Never write code.',
    "strict_scale": (
        'You are an anomaly severity judge. Return ONLY JSON {"severity": s} with s in [0.0,1.0]. '
        '0.00 means certainly normal noise. 0.95 means an extreme outlier. '
        'Do not default to high values. Judge the last value against the preceding 24 values. Never write code.'
    ),
    "zscore_last": (
        'You are an anomaly severity judge. The sequence is z-scored over 25 values: mean 0, std 1. '
        'Normal noise usually stays within [-2,2] and has no isolated jump at the last value. '
        'Score only the likelihood that the LAST value is anomalous compared with the previous 24. '
        '0.00 = certainly normal; 0.95 = extreme outlier. Return ONLY JSON {"severity": s}. Never write code.'
    ),
}


def collect():
    normals, anomalies = [], []
    files = sorted(f for f in os.listdir(DATA) if f.endswith(".csv"))
    for fname in files:
        df = pd.read_csv(os.path.join(DATA, fname), usecols=[1, 2], header=0, names=["value", "anomaly"]).astype(np.float32)
        df["value"] = MinMaxScaler().fit_transform(df[["value"]])
        vals = df["value"].values
        lab = df["anomaly"].values
        for i in range(25, len(vals)):
            w = vals[i - 25 : i]
            if lab[i] == 1 and len(anomalies) < N * 4:
                anomalies.append((fname, i, w))
            elif lab[i] == 0 and len(normals) < N * 4:
                normals.append((fname, i, w))
    # spread across series deterministically
    def spread(xs, n):
        if len(xs) <= n:
            return xs
        idx = np.linspace(0, len(xs) - 1, n).astype(int)
        return [xs[i] for i in idx]

    return spread(normals, N), spread(anomalies, N)


def ask(window, system):
    z = llm_shaping._normalize_for_prompt(window)
    prompt = llm_shaping._build_prompt(", ".join(f"{v:.2f}" for v in z))
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 64,
    }
    r = requests.post(BASE + "/chat/completions", json=payload, timeout=60)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"].get("content") or ""
    try:
        return float(json.loads(content)["severity"]), content
    except Exception:
        return None, content


def report(name, normals, anomalies):
    ns, an = [], []
    fails = 0
    for _, _, w in normals:
        s, _ = ask(w, SYSTEMS[name])
        if s is None:
            fails += 1
        else:
            ns.append(s)
    for _, _, w in anomalies:
        s, _ = ask(w, SYSTEMS[name])
        if s is None:
            fails += 1
        else:
            an.append(s)
    out = {
        "system": name,
        "n_normal": len(ns),
        "n_anomaly": len(an),
        "fail": fails,
        "normal_mean": round(statistics.mean(ns), 3) if ns else None,
        "normal_median": round(statistics.median(ns), 3) if ns else None,
        "anomaly_mean": round(statistics.mean(an), 3) if an else None,
        "anomaly_median": round(statistics.median(an), 3) if an else None,
        "normal_high_frac": round(sum(x >= 0.9 for x in ns) / len(ns), 3) if ns else None,
        "anomaly_high_frac": round(sum(x >= 0.9 for x in an) / len(an), 3) if an else None,
    }
    if ns and an:
        u = mannwhitneyu(an, ns, alternative="greater")
        out["auc"] = round(float(u.statistic) / (len(ns) * len(an)), 3)
        out["p_greater"] = round(float(u.pvalue), 4)
    print(json.dumps(out, sort_keys=True), flush=True)


normals, anomalies = collect()
print("selected", len(normals), "normal", len(anomalies), "anomaly", flush=True)
for name in SYSTEMS:
    report(name, normals, anomalies)
