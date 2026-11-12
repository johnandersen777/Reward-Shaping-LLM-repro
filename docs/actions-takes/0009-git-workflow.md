# 0009 Git Workflow

Branch: `repro-setup`. Remote: `https://github.com/johnandersen777/Reward-Shaping-LLM-repro`.

Paper repo added as submodule. Existing clone reused.

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
git submodule add https://github.com/baharehgl/Reward-Shaping-LLM.git Reward-Shaping-LLM
cat .gitmodules
git submodule status
```

Seen: gitlink `160000` at paper repo HEAD `2e00998`.

## Ignored

`.gitignore` entries:

```text
.venv/
.venv38/
run/
env/fakehome/
env/instructhome/
mock_llm/*.jsonl
mock_llm/oracle_lookup.pkl
*.log
*.swp
__pycache__/
src/
tools/
```

## Commit And Push

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
git add .gitignore .gitmodules Reward-Shaping-LLM notes.md docs env mock_llm
git commit -m "docs: ..."
git push -u origin repro-setup
```

Seen: branch pushed. Tracking set.
