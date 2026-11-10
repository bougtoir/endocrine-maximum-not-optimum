# Gate A correction — pre-specification (written before the corrected scan was run)

Grounds (see GATE_A_PARAMETER_PROVENANCE.csv, GATE_A_PROTOCOL_COMPARISON.csv):
1. The historical implementation uses the BioSorSimo OGTT-refit insulin-secretion parameters (Panunzi et al. 2020,
   Table 3; refit to compensate for the absent incretin effect) for every protocol, including IVGTT/IVITT/CIVII/fasting.
   The upstream IV implementation (Sorensen variant) uses Sorensen's original secretion values for IV protocols.
2. Panunzi et al. 2020 map the state GlucPV (peripheral vascular blood-water glucose) to observations with
   protocol-specific factors: x0.84 = venous whole-blood glucose (IVGTT, Fig 2); x0.925 = venous plasma glucose
   (IVITT/CIVII, Fig 3). The historical endpoints apply fixed clinical plasma-glucose thresholds (70/140 mg/dL,
   target 90) to untransformed GlucPV.

Configurations (all other code, loss, weights, NORM scales, u-grid, classification threshold 2% unchanged):
- H  (historical): BioSorSimo secretion for all challenges; raw GlucPV. Must reproduce 4/50 Type II.
- S  (secretion-corrected): Sorensen IV secretion for fasting/IVGTT/IVITT/CIVII; BioSorSimo for OGTT; raw GlucPV.
- O  (observation-corrected): BioSorSimo secretion for all; glucose endpoints on 0.925 x GlucPV (venous plasma).
- C  (corrected reference, PRIMARY for Gate A): S + O. 0.925 is chosen because the endpoint thresholds are
     plasma-glucose criteria; 0.84 (whole blood) is used only for IVGTT trajectory validation against Sorensen (1985).
Fasting is assigned the original Sorensen secretion parameters because the oral refit has no rationale without
an enteral stimulus. The C configuration was fixed before any corrected result was seen; no configuration is
selected post hoc. All four are reported.
