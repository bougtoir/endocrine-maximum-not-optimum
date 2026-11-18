# Gate C (exploratory) — plan and compute budget

Instruction: `docs/rebuild/JOE_GATE_C_EXPLORATORY_DEVIN_PROMPT.txt`.

## Starting state

- Branch `devin/1794964179-joe-gate-c-exploratory` was created from `a770f49`, the head of the PR #7 branch. PR #7 is not merged.
- Archive `JOE_REBUILD_GATE_AB_a770f49.zip` has SHA-256 `25ac8542…102ce`.
- All 66 files in the archive match `a770f49` byte for byte.
- Gate A/B outputs under `results/rebuild/gate_a`, `results/rebuild/gate_b` are kept read-only. Every Gate C output goes to `results/rebuild/gate_c/`.

## Order of work

1. **C1 (prerequisite for C2).**
   - Map every intervention to its equations and to the flux it actually changes at u=0/1.
   - Check basal states: whether secretion scaling shifts basal insulin/glucagon and whether the run starts at a re-equilibrated state.
   - Run Sorensen protocol-specific basal states for IVITT/CIVII.
   - Count how often clipping binds.
2. **C2 (main discovery work).** Corrected config C only. Cases in order:
   - (a) insulin_secretion × OGTT
   - (b) insulin_secretion_inhibition × CIVII
   - (c) glucagon_secretion_inhibition × OGTT, the critical interpretation / negative case.
   For each case:
   - Directly measurable outcomes, predeclared: nadir, peak, minutes <70 and >140, hypo/hyper burden, time to return to basal ±10 mg/dL.
   - Targeted ablations: glucagon counterregulation off; hepatic vs peripheral insulin action fixed at basal; infusion strength; basal state.
   - Negative controls.
3. **C0.** Domain context, competing explanations and the claim–prediction matrix, written alongside C2 and drawing on the primary sources already in the repo plus targeted literature checks.
4. **C3.** Run only if C2 identifies a specific mechanism. Stage 1 is OAT plus 2-factor grids. Stages 2 and 3 run only if Stage 1 shows informative variation.
5. **C4/C5.** Independent evidence audit, falsifiable predictions, Braess boundary, plain-language framing.
6. Master report, adversarial review, updated evidence matrix, execution manifest, PR.

## Compute budget (fixed before running)

- One model evaluation is one challenge simulation, about 0.1 s on 2 cores.
- C1+C2 cap: 6,000 evaluations.
- C3 Stage 1 cap: 6,000 evaluations.
- C3 Stage 2 cap: 200 parameter samples × 3 cases × 11 u = 6,600 evaluations.
- C3 Stage 3: only with a surrogate, at most 5,000 evaluations.
- Total cap: about 25,000 evaluations, roughly 1 h CPU.
- Each script logs its own evaluation count and wall time.
