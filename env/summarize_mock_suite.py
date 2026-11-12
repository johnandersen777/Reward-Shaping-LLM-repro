"""Summarize the 10-run mock suite: per-run F1 and group mean/std."""

import glob
import os
import re
import statistics

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
PAT = re.compile(r"F1-score:([0-9.]+)")

groups = {"heuristic": [], "oracle": []}
for prefix, group in (("h", "heuristic"), ("o", "oracle")):
    for i in range(1, 6):
        d = os.path.join(ROOT, "run", f"mock_{prefix}{i}")
        perf = glob.glob(os.path.join(d, "repo", "exp", "*performance.txt"))
        f1s = []
        if perf:
            with open(perf[0]) as fh:
                for line in fh:
                    m = PAT.search(line)
                    if m:
                        f1s.append(float(m.group(1)))
        done = os.path.exists(os.path.join(d, "repo", "exp", "A1_LP200_AL1000_d0.96", "llm_potentials.csv"))
        mean = statistics.mean(f1s) if f1s else float("nan")
        groups[group].append(mean)
        print(f"{prefix}{i}: episodes={len(f1s)} mean_f1={mean:.4f} done={done} f1s={[round(x,3) for x in f1s]}")

for group, vals in groups.items():
    ok = [v for v in vals if v == v]
    if ok:
        print(f"{group}: n={len(ok)} mean={statistics.mean(ok):.4f} std={statistics.pstdev(ok):.4f} min={min(ok):.4f} max={max(ok):.4f}")
