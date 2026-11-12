# 0029 Budget C Result

Config C: 10 episodes, 100 updates/episode, epsilon decay 1000. Seed 200.

## F1

| Episode | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: |
| 1 | 0.0426 | 0.1176 | 0.0625 |
| 2 | 0.4000 | 0.4762 | 0.4348 |
| 3 | 0.7619 | 0.6957 | 0.7273 |
| 4 | 0.5789 | 0.3607 | 0.4444 |
| 5 | 0.1500 | 0.3000 | 0.2000 |
| 6 | 0.0000 | 0.0000 | 0.0000 |

```text
Average F1 = 0.3114999634021373
Max episode F1 = 0.7273
```

Below B config (0.4854). More episodes did not help this seed.

## Checkpoint

```text
models/budget_c10_e100_d1000_s200/checkpoints/
commit 00dc728
```

## Comparison

```text
paper Llama          0.7413
B: 5 ep, 100 upd     0.4854
C: 10 ep, 100 upd    0.3115
previous raw avg     0.4033
```

## Next

B seeds 201 and 202 running sequentially. All runs kept.
