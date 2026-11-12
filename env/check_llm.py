"""Minimal LLM-path check: calls compute_potential on two canary windows."""

from llm_shaping import compute_potential, llm_logs

zeros = compute_potential((0.0,) * 25)
spike = compute_potential(tuple([0.0] * 24 + [10.0]))
print("phi(zeros) =", zeros)
print("phi(spike) =", spike)
print("log entries:", llm_logs)
