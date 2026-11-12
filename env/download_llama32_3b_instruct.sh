#!/bin/bash
set -euo pipefail
TOKEN="$(cat "$HOME/.cache/huggingface/token")"
DEST="$HOME/llama-models/Llama-3.2-3B-Instruct"
mkdir -p "$DEST"
FILES=(
  config.json
  generation_config.json
  model.safetensors.index.json
  model-00001-of-00002.safetensors
  model-00002-of-00002.safetensors
  special_tokens_map.json
  tokenizer.json
  tokenizer_config.json
)
for f in "${FILES[@]}"; do
  echo "downloading $f"
  curl -L --fail --retry 5 --retry-delay 5 -C - \
    -H "Authorization: Bearer $TOKEN" \
    -o "$DEST/$f" \
    "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct/resolve/main/$f"
done
echo "DONE"
