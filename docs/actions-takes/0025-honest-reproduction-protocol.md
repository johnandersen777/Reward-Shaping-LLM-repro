# 0025 Honest Reproduction Protocol

Author states prior reported numbers came from selected runs. Disclosure planned.

This protocol removes selection.

## Fixed Before Runs

- Seeds: `0..9`. Fixed before execution.
- One fresh repo copy per seed.
- Remote Llama Instruct BF16, chat, system JSON instruction.
- Raw min-max window shim.
- No prompt or environment changes during the suite.
- No run deleted or filtered.

## Seed Control

`env/sitecustomize.py`, flag `RSL_SEED`:

```python
random.seed(seed)
numpy.random.seed(seed)
tensorflow.compat.v1.set_random_seed(seed)
```

Runner also sets `PYTHONHASHSEED=0`.

Verified: same seed gives identical `random`, NumPy, TF draws across processes.

## Runs

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env/run_llama_seeds.sh 10
```

Per seed:

```text
run/llama_seed_<N>/repo
run/llama_seed_<N>/run.log
```

All exp outputs retained.

## Reporting

```bash
.venv38/bin/python env/summarize_llama_seeds.py
```

Reports:

- per-seed mean F1, precision, recall
- mean, std, median, min, max across seeds
- delta vs paper 0.7413
- best-of-N, explicitly labeled as best-of-N
- full CSV
- all-seed plot

No best-run headline. No selected subset.

## Caveats

- Setup differs from paper code: Instruct checkpoint, system message, raw inputs, remote runtime.
- Code has no original seeds. Lost exact run not recoverable.
- This characterizes the method in this environment, not the original unpublished run.
- If published record used selected runs, correction or erratum should accompany it.

## Outputs

```text
docs/actions-takes/llama_seed_results.csv
docs/actions-takes/llama_seed_distribution.svg
```
