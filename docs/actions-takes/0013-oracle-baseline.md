# 0013 Oracle Baseline Rationale

User asked: run real labels through mock server, simulate perfect LLM. Sound baseline?

Answer: yes, as diagnostic. No, as paper baseline.

## Already implemented

`MOCK_MODE=oracle`. Server port 8766.

`mock_llm/build_oracle_lookup.py` maps prompt text to ground-truth label at window end.

- 93,258 windows.
- 85,778 unique prompt texts.
- 7,480 text collisions.
- 616 label conflicts (0.7%).
- 1,613 anomalous unique texts.

Lookup keys reproduce env.py MinMaxScaler plus llm_shaping z-score formatting exactly.

All oracle requests during runs hit: 2,128/2,128 at last check.

## Sound parts

- Tests whether shaped reward reaches Q-learning.
- Perfect phi removes LLM noise and parsing errors.
- Matches note 4 diagnostic: if oracle changes nothing, reward path broken.
- No prompt or code changes.

## Not sound as paper baseline

- Oracle is not an LLM. Numbers not comparable to Table II.
- Severity binary 0/1. LLM severity graded.
- Text collisions: 616 keys ambiguous.
- Severity tied to window-end label. Other definitions possible.
- Canary windows miss lookup, fall back to heuristic.
- Fixed 3 episodes, 10 updates each, epsilon near 1. Learning ceiling low.
- F1 variance across runs is large. Reward effect may be masked.

## Final results

Heuristic, 5 runs, fresh copy each:

```text
h1 0.0000
h2 0.2888
h3 0.0000
h4 0.0548
h5 0.0000
mean 0.0687  std 0.1120
```

Oracle, 5 runs:

```text
o1 0.1340
o2 0.2350
o3 0.2988
o4 0.1905
o5 0.0000
mean 0.1716  std 0.1014
```

Mean difference: +0.1032.

```text
bootstrap 95% CI  [-0.0397, +0.2223]
P(diff > 0)        0.9274
Welch t-test p     0.2106
Mann-Whitney p     0.1179
```

## Interpretation

Direction favors oracle. Not statistically significant at n=5. Variance high. One oracle run 0.0.

Both means low: 3 episodes, 30 gradient updates, epsilon near 1. Policy barely trained.

This tests reward plumbing. Not paper performance.

All 25,819 oracle prompts hit lookup. Zero misses.

## Phi-2 pause

Phi-2 full run stopped to free CPU for oracle suite. Log: `run/A1_phi2/run.log`. Restart later.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_winorder/repo
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/run_real_a1_phi2.sh \
  > /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_phi2/run.log 2>&1
```
