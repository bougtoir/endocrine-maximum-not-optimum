# JOE-26-0382 — Reviewer response evidence matrix

Source of comments: `docs/rebuild/JOE-26-0382_decision_letter.txt`. Gate files: `results/rebuild/gate_a/`, `results/rebuild/gate_b/`.

Status vocabulary:
- **Evidence produced**: the analysis requested was performed; the result is stated, whichever way it falls.
- **Reviewer concern confirmed**: the evidence supports the criticism.
- **Not addressed**: no analysis was performed. Gate C was not run because Gate B failed.
- **Human decision**: requires the author.

No comment is marked resolved on the basis of drafted wording. No manuscript text was drafted.

| ID | Comment (abridged) | Analysis / evidence | File(s) | Status | Unresolved limitation |
|---|---|---|---|---|---|
| SE-1 | Reject in current form; a new version may be considered if issues are resolved | Gate A–B rebuild | `JOE_REBUILD_MASTER_REPORT.md` | Evidence produced. The core claim is not supported | Resubmission not recommended |
| ED-1 | Generative-AI disclosure (name, version, model, source) | none | — | Human decision | The statement must disclose AI assistance in analysis and text (Devin, Cognition AI) and any other tools used |
| R2-1a | Precise novelty beyond known glucose-control trade-offs (Wang 2012; Garzilli & Itzkovitz 2018) | Gate B: surviving optima are summed opposing hypo/hyper penalties (C: insulin_secretion×OGTT, insulin_secretion_inhibition×CIVII), i.e. the known trade-off | `GATE_B_DECISION.md` | Reviewer concern confirmed | No novel insight identified |
| R2-1b | Interior minimum may come from competing penalties; test feedback links/delays by targeted perturbation; distinguish the Braess analogy | Decomposition shows a penalty trade-off. Targeted feedback perturbations not run | `GATE_B_LOSS_DECOMPOSITION.csv` | Reviewer concern confirmed (penalty origin); feedback tests not addressed | Braess-like claim unsupported |
| R2-2a | Exact loss formula, endpoints entering, weights, scales, units, windows, recovery, non-recovery penalty, exposure, fixed vs challenge-specific scales | Full specification | `GATE_B_OBJECTIVE_SPECIFICATION.md` §1–3 | Evidence produced | Weights lack clinical calibration; no non-recovery penalty; windows differ by challenge |
| R2-2b | Endpoint contributions at baseline/optimum/maximum for each Type II case; justify exposure penalties; endpoint overlap | Decomposition for the 4 original and 3 corrected cases under H and C. Exposure terms contribute <2%. Overlap ρ: SD–RMSD 0.93, hypo–undershoot 0.83 | `GATE_B_LOSS_DECOMPOSITION.csv`, `GATE_B_ENDPOINT_OVERLAP.csv` | Evidence produced | Double counting of variability and hypoglycaemia |
| R2-3.1 | Model does not reproduce observed OGTT glucose | Offset explained by observation scale: Data.xlsx is blood glucose, the model state is blood water. ×0.84 gives bias −2.2 mg/dL, RMSE 5.9 | `GATE_A_REFERENCE_VALIDATION.md` §3 | Evidence produced | Data.xlsx is the calibration set, so this is not independent validation |
| R2-3.2 | IVGTT 1349 mU/L / 40 mg/dL: robust trade-off or overreactive parameterisation? Compare with upstream and data; document oral vs IV parameters and units | Implementation error: OGTT secretion refit used for IVGTT. Upstream IV values give 101 mU/L and 76 mg/dL, matching the Octave upstream run (99 / 75.8). Units verified | `GATE_A_MODEL_PROVENANCE.md`, `GATE_A_CROSS_IMPLEMENTATION.csv` | Reviewer concern confirmed; the IVGTT Type II cases disappear | No digitised experimental IVGTT data |
| R2-3.3 | Persistence across secretion, action, delay and starting-state parameters; 14 mg/dL offset vs fixed thresholds; grid/solver ≠ physiological robustness; "not model-dependent" claim | Offset/threshold effect quantified (configs O, C, CB change the case sets). Physiological uncertainty analysis not run | `GATE_A_DECISION.md`, `GATE_A_CORRECTED_50_CASES*.csv` | Partly evidence produced; physiological robustness not addressed | The "not model-dependent" statement is unsupported and must be withdrawn |
| R2-4a | Relate u, f(u), s(u); map interventions to equations; s=0 gives multiplier 1, not zero action; "complete insulin resistance" | Semantic audit item #8 confirms M_eff = 1 + s(M−1). Full equation map not produced | `GATE_A_SEMANTIC_CODE_AUDIT.md` | Reviewer concern confirmed; map not addressed | "complete insulin resistance" wording is incorrect |
| R2-4b | Justify 3-fold limit and 0.05 floor; clipping activity; sensitivity; acute vs equilibrated modulation | not run (Gate C) | — | Not addressed | — |
| R2-5a | Experimentally testable implication; persistence in mixed-meal, starting conditions, repeated disturbances | not run (Gate C) | — | Not addressed | Conclusions would at most be challenge-specific |
| R2-5b | Scope of T1DM/T2DM-like configurations; unfitted HPT does not validate generality | Historical disease analysis covers fasting/OGTT only. No new analysis | `GATE_B_OBJECTIVE_SPECIFICATION.md` §5 | Not addressed | Disease and HPT generality claims unsupported |
| R2-6a | Report strict Type II retention separately; define thresholds; include all four cases incl. CIVII; explain selection of six sensitivity cases | Strict Type II defined. Strict retention: 1/4 under corrected C; all 4 in 2/8 weight sets under H. CIVII case was omitted from the historical robustness files without a criterion | `GATE_B_OBJECTIVE_SPECIFICATION.md` §3, §5; `GATE_B_WEIGHT_SENSITIVITY_SUMMARY.csv`; `GATE_B_STRICT_TYPEII_AUDIT.csv` | Evidence produced; reviewer concern confirmed | — |
| R2-6b | Distinguish dominance over max, dominance over baseline and frontier membership; explain loss terms favouring dominated settings | Per-case Pareto status. No strict Type II case has an interior point dominating both ends. The retained OGTT case is dominated by u=0 and gains only via recovery/undershoot | `GATE_B_PARETO.csv`, `GATE_B_DECISION.md` | Evidence produced; reviewer concern confirmed | — |
| R2-m1 | Table 3 layout; define G0/G1; nan notation; magnify shallow curves | none (no manuscript work) | — | Not addressed | — |
| R2-m2 | u* = 0.83 across Figure 6 panels | none | — | Not addressed | IVGTT case no longer exists under C |
| R2-m3 | Define abbreviations | none | — | Not addressed | — |
| R1-1 | Interior optima are artefacts of the weighted loss (incl. 46% retention under pooled perturbations) | Weight dependence confirmed: strict counts range 2–7 across 8 sets and case identity changes. The mechanism differs from the reviewer's account: exposure penalties are negligible, and the optima come from hypo/hyper/variability/recovery terms | `GATE_B_WEIGHT_SENSITIVITY*.csv`, `GATE_B_LOSS_DECOMPOSITION.csv` | Reviewer concern confirmed (with a correction of mechanism) | — |
| R1-2 | Single nominal parameter set; virtual cohort required | not run (Gate C) | — | Not addressed | — |
| R1-3 | One-at-a-time axes ignore compensation | not run | — | Not addressed | — |
| R1-4 | 3-fold bound, linear inhibition to zero, cross-talk; GSA required | not run | — | Not addressed | — |
| R1-m1 | Heterogeneous virtual cohorts | not run | — | Not addressed | — |
| R1-m2 | Moderate/reframe the Braess-like claim | No structural rerouting was demonstrated; the optima are penalty trade-offs | `GATE_B_DECISION.md` | Reviewer concern confirmed | Claim should be removed |
