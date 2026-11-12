# 0017 Graded vs Binary Phi and F1 Variance

Question: does graded JSON severity vs binary 0/1 explain F1 variance?

Short answer: F1 does not use severity. Gradedness changes training, so it can shift mean and stability. Random run variance has other causes.

## F1 uses hard predictions only

Validation policy:

```text
action = argmax Q(state, 0), Q(state, 1)
```

F1 = harmonic mean of precision and recall from those hard 0/1 actions.

Severity value is never used in F1. Graded vs binary does not enter the metric.

## What binary vs graded changes

Binary oracle phi:

- values 0/1.
- shaping delta `gamma*phi(s') - phi(s)` is 0 on most steps.
- nonzero at anomaly boundaries, ±0.96 jumps.
- Q targets see sparse, large jumps.

Graded phi:

- values in [0,1], continuous.
- shaping delta small and nonzero on most steps.
- Q targets see denser, smoother signal.

Both go through the same PBRS formula:

```text
r' = r + gamma*phi(s') - phi(s)
```

## Can this cause F1 variance?

Yes, in two ways.

1. Systematic mean shift: different reward signal → different learned policy → different mean F1.
2. Stability: sparse large jumps can destabilize Q updates; smooth dense signal can stabilize. This can change run-to-run spread.

But gradedness is a fixed treatment, not random noise. Within one fixed config, it does not create variance. It moves the distribution.

## Main sources of random F1 variance

- No seeds anywhere.
- Initial series index `random.randint`.
- Q-network random init.
- Random replay batches.
- Active-learning selection depends on current Q.
- Label propagation pseudo-labels.
- Epsilon near 1.0: mostly random actions during training.
- VAE weights reinitialized after load, so VAE reward term is random.

These dominate run-to-run spread. Five-run std here ~0.10.

## Observed numbers

```text
heuristic mock   n=5  mean 0.0687  std 0.1120
binary oracle    n=5  mean 0.1716  std 0.1014
```

Differences below ~0.1 are hard to resolve with n=5.

## Experiment that isolates it

Noisy graded oracle curve, `0016-noisy-oracle-curve.md`:

- p=0: graded correct severity. Compare with binary oracle baseline. Isolates shape.
- p>0: wrong severity rate. Tests accuracy sensitivity.
- 5 runs per rate. Same seeds/noise pattern.

Only with matched runs can we say gradedness changed mean or variance.

## One line

F1 scores hard actions. Severity shape changes learning, not the metric. Gradedness can move mean and stability; random seeds drive most run-to-run variance.
