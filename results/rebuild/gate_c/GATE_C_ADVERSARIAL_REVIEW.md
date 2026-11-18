# Gate C — Adversarial review

This is a self-review by the analysing agent, written from the stance of a sceptical endocrinologist or control theorist. It is not an independent external review. That must be obtained from a human expert.

## Arguments against the Gate C conclusion (and responses)

1. **"Monotone outcomes do not rule out a mechanism; the trade-off itself could be the finding."**
   - Correct. But a trade-off between hyperglycaemia and hypoglycaemia under insulin gain is textbook. Its location depends on basal glucose, dose and thresholds (C1, C3).
   - A paper would need a non-trivial, model-specific quantity that is testable. The only candidate (u70 versus delay) is generic and conditional.

2. **"The 82.4 mg/dL basal state is the upstream default; using 90 mg/dL is cherry-picking."**
   - 90/91 mg/dL is Sorensen's own reported basal state for CIVII/IVITT (thesis pp. 276–278). 82.4 is a default; Panunzi notes that Sorensen's actual basal values were not reported.
   - Both are model-credible starting states. A result that flips between them is not robust.

3. **"P1/P3 change the protocol, so the case (c) result is just a different experiment."**
   - Yes, and that is the point. Case (c) depends entirely on a 30-min pre-challenge run-in that was never stated as a design choice in v3. It also depends on endpoints that are referenced to the drifted G(0).

4. **"Ablations A3–A6 were labelled non-comparable, which hides informative perturbations."**
   - They are reported in full in `C2_TARGETED_ABLATIONS_SUMMARY.csv`. They are only excluded from causal attribution, by a rule pre-specified in `C2_PRESPEC.md`.

5. **"Stage 2/3 were skipped; a virtual cohort might reveal a robust subgroup."**
   - Searching a cohort for a subgroup in which a composite optimum appears would be outcome-chasing. Stage 1 already showed that the direct outcomes are monotone in u.
   - Stage 2 can still be run if a reviewer specifies a mechanism to test.

6. **"The custom integrator could differ from the historical path."**
   - Checked: max |ΔG| = 0.0 mg/dL for all three cases at u = 0.5.

## Weaknesses that remain

- No independent experimental data. Sorensen's figures are not digitised.
- Two literature matches (Saccà 1979, Gerich 1979/1980) are unverified.
- The C1 evaluation cap was exceeded (2,244 against 1,500).
- The comparability bounds (2 and 5 mg/dL) are judgement calls.
- Only three cases were analysed, by design. No nearby non-Type II cases were added, because no mechanism found in C2 predicted any.
