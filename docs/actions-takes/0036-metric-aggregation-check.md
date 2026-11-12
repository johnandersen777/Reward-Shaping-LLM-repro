# 0036 Metric Aggregation Check

Purpose: check if mean-of-episode F1 hides a higher pooled F1. Paper Table II reports P 0.6051, R 0.9565, F1 0.7413, which is a pooled-style triple.

## Method

Validator reports per-episode precision, recall, F1. Positives per test series are known:

```text
real_65  17
real_66  21
real_67  23
real_7   61
real_8   10
real_9    8
total   140
```

From recall: TP = recall * positives.

From precision: FP = TP * (1 - P) / P.

Sum over all 6 episodes, compute pooled P, R, F1.

## Result

| Tag | Mean F1 | Pooled P | Pooled R | Pooled F1 |
| --- | ---: | ---: | ---: | ---: |
| B200 | 0.4854 | 0.2033 | 0.6071 | 0.3047 |
| B205 | 0.4095 | 0.2069 | 0.3857 | 0.2693 |
| B207 | 0.3377 | 0.7500 | 0.1714 | 0.2791 |
| C200 | 0.3115 | 0.3510 | 0.3786 | 0.3643 |
| D200 | 0.4348 | 0.5632 | 0.3500 | 0.4317 |
| E200 | 0.4710 | 0.4097 | 0.4214 | 0.4155 |
| F200 | 0.4681 | 0.4146 | 0.4857 | 0.4474 |

Full table in `docs/actions-takes/0034-full-budget-search-state.md` runs.

## Conclusion

Pooled F1 is lower than mean-of-episode F1 for every run. Best pooled F1 is F200 0.4474.

No aggregation hides a 0.76 result. Code reports mean F1. Both are below target.

## Caveat

TP/FP reconstructed by rounding. Integer check passed for sampled runs. Not a substitute for saved prediction arrays.
