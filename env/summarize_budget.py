"""Summarize every budget run. No filtering, no selection."""

import glob
import os
import re
import statistics

ROOT = "/home/baptist777/.tmp/tmp.VjJfPBPNr4"
PAT = re.compile(r"F1-score:([0-9.]+)")
PREC = re.compile(r"Precision:([0-9.]+)")
REC = re.compile(r"Recall:([0-9.]+)")


def config_of(tag):
    if tag.startswith("budget_b5"):
        return "B: 5 ep, 100 upd, decay 500"
    if tag.startswith("budget_c10_e100"):
        return "C: 10 ep, 100 upd, decay 1000"
    if tag.startswith("budget_d10_e200"):
        return "D: 10 ep, 200 upd, decay 1000"
    return tag


rows = []
for perf in sorted(glob.glob(os.path.join(ROOT, "run", "budget_*", "performance.txt"))):
    tag = os.path.basename(os.path.dirname(perf))
    text = open(perf).read()
    f1 = [float(x) for x in PAT.findall(text)]
    p = [float(x) for x in PREC.findall(text)]
    r = [float(x) for x in REC.findall(text)]
    if not f1:
        continue
    rows.append((tag, config_of(tag), statistics.mean(f1), statistics.mean(p), statistics.mean(r), len(f1), max(f1)))

print("tag,config,mean_f1,mean_precision,mean_recall,episodes,max_episode_f1")
for tag, cfg, f1, p, r, n, mx in rows:
    print(f"{tag},{cfg},{f1:.6f},{p:.6f},{r:.6f},{n},{mx:.6f}")

by_cfg = {}
for tag, cfg, f1, p, r, n, mx in rows:
    by_cfg.setdefault(cfg, []).append(f1)
print()
for cfg, vals in by_cfg.items():
    print(f"{cfg}: n={len(vals)} mean={statistics.mean(vals):.6f} std={statistics.pstdev(vals):.6f} "
          f"min={min(vals):.6f} max={max(vals):.6f}")
if rows:
    allv = [row[2] for row in rows]
    best = max(rows, key=lambda row: row[2])
    print()
    print(f"best_of_n={best[2]:.6f} tag={best[0]} config={best[1]} n={len(rows)}")
    print(f"paper_llama=0.7413 delta_best={best[2]-0.7413:+.6f}")
    print(f"runs_over_0.76={sum(1 for v in allv if v >= 0.76)}")

csv_path = os.path.join(ROOT, "docs", "actions-takes", "budget_results.csv")
with open(csv_path, "w") as fh:
    fh.write("tag,config,mean_f1,mean_precision,mean_recall,episodes,max_episode_f1\n")
    for tag, cfg, f1, p, r, n, mx in rows:
        fh.write(f"{tag},{cfg},{f1:.6f},{p:.6f},{r:.6f},{n},{mx:.6f}\n")
print("saved", csv_path)
