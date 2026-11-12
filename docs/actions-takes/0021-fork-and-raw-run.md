# 0021 Fork And Raw-Scale Run

## Fork

Paper repo fork:

```text
https://github.com/johnandersen777/Reward-Shaping-LLM
```

Branch: `repro-setup`. Head `691b8b8`. Pushed. Kept unused.

Contains one doc commit: `REPRO_SETUP.md` linking parent repo. No paper code edits.

Parent submodule reverted to upstream:

```text
gitlink 2e00998
url https://github.com/baharehgl/Reward-Shaping-LLM.git
```

Parent commit: `5732d57`.

Parent repro repo:

```text
https://github.com/johnandersen777/Reward-Shaping-LLM-repro
branch repro-setup
```

## Calibration Findings

Remote endpoint: `192.168.0.20:8001`, `llama-3.2-3b-instruct`, BF16, GPU.

Speed:

```text
prefill 2,008 tok/s
decode     64.9 tok/s
proxy       156 ms/call
local Bonsai 562-641 ms/call
```

Calibration, 20 normal + 20 anomaly windows:

```text
z-score + minimal system: normal 0.950 anomaly 0.950 AUC 0.500
z-score + scale system:   normal 0.755 anomaly 0.832 AUC 0.616
raw min-max + minimal:    normal 0.362 anomaly 0.725 AUC 0.764
raw min-max + scale:      normal 0.250 anomaly 0.619 AUC 0.675
raw min-max + temp 0.7:   normal 0.445 anomaly 0.674 AUC 0.682
integer 0..100:           normal 0.009 anomaly 0.009 (format mismatch)
```

Root cause: code z-scores windows; prompt examples use raw values. Normal z-window looks like a spike. Model returns 0.95. Raw inputs separate classes.

## Raw Shim

`env/sitecustomize.py`, flag `RSL_RAW_WINDOWS=1`:

```python
module._normalize_for_prompt = lambda xs: list(xs)
```

Applied after `llm_shaping` import/reload. No paper code edit.

Test:

```bash
env PYTHONPATH=$PWD/env:$PWD/run/A1_winorder/repo RSL_RAW_WINDOWS=1 \
  LLM_CHOICE=gpt-3.5-turbo OPENAI_API_KEY=x \
  .venv38/bin/python -c "import importlib, llm_shaping; importlib.reload(llm_shaping); print(llm_shaping._normalize_for_prompt([0.1,0.2,0.3]))"
```

Output: `[0.1, 0.2, 0.3]`.

## Full Run

Repo: `run/A1_remote_llama_raw/repo`.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
RSL_RAW_WINDOWS=1 env/run_real_a1_remote.sh \
  > run/A1_remote_llama_raw/run.log 2>&1
```

Proxy: `192.168.0.20:8001/v1`, chat, system JSON instruction.

Status: running. Results pending. Wrapper and input-scale changes; user-directed. Not paper code path.
