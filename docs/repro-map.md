# Reproduction Map: LLM-Enhanced RL for Time Series Anomaly Detection

Working root: `/home/baptist777/.tmp/tmp.VjJfPBPNr4`
Research code: `Reward-Shaping-LLM/` (never edited)
Paper target: Table II, Yahoo-A1 and SMD, Llama-3.2-3B rows.

## Current status

- Environment built: Python 3.8.20, TensorFlow CPU 2.13.1, torch 2.4.1+cu118,
  transformers 4.46.3, scikit-learn 1.3.2, pyc38 venv at `.venv38/`.
- LLM path verified with a mock OpenAI-compatible server: numeric severities
  parsed, fallback not triggered.
- Full `myasp-A1.py` pipeline completed end-to-end with the mock LLM
  (exit 0): canaries, VAE training, 1500-step warm-up, 3 training episodes,
  6 validation episodes, all CSV/SVG/TF-event outputs written. Mock average
  F1 = 0.2457. This validates plumbing only; it is not a paper result.
- Local HF path validated with a tiny ungated Llama-format model on GPU and
  on CPU fp16: model loads through `device_map="auto"`, generation runs,
  parsing behaves as coded. CPU fp16 works, so accelerate CPU offload for the
  3B model should work.
- Real Llama-3.2-3B download is blocked: HF token account `baptist777001`
  is not authorized for gated repo `meta-llama/Llama-3.2-3B` (HTTP 403).
  User must accept the license on the model page.

## Environment

Installed with `uv`:

```
Python 3.8.20
tensorflow-cpu 2.13.1
torch 2.4.1+cu118 (CUDA available, RTX 3050 Laptop, 4 GB)
transformers 4.46.3
tokenizers 0.20.3
accelerate 0.34.2
numpy 1.24.3
pandas 2.0.3
scipy 1.10.1
scikit-learn 1.3.2
matplotlib 3.7.5
h5py 3.10.0
openai 1.54.4
httpx 0.27.2 (0.28 breaks openai 1.54.4: `proxies` kwarg)
fastapi 0.115.6
uvicorn 0.32.1
```

Notes:

- TF 2.13 pins `numpy<=1.24.3` and `typing-extensions<4.6`, but torch 2.4.1
  requires `typing-extensions>=4.8`. Installed with
  `--override env/overrides.txt` (`typing-extensions==4.13.2`). TF imports and
  runs fine with 4.13.2.
- TensorFlow is CPU-only on purpose. TF 2.13 GPU needs CUDA 11.8/cuDNN 8.6
  and conflicts with torch's CUDA stack.
- Import-order bug found: importing TensorFlow first, then running any torch
  CUDA op, segfaults. Torch CUDA first is stable. `env/sitecustomize.py`
  preloads torch when `RSL_PRELOAD_TORCH=1`, without editing research code.

## Windows file order

Windows/NTFS enumerates directory entries from the `$I30` B-tree in
case-insensitive ordinal order, i.e. lexicographic, not natural numeric order.
For the repo names this equals Python `sorted()`:

```
real_1.csv, real_10.csv, ..., real_19.csv, real_2.csv, real_20.csv, ...
```

Zero-padding would change the order to numeric and therefore would NOT match
windows. No files renamed. `env/sitecustomize.py` forces this order for
`os.scandir`/`os.walk` (Linux btrfs otherwise returns hash order).

A1 split under Windows order (`datasetsize=67`, train fraction 0.9):

- train indices 0-60
- validation indices 61-66 = `real_65.csv, real_66.csv, real_67.csv, real_7.csv, real_8.csv, real_9.csv`
- validator runs `int(67*0.1) = 6` episodes, one series each; F1 is their
  unweighted mean.

SMD checkout has 28 `.txt` plus 28 `.csv` in `test/`, so `env_smd` sees 56
files, not 28 series. Sorted order pairs each machine's `.csv` then `.txt`.
A 0.8 split gives 45 train files and 11 validation files (6 unique machines,
five duplicated, one machine split across the boundary).

## A1 execution facts (`myasp-A1.py`)

- No `__main__` guard. Import runs canaries and calls
  `train_wrapper(200, 1000, 0.96)` at line 1027.
- `llm_shaping` is imported then `importlib.reload`ed: with a local model this
  loads the 3B checkpoint twice (peak ~2x memory).
- `llm_shaping` requires `OPENAI_API_KEY` at import even for local Llama.
- Local model path is hardcoded: `~/llama-models/Llama-3.2-3B`.
- `EPISODES=3` is dead; the real episode count is the literal `num_episodes=3`
  in the `q_learning` call. `num_epoches=10`, batch 256.
- Warm-up fills replay memory with 1500 transitions (150 iterations x 10
  sampled states), then 3 training episodes. Each episode queries
  `num_AL=1000` states by Q-margin, labels them from the oracle `anomaly`
  column, steps through all labeled indices (LLM + VAE reward), propagates up
  to 200 pseudo-labels, then performs 10 gradient updates.
- Epsilon is `linspace(1.0, 0.1, 500000)`; with only 30 updates epsilon stays
  near 1.0, so training actions are effectively random. Validation uses
  epsilon 0 / argmax.
- `dynamic_coef` is computed and plotted but never used: `shaping_fn` hardcodes
  `dynamic_coef=10.0`.
- PBRS gamma is the passed `discount_factor=0.96`.
- Reward: TP/TN/FP/FN = 5/1/-1/-5, plus `10 * VAE reconstruction MSE`, plus
  `0.96*phi(s2) - phi(s)`.
- `label`, not `anomaly`, drives training rewards; active learning writes
  oracle labels, label propagation writes pseudo-labels, so rewards use a mix.
- VAE is trained 20 epochs on `normal-data/*.csv`, saved to cwd-relative
  `vae_model.h5`, graph reset, loaded back, then
  `global_variables_initializer()` runs afterwards, which reinitializes the
  loaded VAE weights. The VAE used in the reward is therefore randomly
  initialized, not the trained one. Same pattern in SMD.
- LLM calls: 3 canaries at import, 2 windows in the smoke test, roughly 1-2
  new generations per environment step after cache. Estimated ~10^4
  generations per A1 run.
- Writes: `vae_model.h5`, `exp/A1_LP200_AL1000_d0.96/...`, six detection SVGs,
  `llm_potentials.csv`, plots, and a mis-joined
  `exp/A1_LP200_AL1000_d0.96performance.txt` (missing path separator).

## SMD execution facts (`myasp-smd.py`, `env_smd.py`)

- Bottom of file calls `train_wrapper(200, 1000, 0.96)` then `(200, 5000,
  0.96)` then `(200, 10000, 0.96)` sequentially in one process.
- `env_smd` keeps only sensor column 0; the other 37 SMD channels are
  discarded. Each file is min-max scaled independently.
- VAE training uses `train/*.txt`, first column, StandardScaler (zero mean,
  unit variance), while env values are min-max [0,1]; decoder ends in sigmoid.
- Sensor list includes both `.csv` and `.txt`, so `datasetsize=56`.
  `convert_txt_to_csv` is a no-op when `.csv` exist.
- Critical divergence: `q_learning` overwrites `env.rewardfnc` with the raw
  `RNNBinaryRewardFuc` at the start of every training episode. LLM shaping is
  active only during warm-up and the smoke test, not episode training.
- Reward values are 5/10/-5/-10, validation fraction 0.8, 10 episodes,
  batch 128, VAE 2 epochs, dynamic coefficient starts at 20 and clips to 10.
- Validator averages F1 and a binary-operating-point AUPR over 11 files.
- Same VAE reinitialization-after-load issue.

## Environment shims (outside the research repo)

- `env/sitecustomize.py`
  - sorts `os.scandir` entries case-insensitively to match NTFS;
  - `RSL_PRELOAD_TORCH=1`: imports torch before TensorFlow to avoid the CUDA
    segfault;
  - `RSL_OPENAI_SHIM=1`: optional openai 0.x compatibility (not needed with
    openai 1.54.4).
- `.venv38/`: Python 3.8.20 environment.
- `run/A1_winorder/repo/`: pristine repo copy for the real Llama run.
- `run/A1_mock/repo/`: pristine copy used for the mock plumbing run.
- `mock_llm/server.py`: FastAPI OpenAI-compatible mock server, port 8765.
  Deterministic severity `0.05 + 0.18*max|z|`. Logs to
  `mock_llm/requests.jsonl`. Never use its outputs as paper results.
- `env/check_llm.py`: two-window LLM canary.
- `env/run_mock_a1.sh`: launcher for the mock run.

## Commands

Mock LLM server:

```
cd mock_llm
../.venv38/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8765
```

LLM canary:

```
env PYTHONPATH=$PWD/run/A1_mock/repo:$PWD/env \
  PYTHONDONTWRITEBYTECODE=1 OPENAI_API_KEY=mock-key \
  OPENAI_BASE_URL=http://127.0.0.1:8765/v1 LLM_CHOICE=gpt-3.5-turbo \
  PHI_DEBUG=1 .venv38/bin/python env/check_llm.py
```

Mock A1 run:

```
env/run_mock_a1.sh
```

Real local-Llama run (after model access):

```
cd run/A1_winorder/repo
env PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/env \
  PYTHONDONTWRITEBYTECODE=1 RSL_PRELOAD_TORCH=1 TF_CPP_MIN_LOG_LEVEL=2 \
  OPENAI_API_KEY=unused LLM_CHOICE=llama-3 PHI_DEBUG=1 \
  /home/baptist777/.tmp/tmp.VjJfPBPNr4/.venv38/bin/python myasp-A1.py
```

## Additional audit facts

- `LLM_CHOICE` must be exactly `llama-3`, `phi-2`, or a string starting with
  `gpt`. Any other value (including the README's `llama-3.2-3b-instruct`)
  leaves the local pipeline as `None`, every call raises, and the code silently
  uses the z-score fallback.
- The `lru_cache` key is the exact unrounded window. Rounding happens inside
  the function after the cache lookup. Consecutive windows still share keys
  because `s2` of step t is exactly `s` of step t+1.
- `debug_llm_potentials.csv` in the repo has one 0.0 and six 0.2 values. The
  fallback would have produced different continuous values (about 0.25, 0.28,
  0.02, 0.005, 0.005, 0.97), so those 0.2 values are parsed LLM output. This
  confirms the authors' statement that Table II used LLM ratings.
- `return_full_text=False` is honored by transformers 4.46.3; the prompt is
  not echoed into the parsed answer.
- SMD `LabelSpreading` uses the default RBF kernel and builds an n x n matrix.
  SMD series have 23k-28k rows, so each fit allocates about 6.3 GB. On a
  31 GB machine this is possible but slow; it is a main SMD runtime risk.
- `A1Benchmark/.json` is a tracked 204-byte hidden file. `env.py` ignores it
  because it only loads `.csv`, but `build_phi_lookup.py` and `test.py` call
  `os.listdir` without filtering and would fail on it. Neither produces Table
  II.
- `myasp-smd.py` runs three configurations at the bottom; the repo does not say
  which one maps to the single Table II SMD row.
- KPI/WADI/A2/newdataset scripts and `convert_hdf_to_csv.py` are irrelevant to
  Table II; KPI data paths are incomplete in the checkout.
- Running any A1/A2/SMD script from the repo root overwrites tracked
  `vae_model.h5` / `vae_smd_model.h5` and writes untracked `exp/` output.
  Always run from a copy, as the `run/` directories do.

## Open blockers and risks

1. Llama-3.2-3B gated access. Blocked until the HF account accepts the license.
2. 4 GB GPU cannot hold the 3B fp16 model. `device_map="auto"` will offload
   layers to CPU; generation will be slow and two model loads at import double
   peak RAM (~12.8 GB, within 31 GB).
3. No seeds anywhere in the code. Initial series index is `random.randint`,
   TF/Keras and replay sampling are unseeded. Run-to-run numbers will vary.
4. The VAE reinitialization and SMD reward-override issues are in the published
   code. They are recorded as-is; do not patch if the goal is faithful
   reproduction.
5. Full A1 run needs roughly 10^4 Llama generations. On CPU/offload this may
   take many hours per run.
