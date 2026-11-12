# 0002 Python 3.8 Environment

Target versions from notes: Python 3.8.20, transformers 4.46.3, torch 2.4.1+cu118.

## Install Python

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
/home/baptist777/.local/.venv/bin/uv python install 3.8.20
/home/baptist777/.local/.venv/bin/uv venv --python 3.8.20 .venv38
.venv38/bin/python --version
```

Output: `Python 3.8.20`.

## Install torch cu118

Default PyPI torch pulled by `accelerate` is wrong CUDA stack. Pin first.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
/home/baptist777/.local/.venv/bin/uv pip install --python .venv38/bin/python \
  "torch==2.4.1+cu118" \
  --index-url https://pypi.org/simple \
  --extra-index-url https://download.pytorch.org/whl/cu118
```

## Override typing-extensions

TF 2.13 caps `typing-extensions<4.6`. torch 2.4.1 needs `>=4.8`. Override file.

`env/overrides.txt`:

```text
typing-extensions==4.13.2
```

## Install rest

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
/home/baptist777/.local/.venv/bin/uv pip install --python .venv38/bin/python \
  --override env/overrides.txt \
  "numpy==1.24.3" "pandas==2.0.3" "scipy==1.10.1" \
  "scikit-learn==1.3.2" "matplotlib==3.7.5" \
  "tensorflow-cpu==2.13.1" "h5py==3.10.0" \
  "openai==1.54.4" "transformers==4.46.3" "accelerate==0.34.2" \
  "fastapi==0.115.6" "uvicorn==0.32.1"
```

## Pin httpx

openai 1.54.4 breaks on httpx 0.28. Error: `__init__() got an unexpected keyword argument 'proxies'`.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
/home/baptist777/.local/.venv/bin/uv pip install --python .venv38/bin/python "httpx==0.27.2"
```

## Verify

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
.venv38/bin/python -c "
import tensorflow as tf, torch, transformers, sklearn, pandas, numpy, h5py, fastapi, openai
print('tf', tf.__version__)
print('legacy Adam', tf.keras.optimizers.legacy.Adam is not None)
print('LSTMCell', tf.compat.v1.nn.rnn_cell.LSTMCell is not None)
print('static_rnn', tf.compat.v1.nn.static_rnn is not None)
print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), torch.version.cuda)
print('transformers', transformers.__version__)
print('sklearn', sklearn.__version__, 'numpy', numpy.__version__)
print('h5py', h5py.__version__, 'openai', openai.__version__)
"
```

Seen: TF 2.13.1 APIs present. torch CUDA true, CUDA 11.8. transformers 4.46.3. sklearn 1.3.2. numpy 1.24.3.

TF is CPU build. Avoids CUDA conflict with torch.
