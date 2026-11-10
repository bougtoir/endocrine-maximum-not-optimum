# JOE-26-0382 rebuild — working notes (Gate A in progress)

Baseline: FINAL_JOE_SUBMISSION_REVISED_v3.zip == main cfe7a9a (PR #6). Branch devin/1794349380-joe-rebuild-gate-a.
Decision letter: docs/rebuild/JOE-26-0382_decision_letter.txt (SE + R1 (attached PDF text) + R2 6 major / 3 minor + AI disclosure).
Panunzi 2020 PLoS ONE PDF/XML: data/raw/literature/ (ledger still TODO). Upstream repo iasi-cnr/A-Revised-Sorensen-Model HEAD == 1ad9495 (same as frozen).

## Confirmed findings
- A1: src BASE_PARAMS uses BioSorSimo OGTT-refit insulin-secretion params (beta1-5PIR, KappaRinsu, KappaRinsuPotn,
  KappaPotnPtgt, KappaPinhPrp, EMME1, EMME2) for ALL protocols incl. IVGTT/IVITT/CIVII. Upstream Sorensen IV variant uses
  original values. Panunzi 2020 Discussion: refit compensates absent incretin effect -> OGTT-specific. (GATE_A_PARAMETER_PROVENANCE.csv)
- Upstream IVGTT window TimeIVG=-3..0; manuscript 0..3 (time shift only).
- Panunzi 2020: IVGTT Fig2 "peripheral venous blood glucose = 0.84 x GPV"; IVITT/CIVII Fig3 "venous plasma glucose = 0.925 x GPV".
  Basal 89 mg/dL / 12.8 mU/L for 0.5 g/kg IVGTT. Manuscript applies no transform (endpoints on raw GlucPV).
- A3: IVGTT manuscript params: insulin peak 1349 mU/L, nadir 40.2 mg/dL (reproduces manuscript). Upstream IV params:
  peak 100.9 mU/L, nadir 76.4 mg/dL. Cause = OGTT secretion recalibration transferred to IV protocol. Units OK (pM/6.944).
- A4: Data.xlsx OGTT VARIABLE 1 labelled "Blood Glucose Concentration (GlucPV) [mg/dL]", basal 75.3; model GlucPV basal 89.1;
  0.84*89.1=74.8 -> discrepancy consistent with blood-vs-plasma-water observation transform (to verify vs BioSorSimo fit code).
- IVITT/CIVII nearly unaffected by secretion set (insulin peak 462 both).
- PRIMARY SOURCE for observation factors: Sorensen 1985 thesis (models/primary/upstream/Sorensen_phd.pdf, pdftotext line ~3060-3076):
  vascular glucose states = whole-blood-water concentration; "plasma glucose concentration is 92.5% of whole blood water
  glucose concentration, and blood glucose concentration is 84%". Upstream MATLAB applies no factor (raw state output).
- OGTT vs Data.xlsx (12 glucose points): raw GlucPV RMSE 14.4 / bias +14.1; x0.84 RMSE 5.9 / bias -2.2; x0.925 RMSE 7.7 / bias +6.4
  (BioSorSimo secretion). With Sorensen IV secretion OGTT RMSE 44.5 -> refit genuinely needed for oral.
  Data glucose basal 75.3 = 0.845 x 89.1 -> 14 mg/dL offset = blood-vs-blood-water observation mismatch (basal state fixed by steady state).
- Corrected scan pre-spec: docs/rebuild/GATE_A_CORRECTION_PRESPEC.md (configs H/S/O/C; C primary = protocol secretion + 0.925).
- Octave installed (apt) -> upstream MATLAB AutoTester run directly for cross-implementation check.
- Sorensen thesis protocol basal states (pdftotext /tmp/phdall.txt): default/IVGTT blood 75 mg/dL <-> GPV 89, insulin 13 mU/L (l.18899,19299);
  IVITT (Gerich 1980, n=15) plasma 91 <-> GPV 98 (l.19899); CIVII 0.25 mU/kg/min x150 min (Sacca 1979, n=5) plasma 90 <-> GPV 97, insulin 11 (l.20125).
  Manuscript uses single basal GPV 89.1/13.1 for all protocols. Data.xlsx OGTT basal 75.3 == Sorensen blood 75 -> OGTT data on blood (x0.84) scale.
  Thesis: IV infusions enter heart/lung compartment (python matches).
- Octave cross-impl (GATE_A_CROSS_IMPLEMENTATION.csv): IVGTT python(IV secretion) vs upstream peak ins 100.9/99.0, nadir 76.4/75.8; CIVII max diff 0.23 mg/dL;
  IVITT: upstream AutoTester ForceVars caps GammaIVI at VARMAX=1000 pmol/min (off-by-one v+1 index) -> under-delivers bolus (3100 vs 19443 pmol);
  with cap lifted (nocap) upstream vs python nadir 47.1/47.9, peak ins 477/466, max glucose diff 1.1.
- Corrected scan (GATE_A_CORRECTED_50_CASES.csv): H 4 TypeII (=published 4/4; 48/50 cases identical, 2 near-tie diffs);
  S 5 TypeII; O 4; C 3 TypeII = insulin_secretion@ogtt 0.50 (new), glucagon_secretion_inhibition@ogtt 0.85 (retained), insulin_secretion_inhibition@civii 0.45 (new).
  Original IVGTT x2 and CIVII insulin_secretion lost under S and C. CB (0.84 sens.) 5 TypeII all different (ivgtt/ogtt insulin-axis).
  => only 1/4 original strict Type II retained under pre-specified corrected reference; set of Type II cases unstable to observation scale.

## Gate A done (commit 39539b4, PR #7 https://github.com/bougtoir/endocrine-maximum-not-optimum/pull/7). CONDITIONAL PASS for config C. User informed (Japanese). Blueprint saved (octave, poppler). Memory note written.

## Gate B plan (in progress)
Objective (src/homeostatic_loss.py): L = sum_k w_k * E_k / NORM_k over 15 endpoints; nonzero w: hypo 10/100, hyper 5/2000, SD 5/20,
RMSD(successive diff) 20/5, recovery 0.5/120, undershoot 2/20, insulin AUC 0.02/1e4, glucagon AUC 0.002/3e3. NORM fixed across u and challenges.
Endpoints (src/endpoints.py): window t>=0 to challenge t_end (fasting 600, ivgtt 180, ogtt 300, ivitt 180, civii 330); 0.5-min grid; trapezoid;
thresholds 70/140, target 90 (target unused, w=0); recovery = last time |g-g(0)| > 10% of max excursion (no explicit non-recovery penalty;
capped at window length, e.g. OGTT 300); undershoot = g(0)-nadir. Classification classify_response rel_thresh 0.02.
Steps: B1 spec md; B2 decomposition (H: 4 orig cases; C: 3 C TypeII + 4 orig) at u=0/u*/u=1 -> GATE_B_LOSS_DECOMPOSITION.csv;
B3 predefined weight sets (orig, no-exposure, glycemic-heavy, hypo x3, equal-norm, alt-risk e.g. abs_dev / LBGI-HBGI) -> GATE_B_WEIGHT_SENSITIVITY.csv;
B4 strict audit incl. grid refinement (0.01 local), solver (rtol 1e-9, LSODA), near-optimal width; B5 Pareto (hypo, hyper, SD?) reconcile.
Reuse corrected_scan_endpoints.csv (configs H/S/O/C, 21-pt grid) for recomputing losses under alternative weights without re-simulating.
- B2 done: results/rebuild/gate_b/GATE_B_LOSS_DECOMPOSITION.csv (analysis/rebuild/gate_b_loss_decomposition.py). Exposure terms (insulin+glucagon AUC)
  contribute <=0.13 loss units (<2%) in every case/point -> optima NOT driven by hormone-exposure penalties (contra R1). Loss dominated by hypo burden,
  glucose SD, RMSD (successive-diff; IVGTT ~29-32 constant from bolus spike), undershoot, recovery. C insulin_secretion@ogtt: u=1 loses via hypo (14.2);
  C insulin_secretion_inhibition@civii: baseline hypo 71 -> u*=0.45 0.02 vs u=1 hyper 3.5 + SD. C glucagon_secr_inhib@ogtt: gain from recovery/undershoot only (no hypo/hyper change; SD worsens).
  Next: B3 weight sensitivity (recompute from endpoints CSV), B4 strict audit (grid 0.01 refine, solver), B5 Pareto (analysis/run_pareto.py pareto_front(df,a,b)).
- B3 done: GATE_B_WEIGHT_SENSITIVITY(.csv,_SUMMARY.csv). 8 predefined sets W0..W7. Under C the 3 C-cases survive in W0-W4,W6 (6/8 sets); W5 equal keeps 2, W7 baseline-norm keeps 0
  (gives 2 fasting cases instead). Under H the original 4 all survive only in W0/W1 (W2 3/4, W3 2/4, W4 3/4, W5 2/4, W6 3/4, W7 2/4).
  Strict Type II count ranges 2-7 (C) and 2-7 (H) across sets -> case identity weight-dependent; removing exposure terms ADDS cases (exposure not driving).
- B4 done: GATE_B_STRICT_TYPEII_AUDIT.csv + fine_curves/. All classifications identical across 21-pt grid, 101-pt grid, tight tol (rtol1e-10).
  u* shifts <=0.03 on refinement. C cases rel gain vs better endpoint: glucagon_secr_inhib@ogtt 6.9% (near-opt band 0.54-0.97, wide),
  insulin_secretion@ogtt 34% (0.39-0.58), insulin_secr_inhib@civii 43% (0.43-0.94). Numerical stability != physiological robustness.
- B5 done: GATE_B_PARETO.csv (hypo, hyper, SD). NO strict Type II case (H or C) has an interior u Pareto-dominating both u=0 and u=1.
  C glucagon_secr_inhib@ogtt: frontier = {u=0} only -> composite optimum dominated by baseline on glycaemic axes (gain only via recovery/undershoot/RMSD).
  C insulin_secretion@ogtt dominates u=0 but not u=1; C insulin_secr_inhib@civii dominates neither -> weight-dependent hypo/hyper trade-offs.
  Only weight-independent interior dominance: fasting TypeIII plateaus (negligible magnitude).
- Overlap (GATE_B_ENDPOINT_OVERLAP.csv): SD~RMSD rho .93 pooled (1.00 OGTT), hypo~undershoot .83; IVGTT RMSD~recovery -.99 -> double counting of variability & hypo.
- Gate B verdict planned: FAIL (confirmatory) -> stop; Gate C not started confirmatorily.
