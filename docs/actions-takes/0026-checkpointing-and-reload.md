# 0026 Checkpointing And Reload

Goal: save RL agent state and reload for validation at any time.

## Instrumentation

Only run copies under `run/` are edited. Paper repo untouched.

`env/instrument_checkpoint.py` inserts:

```python
saver.save(sess, checkpoint_path)
print("Saved final checkpoint:", checkpoint_path)
return episode_rewards, coef_history
```

and changes:

```python
test = 1 if os.environ.get("RSL_TEST") == "1" else 0
...
if test:
    return [], []
```

The existing restore path in `q_learning` loads the checkpoint when present. With `RSL_TEST=1`, training is skipped and validation runs on the restored estimator.

## Save

Every seed run saves:

```text
run/llama_seed_<N>/repo/exp/A1_LP200_AL1000_d0.96/checkpoints/model.*
```

`env/commit_seed_artifact.sh` copies to:

```text
models/llama_seed_<N>/
  checkpoints/
  meta.json
  seed_log.json
  performance.txt
  llm_potentials.csv
  run.log
```

and commits/pushes after each seed.

## Reload Validation

```bash
env/validate_llama_checkpoint.sh <SEED>
```

Fresh copy, instrument, copy checkpoint into expected exp path, `RSL_TEST=1`, run. Validation only. Output:

```text
run/validate_seed_<N>/performance.txt
run/validate_seed_<N>/run.log
```

## Search Policy

Seeds fixed before runs. All runs kept. Highest F1 reported as best-of-N with N and full distribution. No selected-run headline. No prompt/config tuning after seeing validation results.

## Status

Suite restarted with checkpointing. Results pending.
