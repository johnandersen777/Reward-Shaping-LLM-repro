#!/bin/bash
set -euo pipefail
DEST="$HOME/llama.cpp-prism"
mkdir -p "$DEST"
URL="https://github.com/PrismML-Eng/llama.cpp/releases/download/prism-b10776-d00e252/llama-prism-b10776-d00e252-bin-linux-cuda-13.3-x64.tar.gz"
curl -L --fail --retry 5 --retry-delay 5 -C - -o "$DEST/llama-prism.tar.gz" "$URL"
tar -xzf "$DEST/llama-prism.tar.gz" -C "$DEST"
echo DONE
ls -la "$DEST"
