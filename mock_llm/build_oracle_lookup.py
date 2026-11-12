"""Build a prompt-text -> ground-truth severity lookup for oracle mock mode.

Replicates env.py scaling and llm_shaping normalization exactly, then maps
each 25-value window's prompt text to the anomaly label of the window's last
timestamp (1.0 anomalous, 0.0 normal). Window text collisions are resolved to
the maximum label, and collision statistics are printed.
"""

import csv
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
DATA = os.path.join(
    ROOT, "Reward-Shaping-LLM", "ydata-labeled-time-series-anomalies-v1_0", "A1Benchmark"
)
OUT = os.path.join(ROOT, "mock_llm", "oracle_lookup.pkl")
N_STEPS = 25
ROUND_DIGITS = 2


def prompt_sequence(window):
    rounded = tuple(round(float(x), ROUND_DIGITS) for x in window)
    xs = np.asarray(rounded, dtype=float)
    mu = xs.mean()
    sd = xs.std()
    z = [0.0] * len(xs) if sd < 1e-8 else ((xs - mu) / sd).tolist()
    return ", ".join(f"{v:.2f}" for v in z)


lookup = {}
wins = 0
collisions = 0
conflicts = 0

for fname in sorted(f for f in os.listdir(DATA) if f.endswith(".csv")):
    df = pd.read_csv(os.path.join(DATA, fname), usecols=[1, 2], header=0, names=["value", "anomaly"])
    df = df.astype(np.float32)
    scaler = MinMaxScaler()
    df["value"] = scaler.fit_transform(df[["value"]])
    values = df["value"].values
    labels = df["anomaly"].values
    for i in range(len(values) - N_STEPS + 1):
        text = prompt_sequence(values[i : i + N_STEPS])
        label = float(labels[i + N_STEPS - 1])
        wins += 1
        if text in lookup:
            collisions += 1
            if lookup[text] != label:
                conflicts += 1
                lookup[text] = max(lookup[text], label)
        else:
            lookup[text] = label

with open(OUT, "wb") as fh:
    pickle.dump(lookup, fh, protocol=4)

pos = sum(1 for v in lookup.values() if v >= 0.5)
print(f"windows={wins} unique_texts={len(lookup)} collisions={collisions} conflicts={conflicts}")
print(f"anomalous_unique={pos} normal_unique={len(lookup)-pos}")
print(f"saved {OUT}")
