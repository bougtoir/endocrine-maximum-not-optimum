# Gate B — Decision

**Status: FAIL (confirmatory).** The objective function is reconstructed and documented, and the strict Type II classifications are numerically stable. But no strict Type II optimum, whether historical (H) or corrected (C), meets the pre-stated requirement of a meaningful, objective-robust, non-monotonic improvement in whole-body glycaemic performance. Under the user-specified gate rules, confirmatory progression stops here. Gate C was **not** started confirmatorily.

Primary specification: corrected reference C (Gate A). The historical specification H is reported alongside it.

## Criteria and evidence

| Criterion (from rebuild instruction) | Result | Evidence |
|---|---|---|
| Objective reconstructed (endpoints, weights, normalisation, units, windows, recovery, baselines, penalties, quadrature) | Met | `GATE_B_OBJECTIVE_SPECIFICATION.md` |
| Type II / Type II* mathematically defined, not redefined | Met (historical definition retained unchanged) | spec §3 |
| Hormone-exposure penalties vs glycaemic improvement | Exposure terms ≤0.13 loss units (<2%) at every point. **Optima are not driven by exposure penalties.** Removing them adds cases (C: 3→5) | `GATE_B_LOSS_DECOMPOSITION.csv`, `GATE_B_WEIGHT_SENSITIVITY_SUMMARY.csv` |
| Numerical robustness (grid 0.01, rtol 1e-10) | Met. Every class is unchanged; u* shifts ≤0.03 | `GATE_B_STRICT_TYPEII_AUDIT.csv` |
| Robustness to predefined objective-weight sensitivity | **Partial.** The three C cases are Type II in 6/8 sets. With baseline normalisation (W7) none of them is, and the Type II set is replaced by two fasting cases. The count ranges from 2 to 7 across sets. Under H, all 4 original cases survive in only 2/8 sets | `GATE_B_WEIGHT_SENSITIVITY*.csv` |
| Weight-independent (Pareto) support on glycaemic outcomes (hypo, hyper, SD) | **Not met.** No strict Type II case in H or C has an interior u that Pareto-dominates both u=0 and u=1 | `GATE_B_PARETO.csv` |
| Clinically meaningful glycaemic improvement | **Not met as an emergent effect.** See case table | below |
| Double counting | Present. SD vs RMSD ρ=0.93 (1.00 OGTT); hypo burden vs undershoot ρ=0.83; IVGTT RMSD vs recovery ρ=−0.99. Variability and hypoglycaemia are effectively double-weighted | `GATE_B_ENDPOINT_OVERLAP.csv` |
| Prior CIVII exclusion | Confirmed. The historical weight, grid and solver robustness analyses omitted the CIVII Type II case (insulin_secretion × CIVII) without a stated criterion. `PRIMARY_CHALLENGES` excludes CIVII. In the corrected reference this case is Type 0 | spec §5 |

## Strict Type II cases of the corrected reference (C)

| Case | u* (fine grid) | Gain vs better endpoint | Mechanism of the composite gain | Glycaemic Pareto status |
|---|---|---|---|---|
| glucagon_secretion_inhibition × OGTT (only original case retained) | 0.88 | 6.9% | Recovery time and undershoot only. Hypo/hyper burden are unchanged and SD rises | Dominated by u=0 (the frontier is {u=0}) |
| insulin_secretion × OGTT (new) | 0.52 | 34% | Trade-off: u=1 causes hypoglycaemia (hypo contribution 14.2). Low u leaves greater variability | Dominates u=0, not u=1 |
| insulin_secretion_inhibition × CIVII (new) | 0.46 | 43% | Baseline CIVII is hypoglycaemic (131 min <70 mg/dL). Withdrawing endogenous secretion offsets exogenous insulin, and full withdrawal produces hyperglycaemia | Dominates neither end |

The two new cases are interior minima that arise because opposing hypo- and hyper-glycaemic penalty terms are summed, one rising and one falling in u. Under the stated weights their location is determined by the weights. They are neither weight-independent nor evidence of an emergent "maximum ≠ optimum" property of the feedback system. The retained original case is not a glycaemic improvement: on the three glycaemic outcomes it is worse than doing nothing.

## Consequence

- The manuscript's central claim cannot be supported confirmatorily in either form ("strict interior optima of whole-body homeostatic performance", "4/50", or a corrected count).
- Gate C (mechanism, virtual cohort, GSA, generalisation) is not run confirmatorily.
- Exploratory Gate C work, if any, must be labelled as such and cannot rescue the claim.
