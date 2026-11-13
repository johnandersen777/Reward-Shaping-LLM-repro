# 0038 Parallel Window And Prompt Tests

Predeclared before results.

Purpose: cheap parallel screen while full budget run continues. Test two levers: LLM prompt window length, LLM system prompt wording.

## Why

Full budget run flat so far:

```text
ep49 mean F1 0.437572
ep99 mean F1 0.405053
```

No run average reaches 0.76. Best average B200 0.485391.

Short runs cheap. B200 config took 29 min alone.

## Control

B200 historical run, same config, seed 200:

```text
tag       budget_b5_e100_d500_s200
episodes  5
updates   100 per episode
decay     500
seed      200
window    25
prompt    current proxy system prompt
mean F1   0.485391
```

## Variants

Window axis. Paper `n_steps=25` feeds both LSTM state and LLM. Instrumentation changes only the slice sent to the LLM; LSTM state stays 25. `env/instrument_llm_window.py` rewrites the four reward call sites in the run copy.

```text
win10_b5_e100_d500_s200    RSL_LLM_WINDOW=10
win50_b5_e100_d500_s200    RSL_LLM_WINDOW=50
win100_b5_e100_d500_s200   RSL_LLM_WINDOW=100
```

Prompt axis. Proxy system prompt only. Paper user prompt unchanged.

```text
prompt_s1_b5_e100_d500_s200
  S1: judge whole window against its own normal variation,
      periodic repeating patterns normal, use full range

prompt_s2_b5_e100_d500_s200
  S2: focus on last value, score departure from rest of window,
      periodic repeating patterns normal
```

Control prompt, current proxy:

```text
You are an anomaly severity judge. Return ONLY JSON {"severity": s} with s in [0.0,1.0]. Never write code.
```

## Config

All variants same budget and seed as control:

```text
seed 200, 5 episodes, 100 updates, decay 500, RSL_RAW_WINDOWS=1
OMP_NUM_THREADS=2, RSL_WATCH_EPISODES=0
proxy 8772 for window tests, 8773 for S1, 8774 for S2
remote Llama 3.2 3B Instruct, chat, temperature 0
```

## Commands

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
RSL_LLM_WINDOW=50 RSL_WATCH_EPISODES=0 OMP_NUM_THREADS=2 \
  env/run_llama_budget_seed.sh win50_b5_e100_d500_s200 200 5 100 500
PROXY_PORT=8773 RSL_WATCH_EPISODES=0 OMP_NUM_THREADS=2 \
  env/run_llama_budget_seed.sh prompt_s1_b5_e100_d500_s200 200 5 100 500
```

Each wrapper commits artifact after run with `env/commit_budget_artifact.sh`.

## Limits

Single seed per variant. B seed spread is large: n=11, mean 0.154252, std 0.176613. Treat as screen, not proof. Any positive signal needs repeat seeds.

Window instrumentation is a run-copy change, not paper repo. Paper repo stays at `2e00998`.

## Status

Started 2026-11-13T08:52-08:00. Five runs in parallel with full budget run. Results appended when done.
