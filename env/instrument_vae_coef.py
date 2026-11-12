"""Instrument a run copy with env-overridable VAE reward coefficient."""

import sys

path = sys.argv[1]
with open(path) as fh:
    text = fh.read()

old = "dynamic_coef=10.0"
new = 'dynamic_coef=float(os.environ.get("RSL_VAE_COEF", "10.0"))'
assert text.count(old) >= 1, "dynamic_coef=10.0 not found"
text = text.replace(old, new)

with open(path, "w") as fh:
    fh.write(text)
print("vae coef instrumented", path)
