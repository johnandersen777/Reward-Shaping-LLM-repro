# 0031 Budget E Result

Config E: 5 episodes, 500 updates/episode, epsilon decay 2500. Seed 200.

## F1

| Episode | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: |
| 1 | 0.0889 | 0.2353 | 0.1290 |
| 2 | 0.8333 | 0.7143 | 0.7692 |
| 3 | 0.9231 | 0.5217 | 0.6667 |
| 4 | 0.3462 | 0.2951 | 0.3186 |
| 5 | 0.6000 | 0.9000 | 0.7200 |
| 6 | 1.0000 | 0.1250 | 0.2222 |

```text
Average F1 = 0.47095599783010583
Max episode F1 = 0.7692
```

Max episode is one validation series. Not a headline.

## Checkpoint

```text
models/budget_e5_e500_d2500_s200/checkpoints/
commit 074a7e8
```

## Comparison

```text
paper Llama          0.7413
B: 5 ep, 100 upd     0.4854
E: 5 ep, 500 upd     0.4710
C: 10 ep, 100 upd    0.3115
```

More updates did not improve average. Seed variance dominates.

## Next

F config: same as B, but VAE reward coefficient 0.

Reason: code reloads VAE then reinitializes weights, so the VAE reconstruction reward is random noise. Remove it to test reward path.

Config:

```text
budget_f5_e100_d500_vae0_s200
5 episodes, 100 updates, decay 500, RSL_VAE_COEF=0
```

Predeclared before run. Status: running.
