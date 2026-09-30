# Phase 0 Report — "Maximum is not optimum" (Journal of Endocrinology)

Date: 2026-09-23 (UTC). Prepared by Devin.

## 0.1 Journal constraints (Journal of Endocrinology, Bioscientifica)

Sourced from the journal's author instructions (checked during this session):

- Full research article: ≤ 5000 words main text.
- Abstract: ≤ 250 words, unstructured.
- References: ≤ 60, Vancouver style, numbered in order of first citation.
- Figures: ≤ 10; separate figure files supplied at submission (not embedded).
- Keywords: ≥ 4.
- Title page carries word count; separate editable Word tables.
- Cover letter required.
- AI-use disclosure statement required (no AI authorship).
- Journal requirements override any conflicting item in the project prompt.

## 0.2 Author prior-work verification (Crossref/OpenAlex)

- Onishi et al., *yoshika: A python package for PK–PD simulation of local
  anesthetics*, Array 2026, DOI 10.1016/j.array.2026.101106 — verified.
- Onishi et al., *When medicine repays physics: A pharmacokinetic toolkit
  for chaotic three-body scattering*, Chaos, Solitons & Fractals 2026,
  DOI 10.1016/j.chaos.2026.119159 — verified.
- "Paper 1" of the current series (reaction capacity → flux redistribution
  → metabolic performance) is treated as companion work; this manuscript
  (Paper 2, network/feedback optimality) is written to stand alone.

## 0.3 Model audit and selection

Candidates evaluated:

1. **Revised Sorensen model (Panunzi et al. 2020, PLoS ONE 15(8):e0237215,
   CC-BY)** — SELECTED.
   - 22 ODEs + 4 GI-tract states, ~146 parameters; coupled glucose–insulin–
     glucagon dynamics with explicit glucagon secretion (GammaPCR =
     GammaBPCR·MGPCR·MIPCR) and glucagon action on hepatic glucose
     production (MCHGP, Fun2 delay τ=65 min).
   - Upstream source frozen locally:
     `models/primary/upstream/` (iasi-cnr/A-Revised-Sorensen-Model,
     commit 1ad94954a708a4ae1f4415c494f94716ef2ff144, 2020-07-31),
     SHA-256 ledger in `models/primary/SHA256SUMS.txt`.
   - Two upstream variants merged into one Python port
     (`src/sorensen_model.py`): Sorensen (IV infusions) + BioSorSimo
     (GI absorption chain; uses BioSorSimo-refitted secretion parameters).
   - Validation: basal steady state drift 0.0016 mmol/L/630 min;
     OGTT overlay vs upstream `Data.xlsx` (insulin RMSE ≈ 10 mU/L;
     glucose excursion reproduced, Δpeak model 42.5 vs data 47 mg/dL;
     documented systematic +14 mg/dL basal offset — dataset subject had
     lower fasting glucose). See `results/qc/model_validation_summary.csv`.

2. **OSP Glucose–Insulin model (MoBi .mbp3)** — REJECTED: requires
   Windows/.NET toolchain; not reproducible on Linux; cannot be frozen
   as executable code.

## 0.4 Prior-art / novelty audit (results/novelty/)

- Braess' paradox formalized for homeostasis: "Biological version of
  Braess' paradox arising from perturbed homeostasis" (Phys Rev E 98,
  062406, 2018) — infinitesimal-homeostasis framework, asthma network
  example. Our contribution differs: validated whole-body glucose–
  insulin–glucagon ODE + systematic dose-response u-sweeps + explicit
  loss-classification; we use "Braess-like" terminology without claiming
  exact equivalence.
- Islet α/β "paradoxical" feedback design (Sci Rep 8, 2018;
  s41598-018-29084-4) — same endocrine circuit, supports the mechanism
  interpretation that antagonistic feedback tunes overshoot; we extend to
  whole-body challenge responses.
- Non-monotonic dose-response/hormesis is widely documented; the specific
  claim here — interior optima of endocrine feedback *efficacy* under a
  justified composite homeostatic loss in a validated human model — is, to
  our audit, not previously demonstrated.

See `results/novelty/prior_art_audit.csv` for the full audit table.

## 0.5 Endpoint & loss design decisions

- Endpoints (15): hypo/hyper burdens, |G−90| deviation, AUCs, SD, RMSD,
  peak, nadir, recovery time, undershoot, insulin & glucagon exposure,
  means. Machine-readable `ENDPOINT_META` in `src/endpoints.py`.
- Composite loss: weighted normalized sum; weights in
  `src/homeostatic_loss.py` with rationale; sensitivity analysis in
  `results/robustness/`.
- Classification: Type 0 (no benefit), I (monotone benefit), II (interior
  optimum beats both ends — primary finding), II* (interior beats baseline
  but not max), III (flat/plateau), IV (context-dependent optimum,
  assigned by caller).

## 0.6 Intervention convention

Uniform u ∈ [0,1]: u=0 baseline, u=1 defined maximum.
Potentiation f(u)=1+u·(GMAX−1), GMAX=3; inhibition f(u)=1−u.
Signalling interventions apply f(u) as an *action-efficacy* factor on the
deviation of each hormone-action multiplier from neutral:
M_eff = 1 + s·(M − 1) (floor 0.05); secretion interventions scale the
secretion rate directly. u=0 reproduces the unmodified model exactly for
all 10 interventions (unit-tested).
