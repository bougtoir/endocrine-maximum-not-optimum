# C1 — Basal-state and observation audit

## Basal starting state

**Upstream implementation.** It uses one basal state for every protocol: GlucH0 = 5.07333 mM, InsuPV0 = 91 pM, Cgon0 = 11.48 (source: `SorensenInitializeParvals.m`). Python is identical, giving plasma G = 0.925 × 89.08 = 82.4 mg/dL and insulin 13.1 mU/L.

**Panunzi et al. 2020.** The initial conditions are inputs (GPV^B, IPV^B, Γ^B). Their Fig 2 IVGTT used basal values of 89 mg/dL and 12.8 mU/L. They state that Sorensen's exact simulated basal values were "not reported" for some experiments.

**Sorensen 1985 thesis.** It does report protocol-specific basal states (text pp. 276–278, extracted from `models/primary/upstream/Sorensen_phd.pdf`):

| protocol | plasma glucose | GPV | insulin | glucagon | data source |
|---|---|---|---|---|---|
| IVITT 0.04 U/kg | 91 mg/dL | 98 mg/dL | 13 mU/L (assumed) | 120 pg/mL | Gerich et al. 1980, n = 15 |
| CIVII 0.25 mU/kg/min | 90 mg/dL | 97 mg/dL | 11 mU/L | — | Saccà et al. 1979, n = 5 |

The current reference therefore starts IVITT and CIVII about 8 mg/dL (plasma) lower than Sorensen's own protocol simulations.

Sorensen describes the CIVII response as reaching a *hypoglycaemic steady state* set by the balance of insulin action and counterregulation. He reports that the model reproduced the mean data of Saccà et al. 1979 for both the final level and the transition. **A low-glucose plateau at baseline under CIVII is therefore the intended, experimentally observed physiology, not an artifact.** Whether its level is realistic depends on the starting basal state (see C2 P2).

## Sensitivity of classification to the basal state (configuration C, historical objective)

Source: `C1_BASAL_STATE_AND_OBSERVATION_AUDIT` data in `C1_BASAL_STATE_ALTERNATIVES.csv`. Each alternative re-derives the basal steady state; the residual |dy| is reported there.

| basal alternative | (a) insulin_secretion × OGTT | (b) insulin_secretion_inhibition × CIVII | (c) glucagon_secretion_inhibition × OGTT |
|---|---|---|---|
| reference (82.4 mg/dL, 13.1 mU/L) | Type II, u*=0.50 | Type II, u*=0.45 | Type II, u*=0.85 |
| plasma glucose 90 mg/dL | **Type I**, u*=1.00 | Type II, u*=0.15 | **Type I**, u*=0.90 |
| insulin ×0.7 | Type II, 0.50 | **Type I**, 0.90 | Type II, 0.85 |
| insulin ×1.3 | Type II, 0.50 | Type II, 0.20 | Type II, 0.85 |
| glucagon ×0.7 | Type II, 0.50 | Type II, 0.45 | Type II, 0.85 |
| glucagon ×1.3 | Type II, 0.50 | Type II, 0.45 | Type II, 0.85 |

With a basal glucose of 90 mg/dL (Sorensen's CIVII/IVITT value), the composite optimum moves:
- The two OGTT cases become Type I, meaning maximal modulation is composite-optimal.
- CIVII u* moves from 0.45 to 0.15.

Under the historical thresholds (70/140 mg/dL), the composite classification is therefore sensitive to an 8 mg/dL difference in starting glucose. This is a basal-state/threshold-proximity effect and must be separated from any mechanism (C2).

## Observation scale

As fixed in Gate A:
- C applies 0.925 × GlucPV (plasma) for all protocols.
- CB (0.84, blood) is a sensitivity analysis only.
- No mixing of scales was introduced in Gate C. All Gate C direct outcomes are plasma mg/dL.
- Sorensen's GPV-to-plasma correspondences (98 → 91 and 97 → 90 mg/dL) confirm the 0.925 factor (91/98 = 0.929, 90/97 = 0.928).
