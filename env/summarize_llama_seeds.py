"""Summarize every seeded Llama run. No filtering, no selection."""

import glob
import os
import re
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
PAT = re.compile(r"F1-score:([0-9.]+)")
PREC = re.compile(r"Precision:([0-9.]+)")
REC = re.compile(r"Recall:([0-9.]+)")

rows = []
for d in sorted(glob.glob(os.path.join(ROOT, "run", "llama_seed_*"))):
    seed = os.path.basename(d).replace("llama_seed_", "")
    perf = glob.glob(os.path.join(d, "repo", "exp", "*performance.txt"))
    if not perf:
        rows.append((seed, None, None, None, 0))
        continue
    text = open(perf[0]).read()
    f1 = [float(x) for x in PAT.findall(text)]
    p = [float(x) for x in PREC.findall(text)]
    r = [float(x) for x in REC.findall(text)]
    rows.append((seed, statistics.mean(f1) if f1 else None, statistics.mean(p) if p else None,
                 statistics.mean(r) if r else None, len(f1)))

vals = [row[1] for row in rows if row[1] is not None]
print("seed,mean_f1,mean_precision,mean_recall,episodes")
for seed, f1, p, r, n in rows:
    print(f"{seed},{'' if f1 is None else round(f1,6)},{'' if p is None else round(p,6)},"
          f"{'' if r is None else round(r,6)},{n}")

if vals:
    mean = statistics.mean(vals)
    std = statistics.pstdev(vals)
    med = statistics.median(vals)
    print(f"runs={len(vals)} mean={mean:.6f} std={std:.6f} median={med:.6f} min={min(vals):.6f} max={max(vals):.6f}")
    print(f"paper_llama_f1=0.7413 delta_mean={mean-0.7413:+.6f}")
    print(f"best_of_n={max(vals):.6f} n={len(vals)} (must be labeled best-of-N)")

csv_path = os.path.join(ROOT, "docs", "actions-takes", "llama_seed_results.csv")
with open(csv_path, "w") as fh:
    fh.write("seed,mean_f1,mean_precision,mean_recall,episodes\n")
    for seed, f1, p, r, n in rows:
        fh.write(f"{seed},{'' if f1 is None else f1:.6f},{'' if p is None else p:.6f},"
                 f"{'' if r is None else r:.6f},{n}\n")
print("saved", csv_path)

if vals:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(range(len(vals)), vals, marker="o", linestyle="-", label="all seeds")
    ax.axhline(0.7413, color="gray", linestyle="--", label="paper Llama 0.7413")
    ax.axhline(mean, color="tab:red", linestyle=":", label=f"seed mean {mean:.3f}")
    ax.set_xlabel("seed index")
    ax.set_ylabel("mean F1 over 6 validation series")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(ROOT, "docs", "actions-takes", "llama_seed_distribution.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("saved", out)
