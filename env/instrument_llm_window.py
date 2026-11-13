"""Instrument a run copy: LLM prompt window length from RSL_LLM_WINDOW.

Only edits a copy under run/. Original paper repo untouched.
LSTM state window n_steps stays 25. Only the values sent to the LLM change.
"""

import sys

path = sys.argv[1]
with open(path) as fh:
    text = fh.read()

ns_old = "n_steps = 25  # sliding window length\n"
ns_new = ns_old + (
    'llm_window = int(os.environ.get("RSL_LLM_WINDOW", n_steps))  # instrumentation: LLM prompt window\n'
)
assert text.count(ns_old) == 1, "n_steps line not found"
text = text.replace(ns_old, ns_new, 1)

s_old = "s=ts['value'][tc - n_steps:tc].values,"
s_new = "s=ts['value'][max(0, tc - llm_window):tc].values,"
assert text.count(s_old) == 4, "s slice count %d" % text.count(s_old)
text = text.replace(s_old, s_new)

s2_old = "s2=ts['value'][tc - n_steps + 1:tc + 1].values,"
s2_new = "s2=ts['value'][max(0, tc - llm_window + 1):tc + 1].values,"
assert text.count(s2_old) == 4, "s2 slice count %d" % text.count(s2_old)
text = text.replace(s2_old, s2_new)

with open(path, "w") as fh:
    fh.write(text)
print("llm window instrumented", path)
