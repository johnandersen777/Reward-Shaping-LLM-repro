# 0028 Budget B Result

Config B: 5 episodes, 100 updates/episode, epsilon decay 500. Seed 200.

## F1

| Episode | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: |
| 1 | 0.1389 | 0.5882 | 0.2247 |
| 2 | 0.6333 | 0.9048 | 0.7451 |
| 3 | 0.9167 | 0.9565 | 0.9362 |
| 4 | 0.0852 | 0.3770 | 0.1390 |
| 5 | 0.4762 | 1.0000 | 0.6452 |
| 6 | 1.0000 | 0.1250 | 0.2222 |

```text
Average F1 = 0.4853906125529526
Max episode F1 = 0.9362
```

Max episode is one validation series. Headline is the average. Not cherry-picked.

Paper Llama: 0.7413. Still below.

## Checkpoint

```text
models/budget_b5_e100_d500_s200/checkpoints/
commit 17edcf2
```

Reload:

```bash
env/validate_llama_checkpoint.sh budget_b5_e100_d500_s200
```

Note: validation script expects `models/<tag>/checkpoints`; tag here is the model dir name.

## Comparison

```text
paper Llama          0.7413
budget B avg         0.4854
previous raw avg     0.4033
baseline seed 1      0.1652
baseline seed 0      0.0325
```

More training updates improved average over baseline. Still no 0.76 average.

## Next

C config running: 10 episodes, 100 updates, epsilon decay 1000, seed 200.
