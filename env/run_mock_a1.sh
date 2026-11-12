#!/bin/bash
# Run the research code against the mock OpenAI-compatible server.
# Usage: run_mock_a1.sh [/path/to/repo-copy]
set -euo pipefail
ROOT="${1:-/home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_mock/repo}"
PY=/home/baptist777/.tmp/tmp.VjJfPBPNr4/.venv38/bin/python
export PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/env
export PYTHONDONTWRITEBYTECODE=1
export OPENAI_API_KEY=mock-key
export OPENAI_BASE_URL="http://127.0.0.1:${MOCK_PORT:-8765}/v1"
export LLM_CHOICE=gpt-3.5-turbo
export PHI_DEBUG=1
cd "$ROOT"
exec "$PY" myasp-A1.py
