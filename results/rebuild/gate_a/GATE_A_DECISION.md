# Gate A — Decision

**Status: CONDITIONAL PASS for the corrected reference implementation (config C). The historical implementation (config H) FAILS protocol-specific validation for the intravenous challenges, and the original central result (4/50 strict Type II) is not retained.**

## Criteria

| Criterion | Result | Evidence |
|---|---|---|
| 1. Verified model provenance | Met | `GATE_A_MODEL_PROVENANCE.md`, `GATE_A_PARAMETER_PROVENANCE.csv`, `models/primary/SHA256SUMS.txt`, `data/raw/literature/ACQUISITION_LEDGER.csv` |
| 2. Protocol-specific implementation audit | Met; 2 major discrepancies found | `GATE_A_SEMANTIC_CODE_AUDIT.md` (#1 secretion parameter set, #2 observation transform) |
| 3. Reproducible reference simulations | Met | Python vs upstream Octave agreement (`GATE_A_CROSS_IMPLEMENTATION.csv`); H reproduces 48/50 published classes, 4/4 Type II |
| 4. Extreme IVGTT response explained | Met | Caused by OGTT secretion refit applied to IVGTT: insulin peak 1349 → 101 mU/L, nadir 40 → 76 mg/dL GPV under upstream IV parameters |
| 5. OGTT discrepancy resolved/characterised | Met | ~14 mg/dL offset = blood-glucose data vs blood-water state (×0.84: bias −2.2 mg/dL, RMSE 5.9) |
| 6. No unexplained implementation error compromising the central result | Met for C; **not met for the published result** | The errors are explained and corrected; they change the result (below) |

## Effect on the 50-case scan (pre-specified configurations; `docs/rebuild/GATE_A_CORRECTION_PRESPEC.md`)

Counts from `GATE_A_CORRECTED_50_CASES.csv` / `_CB.csv`:

| Config | Secretion | Glucose scale | Type 0 | Type I | Type II | Type II* | Type III |
|---|---|---|---|---|---|---|---|
| H (historical) | refit, all | blood water | 25 | 12 | 4 | 1 | 8 |
| S | protocol-specific | blood water | 22 | 14 | 5 | 0 | 9 |
| O | refit, all | plasma ×0.925 | 25 | 12 | 4 | 1 | 8 |
| **C (primary corrected)** | protocol-specific | plasma ×0.925 | 24 | 12 | **3** | 2 | 9 |
| CB (exploratory) | protocol-specific | blood ×0.84 | 26 | 14 | 5 | 1 | 4 |

Original strict Type II cases under C:

| Case | H | C |
|---|---|---|
| insulin_signal_global_inhibition × IVGTT | Type II, u*=0.70 | Type 0 (baseline best) |
| insulin_secretion_inhibition × IVGTT (headline example) | Type II, u*=0.85 | Type 0 |
| glucagon_secretion_inhibition × OGTT | Type II, u*=0.85 | **Type II, u*=0.85** (loss 7.02 → 6.15 vs 6.59 at max; 6.8% below best endpoint) |
| insulin_secretion × CIVII | Type II, u*=0.50 | Type 0 |

New strict Type II cases under C: insulin_secretion × OGTT (u*=0.50) and insulin_secretion_inhibition × CIVII (u*=0.45). Neither was pre-specified; both are reported as observed. The CB sensitivity yields a disjoint set of five Type II cases, so case identity depends on the glucose observation scale against fixed thresholds.

**Strict Type II retention of the original four cases under the corrected reference: 1/4.**

## Conditions attached to the pass

1. Gate B uses C as the primary corrected specification, H as the preserved historical specification, CB as a pre-declared observation-scale sensitivity.
2. Protocol-specific basal states (Sorensen IVITT/CIVII) were not imposed; starting-state sensitivity is required in Gate C.
3. No independent experimental validation exists in the repository; IV fidelity is to the upstream/original simulations only; OGTT fit is to calibration data.
4. Python dependency versions must be pinned for reproduction (2/50 near-tie class differences).

## Consequence for the manuscript

The IVGTT example, the four-case headline and the CIVII case cannot be presented as findings of the validated model. Any resubmission would need to be rebuilt on configuration C and Gates B–C.
