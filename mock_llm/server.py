"""OpenAI-compatible mock LLM server for plumbing tests.

Serves POST /v1/chat/completions with deterministic mock severity scores.
It is NOT Llama and must never be used to claim reproduction numbers.
Every request/response is appended to mock_llm/requests.jsonl.
"""

import json
import math
import os
import pickle
import re
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="mock-llm", version="0.1.0")

LOG_PATH = os.environ.get(
    "MOCK_LLM_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests.jsonl"),
)
MODE = os.environ.get("MOCK_MODE", "heuristic")
ORACLE_PATH = os.environ.get(
    "ORACLE_LOOKUP",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle_lookup.pkl"),
)
SEQ_RE = re.compile(r"Sequence:\s*\[([^\]]*)\]")
NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")

_ORACLE = None
if MODE == "oracle":
    with open(ORACLE_PATH, "rb") as _fh:
        _ORACLE = pickle.load(_fh)



def parse_sequence(prompt: str):
    match = SEQ_RE.search(prompt or "")
    if not match:
        return []
    return [float(x) for x in NUM_RE.findall(match.group(1))]


def canonical_sequence(prompt):
    """Reproduce the comma-space 2-decimal sequence text emitted by llm_shaping."""
    return ", ".join(f"{v:.2f}" for v in parse_sequence(prompt))


def mock_severity(values):
    """Deterministic, monotone in max |z|. Distinguishable from the z-fallback."""
    if not values:
        return 0.5
    zmax = max(abs(v) for v in values)
    score = 0.05 + 0.18 * zmax
    score = max(0.0, min(0.95, score))
    return round(score, 2)


def log_record(record):
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


@app.get("/health")
def health():
    return {"status": "ok", "log": LOG_PATH}


@app.get("/v1/models")
def models():
    now = int(time.time())
    return {
        "object": "list",
        "data": [
            {
                "id": "mock-llama-3.2-3b",
                "object": "model",
                "created": now,
                "owned_by": "local-mock",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages") or []
    prompt = "\n".join(str(m.get("content", "")) for m in messages)
    values = parse_sequence(prompt)
    hit = None
    if MODE == "oracle":
        text = canonical_sequence(prompt)
        if text in _ORACLE:
            severity = float(_ORACLE[text])
            hit = True
        else:
            severity = mock_severity(values)
            hit = False
    else:
        severity = mock_severity(values)
    content = json.dumps({"severity": severity})

    log_record(
        {
            "ts": time.time(),
            "mode": MODE,
            "hit": hit,
            "model": body.get("model"),
            "n_values": len(values),
            "max_abs": max((abs(v) for v in values), default=None),
            "severity": severity,
            "prompt_chars": len(prompt),
        }
    )

    now = int(time.time())
    return JSONResponse(
        {
            "id": "chatcmpl-mock",
            "object": "chat.completion",
            "created": now,
            "model": body.get("model", "mock-llama-3.2-3b"),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": max(1, len(prompt) // 4),
                "completion_tokens": 8,
                "total_tokens": max(9, len(prompt) // 4 + 8),
            },
        }
    )
