# 0033 Budget B Extended Search

All B seeds 200-205. No filtering.

## B config: 5 episodes, 100 updates, decay 500

| Seed | Mean F1 | Max episode F1 |
| ---: | ---: | ---: |
| 200 | 0.485391 | 0.9362 |
| 201 | 0.000000 | 0.0000 |
| 202 | 0.151598 | 0.2597 |
| 203 | 0.071702 | 0.1818 |
| 204 | 0.074126 | 0.2308 |
| 205 | 0.409537 | 0.7222 |

```text
B n=6 mean=0.198726 std=0.182570 min=0.0 max=0.485391
```

## Other configs

| Config | Mean F1 | Max episode |
| --- | ---: | ---: |
| C: 10 ep, 100 upd | 0.311500 | 0.7273 |
| E: 5 ep, 500 upd | 0.470956 | 0.7692 |
| F: no VAE | 0.468059 | 0.7556 |

## Best Honest Result

```text
highest run average: 0.485391  B200
runs with average >= 0.76: 0
highest per-episode: 0.9362  B200 episode 3
```

Per-episode max is one validation series. Not a headline. Average is the honest metric.

## Checkpoints

All under `models/<tag>/checkpoints/`.

```text
B200 17edcf2
B201 4c607cc
B202 fbff605
B203 827f9d4
B204 aec878b
B205 e036bb1
C200 00dc728
E200 074a7e8
F200 ec360c0
```

B200 reload validation exact: `models/budget_b5_e100_d500_s200/validation_performance.txt`.

## Status

D config running: 10 episodes, 200 updates, decay 1000, seed 200.

Honest limit: no run average reaches 0.76. Best average 0.4854. More seeds are the only honest lever left without changing the method.
