# 0024 Paper Comparison

A1 comparison.

## Direct

| Run | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Paper Llama-3.2-3B | 0.6051 | 0.9565 | 0.7413 |
| Remote Llama Instruct raw-scale | 0.4408 | 0.3940 | 0.4033 |

Gap:

```text
F1         -0.338   ours 54% of paper
Precision  -0.164
Recall     -0.5625  largest gap
```

Paper is recall-heavy (95.7%). Ours is balanced-low (39.4%).

## Against paper baselines

| Model | F1 |
| --- | ---: |
| CARLA | 0.7233 |
| TranAD | 0.5654 |
| Phi-2 | 0.5555 |
| TimesNet | 0.5135 |
| Our Llama raw | 0.4033 |
| GPT-3.5 | 0.1372 |

Ours sits between GPT-3.5 and TimesNet. Below CARLA, TranAD, Phi, TimesNet.

## Why not clean

- Paper never states base vs Instruct, precision, chat template, or system prompt.
- Public code path: base Llama, raw prompt, no system role, z-scored inputs. Returns empty.
- Our run changed: Instruct checkpoint, chat system message, raw min-max inputs instead of z-scores.
- No seeds. One run. Per-episode F1 0.0 to 0.769.
- Paper numbers from authors' environment, not reproduced.

## What it shows

- Llama-shaped reward beats mocks: 0.4033 vs oracle 0.1716, heuristic 0.0687, Bonsai 0.0094.
- Not enough to reach paper numbers.
- Judge calibration AUC 0.764. Noisy severity gives noisy reward.

## Bottom line

Working end-to-end Llama-shaped run. Not a paper reproduction. Paper 0.7413 not reproduced. Our 0.4033 is below paper baselines and high variance. Multiple runs needed for variance.
