# QC Report — numerical, reference and integrity checks

Date: 2026-09-23 (UTC).

## Numerical integrity
- LSODA rtol=1e-7, atol=1e-9 (production). Tolerance check
  `results/robustness/solver_tolerance.csv`: loss values differ ~4 % at
  rtol=1e-5; all classifications unchanged.
- Basal steady state: |dG/dt| drift 0.02 mg/dL over 630 min
  (`results/qc/basal_drift.csv`).
- u = 0 reproduces the unmodified model exactly for all 10 interventions
  (unit test, max |Δstate| = 0).
- Determinism: repeated simulations identical to < 1e-10.
- Grid checks: optimum u* stable within ±0.05 across steps 0.10/0.05/0.025.
- Classifier controls (`results/controls/`): monotone/flat/planted-U/
  edge/noisy cases all classified correctly; cubic-spline refinement
  keeps the label.
- Note: LSODA `max_step` had to be bounded in the HPT model (pulsed input
  could be stepped over by the solver) — fixed in `src/hpt_model.py`.

## Model validation (`results/qc/model_validation_summary.csv`)
| variable | RMSE | bias | peak model | peak data |
|---|---|---|---|---|
| glucose (mg/dL) | 14.4 | +14.1 | 132.2 | 122.3 |
| insulin (mU/L) | 10.1 | +1.2 | 92.6 | 96.6 |
| insulin release (mU/min) | 21.4 | +5.1 | 159.6 | 140.7 |
| gut absorption Roga (mg/min) | 43.1 | −10.4 | 823.6 | 807.6 |

Interpretation: insulin secretion and glucose excursion shape reproduce
the reference OGTT dataset; the systematic +14 mg/dL glucose offset
reflects the reference subject's lower fasting level (documented, not
corrected — parameters were not refit).

## Known limitations flagged for reviewers
- The model produces a deeper IVGTT reactive hypoglycaemia (nadir ≈
  40 mg/dL) than typical clinical FSIGT responses; u* positions for IVGTT
  are therefore model-dependent even though the existence of an interior
  optimum is robust.
- HPT model is exploratory (order-of-magnitude parameters, not fitted).
- Disease states are stylised (insulin signalling ×0.5; secretion ×0).

## Reference verification (`results/qc/reference_verification.csv`)
All cited references were verified against Crossref metadata during this
session (authors, journal, year, volume, DOI).

## Provenance
- Upstream model: iasi-cnr/A-Revised-Sorensen-Model @ 1ad94954 (frozen in
  `models/primary/upstream/`, SHA-256 ledger `models/primary/SHA256SUMS.txt`).
- Validation data: upstream `Data.xlsx` (OGTT, ~100 g dose).
- Python 3.10, numpy/scipy/pandas/matplotlib/openpyxl/python-docx
  (see requirements.txt).
- Reproduce: `python scripts/run_all.py`.
