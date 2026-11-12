#!/bin/bash
set -euo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
export HF_HUB_ENABLE_HF_TRANSFER=0
"$ROOT/.venv38/bin/python" - <<'PY'
from huggingface_hub import snapshot_download
patterns = [
    "*.json", "*.safetensors", "*.txt", "*.model", "*.vocab",
    "merges.txt", "vocab.json", "tokenizer.json",
    "config.json", "generation_config.json",
]
path = snapshot_download("microsoft/phi-2", allow_patterns=patterns)
print("DONE", path)
PY
