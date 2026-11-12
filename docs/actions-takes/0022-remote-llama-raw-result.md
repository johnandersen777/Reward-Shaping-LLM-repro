# 0022 Remote Llama Raw A1 Result

## Result

Average F1 = 0.403282.

Per-episode:

```text
Episode 1  P 0.3333  R 0.2941  F1 0.3125
Episode 2  P 0.7059  R 0.5714  F1 0.6316
Episode 3  P 0.9375  R 0.6522  F1 0.7692
Episode 4  P 0.0679  R 0.2459  F1 0.1064
Episode 5  P 0.6000  R 0.6000  F1 0.6000
Episode 6  P 0.0000  R 0.0000  F1 0.0000
```

Mean precision 0.4408. Mean recall 0.3940.

Paper Llama A1: P 0.6051, R 0.9565, F1 0.7413. Not matched.

## Phi Distribution

5,285 unique windows:

```text
0.00 2472
0.95 1255
0.25 1235
0.50  133
0.01   82
0.02   36
0.03   30
0.05   26
0.11    8
0.04    6
0.68    1
0.18    1
```

## Setup

Remote: `192.168.0.20:8001/v1`, `llama-3.2-3b-instruct`, BF16 GGUF, GPU.

Proxy: `mock_llm/server.py` mode `remote_openai`, chat, system JSON instruction.

Input shim: `RSL_RAW_WINDOWS=1`. Min-max values instead of z-scores. Environment-only patch.

Run:

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
RSL_RAW_WINDOWS=1 env/run_real_a1_remote.sh \
  > run/A1_remote_llama_raw/run.log 2>&1
```

Actual repo path: `run/A1_remote_llama/repo` (runner default). Log path: `run/A1_remote_llama_raw/run.log`.

Proxy calls: 5,293. Wall time: ~18 min.

## Comparison

```text
paper Llama          0.7413
remote Llama raw     0.4033
binary oracle mock   0.1716
heuristic mock       0.0687
Bonsai A1            0.0094
```

Not directly comparable to paper:

- system role added,
- raw min-max inputs instead of z-scores,
- different runtime and quantization,
- no seeds, different random training path.

Evidence: judge calibration raw AUC 0.764. Not strong. Result is a working end-to-end Llama-shaped run, not a paper reproduction.
