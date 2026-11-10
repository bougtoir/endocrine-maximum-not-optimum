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
