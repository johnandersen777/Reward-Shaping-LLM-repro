# Model Comparison: Llama-3.2-3B vs Ternary-Bonsai-2-9B

Question: which model is more capable, and which would we expect higher F1?

## Fact table

| Model | Params | Type | MMLU | IFEval | GSM8K |
| --- | ---: | --- | ---: | ---: | ---: |
| Llama-3.2-3B base | 3.21B | base, no chat template | 58 | ~13.7 avg | n/a |
| Llama-3.2-3B-Instruct | 3.21B | SFT+DPO chat | 63.4 | 77.4 | 77.7 |
| Qwen3.5-9B | ~9B | post-trained chat | 82.6 indep / 82.5 MMLU-Pro vendor | 69.9 indep / 91.5 vendor | 81.3 indep |
| Bonsai-2-9B | ~8.95B LM + 0.46B vision | ternary Qwen3.5-9B | 86.95 MMLU-Redux vendor | 90.02 vendor, thinking on | 95.07 vendor |

Sources:

- Llama base: https://huggingface.co/meta-llama/Llama-3.2-3B
- Llama Instruct: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
- Qwen3.5-9B: https://huggingface.co/Qwen/Qwen3.5-9B
- Independent Qwen: https://trustthebench.com/models/qwen-qwen3-5-9b
- Bonsai: https://huggingface.co/prism-ml/Ternary-Bonsai-2-9B-gguf
- PrismML whitepaper: https://github.com/PrismML-Eng/Bonsai-demo/blob/main/bonsai-2-small-whitepaper.pdf

## Capability

General capability ranking:

```text
Bonsai-2-9B / Qwen3.5-9B  >  Llama-3.2-3B-Instruct  >  Llama-3.2-3B base
```

Bonsai caveats:

- Ternary 2-bit weights. Vendor claims 95.1% average retention.
- Independent dev NLL 3.191 vs Qwen BF16 2.423. About 2.16x perplexity on that set.
- Task scores mixed: GSM8K 77/100 both, HumanEval 45/50 vs 44/50, ARC 17/20 vs 19/20.
- Independent JSON tests: legal syntax, but 43% self-contradictory semantics in one production replay.

Llama base caveat:

- IFEval ~13.7. Poor instruction following.
- Raw completion mode. No chat template.

## Expected F1

F1 measures the trained RL policy, not model benchmark score.

Task-specific evidence:

- Llama-3.2-3B-Instruct zero-shot anomaly label F1: 0.5391 univariate, 0.5860 multivariate (Time-RA, arXiv 2507.15066).
- Same model as numeric scoring judge: zero-shot Spearman 0.217, 4-shot collapses (IndicQE/WMT 2026).
- No independent Bonsai-2-9B anomaly-detection or numeric-judge evaluation found.
- Our Bonsai A1 run: F1 0.00938. Phi >=0.70 on ~88% of windows.
- Our Llama-3.2-3B base raw: empty output, fallback. F1 would be fallback-level.
- Our Llama-3.2-3B-Instruct raw: writes Python code. Parse score 0.0.
- Our Llama-3.2-3B-Instruct chat, user-only: writes Python code.
- Our Llama-3.2-3B-Instruct chat + system JSON instruction: valid JSON, but 0.95 on all tested normal and anomaly windows. No discrimination.

Expected ranking on this task, if both produce numeric severity:

```text
Llama-3.2-3B-Instruct  >  Bonsai-2-9B  ~  Llama-3.2-3B base (fallback)
```

Reason: Llama-Instruct has published anomaly-label F1 around 0.54-0.59 and is instruction tuned. Bonsai is more capable generally but has no anomaly calibration evidence, and our run over-flagged.

But: our exact prompt tests show both over-flag. Paper Llama F1 0.7413 remains unreproduced. Paper says system-level JSON instructions; public code has no system role. Paper never states base vs instruct. Repo conflict: code path base, README example Instruct.

## Bottom line

More capable model: Bonsai-2-9B.

Likely higher F1 on this anomaly-labeling task: Llama-3.2-3B-Instruct, if properly formatted. General capability does not imply calibrated severity.

Neither public path reproduces 0.7413. Missing setup: exact model variant, system prompt, template, or training details.
