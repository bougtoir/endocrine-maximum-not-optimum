# endocrine-maximum-not-optimum

**Maximum hormonal action is not optimal: interior optima of endocrine
feedback efficacy in a validated glucose–insulin–glucagon model.**

Paper 2 of the series. Companion to a Journal of Endocrinology submission.

## Reproduce everything

```
pip install -r requirements.txt
python scripts/run_all.py
```

This runs the unit tests (16), the full 10-intervention × 5-challenge
u-grid scan with local refinement, synthetic controls, robustness and
Pareto analyses, feedback-mechanism extraction, T2DM/T1DM extensions, the
exploratory HPT-axis scan, and regenerates all figures, tables,
`manuscript_values.csv`, and the manuscript DOCX/MD/cover letter/supplement
in `manuscript/`.

## Layout

- `src/sorensen_model.py` — unified Python port of the revised Sorensen
  model (Sorensen + BioSorSimo variants), frozen upstream in
  `models/primary/upstream/` (commit 1ad94954, SHA-256 ledger in
  `models/primary/SHA256SUMS.txt`).
- `src/interventions.py` — uniform u ∈ [0,1] convention (potentiation
  1+2u, inhibition 1−u, action-efficacy semantics M_eff = 1 + s(M−1)).
- `src/endpoints.py`, `src/homeostatic_loss.py`, `src/scan.py`,
  `src/challenges.py`, `src/hpt_model.py` — endpoints, composite loss,
  grid machinery, challenges, exploratory HPT model.
- `analysis/` — scans, controls, robustness, Pareto, feedback, disease,
  HPT, figures, tables, manuscript generator.
- `results/` — all machine-readable outputs (scans, qc, controls,
  robustness, feedback, disease, hpt, novelty, figures, tables).
- `reports/PHASE_0_REPORT.md` — journal guidelines, model audit, prior-art
  audit, design decisions.
- `manuscript/` — manuscript.md/.docx, cover_letter, supplement.
