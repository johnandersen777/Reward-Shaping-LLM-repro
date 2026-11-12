# 0006 A1 Mock Runs

Research code untouched. Fresh copies. Mock LLM. Plumbing only.

## First Full Run

Copy: `run/A1_mock/repo`. Server port 8765.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env/run_mock_a1.sh /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_mock/repo
```

Run in background. Log: `run/A1_mock/run.log`.

Result: exit 0. Full pipeline. 3 train episodes. 6 validation episodes.

Per-episode F1:

```text
0.1333 0.3111 0.7083 0.1472 0.1739 0.0000
```

Average F1 = 0.2457. Mock reward. Not paper result.

LLM requests: 4607. Duration over requests: 171 s. Fallback never fired. Smoke reward check: `0.96*0.38 - 0.49 = -0.1252`, matched printed `-0.1252`.

Outputs:

```text
run/A1_mock/repo/exp/A1_LP200_AL1000_d0.96/llm_potentials.csv
run/A1_mock/repo/exp/A1_LP200_AL1000_d0.96/plots/
run/A1_mock/repo/exp/A1_LP200_AL1000_d0.96/detections_episode_0..5.svg
run/A1_mock/repo/exp/A1_LP200_AL1000_d0.96performance.txt
```

## Suite

5 heuristic runs + 5 oracle runs. Fresh copy each. Sequential.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env/run_mock_suite.sh
```

Run in background. Dirs:

```text
run/mock_h1 .. run/mock_h5   heuristic, port 8765
run/mock_o1 .. run/mock_o5   oracle, port 8766
```

Each log: `run/mock_hN/run.log`. Each exp output inside copy.

## Summarize

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
.venv38/bin/python env/summarize_mock_suite.py
```

Status: suite done. Heuristic mean 0.0687, std 0.1120. Oracle mean 0.1716, std 0.1014. Difference not significant at n=5. See `0013-oracle-baseline.md`.
