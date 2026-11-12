# 0030 Budget B/C Search Summary

All completed runs. No filtering.

## B config: 5 episodes, 100 updates, epsilon decay 500

| Tag | Seed | Mean F1 | Max episode F1 |
| --- | ---: | ---: | ---: |
| budget_b5_e100_d500_s200 | 200 | 0.485390 | 0.9362 |
| budget_b5_e100_d500_s201 | 201 | 0.000000 | 0.0000 |
| budget_b5_e100_d500_s202 | 202 | 0.151598 | 0.2597 |

B mean across seeds: 0.212329. B max: 0.485390.

## C config: 10 episodes, 100 updates, epsilon decay 1000

| Tag | Seed | Mean F1 | Max episode F1 |
| --- | ---: | ---: | ---: |
| budget_c10_e100_d1000_s200 | 200 | 0.311500 | 0.7273 |

## Baseline

```text
seed 0: 0.032482
seed 1: 0.165238
```

## Highest

```text
highest run average: 0.485390  budget_b5_e100_d500_s200
highest per-episode: 0.9362    same run, validation episode 3
```

Per-episode max is one validation series. Not a headline. Average is the honest metric.

No run average reaches 0.76 or paper 0.7413.

## Checkpoints

All committed under `models/<tag>/checkpoints/`.

```text
B200 17edcf2
B201 4c607cc
B202 fbff605
C200 00dc728
```

## Reload

```bash
env/validate_llama_checkpoint.sh budget_b5_e100_d500_s200
```

Seed 0 legacy checkpoint reload already proven exact. Budget-tag reload proof:

```text
Loading model checkpoint .../budget_b5_e100_d500_s200/checkpoints/model...
Average F1-score over 6 episodes: 0.4853906125529526
```

Original B200 average: 0.4853906125529526. Exact match. Per-episode F1 identical.

Artifact: `models/budget_b5_e100_d500_s200/validation_performance.txt`.

## Files

```text
docs/actions-takes/budget_results.csv
```

## Status

Search continues. Next candidate: 5 episodes, 500 updates, epsilon decay 2500, seed 200. Predeclared before run.
