#!/bin/bash
# Watch a run for per-episode checkpoints. Copy each to models/<tag>/episodes/,
# validate it (restore-only), append F1, commit and push.
# Usage: watch_episode_checkpoints.sh <tag>
# Stop: touch run/STOP_WATCH_<tag>
set -uo pipefail
ROOT=/home/baptist777/.tmp/tmp.VjJfPBPNr4
TAG="$1"
RUN="$ROOT/run/$TAG"
MODEL="$ROOT/models/$TAG"
CSV="$MODEL/episode_f1.csv"
LOG="$RUN/watcher.log"
STOP="$ROOT/run/STOP_WATCH_$TAG"
mkdir -p "$MODEL/episodes" "$RUN"
shopt -s nullglob
echo "watcher start $TAG $(date -Is)" >> "$LOG"
while [ ! -f "$STOP" ]; do
  if [ -f "$RUN/meta.json" ] && [ ! -f "$MODEL/meta.json" ]; then
    cp "$RUN/meta.json" "$MODEL/meta.json"
  fi
  for d in "$RUN"/repo/exp/*/checkpoints/ep[0-9][0-9][0-9][0-9]; do
    [ -d "$d" ] || continue
    ep="$(basename "$d")"
    dst="$MODEL/episodes/$ep"
    if [ ! -f "$dst/model.index" ]; then
      tmp="$MODEL/episodes/.tmp_$ep"
      rm -rf "$tmp"; mkdir -p "$tmp"
      if cp -a "$d/model.data-00000-of-00001" "$d/model.index" "$d/checkpoint" "$tmp/" 2>/dev/null; then
        mv "$tmp" "$dst"
        # Relative state file so the committed copy restores on any machine.
        printf 'model_checkpoint_path: "model"\nall_model_checkpoint_paths: "model"\n' > "$dst/checkpoint"
        echo "copied $ep $(date -Is)" >> "$LOG"
      else
        rm -rf "$tmp"
        echo "incomplete $ep, retry next loop" >> "$LOG"
        continue
      fi
    fi
    if [ -f "$MODEL/episodes/.failed_$ep" ]; then continue; fi
    if grep -q "^$ep," "$CSV" 2>/dev/null; then continue; fi
    until curl -sf -o /dev/null --max-time 5 http://127.0.0.1:8772/health; do
      echo "waiting for proxy $(date -Is)" >> "$LOG"
      sleep 30
      [ -f "$STOP" ] && break
    done
    if "$ROOT/env/validate_episode_checkpoint.sh" "$TAG" "${ep#ep}" >> "$LOG" 2>&1; then
      if [ "${RSL_WATCH_COMMIT:-1}" = "1" ]; then
        "$ROOT/env/commit_episode_checkpoint.sh" "$TAG" "${ep#ep}" >> "$LOG" 2>&1 || echo "commit failed $ep" >> "$LOG"
      fi
    else
      touch "$MODEL/episodes/.failed_$ep"
      echo "validate failed $ep, marker set" >> "$LOG"
    fi
  done
  pending=0
  if [ ! -f "$RUN/DONE" ]; then
    pending=1
  else
    for d in "$RUN"/repo/exp/*/checkpoints/ep[0-9][0-9][0-9][0-9]; do
      ep="$(basename "$d")"
      if ! grep -q "^$ep," "$CSV" 2>/dev/null && [ ! -f "$MODEL/episodes/.failed_$ep" ]; then
        pending=1
      fi
    done
  fi
  if [ "$pending" = "0" ]; then
    echo "run DONE, all episodes processed $(date -Is)" >> "$LOG"
    break
  fi
  sleep 60
done
echo "watcher stop $TAG $(date -Is)" >> "$LOG"
