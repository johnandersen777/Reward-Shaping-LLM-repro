# 0008 Historical Artifacts

Checked paper repo git history. Findings contradict note 6.

## debug CSV date

`debug_llm_potentials.csv` commits: 2025-07-23.

`llm_shaping.py` default changed to `llama-3` on 2025-08-22, commit `aa387de`.

So 0.2 values in debug CSV came from default `gpt-3.5-turbo`. Not Llama.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/Reward-Shaping-LLM
git log --format='%h %ad %s' --date=short -- debug_llm_potentials.csv
git log -1 --format='%h %ad %s' --date=short aa387de
```

## Llama exp artifacts

Commit `aa387de` has A1 exp output. Phi values continuous, not discrete JSON.

Example: `0.5067615092546955`, `0.4606004583731478`. Matches z-score fallback formula.

Per-episode F1:

```text
0.0 0.01694915254237288 0.0 0.014598540145985403 0.021978021978021976 0.1081081081081081
```

Mean = 0.0269. Paper Llama A1 F1 = 0.7413.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/Reward-Shaping-LLM
git show aa387de:exp/A1_LP200_AL1000_d0.96performance.txt
git show aa387de:exp/A1_LP200_AL1000_d0.96/llm_potentials.csv | head
```

## Phi exp artifacts

Commit `1ce3f40` has discrete phi 0.0-0.9. F1 mean 0.3107. Paper Phi A1 F1 = 0.5555.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/Reward-Shaping-LLM
git show 1ce3f40:exp/A1_LP200_AL1000_d0.96performance.txt
git show 1ce3f40:exp/A1_LP200_AL1000_d0.96/llm_potentials.csv | head
```

## Consequence

Committed artifacts do not match Table II Llama row. Final Llama path unchanged since 2025-08-22.

Real base Llama returns empty text here. Fallback fires. Paper numbers need another model state or environment.

No code edits. Diagnose only.
