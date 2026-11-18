# C2 pre-specification (written before any C2 simulation)

Configuration C throughout: protocol-specific secretion parameters and plasma observation 0.925 × GlucPV. The historical composite loss is kept as is and reported next to the direct outcomes. It is not re-weighted.

## Cases (priority order)

- (a) `insulin_secretion` × OGTT
- (b) `insulin_secretion_inhibition` × CIVII
- (c) `glucagon_secretion_inhibition` × OGTT: interpretation / negative case
- Nearby cases, added after C1 only if a mechanism predicts them. Any such selection will be reported.

## Direct outcomes (`gate_c_common.direct_outcomes`, plasma mg/dL, window t ≥ 0)

- Nadir and peak (with times).
- Minutes below 70 and below 54 mg/dL.
- Minutes above 140 and above 180 mg/dL.
- Area below 70 and area above 140 mg/dL.
- Glucose at end of window.
- Pre-challenge drift G(0) − G(−30).
- Last time outside ±10 mg/dL of the pre-intervention basal G(−30).

These are reported separately. They are not combined into a new score.

## Perturbations

Each perturbation is crossed with the full 11-point u grid. A, P, C and N rows are preserved-basal ablations unless stated otherwise.

| id | perturbation | implementation | basal preserved? |
|---|---|---|---|
| A0 | reference C | – | yes |
| A1 | α-cell feedback clamped (glucagon secretion fixed at basal) | beta0PCR=1, beta1PCR=0, beta4PCR=1, beta5PCR=0 | yes (MGPCR0 = MIPCR0 = 1) |
| A2 | hepatic glucagon action clamped | mods glucagon_hgp=0 → MCHGP≡1 | yes |
| A3 | hepatic glucose autoregulation clamped | beta6HGP=1, beta7HGP=0, beta2HGU=1, beta3HGU=0 | yes (MGHGP0 = MGHGU0 = 1) |
| A4 | hepatic insulin action clamped | mods insulin_hgp=0, insulin_hgu=0 | yes |
| A5 | peripheral insulin action clamped | mods insulin_pgu=0 | approximately (MIPGU basal 0.993 → 1) |
| A6 | first-phase (rate-sensitive) insulin secretion removed | EMME2=0 | yes (Pinh0 = Pprp0) |
| A7a/b | potentiator time constant ×0.5 / ×2 | KappaPotnPtgt | yes |
| A8a/b | insulin action delay ×0.5 / ×2 | tauInsu | yes |
| P1 | intervention switched on at t=0 rather than at t=−30 | segmented integration | protocol check |
| P2 | Sorensen protocol-specific basal state (CIVII: plasma 90 mg/dL, 11 mU/L; IVITT: 91 mg/dL, 13 mU/L) | GlucH0, InsuPV0 | alternative basal |
| C1–C4 | case (b) only: CIVII infusion ×0.5, ×0.75, ×1.25, ×1.6 (×1.6 = Sorensen 0.4 mU/kg/min) | GammaIVIin | protocol dose |
| D1–D2 | cases (a, c) only: oral dose 50 g, 75 g | oral_dose_mmol | protocol dose |
| N1 | negative control: renal excretion slope above threshold ×0 | beta5KGE ×0, beta4KGE ×0 | null expected if GlucK stays below threshold (checked) |
| N2 | negative control: brain glucose uptake ×1.02 (matched small flux change on a feedback-free sink) | GammaBGU | basal shifts slightly; reported |

## Hypotheses and how they are decided

**Null for all cases (known control trade-off).** Every direct outcome is monotone in u. The composite interior optimum is then just the crossing of two opposing monotone outcomes under the historical weights.

**Mechanistic claim.** A mechanistic claim needs one of two kinds of evidence:
- (i) A direct outcome that is non-monotone in u, by more than 1 mg/dL or 1 min.
- (ii) A preserved-basal ablation of one named feedback path that removes or relocates the interior optimum, or reverses a direct-outcome trend, while the u=0 trajectory stays comparable.

**Comparability.** An ablation counts as comparable when, against A0 at u=0, |Δnadir| ≤ 2 mg/dL and |Δpeak| ≤ 5 mg/dL. An ablation outside these bounds is labelled "non-comparable". It is reported but not used for causal attribution.

**Case (a), insulin secretion × OGTT.** Expected under the null: peak falls and nadir falls monotonically in u.
- If the late nadir is driven by first-phase secretion plus delayed insulin action, A6 and A8a raise the nadir at high u and move u* upward.
- If α-cell counterregulation shapes it, A1 and A2 lower the nadir and move u* downward.

**Case (b), insulin secretion inhibition × CIVII.** Exogenous-excess explanation: u* moves with infusion rate (C1–C4), and endogenous insulin removed at u* roughly offsets the added exogenous insulin. Under P2 the baseline nadir changes, and the classification may change with it.

**Case (c), glucagon secretion inhibition × OGTT.** Deprioritise unless a direct outcome other than recovery time or undershoot improves at u*.

**Budget.**
- Base grid: 3 cases × 11 u × about 18 perturbations ≈ 600 evaluations.
- Trajectories are cached for u ∈ {0, u*, 1} of A0.
- Cap: 2,000 evaluations.

## Addendum (written after C1 and before any C2 run)

C1 found that the two secretion interventions are not basal-neutral. They act from t=−30, so glucose has already drifted by t=0:

| case | G(0) at u=1 | vs basal 82.4 mg/dL |
|---|---|---|
| (a) `insulin_secretion` × OGTT | 70.5 mg/dL | −11.9 |
| (c) `glucagon_secretion_inhibition` × OGTT | 70.0 mg/dL | −12.4 |
| (b) `insulin_secretion_inhibition` × CIVII | 97.9 mg/dL | +15.5 |

The historical endpoint code measures recovery and undershoot relative to G(0), that is, relative to this drifted value.

One protocol check is therefore added. **P3** starts from the steady state re-equilibrated with the intervention active, using a 3000-min pre-run with protocol parameters and no challenge input. The intervention stays on throughout. P3 separates chronic modulation from the acute run-in.

P1 (onset at t=0) and P3 together bracket the run-in artifact. Neither one replaces the historical protocol. Both are reported as protocol checks.
