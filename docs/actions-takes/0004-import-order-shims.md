# 0004 Import Order And Shims

## Segfault

TF imported first, then torch CUDA op: segfault. Exit 139.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
.venv38/bin/python -c "import tensorflow as tf; import torch; torch.cuda.get_device_name(0)"
```

Torch first works.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
.venv38/bin/python -c "import torch; print(torch.cuda.get_device_name(0)); import tensorflow as tf; print(tf.__version__)"
```

## Fix

`env/sitecustomize.py`. Env flag `RSL_PRELOAD_TORCH=1` imports torch before research code imports TF.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/env RSL_PRELOAD_TORCH=1 \
  .venv38/bin/python -c "import tensorflow as tf; import torch; print(torch.cuda.get_device_name(0))"
```

## Scandir Proxy

First shim was function. `pathlib._NormalAccessor.scandir` holds it as class attribute. Function became bound method. Error:

```text
TypeError: scandir() takes at most 1 argument (2 given)
```

Fix: callable class instance. No `__get__`. No binding.

## Verify Order Walk

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/env PYTHONDONTWRITEBYTECODE=1 \
  .venv38/bin/python -c "
import os
d='run/A1_mock/repo/ydata-labeled-time-series-anomalies-v1_0/A1Benchmark'
fs=[f for _,_,files in os.walk(d) for f in files]
print(fs[-6:])
"
```

Expected: `['real_65.csv', 'real_66.csv', 'real_67.csv', 'real_7.csv', 'real_8.csv', 'real_9.csv']`.

## Run Policy

All training runs background. Monitor set. No foreground run.
