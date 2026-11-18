# C3 — Compute budget and log

Caps were fixed in `GATE_C_PLAN.md` before any run. Actual counts are in `compute_log.csv`; one evaluation is one challenge simulation.

| script | evaluations | cap | wall time (2 cores) |
|---|---|---|---|
| gate_c1_audit | 2,244 | 1,500 | 118 s |
| gate_c2_mechanism | 1,203 | 2,000 | 54 s |
| gate_c3_stage1 | 840 | 6,000 | 32 s |
| **total** | **4,287** | 25,000 overall | about 3.5 min |

**C1 cap overrun.** C1 went over its cap. The pre-run check assumed an 11-point u grid; the historical `U_GRID` has 21 points. The overrun is reported here rather than corrected after the fact. Total use stayed well under the overall cap.

**C3 Stages 2 and 3 not run.** They were not triggered, because no robust model-specific mechanism survived Stage 1.
