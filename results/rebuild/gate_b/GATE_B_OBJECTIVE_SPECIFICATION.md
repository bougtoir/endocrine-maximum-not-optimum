# Gate B — Objective-function specification (historical, unchanged)

Source: `src/homeostatic_loss.py`, `src/endpoints.py`, `src/challenges.py` at `cfe7a9a`. Gate B does not modify these files. The corrected reference C changes only the inputs (Gate A): protocol-specific secretion parameters and glucose ×0.925 before endpoint computation.

## 1. Endpoints (15) and composite loss

L(u) = Σ_k w_k · E_k(u) / N_k. N_k is fixed across u, interventions and challenges.

| Endpoint E_k | Definition | Unit | w_k | N_k | Enters L |
|---|---|---|---|---|---|
| hypo_burden | ∫ max(0, 70 − G) dt | mg/dL·min | 10 | 100 | yes |
| hyper_burden | ∫ max(0, G − 140) dt | mg/dL·min | 5 | 2000 | yes |
| glucose_sd | SD of G on the window | mg/dL | 5 | 20 | yes |
| glucose_rmsd | RMS of successive 0.5-min differences | mg/dL | 20 | 5 | yes |
| recovery_time | last t with \|G − G(0)\| > 10% of max excursion (0 if excursion ≤0.5 mg/dL) | min | 0.5 | 120 | yes |
| undershoot | max(0, G(0) − nadir) | mg/dL | 2 | 20 | yes |
| insulin_auc | ∫ I dt | mU/L·min | 0.02 | 1e4 | yes |
| glucagon_auc | ∫ Γ dt | pM·min | 0.002 | 3e3 | yes |
| abs_dev_from_target (90), glucose_auc, peak, nadir, mean glucose/insulin/glucagon | — | — | 0 | — | no |

- **Signals:** G = GlucPV × 18.016 (× observation factor in configs O/C/CB); I = InsuPV / 6.944; Γ = Cgon.
- **Window:** t ≥ 0 to the end of the challenge. Fasting 600 min, IVGTT 180, OGTT 300, IVITT 180, CIVII 330. The pre-period is −30 min.
- **Quadrature:** linear interpolation to a 0.5-min uniform grid, then the trapezoid rule.
- **Baseline:** G(0) of the same run, i.e. it already includes the intervention's effect on the basal state.
- **Non-recovery:** there is no explicit penalty. Recovery time is capped at the window length.
- **Fixed scales:** thresholds and scales are the same for every protocol.
- **Weights:** the weights are author-chosen and have no stated clinical calibration.

## 2. Protocol-specific differences

- Window lengths differ, so time-integrated burdens are not comparable across challenges.
- `recovery_time` saturates at the window length (e.g. 300 in OGTT).
- `glucose_rmsd` is dominated by the infusion/bolus slope in IVGTT (contribution ≈29–32 at every u).

## 3. Classification (historical definitions, retained)

Grid U = {0, 0.05, …, 1}. u* = argmin_U L. ε = 0.02 · max(|L(0)|, |L(1)|).

- **Strict Type II:** 0 < u* < 1, L(u*) < L(0) − ε, and L(u*) < L(1) − ε.
- **Type II\*:** 0 < u* < 1 and L(u*) < L(0) − ε, but not L(u*) < L(1) − ε.
- **Type III:** max L − min L ≤ ε and not both of the above.
- **Type 0:** not L(u*) < L(0) − ε.
- **Type I:** otherwise, with u* ≥ 0.9.

ε scales with the *larger* endpoint loss. When the baseline loss is large (e.g. hypoglycaemic C-CIVII baseline 76.9), the threshold for beating u=1 is loosened.

## 4. Endpoint overlap

`GATE_B_ENDPOINT_OVERLAP.csv` holds Spearman ρ over all C points.
- SD vs RMSD: ρ = 0.93 pooled (1.00 OGTT).
- hypo_burden vs undershoot: ρ = 0.83.
- IVGTT RMSD vs recovery: ρ = −0.99.

Variability enters effectively twice, with combined weight 25 on its two terms. Hypoglycaemia also enters twice.

## 5. Prior CIVII exclusion

- `PRIMARY_CHALLENGES = ["fasting","ivgtt","ogtt","ivitt"]` was introduced in commit `8709099`. No analysis script imports it.
- The historical robustness analyses still omit the CIVII Type II case:
  - `results/robustness/weight_sensitivity.csv` has 6 cases and none is CIVII.
  - `grid_density.csv` and `solver_tolerance.csv` have 3 cases and none is CIVII. Only 2 of their cases are among the 4 published Type II cases.
  - `results/disease/disease_classification.csv` covers fasting and OGTT only.
- No exclusion criterion is documented. Gate B therefore audits all four original cases (`GATE_B_STRICT_TYPEII_AUDIT.csv`).

## 6. Predefined sensitivity sets (`analysis/rebuild/gate_b_weight_sensitivity.py`)

| Set | Change |
|---|---|
| W0 | original |
| W1 | exposure weights set to 0 |
| W2 | hypo and hyper weights ×3 |
| W3 | hypo weight ×3 |
| W4 | SD and RMSD set to 0 (burden only) |
| W5 | every non-zero term weighted 1 |
| W6 | SD and RMSD replaced by \|G − 90\| integral (w = 10) |
| W7 | each endpoint normalised by its own u=0 value (floor N_k/100) |

Glycaemic Pareto axes: hypo_burden, hyper_burden, glucose_sd (as in the historical `make_evidence_table.py`).
