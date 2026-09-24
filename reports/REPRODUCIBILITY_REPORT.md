# Reproducibility report

- Single command: `python scripts/run_all.py` (12 steps) regenerates
  every result, table, figure and the manuscript from source.
- Upstream model frozen: iasi-cnr/A-Revised-Sorensen-Model @ 1ad94954;
  integrity ledger `models/primary/SHA256SUMS.txt`.
- Environment: Python 3.10, pinned deps in requirements.txt.
- Determinism: u=0 reproduces the unmodulated baseline exactly
  (unit test); solver output deterministic (unit test); endpoints are
  resampled onto a fixed 0.5-min grid, so results are independent of
  solver step size.
- No hard-coded results: all manuscript numbers are injected from
  `results/` CSVs at generation time (`manuscript_values.csv`,
  `table3_typeII_evidence.csv`).
- Tests: 16/16 pass (`python tests/test_pipeline.py` via unittest).
- Revision-1 status: full pipeline re-run completed on this branch;
  numbers unchanged from the post-review corrected results
  (Type II 4/50; u* = 0.83/0.71/0.88/0.51).
