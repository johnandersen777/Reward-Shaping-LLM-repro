# Aborted Full Budget Run

Run: `paperbudget_e200_u1000_d500000_s200`
Aborted: 2026-11-14 about 03:00-08:00.

## Cause

Claude Code low-memory reaper killed background shell `blfq8hy3k` (the chain wrapper) while the session sat idle. Training process died with it. Host had two external qemu VMs using 12.6 GB and 7.4 GB.

Not a training crash. Not a code fault.

## State at abort

```text
episodes reached   140 / 200
updates            140,000
LLM call failures  0
```

## Checkpoint

Latest saved checkpoint: episode 99 (paper code saves every 50 episodes). Validated earlier: mean F1 0.405053.

Aborted before episode 149 save.

## Artifacts

```text
checkpoints/   episode 99 checkpoint, relative state file
meta.json      run metadata
run.log.gz     full training log
```

## Status

No final average. Not a result. Kept for disclosure.
