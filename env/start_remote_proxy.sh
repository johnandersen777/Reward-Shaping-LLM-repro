#!/bin/bash
# Generic OpenAI-compatible proxy to a remote inference endpoint.
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
cd "$ROOT/mock_llm"
: "${REMOTE_BASE_URL:?set REMOTE_BASE_URL, e.g. http://host:port/v1}"
: "${REMOTE_MODEL:?set REMOTE_MODEL}"
export MOCK_MODE=remote_openai
export REMOTE_MODE="${REMOTE_MODE:-completion}"
export REMOTE_API_KEY="${REMOTE_API_KEY:-}"
export MOCK_LLM_LOG="${MOCK_LLM_LOG:-$ROOT/mock_llm/remote_requests.jsonl}"
exec "$ROOT/.venv38/bin/python" -m uvicorn server:app \
  --host 127.0.0.1 --port "${PORT:-8772}" --log-level warning
