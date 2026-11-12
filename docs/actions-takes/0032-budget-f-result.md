# 0032 Budget F Result

Config F: 5 episodes, 100 updates, decay 500, VAE reward coefficient 0, seed 200.

Purpose: test removing random VAE reconstruction reward. Code reloads VAE then reinitializes weights, so VAE term is noise.

## F1

| Episode | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: |
| 1 | 0.1864 | 0.6471 | 0.2895 |
| 2 | 0.7083 | 0.8095 | 0.7556 |
| 3 | 0.8462 | 0.4783 | 0.6111 |
| 4 | 0.4186 | 0.2951 | 0.3462 |
| 5 | 0.4348 | 1.0000 | 0.6061 |
| 6 | 0.5000 | 0.1250 | 0.2000 |

```text
Average F1 = 0.4680591338486076
Max episode F1 = 0.7556
```

## Checkpoint

```text
models/budget_f5_e100_d500_vae0_s200/checkpoints/
commit ec360c0
```

## Comparison

```text
paper Llama          0.7413
B: 5 ep, 100 upd     0.4854
E: 5 ep, 500 upd     0.4710
F: no VAE            0.4681
C: 10 ep, 100 upd    0.3115
```

Removing VAE noise did not improve average. Best average still B200.

## Next

Extended B seed search, fixed before runs: seeds 203, 204, 205. All kept. Checkpoints committed.

Status: running.
