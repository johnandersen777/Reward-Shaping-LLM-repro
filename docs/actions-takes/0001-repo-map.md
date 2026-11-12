# 0001 Repo Map

Paper repo: `Reward-Shaping-LLM/`. Never edited. `git status` clean.

Target: Table II. A1 row Llama F1 0.7413. SMD row Llama F1 0.5300.

## Entrypoints

A1: `myasp-A1.py:1027`.

```python
train_wrapper(200, 1000, 0.96)
```

SMD: `myasp-smd.py:943-945`. Three runs.

```python
train_wrapper(200, 1000, 0.96)
train_wrapper(200, 5000, 0.96)
train_wrapper(200, 10000, 0.96)
```

No `__main__` guard. Import runs full pipeline.

## A1 facts

- 3 train episodes. Literal `num_episodes=3`. `EPISODES` constant dead.
- 10 replay updates per episode. Batch 256.
- 6 validation episodes. One series each. Unweighted mean F1.
- Reward: TP/TN/FP/FN = 5/1/-1/-5. VAE MSE times 10. PBRS gamma 0.96.
- Epsilon `linspace(1.0, 0.1, 500000)`. Only 30 updates. Epsilon near 1. Actions near random.
- `dynamic_coef` computed, plotted, never used.
- LLM calls: 3 import canaries, 2 smoke windows, ~1-2 new windows per env step. About 1e4 per run.
- VAE trained 20 epochs. Saved `vae_model.h5`. Graph reset. Loaded back. `global_variables_initializer()` runs after load. Loaded VAE weights reinitialized. Reward VAE random.
- No seeds anywhere. Initial series index random.

## SMD facts

- `env_smd` keeps sensor column 0 only. Other 37 columns dropped.
- `test/` has 28 `.csv` plus 28 `.txt`. `datasetsize=56`. Machines counted twice.
- SMD VAE uses StandardScaler. Env uses MinMaxScaler. Decoder sigmoid.
- `q_learning` overwrites `env.rewardfnc` with raw reward every episode. LLM shaping only warm-up and smoke test.
- Same VAE reinit bug.
- LabelSpreading RBF on 23k-28k rows. About 6.3 GB per fit.

## Files

- `docs/repro-map.md`: full working map.
- `run/A1_mock/`: first mock run copy and output.
- `env/`: venv, shims, runners.
- `mock_llm/`: mock server, oracle lookup, logs.

## Check untouched repo

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/Reward-Shaping-LLM
git status --porcelain
```

Expected: empty.
