# 0012 Phi-2 Control

User approved Phi-2 control. Code supports `LLM_CHOICE=phi-2`. Model ID `microsoft/phi-2`.

## Download

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/download_phi2.sh
```

Seen: 11 files, shards 4995584424 and 563832976 bytes. Cache path:

```text
~/.cache/huggingface/hub/models--microsoft--phi-2/snapshots/810d367871c1d460086d9f82db8696f2e0a0fcd0
```

## Canary

```bash
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/check_phi2.sh
```

Seen:

```text
[PHI DEBUG] raw='\n"""\n\nimport numpy as np\nimport pandas as pd\nimport json\n\ndef get_anomaly_severity(sequence):' -> score=0.000
[PHI DEBUG] raw='\nAnswer: {"severity": 0.95}\n"""\n\nimport numpy as np...' -> score=0.950
phi(zeros) = 0.0
phi(spike) = 0.95
```

Phi-2 sometimes emits JSON. Zeros window emits code text, parsed 0.0, no fallback. Same parser behavior as historical Phi exp.

## Full A1 Run

Fresh copy: `run/A1_phi2/repo`. Started after oracle suite. Background. Monitor set.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_phi2/repo
/home/baptist777/.tmp/tmp.VjJfPBPNr4/env/run_real_a1_phi2.sh \
  > /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/A1_phi2/run.log 2>&1
```

Log: `run/A1_phi2/run.log`.

Target paper Phi A1 F1: 0.5555. Historical Phi exp mean: 0.3107.

ETA: 6-16 h. About 4,600 cached generations. 5-15 s per call on 4 GB GPU split. CPU canary stopped, so less contention.

Status: running. Results pending.

## GPU Split

Phi-2 2.7B fp16 ~5.4 GB. GPU 4 GB. `device_map="auto"` splits GPU/CPU. CPU layers dominate latency.
