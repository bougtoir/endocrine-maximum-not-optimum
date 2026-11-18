# JOE-26-0382 — Gate C exploratory master report

- **Scope.** Exploratory Gate C, run on configuration C, after Gate A (conditional pass) and Gate B (confirmatory FAIL). The Gate B decision stands unchanged.
- **Branch.** `devin/1794964179-joe-gate-c-exploratory`, created from `a770f49`.
- **Reproduction.** Commands, versions and run times are in `EXECUTION_MANIFEST.md`.

## Findings

1. **Direct outcomes are monotone in u.** For all three corrected strict Type II cases, and under every one of the 54 pre-specified perturbations, these are monotone: nadir, peak, minutes and area below 70 mg/dL, and area above 140 mg/dL (C2). Each interior optimum is therefore the weighted crossing of opposing monotone outcomes.
2. **(a) insulin_secretion × OGTT is a gain–delay trade-off.**
   - The optimum survives comparable ablations and both protocol checks.
   - Its location tracks insulin-action delay: τ×2 gives u*=0.30, τ×0.5 gives u*=0.70.
   - This is known delayed-feedback behaviour.
   - The case becomes Type I at Sorensen's basal plasma glucose of 90 mg/dL.
   - The derived prediction (u70 falls with delay) holds only at 100 g with low basal glucose (C3).
3. **(b) insulin_secretion_inhibition × CIVII is a known balance.**
   - Exogenous insulin excess is offset by endogenous withdrawal and read through fixed thresholds.
   - u* moves non-smoothly with infusion rate and basal state.
   - The CIVII hypoglycaemic plateau at baseline is the physiology Sorensen intended (Saccà 1979 data).
4. **(c) glucagon_secretion_inhibition × OGTT is an artifact.**
   - It disappears (Type 0) when the intervention starts at the challenge (P1) or from a re-equilibrated state (P3).
   - It depends on a 30-min pre-challenge run-in plus endpoints referenced to the drifted G(0).
5. **Intervention semantics (C1).**
   - Secretion axes are not basal-neutral: at u=1, G(0) is 70–98 mg/dL.
   - Signalling "inhibition" freezes action at neutral and is not "complete insulin resistance".
   - The 0.05 floor binds only for insulin-signalling potentiation (up to 67% of the OGTT window).
6. **No independent data.** None exists in the archive. No novel testable prediction was found (C4).
7. **Braess.** No structural analogue exists, so the claim should be removed (C5).

## Disconfirming evidence and uncertainty

- The classification depends on basal glucose (82.4 vs 90 mg/dL), dose and the 70/140 mg/dL thresholds.
- Experimental figures were not digitised.
- Two literature matches are unverified.
- This is a self-review only (`GATE_C_ADVERSARIAL_REVIEW.md`).
- The C1 evaluation cap was exceeded and is logged.

## Decisions

- **Scientific decision: C. METHODS/THEORY PIVOT, close to D.**
  - No new endocrine mechanistic prediction survived.
  - What remains of interest is methodological. Composite-loss "optima" in a validated model can be created by basal-state choice, pre-challenge run-in, threshold proximity, and implementation errors (Gate A).
  - That material suits a modelling or methods audience, for example a reproducibility or cautionary note. It does not suit an endocrinology discovery paper.
- **Journal decision: JOE NOT READY.**
  - Neither a direct revision nor a new submission to JOE is defensible on this evidence.
  - Any future submission elsewhere should be a complete new manuscript. It should disclose the corrected model and the invalidation of the original 4/50 headline.

## Next action (human)

1. Accept or reject the pivot.
2. Decide whether to publish the implementation errors and the run-in artifact as a correction or methods note.
3. Choose the AI-disclosure wording.

No submission, editor contact, merge, or financial commitment was made.
