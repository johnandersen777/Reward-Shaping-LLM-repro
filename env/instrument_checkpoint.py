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
