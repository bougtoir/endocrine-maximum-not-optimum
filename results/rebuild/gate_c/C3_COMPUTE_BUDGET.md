# C3 — Compute budget and log

Caps were fixed in `GATE_C_PLAN.md` before any run. Actual counts are in `compute_log.csv`; one evaluation is one challenge simulation.

| script | evaluations | cap | wall time (2 cores) |
|---|---|---|---|
| gate_c1_audit | 2,244 | 1,500 | 118 s |
| gate_c2_mechanism | 1,203 | 2,000 | 54 s |
| gate_c3_stage1 | 840 | 6,000 | 32 s |
| first pass, total | 4,287 | 25,000 overall | about 3.5 min |
| rerun after review fixes (all three scripts) | 4,287 | — | about 3.4 min |
| **cumulative total** | **8,574** | 25,000 overall | about 7 min |

**C1 cap overrun.** C1 went over its cap. The pre-run check assumed an 11-point u grid; the historical `U_GRID` has 21 points. The overrun is reported here rather than corrected after the fact. Total use stayed well under the overall cap.

**C3 Stages 2 and 3 not run.** They were not triggered, because no robust model-specific mechanism survived Stage 1.

**Review fixes and rerun.** Two code fixes were found in review, and all three scripts were rerun after them. The rerun is counted in the cumulative total above.
1. Threshold durations (`min_below70`, `min_above140`, ...) now count left-endpoint intervals. Before, they overcounted by 0.5 min.
2. The "basal 90 mg/dL" condition now solves `GlucH0` so that the initial plasma glucose is exactly 90.0 mg/dL. Before, it was 90.198 mg/dL (`glucH0_for_plasma`).

No response class, u*, or u70 changed. Only those duration values and the basal-90 nadir/peak values moved, by ≤ 0.5 min and ≤ 0.2 mg/dL.
