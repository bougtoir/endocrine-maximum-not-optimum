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
