# Gate C — Execution manifest

- **Branch:** `devin/1794964179-joe-gate-c-exploratory`, created from `a770f49` (PR #7 head; not merged). The final commit is listed in the PR.
- **Input verification:** `JOE_REBUILD_GATE_AB_a770f49.zip` (SHA-256 `25ac854204d56b243eef5d8de9d363ed6fe185d91d52869ac8150b965bf102ce`). All 66 files are byte-identical to `a770f49`.
- **Unchanged:** `src/`, `manuscript/`, `results/rebuild/gate_a/`, `results/rebuild/gate_b/`.
- **Versions:** `requirements_gate_c_pinned.txt`.

## Commands (run from `analysis/rebuild/`)

| command | outputs | evaluations | wall time |
|---|---|---|---|
| `python gate_c1_audit.py` | C1_INTERVENTION_FLUX_AND_REEQUILIBRATION.csv, C1_CLIPPING_AND_INTERVENTION_SENSITIVITY.csv, C1_BASAL_STATE_ALTERNATIVES.csv | 2,244 | 118 s |
| `python gate_c2_mechanism.py` | C2_TARGETED_ABLATIONS.csv, C2_TARGETED_ABLATIONS_SUMMARY.csv, C2_TRAJECTORY_COMPARISONS/*.png/.csv, gate_c2_mechanism.log | 1,203 | 54 s |
| `python gate_c3_stage1.py` | C3_STAGED_ROBUSTNESS.csv, gate_c3_stage1.log | 840 | 32 s |

- **Total:** 4,287 evaluations, about 3.5 min on 2 cores.
- **Compute log:** `compute_log.csv`.
- **Shared helpers:** `gate_c_common.py`.

## Inputs

- Frozen upstream model files: `models/primary/upstream/`, including the Sorensen thesis PDF.
- Panunzi 2020 PDF/XML.
- Crossref snapshots and ledger: `data/raw/literature/crossref_gate_c/`.

## Hand-written documents

The Markdown documents were written by the agent from these outputs. Every number in them can be traced to the CSVs listed above.
