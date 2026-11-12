# 0035 Full Paper Budget Run

Predeclared before launch.

## Why

All reduced budgets top out near 0.49 average F1. Best is B200 0.485391. No run average reaches 0.76.

Paper Table II reports Llama-3.2-3B F1 0.7413.

Published repo hardcodes 3 episodes, 10 updates per episode in both `train_wrapper` definitions. Those are debug values. Paper numbers need the full budget.

This run tests the only faithful remaining lever: full budget with the paper's epsilon schedule.

## Config

```text
tag       paperbudget_e200_u1000_d500000_s200
episodes  200
updates   1000 per episode
epsilon_decay_steps 500000
seed      200
```

Total updates: 200,000.

Epsilon schedule is the paper's: 1.0 to 0.1 over 500,000 steps. At step 200,000 epsilon is about 0.64.

Earlier grid scaled decay to total updates, which is not the paper schedule. This run keeps paper value.

Other settings fixed:

```text
RSL_RAW_WINDOWS=1
RSL_VAE_COEF default 10.0
OMP_NUM_THREADS=4
remote Llama 3.2 3B Instruct, system prompt, chat
```

## Code

Original paper repo untouched. Run copy instrumented only:

```text
env/instrument_checkpoint.py
env/instrument_training_budget.py
```

Paper code already saves a checkpoint every 50 episodes. Final checkpoint also saved.

## Estimated time

Measured 0.79 s/update at 500 updates/episode. 200,000 updates is about 44 to 55 hours.

## Reporting rules

- All results kept. No filtering.
- Average F1 over 6 validation episodes is the metric.
- Best-of-N reported with N, never a selected episode.
- Per-episode max labeled as one series, not a headline.

## Status

Queued after B seed batch (B210). Start is automatic.
