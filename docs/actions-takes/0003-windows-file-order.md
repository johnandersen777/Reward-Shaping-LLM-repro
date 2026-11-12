# 0003 Windows File Order

Result: Windows/NTFS order = case-insensitive lexicographic. Not natural numeric.

NTFS `$I30` B-tree enumerates by uppercase ordinal name. Digits compare as text. So:

```text
real_1.csv, real_10.csv, ..., real_19.csv, real_2.csv, real_20.csv, ...
```

Zero padding would change order to numeric. Would NOT match Windows. No files renamed.

## A1 split

`datasetsize=67`. Train fraction 0.9. Train indices 0-60. Validation indices 61-66.

Windows validation series:

```text
real_65.csv real_66.csv real_67.csv real_7.csv real_8.csv real_9.csv
```

Validator runs 6 episodes. Mean F1 over these 6.

## Linux problem

btrfs returns hash order. `os.walk` gives different order. Split changes.

## Shim

`env/sitecustomize.py` sorts `os.scandir` entries. `os.walk` then sorted.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/env PYTHONDONTWRITEBYTECODE=1 \
  .venv38/bin/python -c "
import os
d='Reward-Shaping-LLM/ydata-labeled-time-series-anomalies-v1_0/A1Benchmark'
fs=[f for _,_,files in os.walk(d) for f in files]
print(fs[:5])
print(fs[-6:])
print('sorted', fs==sorted(fs))
"
```

Expected last 6: `['real_65.csv', 'real_66.csv', 'real_67.csv', 'real_7.csv', 'real_8.csv', 'real_9.csv']`.

## SMD order

`test/` has 28 `.csv` plus 28 `.txt`. Sorted pairs each machine csv then txt. Split 0.8: 45 train files, 11 validation files. Six unique machines only. One machine split across boundary.
