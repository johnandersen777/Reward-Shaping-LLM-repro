# 0015 Bonsai MTP Q8_0 LLM

User directive: stop Phi-2. Use `prism-ml/Ternary-Bonsai-2-9B-gguf`, MTP Q8_0 file.

## Model

File: `Ternary-Bonsai-2-9B-PQ2_0-MTP-Q8_0.gguf`, 2,675,410,720 bytes. SHA256 OK from `SHA256SUMS`.

Path:

```text
~/models/Ternary-Bonsai-2-9B-gguf/Ternary-Bonsai-2-9B-PQ2_0-MTP-Q8_0.gguf
```

Base: Qwen3.5-9B. Ternary 2-bit language weights plus MTP draft head. Fits 4 GB GPU.

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/download_bonsai.sh
```

## llama.cpp Fork

PrismML fork required. Release `prism-b10776-d00e252`. CUDA 13.3 build needs `libcudart.so.13`, unavailable. Used CUDA 12.8 Linux build.

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/download_llama_prism.sh
```

CUDA 12 libs from PyPI:

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
.venv38/bin/python -m uv pip install --target llama-cuda12libs --no-deps \
  "nvidia-cuda-runtime-cu12==12.9.79" "nvidia-cublas-cu12==12.9.3.13"
```

`LD_LIBRARY_PATH` set in server script:

```text
llama-cuda12libs/nvidia/cuda_runtime/lib
llama-cuda12libs/nvidia/cublas/lib
```

## Server

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/start_bonsai_server.sh
```

Flags: `-ngl 99 -fa on --spec-type draft-mtp --spec-draft-n-max 2 --spec-draft-n-min 0 --spec-draft-p-min 0 -c 2048 -t 8`.

Seen:

```text
model loaded
speculative decoding enabled: draft-mtp
listening on http://127.0.0.1:8770
GPU 3331 MiB
```

Speed test: 61 prompt + 32 generated tokens in 0.62 s. Prompt 275 tok/s. Decode 78 tok/s. MTP draft 23, accepted 19.

## Raw Completion Fails

`/completion` raw prompt: model continues the sequence, not JSON.

```text
raw='\nSequence: [0.00, 0.00, 0.00, 0\n' -> score=0.000
```

## Chat Endpoint Works

`/v1/chat/completions` with `chat_template_kwargs={"enable_thinking": false}`, temperature 0, max_tokens 32.

```text
content: {"severity": 0.95}
wall 0.36 s
```

MTP draft 6, accepted 6.

## Proxy

`mock_llm/server.py`, mode `llama_cpp`. Forwards messages to llama-server chat endpoint. Forces `max_tokens=32`, temperature 0, thinking off.

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/start_bonsai_proxy.sh
```

Port 8771. Backend 8770. Log: `mock_llm/bonsai_requests.jsonl`.

Canary: exact llm_shaping prompt.

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/check_bonsai.sh
```

Seen:

```text
raw='{"severity": 0.0}'  -> 0.0
raw='{"severity": 0.95}' -> 0.95
```

## Full A1 Run

Fresh copy: `run/A1_bonsai/repo`.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env/run_real_a1_bonsai.sh > /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_bonsai/run.log 2>&1
```

## Full A1 Result

Run exit 0. Average F1 = 0.009376.

Per-episode F1:

```text
0.01033 0.00585 0.00288 0.02120 0.00750 0.00849
```

Paper Llama A1 F1 = 0.7413. Not reproduced.

## Phi Distribution

5,322 unique logged windows:

```text
0.75  3377
0.95  1027
0.70   835
0.00    32
0.50    28
0.85    22
0.55     1
```

~88% scored >= 0.70. Judge over-flags normal windows. Little discrimination. High, near-constant phi gives weak reward differences.

## Cache-Reuse Test

Fixed 20-prompt benchmark, cold server each time.

```text
default         wall 562.3 ms  prompt 446.6 ms  predict 113.0 ms
CACHE_REUSE=256 wall 564.0 ms  prompt 447.8 ms  predict 113.4 ms
```

Outputs identical. Cached tokens reported 0 in both. No gain. Keep default server flags.

Bench files:

```text
docs/actions-takes/bonsai_bench_before.json
docs/actions-takes/bonsai_bench_cache256.json
env/bench_bonsai.py
```

Command:

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env PYTHONPATH=$PWD/run/A1_winorder/repo \
  .venv38/bin/python env/bench_bonsai.py docs/actions-takes/bonsai_bench_before.json
```

## Experiment Change

Code path is now OpenAI-compatible proxy, not local HF raw pipeline. Chat template wraps the user message. Prompt text inside the message unchanged. This is a wrapper change, required by the requested GGUF model. Note 3 forbids wrapper changes. Documented, user-directed.

Speed estimate: 4,600 calls at ~0.4-1.0 s each = ~1-2 h, plus training.
