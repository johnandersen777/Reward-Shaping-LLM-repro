# 0023 Remote Llama F1 Report

Validation complete.

## Per-Episode F1

| Episode | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: |
| 1 | 0.3333 | 0.2941 | 0.3125 |
| 2 | 0.7059 | 0.5714 | 0.6316 |
| 3 | 0.9375 | 0.6522 | 0.7692 |
| 4 | 0.0679 | 0.2459 | 0.1064 |
| 5 | 0.6000 | 0.6000 | 0.6000 |
| 6 | 0.0000 | 0.0000 | 0.0000 |

```text
Average F1 = 0.403282
Mean precision = 0.4408
Mean recall = 0.3940
```

## Comparison

| Run | F1 |
| --- | ---: |
| Paper Llama | 0.7413 |
| Remote Llama raw | 0.4033 |
| Binary oracle mock | 0.1716 |
| Heuristic mock | 0.0687 |
| Bonsai A1 | 0.0094 |

## Run

```text
proxy calls: 5,293
wall time: ~18 min
exit code: 0
```

## Phi Distribution

```text
0.00 2472
0.95 1255
0.25 1235
0.50  133
```

## Caveats

- System role added.
- Raw min-max shim replaces z-scores.
- Not paper code path. Not a paper reproduction.
- Judge calibration AUC 0.764. Moderate.

## Outputs

```text
run/A1_remote_llama/repo
run/A1_remote_llama_raw/run.log
```

Runner default path wrote to `run/A1_remote_llama/repo`; log redirect used the `_raw` directory.

## Docs

- `docs/actions-takes/0022-remote-llama-raw-result.md`
- Commit `9005df4`
- No upstream PR or issue.
- Submodule back on upstream. Fork unused.
