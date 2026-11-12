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

## FAQ: label confusion

### All data labeled?

Benchmark: yes. Every timestamp in all 67 A1 series has ground truth.

Experiment: no. Code sets `label=-1`. Active learning queries 1000 points per episode. Label propagation adds up to 200 pseudo-labels. Reward uses mixed `label`.

### Oracle smaller dataset?

No. Lookup built from all 67 series, 93,258 windows. 85,778 unique prompt texts. 25,819/25,819 oracle calls hit.

It memoizes full ground truth. Not a model. Not a subset. Has future-label access, so upper-bound diagnostic, not deployable baseline.

### What oracle replaces

Only `phi(s)`:

```text
r' = r + gamma*phi(s') - phi(s)
```

Agent still picks actions. F1 scores agent. Correct hint != correct agent.

### Perfect hint worse? Possible

- PBRS preserves optimal policy. Perfect phi changes learning path, not policy ceiling.
- 3 episodes, 30 updates, epsilon near 1. Weak learner.
- Binary 0/1 oracle is sparse. LLM graded. Potential uses differences. Sparse signal may be worse shaped.
- Reward labels include pseudo-labels. Oracle phi uses true labels. Conflict possible.
- No seeds. High variance. n=5.
- Active learning already supplies up to 1000 true action labels per episode. F1 still low. Training is bottleneck.

### README comparison invalid

README Llama 0.7413 from authors' environment. Our Llama paths fail: base EOS, Instruct code. Phi-2 run pending.

Oracle 0.17 vs README 0.74 is not same experiment.

Valid comparison: oracle vs heuristic, same setup. Oracle better on average, not worse.

### Analogy

Perfect answer key to student who studies 30 minutes with random guessing. Key correct. Score low.

## Why a perfect label is not a perfect potential

Three objects:

1. Ground-truth label: is timestamp t anomalous?
2. Potential / severity hint: reward input.
3. Learned policy: scored by F1.

Oracle is perfect at (1), not necessarily good at (2). F1 scores (3).

Binary oracle on A1:

- Anomaly rate 1.76%.
- `phi=1` ~1.76% of windows, `phi=0` ~98.24%.
- Shaping term `gamma*phi(s') - phi(s)` is zero on most steps.
- Nonzero only at boundaries, as ±0.96 jumps.
- Almost silent. Huge discontinuous deltas.

Graded LLM:

- Scores vary widely.
- Shaping term nonzero on most steps.
- Smaller, smoother deltas.
- Dense guidance.

80% correct dense guidance can beat 100% correct sparse guidance.

Other reasons:

- Perfect label is not a value function. PBRS prefers smooth state value.
- Timing: oracle marks point; graded hint can anticipate.
- Exploration: sparse hard signals can destabilize; smooth hints balance.
- Finite training: PBRS preserves optimal policy, no guaranteed speedup.
- Variance ~0.10 F1. Single-run comparisons meaningless.

What we know:

- No working real LLM run here. Base EOS, Instruct code.
- README 0.7413 from authors' environment. Not controlled comparison.
- Local controlled test: oracle 0.1716 > heuristic 0.0687.
- Noise cannot add 0.57 F1 when perfect hint gives 0.17.

One sentence: oracle perfect at labeling, F1 measures learning. Sparse perfect hint can be less useful than dense imperfect hint.
