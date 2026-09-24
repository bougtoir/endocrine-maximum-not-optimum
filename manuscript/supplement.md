# Supplementary Material

## S1. Full classification table
All 50 intervention–challenge combinations are in
`results/scans/full_classification.csv` (machine-readable) and
Table 2 of the manuscript.

## S2. Sensitivity analyses
`results/robustness/`: weight_sensitivity.csv (each term family ×0.5/×2/0),
grid_density.csv (step 0.10/0.05/0.025), solver_tolerance.csv (rtol 1e-5 vs
1e-7), classification_threshold.csv (rel_thresh 1/2/5 %).

## S3. Synthetic controls
`results/controls/synthetic_controls.csv`: monotonic worsening/improving,
flat, planted U, edge optimum, inverted-U, and noisy-flat responders are
all classified as designed; interpolation consistency confirmed.

## S4. Exploratory HPT-axis model (detail)
Minimal 3-ODE TSH–T4–T3 loop (`src/hpt_model.py`, order-of-magnitude
parameters, NOT fitted to clinical data) challenged with a 60-min T4
infusion. Thyroid-output *inhibition* showed a Type II interior optimum
at u* = 0.45 (L 17.93 →
2.71); feedback potentiation improved monotonically
(Type I); thyroid potentiation gave no benefit (Type 0). Classification:
`results/hpt/hpt_classification.csv`. Status: exploratory,
cross-axis hypothesis-generating corroboration only.

## S5. Disease-state details
`results/disease/disease_classification.csv`: T2DM-like (insulin
signalling × 0.5) and T1DM-like (endogenous insulin secretion abolished) scans for all
interventions × {"fasting", "ogtt"}.

## S6. Numerical integrity
LSODA rtol 1e-7/atol 1e-9; u=0 reproduces baseline exactly (unit test);
solver determinism verified; basal steady-state drift <
0.03 mg/dL/630 min (`results/qc/basal_drift.csv`).

## S7. Provenance
Frozen upstream files: `models/primary/upstream/` (commit 1ad94954,
SHA-256 in `models/primary/SHA256SUMS.txt`). Validation dataset:
upstream `Data.xlsx` (OGTT, ~100 g).
