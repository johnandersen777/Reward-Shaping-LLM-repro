# 0005 Mock LLM Server

FastAPI OpenAI-compatible mock. Stands in for Llama. Plumbing only. Never paper results.

Files:

- `mock_llm/server.py`
- `mock_llm/build_oracle_lookup.py`
- `mock_llm/requests.jsonl`
- `mock_llm/oracle_requests.jsonl`
- `mock_llm/oracle_lookup.pkl`

## Start Heuristic Server

Port 8765. Severity `0.05 + 0.18 * max|z|`, clamp `[0, 0.95]`.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/mock_llm
../.venv38/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8765 --log-level warning
```

## Start Oracle Server

Port 8766. Ground-truth lookup. Severity 1.0 if window-end timestamp anomalous, else 0.0.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/mock_llm
env MOCK_MODE=oracle \
  MOCK_LLM_LOG=/home/baptist777/.tmp/tmp.VjJfPBPNr4/mock_llm/oracle_requests.jsonl \
  ../.venv38/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8766 --log-level warning
```

## Health Check

```bash
curl -sS http://127.0.0.1:8765/health
curl -sS http://127.0.0.1:8766/health
```

## Test Completion

```bash
curl -sS -X POST http://127.0.0.1:8765/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Sequence: [0.0, 0.0, 0.0, 10.0]"}]}'
```

Content: `{"severity": 0.95}`.

## Build Oracle Lookup

Replicates env.py MinMaxScaler and llm_shaping z-score prompt text.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
.venv38/bin/python mock_llm/build_oracle_lookup.py
```

Seen:

```text
windows=93258 unique_texts=85778 collisions=7480 conflicts=616
anomalous_unique=1613 normal_unique=84165
```

## Client Env

openai 1.54.4. Needs `OPENAI_BASE_URL`. httpx pinned 0.27.2.

```bash
export OPENAI_API_KEY=mock-key
export OPENAI_BASE_URL=http://127.0.0.1:8765/v1
export LLM_CHOICE=gpt-3.5-turbo
export PHI_DEBUG=1
```

## Canary

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_mock/repo:/home/baptist777/.tmp/tmp.VjJfPBPNr4/env \
  PYTHONDONTWRITEBYTECODE=1 OPENAI_API_KEY=mock-key \
  OPENAI_BASE_URL=http://127.0.0.1:8765/v1 LLM_CHOICE=gpt-3.5-turbo \
  PHI_DEBUG=1 .venv38/bin/python env/check_llm.py
```

Seen: parsed `0.05` and `0.93`. Fallback not fired.

## Oracle Hit

Real A1 window, `real_1.csv` index 100. Response `{"severity": 0.0}`. True label 0.0. Server log `"hit": true`.
