# 0014 Metrics And Oracle Relation

README table, lines 148-157:

```text
| Dataset  | LLM          | Precision | Recall |   F1   |
| Yahoo-A1 | Llama-3.2-3B |    0.6051 | 0.9565 | 0.7413 |
| SMD      | Llama-3.2-3B |    0.3813 | 0.8685 | 0.5300 |
```

## Columns

- Precision = TP / (TP + FP). Fraction of alarms that are real.
- Recall = TP / (TP + FN). Fraction of anomalies caught.
- F1 = 2 * P * R / (P + R). Harmonic mean.

Validation averages over series, timestamp level.

## Oracle

Oracle changes reward hint only. F1 still measures RL agent actions.

Oracle test asks: does perfect hint improve learning?

## Why oracle may not beat LLM

- 3 episodes, 30 gradient updates, epsilon near 1.
- PBRS preserves optimal policy; hint only.
- Oracle binary, sparse. LLM graded.
- Unlabeled steps: raw reward `[0,0]`. Only potential acts.
- VAE reinitialized after load. Random reward term.
- No seeds. High variance.
- n=5. Difference not significant.
- README numbers from authors' env. Not same protocol.

Oracle correctness = hint correctness, not agent correctness.

## Same-experiment comparison

```text
heuristic mean F1 0.0687
oracle    mean F1 0.1716
diff +0.103, 95% CI [-0.040, +0.222], Welch p 0.21
```

Direction favors oracle. Not significant.
