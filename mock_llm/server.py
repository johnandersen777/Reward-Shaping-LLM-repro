"""OpenAI-compatible mock LLM server for plumbing tests.

Serves POST /v1/chat/completions with deterministic mock severity scores.
It is NOT Llama and must never be used to claim reproduction numbers.
Every request/response is appended to mock_llm/requests.jsonl.
"""

import hashlib
import json
import math
import os
import pickle
import re
import time

import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="mock-llm", version="0.1.0")

LOG_PATH = os.environ.get(
    "MOCK_LLM_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests.jsonl"),
)
MODE = os.environ.get("MOCK_MODE", "heuristic")
ORACLE_FLIP_RATE = float(os.environ.get("ORACLE_FLIP_RATE", "0"))
ORACLE_NOISE_SEED = os.environ.get("ORACLE_NOISE_SEED", "0")
LLAMA_CPP_URL = os.environ.get("LLAMA_CPP_URL", "http://127.0.0.1:8770").rstrip("/")
REMOTE_BASE_URL = os.environ.get("REMOTE_BASE_URL", "").rstrip("/")
REMOTE_MODEL = os.environ.get("REMOTE_MODEL", "")
REMOTE_MODE = os.environ.get("REMOTE_MODE", "chat")
REMOTE_API_KEY = os.environ.get("REMOTE_API_KEY", "")
REMOTE_SYSTEM_PROMPT = os.environ.get("REMOTE_SYSTEM_PROMPT", "")
ORACLE_PATH = os.environ.get(
    "ORACLE_LOOKUP",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle_lookup.pkl"),
)
SEQ_RE = re.compile(r"Sequence:\s*\[([^\]]*)\]")
NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")

_ORACLE = None
if MODE in ("oracle", "noisy_oracle"):
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


def _hash_unit(text, salt):
    digest = hashlib.sha256(
        (ORACLE_NOISE_SEED + "|" + salt + "|" + text).encode("utf-8")
    ).digest()
    return int.from_bytes(digest[:8], "big") / float(2 ** 64)


def noisy_oracle_severity(text, label):
    """Graded severity. Wrong with prob ORACLE_FLIP_RATE, always JSON-ready."""
    wrong = _hash_unit(text, "flip") < ORACLE_FLIP_RATE
    u = _hash_unit(text, "value")
    positive = (label >= 0.5) != wrong
    severity = 0.75 + 0.25 * u if positive else 0.25 * u
    return round(float(severity), 2), wrong


def log_record(record):
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def call_llama_cpp(messages):
    payload = {
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 32,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    resp = requests.post(LLAMA_CPP_URL + "/v1/chat/completions", json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"].get("content") or ""
    return content, data


def call_remote_openai(prompt, messages):
    headers = {}
    if REMOTE_API_KEY:
        headers["Authorization"] = "Bearer " + REMOTE_API_KEY
    if REMOTE_MODE == "completion":
        url = REMOTE_BASE_URL + "/completions"
        payload = {
            "model": REMOTE_MODEL,
            "prompt": prompt,
            "temperature": 0.0,
            "max_tokens": 32,
            "stream": False,
        }
    else:
        url = REMOTE_BASE_URL + "/chat/completions"
        send_messages = messages
        if REMOTE_SYSTEM_PROMPT:
            send_messages = [{"role": "system", "content": REMOTE_SYSTEM_PROMPT}] + list(messages)
        payload = {
            "model": REMOTE_MODEL,
            "messages": send_messages,
            "temperature": 0.0,
            "max_tokens": 32,
        }
    resp = requests.post(url, json=payload, headers=headers, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    if REMOTE_MODE == "completion":
        content = data["choices"][0].get("text") or ""
    else:
        content = data["choices"][0]["message"].get("content") or ""
    return content, data


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": MODE,
        "backend": LLAMA_CPP_URL,
        "remote": REMOTE_BASE_URL,
        "remote_model": REMOTE_MODEL,
        "remote_mode": REMOTE_MODE,
        "remote_system_prompt": REMOTE_SYSTEM_PROMPT,
        "remote_api_key_set": bool(REMOTE_API_KEY),
        "log": LOG_PATH,
    }


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
    severity = None
    backend_ms = None
    flipped = None
    if MODE == "llama_cpp":
        t0 = time.time()
        content, backend = call_llama_cpp(messages)
        backend_ms = round((time.time() - t0) * 1000.0, 1)
    elif MODE == "remote_openai":
        t0 = time.time()
        content, backend = call_remote_openai(prompt, messages)
        backend_ms = round((time.time() - t0) * 1000.0, 1)
    elif MODE == "noisy_oracle":
        text = canonical_sequence(prompt)
        if text in _ORACLE:
            label = float(_ORACLE[text])
            hit = True
            severity, flipped = noisy_oracle_severity(text, label)
        else:
            severity = mock_severity(values)
            hit = False
        content = json.dumps({"severity": severity})
        backend = None
    else:
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
        backend = None

    log_record(
        {
            "ts": time.time(),
            "mode": MODE,
            "hit": hit,
            "flipped": flipped,
            "flip_rate": ORACLE_FLIP_RATE,
            "model": body.get("model"),
            "n_values": len(values),
            "max_abs": max((abs(v) for v in values), default=None),
            "severity": severity,
            "backend_ms": backend_ms,
            "content_prefix": content[:80],
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
