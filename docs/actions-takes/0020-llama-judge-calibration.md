# 0020 Llama Judge Calibration

Endpoint: `192.168.0.20:8001`, `llama-3.2-3b-instruct`, BF16 GGUF, ctx 8192, GPU.

## Speed

Remote server timings:

```text
prefill 2,008 tok/s
decode    64.9 tok/s
```

Proxy call latency: ~156 ms mean over first 5 calls.

Local Bonsai benchmark: 562-641 ms mean. Remote Llama is ~3.6-4x faster wall time. Not apples-to-apples: remote is 3B fully GPU; local is 9B ternary split on 4 GB.

## Calibration: z-scored inputs

Command: `env/test_remote_calibration.py`.

30 normal + 30 anomaly windows.

```text
system minimal:     normal 0.950  anomaly 0.950  AUC 0.500  high-normal 100%  high-anomaly 100%
system strict_scale normal 0.755  anomaly 0.832  AUC 0.616  high-normal 53%   high-anomaly 80%
system zscore_last  normal 0.950  anomaly 0.950  AUC 0.500
```

## Calibration: raw min-max inputs

Prompt examples are raw-scale. Code feeds z-scores. Mismatch.

20 normal + 20 anomaly windows:

```text
raw + minimal system  normal 0.362  anomaly 0.725  AUC 0.764  p 0.0014
raw + scale system    normal 0.250  anomaly 0.619  AUC 0.675  p 0.019
raw + temp 0.7        normal 0.445  anomaly 0.674  AUC 0.682  p 0.023
```

Other variants:

```text
integer 0..100: normal 0.009 anomaly 0.009 (parse/format mismatch)
answer cue:     normal 0.950 anomaly 0.950
```

## Root cause

`llm_shaping._normalize_for_prompt` z-scores each window before prompt formatting. Prompt few-shot examples are raw values like `[0,3.0,0,-2.5,0]`. Normal windows have z-values in [-2,2], so model reads them as spikes and returns 0.95. Raw min-max inputs separate classes better.

Server side cannot fix this. The z-scored prompt has lost raw mean/std.

## Raw-scale shim

Environment flag `RSL_RAW_WINDOWS=1` patches `llm_shaping._normalize_for_prompt` to identity after import/reload. No paper code edit.

Expected full A1 F1: unknown. Judge AUC 0.764, not strong. Wrapper and input-scale change, not paper code path.

Status: shim implemented, test pending.
