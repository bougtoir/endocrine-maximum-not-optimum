# JOE-26-0382 rebuild — Master report

Baseline: `FINAL_JOE_SUBMISSION_REVISED_v3.zip` = `main` @ `cfe7a9a`.
Branch: `devin/1794349380-joe-rebuild-gate-a`.
PR: https://github.com/bougtoir/endocrine-maximum-not-optimum/pull/7 (not merged).
Nothing was submitted, withdrawn, or sent to the journal.

## Final recommendation

**JOE NO-GO — SCIENTIFIC WITHDRAWAL**

The central scientific claim is not supported by the rebuilt evidence. The claim was that maximal endocrine action is not optimal, shown by strict interior optima of whole-body homeostatic performance (4/50) in a validated glucose–insulin–glucagon model.

- Two of the four optima were products of an implementation error.
- The remaining optima are weight-dependent trade-offs between opposing glycaemic penalties.
- No strict optimum has weight-independent glycaemic support.

This failure concerns the claim itself, not a method that a different analysis could repair. A Gate C cohort or GSA could at most find new, exploratory optima. It could not restore the confirmatory claim.

## Gate status

| Gate | Status | Decision file |
|---|---|---|
| A — model/protocol validation | CONDITIONAL PASS for the corrected reference C; FAIL for the historical implementation H (IV protocols) | `results/rebuild/gate_a/GATE_A_DECISION.md` |
| B — objective and optimum validity | **FAIL** (confirmatory) | `results/rebuild/gate_b/GATE_B_DECISION.md` |
| C — mechanism and physiological robustness | Not run (stopped by the gate rule) | — |

## Original vs corrected findings

| Item | Published (H) | Corrected reference (C) |
|---|---|---|
| IVGTT reference | insulin peak 1349 mU/L, nadir 40 mg/dL | 101 mU/L, 76 mg/dL (GPV); upstream Octave: 99 mU/L, 75.8 mg/dL |
| OGTT fit to Data.xlsx | bias +14.1 mg/dL | ×0.84 blood scale: bias −2.2 mg/dL (calibration data) |
| Strict Type II | 4/50 | 3/50 |
| Original 4 retained | — | 1/4 (glucagon_secretion_inhibition × OGTT) |
| New Type II | — | insulin_secretion × OGTT; insulin_secretion_inhibition × CIVII |
| Exploratory 0.84 scale (CB) | — | 5/50, entirely different cases |

## Validation evidence

- The Python port reproduces the frozen upstream MATLAB model run in Octave for IVGTT, IVITT, CIVII and fasting (`GATE_A_CROSS_IMPLEMENTATION.csv`).
- The upstream AutoTester caps the IV insulin infusion at 1000 pmol/min. This was lifted for the IVITT comparison.
- No independent experimental dataset was available. Validation therefore covers implementation fidelity and the calibration-data fit only.

## Objective dependence

- Exposure penalties contribute less than 2% of the loss. The optima are not exposure artefacts.
- The optima arise from summed opposing hypo- and hyper-glycaemic, variability and recovery terms. Variability and hypoglycaemia are double-counted.
- The strict Type II count ranges from 2 to 7 across 8 predefined weight/normalisation sets, and case identity changes between sets.
- The classifications are numerically stable to grid refinement and solver tolerance. Numerical stability is not physiological robustness.
- On the three glycaemic outcomes (hypo, hyper, SD), no strict optimum Pareto-dominates both u=0 and u=1. The one retained original case is dominated by u=0.

## Feedback / mechanism evidence

None generated: targeted feedback perturbations were not run. The decomposition indicates penalty trade-offs rather than a specific feedback-network mechanism.

## Physiological uncertainty

Not assessed. Virtual cohort, GSA, starting states, delays and clipping were not run. Single-parameter-set limits therefore remain.

## Braess assessment

Not supported. No structural rerouting or paradoxical network effect was demonstrated. What remains is ordinary gain tuning against competing penalties, i.e. a standard control trade-off.

## Limitations of this rebuild

- The Gate B pass criteria were taken from the rebuild instruction rather than numerically pre-registered.
- The 8 weight sets were fixed before they were run, but after the Gate B2 decomposition was seen.
- Protocol-specific Sorensen basal states were not imposed.
- The thesis validation figures were not digitised.
- The literature ledger timestamps are file mtimes.

## Human decisions required

1. Accept or reject the recommendation, including whether to withdraw the claim or pursue a different research question outside JOE.
2. Decide whether to report the implementation findings (OGTT secretion refit used for IV protocols; missing blood/plasma conversion) to readers or users of the v3 repository and preprint, if one exists.
3. Write the AI-use disclosure for any future submission.
4. Merging PR #7 into `main` (it changes no historical file).

## Reproduction

Environment: Python 3.10.12, numpy 2.2.6, scipy 1.15.3, pandas 2.3.3, GNU Octave (apt). Solver: `solve_ivp` LSODA, rtol 1e-7, atol 1e-9 (audit: 1e-10 / 1e-12). The analysis is deterministic and uses no random seeds.

```
pip install -r requirements.txt
python analysis/rebuild/gate_a_param_provenance.py
python analysis/rebuild/gate_a_reference_sims.py
python analysis/rebuild/gate_a_cross_implementation.py      # needs upstream_octave/*.csv (octave analysis/rebuild/octave/run_upstream.m <protocol> <out> [nocap])
python analysis/rebuild/gate_a_corrected_scan.py            # H S O C (~4 min, 2 cores)
python analysis/rebuild/gate_a_corrected_scan.py CB
python analysis/rebuild/gate_a_case_comparison.py
python analysis/rebuild/gate_a_endpoint_impact.py
python analysis/rebuild/gate_b_loss_decomposition.py
python analysis/rebuild/gate_b_weight_sensitivity.py
python analysis/rebuild/gate_b_strict_audit.py              # ~1 min
python analysis/rebuild/gate_b_pareto.py
python analysis/rebuild/gate_b_endpoint_overlap.py
```

Reviewer mapping: `JOE_REVIEWER_RESPONSE_EVIDENCE_MATRIX.md`.
