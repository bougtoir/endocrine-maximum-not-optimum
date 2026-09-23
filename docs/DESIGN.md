# Design decisions (frozen)

## u convention
u ∈ [0,1]: u=0 unmodified baseline; u=1 defined maximum. Potentiation
f(u)=1+2u (GMAX=3); inhibition f(u)=1−u. Signalling interventions apply
f(u) as efficacy on the deviation from neutral: M_eff = 1 + s·(M−1),
floor 0.05. Secretion interventions scale the secretion rate directly.
u=0 must reproduce baseline exactly (unit-tested).

## Composite loss
Weighted sum of normalised endpoints (src/homeostatic_loss.py):
hypoglycaemia weighted most (0.1 per mg/dL·min), hyperglycaemia 40× lower
per unit, variability and recovery dynamics moderate, endocrine exposure
small. Sensitivity analysis in results/robustness/ shows classification
stability under ±2× per-family perturbation.

## Classification
Type 0 / I / II / II* / III per classify_response; Type IV reserved for
context-dependent optima (assigned across challenges). Type II (strict
interior optimum) is the primary hypothesis endpoint.

## Model provenance
Upstream revised-Sorensen code frozen in models/primary/upstream/
(commit 1ad94954); SHA-256 ledger models/primary/SHA256SUMS.txt.
BioSorSimo-refitted secretion parameters used (validated vs upstream
OGTT data; see results/qc/model_validation_summary.csv).
