# 0037 Per-Episode Checkpoints And F1 While Training

Purpose: save one checkpoint per training episode, validate each one, record F1 as training runs. Reload any episode on any machine.

Paper repo untouched. Run copies only, same rule as 0026.

## Change

`env/instrument_checkpoint.py` now injects two saves into the run copy:

```python
        episode_rewards.append(episode_reward)
        coef_history.append(dynamic_coef)
        ep_ckpt_dir = os.path.join(checkpoint_dir, "ep{:04d}".format(i_episode + 1))
        if not os.path.exists(ep_ckpt_dir):
            os.makedirs(ep_ckpt_dir)
        saver.save(sess, os.path.join(ep_ckpt_dir, "model"), write_meta_graph=False)
        print("Saved episode checkpoint:", ep_ckpt_dir)
```

Final checkpoint still saved at loop end, with graph meta.

`write_meta_graph=False` because restore rebuilds graph from code. Saves 1.4 MB per episode.

## Files

```text
env/instrument_checkpoint.py         per-episode save injection
env/validate_episode_checkpoint.sh   validate one episode checkpoint, append F1 row
env/watch_episode_checkpoints.sh     watch run, copy, validate, commit each episode
env/commit_episode_checkpoint.sh     commit one checkpoint plus F1 row, push
```

`env/run_llama_budget_seed.sh` now starts the watcher itself. Disable with `RSL_WATCH_EPISODES=0`.

Watcher exits when run writes `run/TAG/DONE` and every episode is processed.

## Checkpoint state file

TF writes an absolute path into `checkpoints/checkpoint`. That breaks restore on another machine.

All scripts rewrite it to relative:

```text
model_checkpoint_path: "model"
all_model_checkpoint_paths: "model"
```

Done in watcher copy, both validate scripts, and both artifact commit scripts. Existing `models/*/checkpoints/checkpoint` files rewritten the same way.

## Run

Training run gets per-episode checkpoints automatically:

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env/run_llama_budget_seed.sh TAG SEED EPISODES EPOCHES EPS_DECAY
```

Run script starts watcher in background. PID in `run/TAG/watcher.pid`. Start watcher by hand for an already running run:

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env/watch_episode_checkpoints.sh TAG
```

Stop watcher:

```bash
touch /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/STOP_WATCH_TAG
```

Watcher loop:

1. Waits for `run/TAG/repo/exp/*/checkpoints/epNNNN`.
2. Copies data, index, checkpoint file to `models/TAG/episodes/epNNNN/` atomically.
3. Waits for proxy health on port 8772.
4. Runs `RSL_TEST=1` validation, low priority, 2 threads.
5. Appends row to `models/TAG/episode_f1.csv`.
6. Commits and pushes checkpoint plus CSV row.

## Validate one checkpoint by hand

```bash
cd /home/baptist777/.tmp/tmp.VjJfPBPNr4
env/validate_episode_checkpoint.sh TAG EP
```

Writes `run/validate_TAG_epNNNN/performance.txt`, appends to CSV.

Reload on another machine:

```bash
git clone https://github.com/johnandersen777/Reward-Shaping-LLM-repro
cd Reward-Shaping-LLM-repro
git submodule update --init --recursive
# set up Python 3.8 env per 0002
env/validate_episode_checkpoint.sh TAG EP
```

Data is tracked in the paper submodule. Copied checkpoint holds `model.index`, `model.data-00000-of-00001`, relative `checkpoint`. No absolute paths.

## Result row format

```text
episode,mean_f1,max_f1,mean_precision,mean_recall,timestamp
ep0001,0.485391,0.936200,0.260000,0.620000,2026-11-12T14:00:00-08:00
```

Mean F1 over 6 validation episodes is the metric, same as 0025 and 0036.

## Cost

```text
checkpoint      1.7 MB per episode
full run        200 episodes, about 340 MB committed
validation      1 to 3 minutes per checkpoint, nice 19, 2 threads
```

Training runs on CPU. Validator competes only for CPU, not GPU. GPU idle.

GitHub repo limit: repo holds 114 MB models now. One full run adds about 340 MB. Watch size; more full runs need pruning or LFS.

## Status

Applied to run copies made after 2026-11-12T14:20-08:00.

Running full budget run `paperbudget_e200_u1000_d500000_s200` started before the change. It keeps paper's 50-episode checkpoints only.

Snapshot and validate the first one without stopping training:

```bash
env/validate_intermediate_checkpoint.sh paperbudget_e200_u1000_d500000_s200 paperbudget_e200_u1000_d500000_s200_ep49
```

Run in background. Waits for `checkpoints/model.index`, copies to `models/<snapshot>/`, validates, commits and pushes. Snapshot tag separate so the final artifact commit does not overwrite it.

## Test

Staged copy of B200 final checkpoint as fake `ep0001` and `ep0002` for tag `test_epcheckpoint`.

Watcher copied `ep0001`, validated it:

```text
episode,mean_f1,max_f1,mean_precision,mean_recall,timestamp
ep0001,0.485391,0.936170,0.541711,0.658595,2026-11-12T14:27:17-08:00
```

Matches committed B200 average `0.4853906125529526` exactly.

`ep0002` used the rewritten relative state file. Restore log:

```text
Loading model checkpoint /home/baptist777/.tmp/tmp.VjJfPBPNr4/run/validate_test_epcheckpoint_ep0002/repo/exp/A1_LP200_AL1000_d0.96/checkpoints/model...
Average F1-score over 6 episodes: 0.4853906125529526
```

Path inside the validation copy, not the training run. Copy restores itself. F1 same.

Watcher exit on `DONE` tested with the same tag.

Test dirs removed after check. Nothing committed from test.
