# 0019 Remote Llama Tests

inference-host on LAN: `192.168.0.20`.

```text
base     http://192.168.0.20:8000/v1  id=llama-3.2-3b-base     Q8_0 GGUF  ctx 8192  raw completion
instruct http://192.168.0.20:8001/v1  id=llama-3.2-3b-instruct BF16 GGUF  ctx 8192  completion + chat
```

Both GPU, ~12 GB VRAM, base 121 tok/s, instruct 72.5 tok/s.

## Local proxy

`mock_llm/server.py` mode `remote_openai`.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
REMOTE_BASE_URL=http://192.168.0.20:8001/v1 \
REMOTE_MODEL=llama-3.2-3b-instruct \
REMOTE_MODE=chat \
env/start_remote_proxy.sh
```

`REMOTE_MODE=completion` uses remote `/v1/completions` with raw prompt. `chat` uses `/v1/chat/completions`.

Canary:

```bash
env/check_remote.sh
```

## Results

Base raw completion:

```text
raw='' -> fallback 0.0
raw='' -> fallback 0.99999
```

Instruct raw completion:

```text
raw=' \n\n```python\ndef score_anomaly_severity(sequence): ...'
score=0.0
```

Instruct chat, user-only:

```text
'Here is a Python function that calculates the anomaly severity...'
score=0.0
```

Instruct chat + system message:

```text
system: You are an anomaly severity judge. Return ONLY JSON ... Never write code.
zeros -> {"severity": 0.00}
spike -> {"severity": 0.95}
normal windows -> 0.95
anomaly windows -> 0.95
```

No discrimination. All tested real windows scored 0.95.

## Conclusion

- Base Llama raw: unusable, fallback.
- Instruct raw: code output, parse 0.0.
- Instruct chat user-only: code output.
- Instruct chat + system: valid JSON, but constant high severity.
- Paper says system-level JSON instructions. Public code has no system role.
- Full A1 run with this judge would likely be low F1. Not run.

## Paper model ambiguity

Paper: Llama-3.2-3B. No base/instruct statement. Repo code path: base. README example: Instruct.

Neither public path reproduces 0.7413. See `docs/model-comparison.md`.
