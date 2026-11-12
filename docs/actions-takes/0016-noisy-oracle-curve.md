# 0016 Noisy Graded Oracle Curve

Purpose: measure F1 vs LLM-style wrongness. Graded severity, always JSON.

## Mode

`MOCK_MODE=noisy_oracle`. `ORACLE_FLIP_RATE` = wrong probability. Deterministic hash per prompt + seed.

Correct answer:

- anomaly: severity uniform 0.75-1.0
- normal: severity uniform 0.0-0.25

Wrong answer: opposite side, same ranges.

Formula:

```text
wrong    = hash(seed|flip|prompt) < rate
positive = (label >= 0.5) XOR wrong
severity = 0.75 + 0.25*hash(...)  if positive
         = 0.25*hash(...)         otherwise
```

Always serialized as `{"severity": <float>}`. Parser sees numeric severity. Fallback never fires.

Verified example: true normal, wrong rate 0.2 → `{"severity": 0.83}`.

## Rates And Runs

| Tag | Port | Wrong rate |
| --- | ---: | ---: |
| n000 | 8781 | 0.00 |
| n010 | 8782 | 0.10 |
| n025 | 8783 | 0.25 |
| n050 | 8784 | 0.50 |
| n100 | 8785 | 1.00 |

5 fresh runs each = 25 runs. Two workers in parallel.

Scripts:

```bash
env/start_noisy_servers.sh
env/run_noisy_suite.sh
```

Output: `run/mock_nXXX_Y/`. Log: `run/mock_nXXX_Y/run.log`.

## What It Measures

- n000 vs binary oracle baseline: effect of graded vs binary phi shape.
- n010-n100: sensitivity to wrong severity.

Binary oracle baseline o1-o5: mean 0.1716, std 0.1014.

Heuristic baseline h1-h5: mean 0.0687, std 0.1120.

## F1 Variance Note

F1 uses hard argmax predictions. Graded severity never enters F1 directly.

Graded vs binary changes reward deltas and Q targets:

- binary: zero delta most steps, ±0.96 jumps at boundaries
- graded: small nonzero deltas most steps

So shape can shift mean F1 and stability. Random run-to-run variance still comes from seeds, series order, replay sampling, AL, label propagation, epsilon near 1.

Five runs per rate. Report mean/std. Differences under ~0.1 hard to resolve.

## Results

| Wrong rate | Mean F1 | Std | n |
| ---: | ---: | ---: | ---: |
| 0.00 | 0.0479 | 0.0582 | 5 |
| 0.10 | 0.1303 | 0.0701 | 5 |
| 0.25 | 0.0519 | 0.0661 | 5 |
| 0.50 | 0.1239 | 0.1343 | 5 |
| 1.00 | 0.0784 | 0.1092 | 5 |

Baselines:

```text
binary oracle  0.1716 +/- 0.1014
heuristic mock 0.0687 +/- 0.1120
```

Files:

```text
docs/actions-takes/noisy_oracle_results.csv
docs/actions-takes/noisy_oracle_curve.svg
```

## Stats

```text
Kruskal-Wallis across 5 rates: p = 0.445
One-way ANOVA:                 p = 0.594
Binary oracle vs p=0.00:       Welch p = 0.076
Binary oracle vs others:       p = 0.089-0.587
```

No significant trend. Variance dominates. Wrong rate does not explain F1 here.

Binary oracle mean highest. Borderline vs graded-correct. n=5.

Interpretation: graded-correct scored lower than binary oracle on average. Wrong rates 0.1-1.0 overlap. Do not claim a curve from 5 runs per rate. Consistent with weak training dominating.
