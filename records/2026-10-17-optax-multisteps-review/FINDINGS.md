# Mathematical purpose and evidenced failure mechanism

## Intended contract

Let e be the Boolean emission decision and u the candidate optimizer update.
For each update leaf, the output contract is piecewise:

- e = false: return an array of zeros, preserving shape and dtype.
- e = true: return u, including non-finite values when the configured optimizer permits them.

For an accumulator a after the emission decision, retain a when e is false and reset it to zeros when e is true. This is a state-selection contract, not merely an algebraic identity over real numbers.

The wrapper's separate skip predicate and inner optimizer's rejection policy have different roles. Skipping a mini-step must retain the previous partial accumulation and counters. An inner optimizer such as apply_if_finite may reject a completed batch while MultiSteps still completes and resets that accumulation cycle.

## Counterexample and cause

The baseline uses e * u and (1 - e) * a. Under IEEE floating-point semantics, 0 * NaN and 0 * infinity yield NaN. The familiar real-number identity 0x = 0 does not implement the stated contract over the extended floating-point input domain.

This produces two related consequences reproduced by the saved regression family:

1. Before an emission step, non-finite candidate updates can reach parameters even though the wrapper should return exact zeros.
2. When an inner optimizer rejects a non-finite completed batch, arithmetic reset can leave a non-finite accumulator. Later finite batches then fail to recover.

The correction selects between the original leaf and zeros_like(leaf) with jnp.where. The accumulator retains its existing dtype conversion. Existing inner optimizer-state selection, scheduling and counter logic remain intact.

## Why the tests are meaningful

The added family has 34 parameterized cases:

| Family | Cases | What is checked |
| --- | ---: | --- |
| Intermediate update is zero | 12 | NaN/+infinity/-infinity, mean/sum, eager/JIT, nested leaves, unchanged parameters and inner state |
| Recovery after inner rejection | 12 | Rejected completed batch clears; subsequent finite accumulation emits independently calculated mean/sum updates |
| Emitted non-finite update is visible | 6 | k=1 does not silently suppress the optimizer's actual output; accumulator resets |
| Skipped mini-step preserves partial sum | 4 | Mean/sum and eager/JIT retain partial accumulation, skip state and counters |

The first three families fail on the recorded baseline (30 cases); the last four cases already pass. These are cases, not 30 independent defects. The two-file corrected suite also exercises existing accumulation and conditionality behavior. Its terminal report separates 55 tests from 30 subtests.

The recovery oracle uses explicit finite-vector arithmetic, not a second copy of the production masking expression. State and parameter assertions prevent a superficially zero return from hiding poisoned persistent state.

## Broader construct and limits

The demonstrated shared mechanism is a mismatch between arithmetic masking and semantic selection over non-finite values. It supports examining similar boundaries elsewhere; it does not establish an institution-wide design failure or explain the historical intentions of the original authors.

Existing issue 828 and PR840 addressed Boolean optimizer-state handling and are credited as related history. Current baseline code already selects inner state; this study covers the remaining output/reset arithmetic masks. The duplicate loss-JVP candidate associated with PR1762 was excluded.

These finite executed regressions are not a formal proof. CPU eager/JIT coverage does not establish GPU/TPU behavior, performance improvement, all configurations, higher-order differentiation through non-finite branches, or a whole-library repair. Selection here is verified for forward update/state behavior; no general claim about gradients through jnp.where is made.
