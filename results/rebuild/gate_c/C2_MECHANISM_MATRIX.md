# C2 — Mechanism matrix (exploratory; configuration C)

**Sources.**
- Data: `C2_TARGETED_ABLATIONS.csv` (21-point u grid for every perturbation) and `C2_TARGETED_ABLATIONS_SUMMARY.csv`.
- Figures and trajectories: `C2_TRAJECTORY_COMPARISONS/`.
- Design: pre-specified in `C2_PRESPEC.md`, including the P3 addendum written before the run.
- Integrator check: the custom integrator reproduces `run_challenge` exactly (max |ΔG| = 0.0 mg/dL).

## Common result

In all three cases and under every perturbation, these direct glycaemic outcomes are **monotone in u**:
- nadir
- peak
- minutes below 70 mg/dL
- area below 70 mg/dL
- area above 140 mg/dL

No direct outcome shows an interior extremum; the largest "non-monotonicity" was ≤ 0 mg/dL.

The only non-monotone quantities are threshold-crossing *times*:
- the historical `recovery_time` endpoint;
- the last time outside ±10 mg/dL of pre-intervention glucose.

Both are discontinuous functions of the trajectory. Each composite interior optimum is therefore the weighted crossing of opposing monotone outcomes. That crossing is the pre-specified null.

## Case (a) — insulin_secretion × OGTT (Type II, u* = 0.50)

**Observation.** Raising u from 0 to 1 changes the response as follows:

| outcome | u = 0 | u = 1 |
|---|---|---|
| peak | 122.3 mg/dL | 94.9 mg/dL |
| nadir | 74.3 mg/dL | 67.7 mg/dL |
| minutes < 70 mg/dL | 0 | 106.5 |

At u = 1, G(0) has already fallen to 70.5 mg/dL during the run-in.

**Ablations that preserve comparability.** The interior optimum survives every perturbation that stays comparable at u = 0:
- α-cell feedback clamp (A1): u* 0.45
- hepatic glucagon action clamp (A2): u* 0.45
- potentiator speed (A7): u* 0.50–0.70
- insulin-action delay (A8): u* 0.30–0.70
- onset at t = 0 (P1): u* 0.50
- re-equilibrated start (P3): u* 0.50
- negative controls N1/N2: u* 0.50

**Ablations that are not comparable.** Hepatic glucose autoregulation, hepatic or peripheral insulin action, and first-phase secretion (A3–A6) change the u = 0 trajectory beyond the comparability bounds. They are reported but not used for attribution.

**Interpretation.** The optimum is a gain–delay trade-off:
- More endogenous secretory gain cuts the hyperglycaemic peak.
- Delayed insulin action then carries glucose past basal, so the trough falls below 70 mg/dL.
- The optimum moves the way a delayed negative-feedback loop predicts: longer insulin-action delay gives a lower optimal gain (τ × 2 → u* 0.30; τ × 0.5 → u* 0.70).
- Counterregulation (glucagon) barely matters here (u* changes by 0.05).

This is textbook control behaviour (a loop gain limited by delay-induced undershoot). It is not a new endocrine mechanism.

**Conditionality.** The classification depends on the starting state and the challenge size:
- With a basal plasma glucose of 90 mg/dL (C1), the case becomes Type I.
- C3 Stage 1 shows that the delay → u* ordering holds only at the reference basal state and 100 g dose.

## Case (b) — insulin_secretion_inhibition × CIVII (Type II, u* = 0.45)

**Observation.** At u = 0, exogenous insulin (0.25 mU/kg/min) drives a hypoglycaemic plateau with a nadir of 62.8 mg/dL. Sorensen describes this plateau as the intended physiology, after Saccà et al. 1979. Removing endogenous secretion moves the response the other way:
- At u = 1, glucose rises to a 162 mg/dL peak because there is no endogenous insulin.
- The composite optimum sits where removing endogenous insulin offsets the exogenous excess.

**Location of the optimum.**
- **Infusion rate:** u* moves with the infusion rate, but not smoothly:

  | infusion | ×0.5 | ×0.75 | ×1 | ×1.25 | ×1.6 |
  |---|---|---|---|---|---|
  | u* | 0.70 | 0.85 | 0.45 | 0.75 | Type I |

  This reflects crossings of the 70/140 mg/dL thresholds, not a smooth physiological set-point.
- **Counterregulation:** clamping glucagon counterregulation (A1/A2) turns the case into Type I. These ablations are non-comparable (Δnadir −3.2 mg/dL).
- **Basal state:** with Sorensen's own CIVII basal state (P2; 90 mg/dL, 11 mU/L), the case stays Type II with u* = 0.40. With basal glucose 90 alone (C1), u* = 0.15. With basal insulin ×0.7, the case becomes Type I.

**Interpretation.** Exogenous insulin excess balanced by endogenous insulin withdrawal, read through fixed thresholds. Physiologically this is the known principle that endogenous insulin secretion falls during exogenous insulin infusion, and that this fall limits hypoglycaemia. Making the dial "inhibit secretion" adds nothing beyond that.

## Case (c) — glucagon_secretion_inhibition × OGTT (Type II, u* = 0.85)

**Observation.** Starting the intervention at the challenge (P1) or from the re-equilibrated state (P3) gives **Type 0**: the baseline is optimal.

The historical optimum exists only because the intervention runs during the 30-min run-in:
- G(0) falls to 70 mg/dL at u = 1.
- That lowers the reference for the recovery and undershoot endpoints.

The direct outcomes give no support either:
- Clamping hepatic glucagon action (A2) gives Type III.
- Nadir, peak and the hypo/hyper burdens never improve on u = 0. They are monotone, or flat when ≈ 0.

**Interpretation.** This is a protocol/endpoint artifact. Deprioritised; no further work.

## Matrix

| case | observed composite optimum | direct outcomes | survives protocol checks P1/P3 | named path that moves u* | best explanation | new mechanism? |
|---|---|---|---|---|---|---|
| (a) | yes | all monotone (peak ↓, nadir ↓) | yes | insulin-action delay, potentiator speed | gain–delay trade-off between peak and undershoot | no (known control result); conditional on basal state and dose |
| (b) | yes | all monotone | yes | infusion rate, basal state, counterregulation | exogenous excess vs endogenous withdrawal at fixed thresholds | no |
| (c) | yes | no improvement over u = 0 | **no** (Type 0) | — | run-in artifact in reference-dependent endpoints | no |
