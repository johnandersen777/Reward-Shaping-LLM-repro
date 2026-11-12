# 0007 Real Llama 3.2 3B

## Access

License accepted. Probe:

```bash
TOKEN=$(cat ~/.cache/huggingface/token)
curl -sS -L -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  https://huggingface.co/meta-llama/Llama-3.2-3B/resolve/main/config.json
```

Seen: 200.

## Download

Script: `env/download_llama32_3b.sh`. Skips `original/*.pth`. Downloads safetensors, tokenizer, configs.

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/download_llama32_3b.sh
```

Sizes seen:

```text
model-00001-of-00002.safetensors  4965799096
model-00002-of-00002.safetensors  1459729952
total 6.0G
```

Path: `~/llama-models/Llama-3.2-3B`.

## GPU Canary

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_winorder/repo:/home/baptist777/.tmp/tmp.VjJfPBPNr4/env \
  PYTHONDONTWRITEBYTECODE=1 RSL_PRELOAD_TORCH=1 \
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  OPENAI_API_KEY=unused LLM_CHOICE=llama-3 PHI_DEBUG=1 \
  .venv38/bin/python env/check_llm.py
```

Seen:

```text
Loading checkpoint shards: 100%
Some parameters are on the meta device because they were offloaded to the cpu.
[PHI DEBUG] raw='' -> score=0.000
[PHI DEBUG] raw='' -> score=1.000
phi(zeros) = 0.0
phi(spike) = 0.9999938557868941
```

Model loaded. Generation empty. Fallback fired. Same bug as notes.

Exit 0. Wall 16.5 s.

## CPU Canary

Test offload vs model.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env CUDA_VISIBLE_DEVICES= \
  PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_winorder/repo:/home/baptist777/.tmp/tmp.VjJfPBPNr4/env \
  PYTHONDONTWRITEBYTECODE=1 RSL_PRELOAD_TORCH=1 \
  OPENAI_API_KEY=unused LLM_CHOICE=llama-3 PHI_DEBUG=1 \
  .venv38/bin/python env/check_llm.py
```

Status: background. Result pending.

## Next

If CPU nonempty: offload causes empty. If CPU empty: model or pipeline. Then inspect token ids, EOS handling, `return_full_text`, generation defaults.

No code edits. Env shims only.
