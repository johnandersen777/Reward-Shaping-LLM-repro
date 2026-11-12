"""Instrument a run copy: save final RL checkpoint and allow restore-only validation.

Only edits a copy under run/. Original paper repo untouched.
"""

import sys

path = sys.argv[1]
with open(path) as fh:
    text = fh.read()

save_old = "    return episode_rewards, coef_history\n"
save_new = (
    "    saver.save(sess, checkpoint_path)\n"
    "    print(\"Saved final checkpoint:\", checkpoint_path)\n"
    "    return episode_rewards, coef_history\n"
)
assert text.count(save_old) >= 1, "q_learning return not found"
text = text.replace(save_old, save_new, 1)

# Save one checkpoint per episode under checkpoints/epNNNN/.
# write_meta_graph=False: graph is rebuilt by the code on restore;
# only data + index needed, saves 1.4 MB per episode.
ep_old = (
    "        episode_rewards.append(episode_reward)\n"
    "        coef_history.append(dynamic_coef)\n"
)
ep_new = ep_old + (
    "        ep_ckpt_dir = os.path.join(checkpoint_dir, \"ep{:04d}\".format(i_episode + 1))\n"
    "        if not os.path.exists(ep_ckpt_dir):\n"
    "            os.makedirs(ep_ckpt_dir)\n"
    "        saver.save(sess, os.path.join(ep_ckpt_dir, \"model\"), write_meta_graph=False)\n"
    "        print(\"Saved episode checkpoint:\", ep_ckpt_dir)\n"
)
assert text.count(ep_old) == 1, "episode append block not found"
text = text.replace(ep_old, ep_new, 1)

test_old = "    test = 0\n"
test_new = '    test = 1 if os.environ.get("RSL_TEST") == "1" else 0\n'
assert text.count(test_old) >= 1, "test = 0 not found"
text = text.replace(test_old, test_new, 1)

restore_old = "        if test:\n            return\n"
restore_new = "        if test:\n            return [], []\n"
assert text.count(restore_old) == 1, "restore return not found"
text = text.replace(restore_old, restore_new, 1)

with open(path, "w") as fh:
    fh.write(text)
print("instrumented", path)
