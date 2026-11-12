"""Second calibration probe: prompt scale, sampling, longer reasoning, integer scale."""

import json
import os
import statistics

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
BASE = "http://192.168.0.20:8001/v1"
MODEL = "llama-3.2-3b-instruct"
N = 20

SYS_MIN = 'You are an anomaly severity judge. Return ONLY JSON {"severity": s} with s in [0.0,1.0]. Never write code.'
SYS_THINK = ('You are an anomaly severity judge. Compare the last value against the previous 24 values. '
             'Then output ONLY the final JSON {"severity": s} with s in [0.0,1.0].')
SYS_INT = 'You are an anomaly severity judge. Return ONLY JSON {"severity": n} with integer n in 0..100. Never write code.'


def collect():
    normals, anomalies = [], []
    for fname in sorted(f for f in os.listdir(DATA) if f.endswith('.csv')):
        df = pd.read_csv(os.path.join(DATA, fname), usecols=[1, 2], header=0, names=['value', 'anomaly']).astype(np.float32)
        df['value'] = MinMaxScaler().fit_transform(df[['value']])
        vals = df['value'].values
        lab = df['anomaly'].values
        for i in range(25, len(vals)):
            if lab[i] == 1 and len(anomalies) < N * 4:
                anomalies.append(vals[i - 25:i])
            elif lab[i] == 0 and len(normals) < N * 4:
                normals.append(vals[i - 25:i])
    def spread(xs, n):
        idx = np.linspace(0, len(xs) - 1, n).astype(int)
        return [xs[i] for i in idx]
    return spread(normals, N), spread(anomalies, N)


def prompt_for(w, raw):
    seq = w if raw else llm_shaping._normalize_for_prompt(w)
    return llm_shaping._build_prompt(', '.join(f'{v:.2f}' for v in seq))


def ask(w, system, raw=False, temperature=0.0, top_p=1.0, max_tokens=64):
    payload = {
        'model': MODEL,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt_for(w, raw)}],
        'temperature': temperature,
        'top_p': top_p,
        'max_tokens': max_tokens,
    }
    r = requests.post(BASE + '/chat/completions', json=payload, timeout=60)
    r.raise_for_status()
    c = r.json()['choices'][0]['message'].get('content') or ''
    try:
        v = float(json.loads(c)['severity'])
        return v / 100.0 if 'integer' in system else v, c
    except Exception:
        return None, c


def run(name, normals, anomalies, **kw):
    ns, an, fails = [], [], 0
    for w in normals:
        s, _ = ask(w, kw.pop('system', SYS_MIN), **kw) if False else ask(w, kw['system'], raw=kw.get('raw', False), temperature=kw.get('temperature', 0.0), top_p=kw.get('top_p', 1.0), max_tokens=kw.get('max_tokens', 64))
        if s is None: fails += 1
        else: ns.append(s)
    for w in anomalies:
        s, _ = ask(w, kw['system'], raw=kw.get('raw', False), temperature=kw.get('temperature', 0.0), top_p=kw.get('top_p', 1.0), max_tokens=kw.get('max_tokens', 64))
        if s is None: fails += 1
        else: an.append(s)
    out = {'name': name, 'fail': fails, 'normal_mean': round(statistics.mean(ns), 3) if ns else None,
           'anomaly_mean': round(statistics.mean(an), 3) if an else None,
           'normal_high': round(sum(x >= 0.9 for x in ns) / len(ns), 2) if ns else None,
           'anomaly_high': round(sum(x >= 0.9 for x in an) / len(an), 2) if an else None}
    if ns and an:
        u = mannwhitneyu(an, ns, alternative='greater')
        out['auc'] = round(float(u.statistic) / (len(ns) * len(an)), 3)
        out['p'] = round(float(u.pvalue), 4)
    print(json.dumps(out), flush=True)


normals, anomalies = collect()
print('selected', len(normals), len(anomalies), flush=True)
run('zscore_min', normals, anomalies, system=SYS_MIN)
run('raw_minmax', normals, anomalies, system=SYS_MIN, raw=True)
run('temp07', normals, anomalies, system=SYS_MIN, temperature=0.7, top_p=0.8)
run('long_think', normals, anomalies, system=SYS_THINK, max_tokens=256)
run('int100', normals, anomalies, system=SYS_INT)
