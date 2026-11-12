#!/bin/bash
set -euo pipefail
DEST="$HOME/models/Ternary-Bonsai-2-9B-gguf"
mkdir -p "$DEST"
BASE="https://huggingface.co/prism-ml/Ternary-Bonsai-2-9B-gguf/resolve/main"
for f in SHA256SUMS Ternary-Bonsai-2-9B-PQ2_0-MTP-Q8_0.gguf; do
  echo "downloading $f"
  curl -L --fail --retry 5 --retry-delay 5 -C - -o "$DEST/$f" "$BASE/$f"
done
cd "$DEST"
sha256sum -c <(grep 'PQ2_0-MTP-Q8_0.gguf' SHA256SUMS)
echo DONE
