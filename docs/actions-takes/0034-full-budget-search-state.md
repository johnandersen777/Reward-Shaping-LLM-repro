# 0034 Full Budget Search State

All completed runs. No filtering.

## Runs

| Tag | Mean F1 | Max episode |
| --- | ---: | ---: |
| baseline seed 0 | 0.032482 | 0.0836 |
| baseline seed 1 | 0.165238 | 0.6667 |
| B200 | 0.485391 | 0.9362 |
| B201 | 0.000000 | 0.0000 |
| B202 | 0.151598 | 0.2597 |
| B203 | 0.071702 | 0.1818 |
| B204 | 0.074126 | 0.2308 |
| B205 | 0.409537 | 0.7222 |
| B206 | 0.000000 | 0.0000 |
| B207 | 0.337709 | 0.6667 |
| B208 | 0.000000 | 0.0000 |
| B209 | 0.017144 | 0.0287 |
| C200 | 0.311500 | 0.7273 |
| D200 | 0.434827 | 0.6471 |
| E200 | 0.470956 | 0.7692 |
| F200 | 0.468059 | 0.7556 |

Best average: B200 0.485391.

Runs with average >= 0.76: 0.

Highest per-episode: 0.9362, B200 episode 3. One validation series. Not a headline.

## Checkpoints

```text
baseline seed 0  checkpoint in models/llama_seed_0
baseline seed 1  checkpoint in models/llama_seed_1
B200 17edcf2
B201 4c607cc
B202 fbff605
B203 827f9d4
B204 aec878b
B205 e036bb1
C200 00dc728
D200 06923fd
E200 074a7e8
F200 ec360c0
```

Reload proof:

```text
seed 0 exact F1 match
B200 exact F1 match 0.4853906125529526
```

## Honest Limit

Current setup tops out near 0.49 average. 0.76 average not reached by 12 runs across 5 configs and 8 B seeds.

Per-episode >=0.76 occurs:
- B200 episode 3: 0.9362
- E200 episode 2: 0.7692

One series each. Reporting either as the result would be cherry-picking.

## Next

Fixed B seed extension, declared before runs: 206, 207, 208, 209, 210.

All kept. Best-of-N reported with N. No selected-run headline.

Status: running.
