"""Summarize noisy-oracle suite and plot F1 vs wrong rate."""

import glob
import os
import re
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
PAT = re.compile(r"F1-score:([0-9.]+)")
RATES = [("n000", 0.0), ("n010", 0.10), ("n025", 0.25), ("n050", 0.50), ("n100", 1.00)]


def run_f1(path):
    perf = glob.glob(os.path.join(path, "repo", "exp", "*performance.txt"))
    if not perf:
        return None
    vals = []
    with open(perf[0]) as fh:
        for line in fh:
            m = PAT.search(line)
            if m:
                vals.append(float(m.group(1)))
    return statistics.mean(vals) if vals else None


results = {}
for tag, rate in RATES:
    vals = []
    for i in range(1, 6):
        v = run_f1(os.path.join(ROOT, "run", f"mock_{tag}_{i}"))
        if v is not None:
            vals.append(v)
    results[tag] = vals
    if vals:
        print(f"{tag} p={rate:.2f} n={len(vals)} mean={statistics.mean(vals):.4f} std={statistics.pstdev(vals):.4f} {[round(v,4) for v in vals]}")
    else:
        print(f"{tag} p={rate:.2f} no results")


def group(prefix, count=5):
    vals = []
    for i in range(1, count + 1):
        v = run_f1(os.path.join(ROOT, "run", f"mock_{prefix}{i}"))
        if v is not None:
            vals.append(v)
    return vals


heuristic = group("h")
oracle_bin = group("o")
if heuristic:
    print(f"heuristic binary mock n={len(heuristic)} mean={statistics.mean(heuristic):.4f} std={statistics.pstdev(heuristic):.4f}")
if oracle_bin:
    print(f"oracle binary n={len(oracle_bin)} mean={statistics.mean(oracle_bin):.4f} std={statistics.pstdev(oracle_bin):.4f}")

rows = []
for tag, rate in RATES:
    vals = results[tag]
    if vals:
        rows.append((rate, statistics.mean(vals), statistics.pstdev(vals), len(vals)))
csv_path = os.path.join(ROOT, "docs", "actions-takes", "noisy_oracle_results.csv")
with open(csv_path, "w") as fh:
    fh.write("wrong_rate,mean_f1,std_f1,n\n")
    for rate, mean, std, n in rows:
        fh.write(f"{rate:.2f},{mean:.6f},{std:.6f},{n}\n")
    if oracle_bin:
        fh.write(f"binary_oracle,{statistics.mean(oracle_bin):.6f},{statistics.pstdev(oracle_bin):.6f},{len(oracle_bin)}\n")

if rows:
    xs = [r[0] for r in rows]
    ys = [r[1] for r in rows]
    es = [r[2] for r in rows]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(xs, ys, yerr=es, marker="o", capsize=4, label="graded oracle")
    if oracle_bin:
        ax.axhline(statistics.mean(oracle_bin), color="gray", linestyle="--", label="binary oracle")
    if heuristic:
        ax.axhline(statistics.mean(heuristic), color="tab:red", linestyle=":", label="heuristic mock")
    ax.set_xlabel("wrong severity rate")
    ax.set_ylabel("mean F1 over 6 validation series")
    ax.set_title("A1 mock: F1 vs wrong LLM severity rate")
    ax.set_ylim(0, 0.5)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(ROOT, "docs", "actions-takes", "noisy_oracle_curve.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("saved", out)
print("saved", csv_path)
