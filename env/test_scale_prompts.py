"""Compact scale-prompt probe: does explicit scale framing break 0.95 collapse?"""

import json
import os
import statistics

import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import MinMaxScaler

os.environ["LLM_CHOICE"] = "gpt-3.5-turbo"
os.environ.setdefault("OPENAI_API_KEY", "x")
import llm_shaping

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
DATA = os.path.join(ROOT, "Reward-Shaping-LLM", "ydata-labeled-time-series-anomalies-v1_0", "A1Benchmark")
BASE = "http://192.168.0.20:8001/v1"
MODEL = "llama-3.2-3b-instruct"
N = 10

SYS_BASE = 'Return ONLY JSON {"severity": s} with s in [0.0,1.0]. Never write code. '
SYS_SCALE = (
    SYS_BASE
    + 'Severity is a continuous scale. Use intermediate values, not just 0.00 or 0.95. '
    + 'Guidance: 0.00-0.20 certainly normal; 0.20-0.40 mild drift; 0.40-0.60 moderate; '
    + '0.60-0.80 sustained; 0.80-1.00 extreme. Normal windows must score below 0.30.'
)
SYS_INT = 'Return ONLY JSON {"severity": n} where n is an integer 0..100 on a continuous anomaly scale. Never write code.'
SYS_CUE = SYS_BASE + 'Output a single decimal number using the full scale. Do not copy the example values.'


def collect():
    normals, anomalies = [], []
    for fname in sorted(f for f in os.listdir(DATA) if f.endswith('.csv')):
        df = pd.read_csv(os.path.join(DATA, fname), usecols=[1, 2], header=0, names=['value', 'anomaly']).astype(np.float32)
        df['value'] = MinMaxScaler().fit_transform(df[['value']])
        vals, lab = df['value'].values, df['anomaly'].values
        for i in range(25, len(vals)):
            if lab[i] == 1 and len(anomalies) < N * 4:
                anomalies.append(vals[i - 25:i])
            elif lab[i] == 0 and len(normals) < N * 4:
                normals.append(vals[i - 25:i])
    return normals[:N], anomalies[:N]


def ask(w, system, suffix="", integer=False):
    z = llm_shaping._normalize_for_prompt(w)
    prompt = llm_shaping._build_prompt(', '.join(f'{v:.2f}' for v in z)) + suffix
    r = requests.post(BASE + '/chat/completions', json={
        'model': MODEL,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}],
        'temperature': 0.0, 'max_tokens': 64,
    }, timeout=30)
    r.raise_for_status()
    c = r.json()['choices'][0]['message'].get('content') or ''
    try:
        v = float(json.loads(c)['severity'])
        return (v / 100.0 if integer else v), c
    except Exception:
        return None, c


def run(name, normals, anomalies, system, suffix="", integer=False):
    ns, an, fails = [], [], 0
    for w in normals:
        s, _ = ask(w, system, suffix, integer)
        if s is None: fails += 1
        else: ns.append(s)
    for w in anomalies:
        s, _ = ask(w, system, suffix, integer)
        if s is None: fails += 1
        else: an.append(s)
    print(json.dumps({
        'name': name, 'fail': fails,
        'normal_mean': round(statistics.mean(ns), 3) if ns else None,
        'anomaly_mean': round(statistics.mean(an), 3) if an else None,
        'normal_vals': [round(x, 2) for x in ns],
        'anomaly_vals': [round(x, 2) for x in an],
    }), flush=True)


normals, anomalies = collect()
print('selected', len(normals), len(anomalies), flush=True)
run('scale_explicit', normals, anomalies, SYS_SCALE)
run('percent_int', normals, anomalies, SYS_INT, integer=True)
run('answer_cue', normals, anomalies, SYS_CUE, suffix='\n\nSeverity:')
