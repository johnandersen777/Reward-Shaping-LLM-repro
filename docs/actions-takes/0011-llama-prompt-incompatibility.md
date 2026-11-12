# 0011 Llama Prompt Incompatibility

## Base

Top-1 token EOS (`128001`, logit 16.5). Empty output. Fallback.

See `0010-base-llama-eos.md`.

## Instruct

Same raw prompt. Same pipeline. Output starts with Python code, not JSON:

```text
\n\n```python\ndef score_anomaly_severity(sequence):\n    """\n    Score anomaly severity in a numeric sequence.
```

`_parse_severity` finds no number. Returns 0.0. Raw nonempty, so fallback does NOT fire.

Both canaries: `phi(zeros)=0.0`, `phi(spike)=0.0`.

Command:

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/check_instruct.sh
```

## pyc Check

Tracked `__pycache__/llm_shaping.cpython-38.pyc` has same prompt and same pipeline strings. No `apply_chat_template`. No chat path.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/Reward-Shaping-LLM
strings __pycache__/llm_shaping.cpython-38.pyc | \
  grep -iE 'apply_chat|chat_template|text-generation|return_full|device_map|from_pretrained'
```

## Conclusion

Public code + official base or Instruct checkpoint + raw prompt gives no numeric severity.

Table II Llama row not reproducible this way.

Causes possible:

1. Authors used chat-template wrapper not in repo.
2. Authors used a different local checkpoint or fine-tune.
3. Prompt differs from repo.

Note 3 forbids prompt or wrapper changes.

## Options

- Phi-2 control: code supports `LLM_CHOICE=phi-2`. Historical Phi exp has discrete phi values. Validates pipeline and another Table II row.
- Chat template for Llama: changes wrapper. Violates note 3.
- Ask authors for exact local model folder and prompt.
- Stop Llama path. Keep mock results and blocker documented.
