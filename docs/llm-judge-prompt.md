# LLM Judge Prompt

Exact prompt from `llm_shaping.py:69-82`, active version.

## Links

- Prompt source: https://github.com/baharehgl/Reward-Shaping-LLM/blob/main/llm_shaping.py#L69-L82
- Raw file: https://raw.githubusercontent.com/baharehgl/Reward-Shaping-LLM/main/llm_shaping.py
- Paper Section III-C: https://arxiv.org/html/2601.02511v1
- README model example: https://github.com/baharehgl/Reward-Shaping-LLM/blob/main/README.md

Paper describes the prompt. Paper does not print the exact string. Code is the source.

```text
Task: Score anomaly severity in a numeric sequence.
Return ONLY JSON {"severity": s} with s in [0.0, 1.0]. Use the full range.
Guidelines: 0.00 normal noise; 0.25 small drift; 0.50 mean shift/moderate spikes; 0.75 sustained spikes; 0.95 extreme outliers.
Examples:
  [0,0,0,0,0]             -> {"severity": 0.00}
  [0,0,0.1,0.2,0.1]       -> {"severity": 0.25}
  [0,0,1.5,1.7,1.6]       -> {"severity": 0.70}
  [0,3.0,0,-2.5,0]        -> {"severity": 0.95}
Sequence: [<25 values>]
```

## Sequence construction

1. Env min-max scales each series to [0,1].
2. Take 25 consecutive values.
3. Round each to 2 decimals.
4. Z-score over the 25 values: `(x - mean) / std`.
5. Format each to 2 decimals. Join with `", "`.
6. Constant window: std < 1e-8 -> all `0.00`.

Example tail:

```text
Sequence: [0.00, 0.23, 0.73, 0.73, 0.71, 0.68, 0.70, 0.64, 0.72, 0.85, 0.93, 0.86, 0.62, 0.48, 0.35, 0.28, 0.29, 0.23, 0.34, 0.43, 0.58, 0.70, 0.69, 0.73, 0.71]
```

## Wrapping

- Llama local path: raw prompt to HF `text-generation` pipeline. `max_new_tokens=32`, greedy.
- Bonsai path: same text as one `user` message. Qwen chat template. `enable_thinking=false`. Greedy. 32 max tokens.
- Remote Instruct path: same text as one `user` message. Llama chat template. Proxy injects a system message. Greedy. 32 max tokens.

## Failure Modes Seen

Base Llama raw:

```text
top token EOS 128001
raw='' -> fallback
```

Instruct Llama raw:

```text
raw='Here is a Python function that calculates the anomaly severity...'
score=0.0
```

Instruct Llama chat, user-only:

```text
raw='Here is a Python function that calculates the anomaly severity...'
score=0.0
```

Instruct Llama chat + system JSON instruction:

```text
zeros -> {"severity": 0.00}
spike -> {"severity": 0.95}
normal windows -> 0.95
anomaly windows -> 0.95
```

Valid JSON. No discrimination.

"Fail" means no discriminative severity under the code prompt/wrapper. Not a claim that the paper is wrong.

## Paper vs Code

Paper: “system-level instructions enforcing JSON-only output.”

Code: one raw string prompt. No system role. No chat template.

Paper: Llama-3.2-3B. No base vs Instruct statement.

Code: base path. README example: Instruct. Conflict unresolved.

## System Prompt Used

```text
You are an anomaly severity judge. Return ONLY JSON {"severity": s} with s in [0.0,1.0]. Never write code.
```

Injected by `mock_llm/server.py` when `REMOTE_SYSTEM_PROMPT` is set. This is a wrapper change. User-directed.

## Comparability

Paper Llama row vs Bonsai row differ in model family, precision, quantization, runtime, and prompt formatting. F1 values not directly comparable.

Bonsai prompt compliance: ~88% of 5,322 unique windows scored >= 0.70, despite prompt saying normal = 0.00. Model over-flags. See `0015-bonsai-mtp-q8.md`.
