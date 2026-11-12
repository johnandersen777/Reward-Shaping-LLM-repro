"""Instrument a run copy with env-overridable training budget.

Only edits a copy under run/. Original paper repo untouched.
"""

import os
import sys

path = sys.argv[1]
with open(path) as fh:
    text = fh.read()

repls = [
    (
        "                    num_episodes=3,\n",
        '                    num_episodes=int(os.environ.get("RSL_NUM_EPISODES", "3")),\n',
    ),
    (
        "                    num_epoches=10,\n",
        '                    num_epoches=int(os.environ.get("RSL_NUM_EPOCHES", "10")),\n',
    ),
    (
        "                    epsilon_decay_steps=500000,\n",
        '                    epsilon_decay_steps=int(os.environ.get("RSL_EPS_DECAY", "500000")),\n',
    ),
]

for old, new in repls:
    assert text.count(old) >= 1, f"not found: {old!r}"
    text = text.replace(old, new, 1)

with open(path, "w") as fh:
    fh.write(text)
print("budget instrumented", path)
