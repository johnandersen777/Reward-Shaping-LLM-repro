# 0010 Base Llama EOS Finding

Single forward probe. Full llm_shaping prompt. 311 input tokens.

Device map: `{'0': 14, 'cpu': 18}`. Split works.

Top next-token candidates:

```text
TOPK_IDS     [128001, 720, 4815, 220, 2355, 320, 29971, 1492, 510, 482]
TOPK_TOKENS  ['<|end_of_text|>', ' \n', ' \n\n', ' ', '  \n', ' (', ' Sequence', ' ->', ' [', ' -']
TOPK_LOGITS  [16.5, 14.3672, 13.1875, 13.0938, 13.0156, 12.7656, 12.4375, 12.1328, 11.9453, 11.6719]
EOS_ID       128001
```

Top-1 is EOS. Greedy decode stops at first token. `return_full_text=False` then returns `""`.

Empty string triggers `_heuristic_phi`. Fallback.

Cause: base checkpoint, not instruction tuned. Not environment bug.

Probe command:

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env PYTHONPATH=/home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_winorder/repo:/home/baptist777/.tmp/tmp.VjJfPBPNr4/env \
  PYTHONDONTWRITEBYTECODE=1 RSL_PRELOAD_TORCH=1 \
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  OPENAI_API_KEY=unused LLM_CHOICE=llama-3 \
  .venv38/bin/python env/llama_topk.py
```

## Consequence

README model example: `llama-3.2-3b-instruct`.

Base checkpoint cannot follow prompt. Instruct checkpoint is next test.

Authors' committed Llama exp has fallback values and mean F1 0.0269. Consistent with base model empty output.

See `0008-historical-artifacts.md`.
