# Gate A — Semantic code audit

| # | Location | Finding | Severity | Action |
|---|---|---|---|---|
| 1 | `src/sorensen_model.py` `BASE_PARAMS` | OGTT-refit insulin-secretion parameters used as the default for every protocol; the IV values are present only as a comment | Major (changes IVGTT reference by an order of magnitude in insulin) | Corrected reference (configs S, C) uses Sorensen IV values for fasting/IVGTT/IVITT/CIVII and the refit for OGTT. `src/` left unchanged so the historical spec stays reproducible |
| 2 | `src/endpoints.py` | Glucose endpoints computed on blood-water glucose (GPV) while thresholds are plasma-glucose criteria (70/140/90 mg/dL); no 0.925 (plasma) or 0.84 (blood) conversion | Major for burden/nadir/time-in-range | Corrected reference (O, C) applies ×0.925; ×0.84 run as exploratory sensitivity (CB) |
| 3 | `src/challenges.py` | `IVITT_RATE` assigned twice; the first expression (`0.04*70*6944/3`) is overwritten by the correct `2800*6.944/3` = 6481 pmol/min | Cosmetic | Documented; effective value correct |
| 4 | `src/challenges.py` | `CIVII_RATE` first assigned with a wrong unit expression, then overwritten with 17.5 mU/min × 6.944 = 121.5 pmol/min (0.25 mU/kg/min × 70 kg; thesis: "0.25 mU/kg/min") | Cosmetic | Documented; effective value correct |
| 5 | `src/challenges.py` | IVGTT infusion 0–3 min vs upstream −3–0 min | None (time shift) | none |
| 6 | `src/challenges.py` | Single basal state for all protocols; Sorensen used protocol-specific basal states for IVITT (GPV 98) and CIVII (GPV 97, insulin 11) | Minor/moderate | Deferred to Gate C starting-state sensitivity |
| 7 | `src/challenges.py` `PRIMARY_CHALLENGES` | CIVII excluded from the primary list used by downstream robustness analyses although it is one of the 5 scanned challenges and held one of the 4 Type II cases | Moderate (selection) | Gate B item |
| 8 | `src/sorensen_model.py` `rhs` | Signalling interventions scale the deviation of a multiplier from 1 (`M_eff = 1 + s(M−1)`); s=0 gives M_eff=1, i.e. loss of hormone *modulation*, not loss of action; secretion interventions scale flux directly | Interpretation | Gate C item (R2 major 4) |
| 9 | `src/sorensen_model.py` | Lower floor `CLIP = 0.05` on multipliers | Interpretation | Gate C (clipping frequency) |
| 10 | units | pM→mU/L ÷6.944; mM→mg/dL ×18.016; IVGTT 64.81 mmol/min × 3 min = 35.0 g | Correct | none |
| 11 | upstream harness | `SorensenForceVars.m` bounds IV infusion variable at 1000 pmol/min (index v+1); affects upstream IVITT test runs only | Upstream artefact | Documented; `nocap` option in Octave driver |
| 12 | reproducibility | Historical config H reproduces the published 50-case classification in 48/50 cases and all 4 Type II cases (class and u*). Differences: glucagon_secretion×IVGTT (published Type I u=0.90 → Type II* u=0.85) and glucagon_signal_hepatic×fasting (Type III u=0.70 → 0.90), both near-flat loss curves; current env numpy 2.2.6 / scipy 1.15.3, `requirements.txt` unpinned | Minor | Pin versions in final reproduction instructions |
