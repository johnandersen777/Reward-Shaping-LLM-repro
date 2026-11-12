#!/bin/bash
# OpenAI-compatible proxy to llama-server raw /completion.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
cd "$ROOT/mock_llm"
export MOCK_MODE=llama_cpp
export LLAMA_CPP_URL="${LLAMA_CPP_URL:-http://127.0.0.1:8770}"
export MOCK_LLM_LOG="${MOCK_LLM_LOG:-$ROOT/mock_llm/bonsai_requests.jsonl}"
exec "$ROOT/.venv38/bin/python" -m uvicorn server:app \
  --host 127.0.0.1 --port "${PORT:-8771}" --log-level warning
