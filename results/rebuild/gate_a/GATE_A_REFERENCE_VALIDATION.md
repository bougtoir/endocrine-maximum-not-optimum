# Gate A — Reference validation

Scripts: `analysis/rebuild/gate_a_reference_sims.py`, `gate_a_cross_implementation.py`, `octave/run_upstream.m`.
Python: numpy 2.2.6, scipy 1.15.3 (`solve_ivp`, rtol 1e-7, atol 1e-9; LSODA piecewise for OGTT). Upstream: GNU Octave, RK4, dt 0.1 min.
Outputs: `GATE_A_PROTOCOL_COMPARISON.csv`, `GATE_A_CROSS_IMPLEMENTATION.csv`, `reference_traces.csv`, `upstream_octave/*.csv`.

## 1. Cross-implementation (Python port vs frozen upstream MATLAB run in Octave)

Same parameters, timing and initial state. GPV in mg/dL; insulin in mU/L.

| Protocol | Python config | Insulin peak (Py / upstream) | GPV nadir (Py / upstream) | Max abs. glucose diff |
|---|---|---|---|---|
| IVGTT | Sorensen IV secretion | 100.9 / 99.0 | 76.4 / 75.8 | 17.3 (bolus phase; RK4 one-step input lag) |
| IVGTT | historical (OGTT refit) | 1349.5 / 99.0 | 40.2 / 75.8 | 94.0 |
| IVITT (upstream bound lifted) | Sorensen IV secretion | 465.9 / 477.1 | 47.9 / 47.1 | 1.1 |
| CIVII | Sorensen IV secretion | 30.5 / 30.6 | 67.8 / 67.7 | 0.23 |
| Fasting | either | 13.1 / 13.1 | 89.1 / 89.1 | ≤0.01 |

Conclusion: the port reproduces the upstream equations. The historical IVGTT reference is not the upstream IVGTT model; it is the upstream model with oral-protocol secretion parameters.

## 2. Extreme IVGTT response (R2 major 3.2)

| Candidate cause | Finding |
|---|---|
| Protocol mismatch | **Confirmed cause.** OGTT secretion refit applied to IVGTT. With upstream IV values: insulin peak 101 mU/L, nadir 76 mg/dL GPV (64 mg/dL venous blood after ×0.84). |
| Parameter mismatch | Same as above (11 secretion parameters). |
| Units | Not a cause (dose 35.0 g; pM/6.944; mM×18.016 verified). |
| Observation compartment | Not a cause of the insulin peak; adds a 7.5–16% glucose-scale offset. |
| Initialisation | Not a cause (identical basal state in both configs). |
| Solver artefact | Not a cause (upstream RK4 reproduces both configurations' behaviour). |
| Genuine model behaviour | Only under the mis-assigned parameter set. |

Qualitative comparison with the original publication: Panunzi et al. report that the upstream IVGTT reproduces Sorensen's Fig 71 within 0.20 mg/dL and 10 mU/L at the maxima; the upstream IV run here has a 99 mU/L insulin peak. No digitised experimental IVGTT data were available in the repository; the thesis figures (Fig 71–75, including Gerich 1980 IVITT n=15 and Saccà 1979 CIVII n=5) are scanned images and were not digitised in Gate A.

## 3. OGTT discrepancy (R2 major 3.1, 3.2)

Data.xlsx glucose (12 points) vs model GPV under the BioSorSimo refit:

| Observation mapping | RMSE (mg/dL) | Mean bias (mg/dL) |
|---|---|---|
| raw GPV (historical) | 14.4 | +14.1 |
| × 0.84 (venous blood) | 5.9 | −2.2 |
| × 0.925 (venous plasma) | 7.7 | +6.4 |

Data.xlsx labels this series "Blood Glucose Concentration"; its basal value (75.3 mg/dL) equals Sorensen's default basal venous blood glucose (75 mg/dL ↔ GPV 89). The ~14 mg/dL offset is therefore explained by comparing blood glucose with blood-water glucose (missing ×0.84), not by a structural model failure. With the Sorensen IV secretion values the OGTT RMSE is 44.5 mg/dL (raw) — the oral refit is genuinely needed for OGTT. Caveat: Data.xlsx is the calibration dataset, so this is goodness of fit, not independent validation.

## 4. Defensible validation criteria and their limits

- IV protocols: comparison is possible only against the upstream implementation and the original Sorensen simulations (via Panunzi's reported agreement). This establishes implementation fidelity, not independent physiological validity.
- OGTT: comparison to measured data (Data.xlsx), but those data were used for calibration.
- No independent measured dataset was used in Gate A. Model output is not treated as experimental validation.
