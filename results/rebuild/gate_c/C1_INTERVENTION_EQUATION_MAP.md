# C1 — Intervention-to-equation map (exploratory Gate C)

**Sources.** The code is `src/interventions.py` and `src/sorensen_model.rhs` (unchanged since v3). The numbers come from `analysis/rebuild/gate_c1_audit.py`, which writes `C1_INTERVENTION_FLUX_AND_REEQUILIBRATION.csv` and `C1_CLIPPING_AND_INTERVENTION_SENSITIVITY.csv`. All results use configuration C.

## Dial → factor → equation

| | |
|---|---|
| Dial | u ∈ [0,1] |
| Potentiation factor | f(u) = 1 + 2u, from 1 to 3 (GMAX = 3) |
| Inhibition factor | f(u) = 1 − u, from 1 to 0 (GMIN = 0) |
| Onset and timing | Active over the whole simulation, including the 30-min run-in from t = −30 |
| Initial state | Unperturbed basal state |

| axis | mod key(s) | equation acted on | form |
|---|---|---|---|
| insulin_signal_peripheral | insulin_pgu | M^I_PGU (peripheral uptake) | M_eff = max(0.05, 1 + s(M−1)) |
| insulin_signal_hepatic | insulin_hgp, insulin_hgu | M^I∞_HGP, M^I∞_HGU (targets of first-order lags, τ = 25 min) | same |
| insulin_signal_global (±inhibition) | all three insulin keys | M^I_PGU, M^I∞_HGP, M^I∞_HGU | same |
| glucagon_signal_hepatic (±inhibition) | glucagon_hgp | M^Γ_HGP = M^Γ0 − f2 | same |
| insulin_secretion (±inhibition) | insulin_secretion | S (pancreatic release) multiplied by f(u). Labile-pool depletion dQ/dt uses the scaled S. | S_eff = f(u)·S |
| glucagon_secretion (±inhibition) | glucagon_secretion | r_PΓR (glucagon release) multiplied by f(u) | r_eff = f(u)·r |

## What each dial actually does

### Signalling axes rescale only the deviation from neutral

At the basal state every hepatic multiplier is exactly 1, so these axes leave the basal state almost unchanged:
- At u = 1, basal peripheral uptake changes by at most 1.4%, because M^I_PGU is 0.993 at basal.
- Basal glucose stays within 0.1 mg/dL of 82.4 mg/dL after 5000 min.

**"Complete insulin resistance" is not what inhibition at u = 1 means.** At u = 1 (s = 0), insulin's effect is frozen at the neutral (basal) action. Basal insulin action is retained, and only the dynamic deviation is removed. The v3 code describes this as "u=1 is complete insulin resistance" (`interventions.py`); that label is semantically wrong.

### Secretion axes scale the whole rate, including basal

They are not basal-neutral. Switching on u = 1 at t = −30:
- **insulin_secretion (×3):** pre-challenge drift of −12.6 mg/dL, so G(0) = 69.8 mg/dL with the IV parameter set and 70.5 mg/dL with the oral refit. The re-equilibrated steady state is 67.4 and 74.3 mg/dL respectively.
- **insulin_secretion_inhibition (×0):** G(0) = 97.9 mg/dL and endogenous insulin is about 0. The steady state is 167 mg/dL, a T1DM-like state.
- **glucagon_secretion_inhibition (×0):** G(0) = 69.5–70.0 mg/dL. Glucagon tends to 0, and the steady state is 73.9–78.2 mg/dL.
- **glucagon_secretion (×3):** G(0) = 85.3–89.9 mg/dL.

**Consequence.** For the three corrected strict Type II cases, the challenge starts from a state that the intervention has already shifted during a 30-min run-in:
- The state is not the basal state, and not a re-equilibrated state either.
- The historical recovery and undershoot endpoints measure from G(0), which is this drifted value.

C2 (P1/P3) tests what this does to the results.

### Clipping (floor 0.05)

| axis | where the floor binds | how much |
|---|---|---|
| insulin_signal_global and insulin_signal_hepatic potentiation | M^I∞_HGP at 0.05 from u = 0.05 upward | up to 64–67% of the OGTT window, 34–39% of IVGTT, 10–14% of IVITT/CIVII |
| insulin_secretion_inhibition, u = 1 only | M^I∞_HGU at 0.05 (native model floor, because insulin is near 0) | up to 100% of the window |
| insulin_secretion, glucagon_secretion_inhibition | never | — |
| all other axes | never | — |

For hepatic and global insulin signalling, "3× potentiation" therefore largely means "hepatic glucose production floored at 5% of basal × other multipliers". It is not a graded 3× action.

None of the three corrected strict Type II cases depends on intervention-induced clipping. The 0.05-floor and GMAX = 3 sensitivity is therefore material only for the insulin-signalling axes. Those axes are not Type II under C, so no floor or gain re-tuning was run for them; the binding frequency above is reported instead.

## Remaining contributions at u = 0 and u = 1 (three cases)

- **(a) insulin_secretion × OGTT.** Endogenous secretion is ×1 at u = 0 and ×3 at u = 1. Glucagon secretion and all action multipliers stay native.
- **(b) insulin_secretion_inhibition × CIVII.** At u = 1 endogenous secretion is 0. The only insulin left is the exogenous 121.5 pmol/min for 150 min, plus residual plasma insulin, which decays from basal during the run-in (0.59 mU/L at t = 0).
- **(c) glucagon_secretion_inhibition × OGTT.** At u = 1 glucagon release is 0 from t = −30. Glucagon decays with clearance, to 1.03 pM at t = 0 (basal 11.48 pM). Hepatic glucagon action M^Γ therefore falls below neutral and is floored by the tanh form, not by the 0.05 clip.
