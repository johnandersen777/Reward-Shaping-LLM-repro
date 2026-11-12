# 0027 Training Budget Grid

Baseline seeds 0 and 1 are low:

```text
seed 0: 0.032482
seed 1: 0.165238
```

Next: longer training. Predeclared grid. All runs kept.

## Instrumentation

Copies only. Original paper repo untouched.

`env/instrument_training_budget.py` replaces:

```text
num_episodes=3
num_epoches=10
epsilon_decay_steps=500000
```

with env overrides.

## Grid

| Tag | Episodes | Updates/episode | Epsilon decay steps |
| --- | ---: | ---: | ---: |
| budget_b5_e100_d500 | 5 | 100 | 500 |
| budget_c10_e100_d1000 | 10 | 100 | 1000 |
| budget_d10_e200_d1000 | 10 | 200 | 1000 |

Seeds fixed before runs: `200, 201, 202`.

3 configs x 3 seeds = 9 runs. 3 workers. `OMP_NUM_THREADS=4`.

## Commands

```bash
env/run_llama_budget_seeds.sh
```

Outputs:

```text
run/<tag>/
models/<tag>/checkpoints/
```

Every run commits its checkpoint via `env/commit_budget_artifact.sh`, serialized with flock.

## Reporting

Highest F1 reported as best-of-9 with N, config, seed, and full distribution. No selected-run headline. No post-hoc prompt or config tuning on validation.

## Caveat

Parallel runs share CPU and remote Llama server. Fixed seeds; wall-clock contention can change floating-point scheduling, not random draws.

## Status

Grid prepared. Starts after baseline seed 2. Results pending.
