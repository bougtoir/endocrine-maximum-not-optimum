# C0 — Established alternative explanations, tested against each case

| alternative | (a) insulin_secretion × OGTT | (b) insulin_secretion_inhibition × CIVII | (c) glucagon_secretion_inhibition × OGTT |
|---|---|---|---|
| ordinary hypo-vs-hyper trade-off | **yes**: peak and nadir are both monotone and move in opposite directions (C2) | **yes**: time below 70 vs peak/area above 140 | no glycaemic gain at all |
| excessive nominal secretion (gain too high) | **yes**: u = 1 means 3× basal secretion, which by itself drives G(0) to 70.5 mg/dL | not applicable | not applicable |
| basal-state miscalibration | **yes**: the case becomes Type I at basal 90 mg/dL (C1, C3) | partly: u* moves from 0.45 to 0.15 at basal 90, and the case is Type I with insulin ×0.7 | **yes**: Type I at basal 90 |
| feedback delay / overshoot | **yes**: u* tracks tauInsu, but only at 100 g with reference basal (C3) | minor: A8 leaves u* at 0.45 | not applicable |
| exogenous insulin replacement / excess | not applicable | **yes**: u* moves with infusion rate (C2 C-series) | not applicable |
| threshold / observation artifact | **yes**: classification depends on the 70 mg/dL crossing (u70 tracks u*) | **yes**: u* moves non-smoothly with infusion rate (threshold crossings) | **yes**: the run-in shifts G(0), which is the reference for the recovery/undershoot endpoints. P1/P3 give Type 0. |
| objective-term redundancy | SD/RMSD/undershoot overlap (Gate B ρ up to 0.93–1.00) | same | the optimum is carried by the recovery/undershoot terms |
