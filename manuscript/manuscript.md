---
title: "Maximum hormonal action is not optimal: interior optima of endocrine feedback efficacy in a previously validated glucose–insulin–glucagon model"
short_title: "Maximum is not optimum"
word_count: 221
---

# Abstract

We tested whether maximal endocrine action equals optimal homeostasis
in a previously validated 26-state glucose–insulin–glucagon model
(revised Sorensen model; the Python port reproduced key upstream
validation outputs). Ten interventions scaling insulin and glucagon
signalling or secretion efficacy via a uniform u in [0,1] convention
were swept across five challenges and scored with a composite
homeostatic loss (hypo-/hyperglycaemic burden, variability, recovery,
endocrine exposure) alongside Pareto analysis of the glycaemic axes.
4 of 50 intervention–challenge combinations showed strict
interior optima (Type II, L(u*) < L(0) and < L(1)). The clearest case is
partial suppression of insulin secretion under IVGTT (u* = 0.83;
loss 234.42 → 55.89 vs 94.84 at u = 1): limiting the
insulin excursion prevents reactive hypoglycaemia while retaining enough
action to clear the load. For all four cases u* strictly improves on u = 1 on the glycaemic axes,
and 2 of 4 lie on the Pareto frontier of glycaemic
burden and variability; the optima
were stable to grid and solver refinement, while classification showed
the expected dependence on loss-function composition (46 % of
weight perturbations preserved Type II/II*). Parallel optima appeared in
insulin-resistant and insulin-deficient states and, exploratorily, in a
minimal HPT-axis model. Maximal endocrine action can therefore be
suboptimal in feedback-controlled systems — a Braess-like regime.

# Keywords

glucose homeostasis; insulin; glucagon; mathematical model; dose-response;
feedback; Braess paradox; homeostatic regulation

# Introduction

Endocrine interventions are commonly described in terms of increased or
decreased hormonal efficacy, whereas the relationship between the
magnitude of a local endocrine action and whole-system homeostatic
performance is less often examined explicitly. Yet the glucose
regulatory system is nonlinear and counter-regulated: insulin suppresses
hepatic output and drives peripheral uptake while glucagon acts
oppositely, and the islet α/β circuit is itself "paradoxical" — insulin
suppresses glucagon secretion while glucagon stimulates insulin
secretion, a design shown to damp glucose overshoot [3]. In such coupled
loops, network theory warns that maximal local capacity need not be
globally optimal — most famously in Braess' paradox, where adding
capacity to a traffic network degrades overall flow [1], and in its
biological analogue where perturbation of a homeostatic network can
produce paradoxical behaviour [2].

Whether maximum endocrine *action* is optimal at the whole-organism level
has not, to our knowledge, been tested in a quantitative model.
Dose-response non-monotonicity is well documented pharmacologically
(hormesis/U-shaped curves) [4], but those observations concern exogenous
agonism of isolated targets, not the efficacy of an intact multi-loop
feedback system under physiological challenge. In a companion study
(Paper 1) we showed that increasing reaction capacity can redistribute
rather than improve metabolic flux; here we test the complementary
hypothesis at the level of endocrine feedback: **there exist interventions
whose effect on whole-body homeostatic performance has an interior
optimum u* in (0,1), i.e. moderate modulation outperforms both the
unperturbed baseline and the maximal modulation.**

We formalise this in the revised Sorensen glucose–insulin–glucagon model
[5] — a 26-state ODE system with explicit insulin and glucagon secretion,
hepatic glucose production/utilisation and peripheral uptake — using a
uniform modulation convention, a justified composite homeostatic loss,
mandatory synthetic negative controls, and sensitivity analysis. We then
ask whether the phenomenon generalises to a second axis, the
hypothalamic–pituitary–thyroid (HPT) loop.

# Materials and Methods

## Model

The primary system is the revised Sorensen model of Panunzi et al. [5]
(CC-BY), a previously validated model ported from the upstream reference
implementation (MATLAB; iasi-cnr/A-Revised-Sorensen-Model, commit
1ad94954) to Python 3. The model
integrates the IV-infusion variant (Sorensen) and the oral-absorption
variant (BioSorSimo) into one 26-state system with a gastrointestinal
transit chain, pancreatic insulin secretion (potentiator/inhibitor/labile
pool), insulin-dependent peripheral glucose uptake (PGU) and hepatic
glucose production/utilisation (HGP/HGU), and glucagon secretion and
action on HGP with a 65-min delay cascade. Integration used LSODA
(rtol = 1e-7, atol = 1e-9). The basal initial condition is the model's
steady state (drift < 0.03 mg/dL over 630 min), and the port reproduced key upstream validation outputs on the OGTT
dataset distributed with the model
(Figure 1): insulin release rate matched the data closely
(RMSE 21.4 mU/min, basal 18.9
vs 18.7), gut absorption reproduced
(peak 824 vs 808 mg/min),
and the glucose excursion shape matched (peak 132
vs 122 mg/dL) with a documented basal offset
of 14 mg/dL reflecting the reference subject's
lower fasting glucose.

## Intervention convention

Every intervention is parameterised by a single modulation fraction
u ∈ [0,1]: u = 0 is baseline (multiplier 1) and u = 1 is the defined
maximum (Figure 2). For signalling interventions the factor s(u) rescales
the deviation of each hormone-action multiplier from neutral,
M_eff = 1 + s(u)·(M − 1) (floor 0.05): s = 1 reproduces baseline exactly,
s → 3 triples action efficacy, s → 0 abolishes it. Secretion
interventions scale the secretion rate directly. Ten interventions were
studied (Table 1): insulin signalling at peripheral, hepatic and global
sites (potentiation and global inhibition), hepatic glucagon signalling
(potentiation and inhibition), insulin secretion (potentiation and
impairment) and glucagon secretion (potentiation and suppression).

## Challenges and endpoints

Five challenge protocols were simulated: prolonged fasting (600-min basal
hold), IVGTT (0.5 g/kg over 3 min), OGTT (100 g oral), IVITT (0.04 U/kg
insulin over 3 min) and continuous IV insulin infusion (CIVII, 0.25 mU/kg/min
for 150 min). Solver outputs were interpolated onto a common 0.5-min grid
before endpoint computation so that sample-based statistics (SD, successive
differences) do not depend on LSODA's internal step sizes. Fifteen endpoints
were computed per run on the post-challenge
window: hypo-/hyperglycaemic burdens (thresholds 70 and 140 mg/dL),
|G − 90| deviation, glucose AUC, SD and successive-difference RMSD, peak,
nadir, recovery time, undershoot, and insulin/glucagon exposure. The
composite loss L(u) — a scalar summary encoding one particular set of
homeostatic priorities — is a weighted sum of normalised endpoints
(weights and normalisation scales documented in the repository),
emphasising hypoglycaemic burden most strongly. It is complemented by a
weight-independent Pareto analysis on the glycaemic axes. Responses were
classified: Type 0 (no
benefit), Type I (monotone benefit, optimum at maximum), Type II (strict
interior optimum beating both ends — the primary hypothesis), Type II*
(interior optimum beating baseline but not the maximum) and Type III
(plateau). u = 0.05 grid spacing was used with local refinement to
0.01 resolution around optima. Local refinement was used only to locate
u*; classifications were always recomputed against the true u = 0 and
u = 1 endpoints.

## Controls and robustness

Mandatory negative controls verified the classifier cannot produce
spurious interior optima: monotone and flat synthetic responders classify
correctly, a planted U-shape is detected, and cubic-spline refinement is
classification-stable (results/controls/). Robustness was assessed by
±2-fold perturbation and zeroing of each loss-term family, grid steps
0.10/0.05/0.025, solver rtol 1e-5/1e-7, and classification thresholds
1/2/5 %. Pareto fronts between hypoglycaemic and hyperglycaemic burden
were extracted per case. Disease extensions rescanned all interventions
under a T2DM-like state (insulin signalling efficacy halved) and a
T1DM-like state (endogenous insulin secretion abolished; glucagon
secretion intact). An exploratory
3-ODE HPT-axis model (TSH secretion with Hill feedback by T3, T4 and T3
pools) tested generality. All analyses regenerate via
`python scripts/run_all.py`; 16 unit tests cover model integrity, the
u = 0 identity, intervention semantics and the classifier.

Disease-state labels: the T2DM-like state halves insulin signalling
efficacy at all sites; the T1DM-like state abolishes endogenous insulin
secretion (glucagon secretion remains simulated and manipulable).

# Results

## Landscape of modulation responses

Figure 3 shows the composite loss L(u) for all 50
intervention–challenge combinations. Three regimes dominate. In the
fasting state every intervention leaves L essentially unchanged until
ablation destabilises homeostasis (Type 0/III). Under IVGTT and IVITT the
insulin axis is strongly non-monotone; under the more physiological OGTT,
suppression of glucagon secretion shows a shallow interior optimum
while most glucagon-axis interventions are near-plateau.

**Strict interior optima (Type II) were found in 4 of 50
combinations** (Table 2).
The strongest result is partial suppression of insulin secretion under
IVGTT: u* = 0.83, with L falling from 234.42 at baseline to
55.89, while full ablation (u = 1) gives 94.84 — worse than
the optimum but still better than baseline, i.e. the dose-response has a
genuine interior minimum (Figure 5A). Global inhibition of insulin
action showed a parallel optimum at u* = 0.71 (L = 60.68).
Under CIVII, modest potentiation of insulin secretion was optimal
(u* = 0.51; L = 4.13 vs 28.06 at maximum),
showing the phenomenon is not restricted to inhibitory interventions.
Interior optima thus occur for insulin secretion, insulin signalling and
glucagon secretion, in both directions of modulation, and across IV and
continuous-infusion challenges (Table 2, Table 3).

## Weight-independent support: Pareto analysis

Because the composite loss is one scalarisation of homeostatic
performance, each Type II case was also assessed on the glycaemic axes
without weights (Figure 4, Table 3). For all four cases u* strictly
improves on maximal modulation u = 1 — equal or lower hypoglycaemic and
hyperglycaemic burden — and 2 of 4 optima lie on the
Pareto frontier (no other u is better on every glycaemic axis). Versus
baseline, the IVGTT optimum is a genuine trade-off rather than universal
dominance: the reactive-hypoglycaemia burden falls from 1760.30
to 0.00 mg/dL·min while hyperglycaemic burden rises
modestly (2155.80 → 2809.70). The shallow OGTT
glucagon-suppression optimum is endpoint-dependent: on the glycaemic
axes it is not Pareto-undominated — its interior minimum reflects a
trade-off between endocrine exposure and glycaemic variability rather
than a glycaemic improvement per se. Individual endpoints for each case
are given in Table 3.

## Mechanism of the IVGTT optimum

The IVGTT interior optimum arises from the trade-off between the insulin
excursion needed to clear the load and the reactive hypoglycaemia it
produces. At baseline the 0.5 g/kg bolus drives a secretion spike (peak
1349 mU/L) followed by a nadir of 40 mg/dL; at
u* the insulin peak is roughly a quarter as high (298 mU/L),
the nadir rises to 77 mg/dL, and peak glucose increases only
modestly (Figure 6). At u = 1,
secretion is abolished, hypoglycaemia disappears but glucose never
returns to target — the optimum interior point balances both failure
modes. Under OGTT, partial glucagon secretion suppression shows a
shallow interior optimum (u* = 0.88; L = 6.57 vs
6.76 at u = 1), driven mainly by reduced glycaemic variability,
consistent with the islet's paradoxical feedback design [3].

## Additional non-IVGTT interior optima

Beyond the insulin IVGTT cases, interior optima appear under
continuous-infusion and disease contexts: CIVII insulin-secretion
potentiation (u* = 0.51; Figure 5D), OGTT glucagon-secretion
suppression (shallow, endpoint-dependent; u* = 0.88), and the
disease-state analogues below — i.e. the phenomenon is not confined to
one hormone, one direction of modulation, or a single challenge, though
its depth and position are context-specific.

## Robustness and endpoint dependence

Optimality is necessarily endpoint-dependent; the relevant question is
whether interior optima remain detectable under multiple reasonable
definitions of homeostatic performance. Grid and solver checks confirmed
classification stability — refined optima differed from coarse-grid
estimates by ≤ 0.05 and tolerances rtol 1e-5/1e-7 did not change labels.
Weight dependence was explicit: the interior-optimum classification of
the headline cases was preserved in 46 % of perturbations,
reverting when the glucose-band terms themselves were removed (removing
the phenotype by construction) or when the optimum is shallow and the
classification threshold is raised to 5 % (Figure 7). Cases whose
optimum is driven by variability revert to Type 0 when variability terms
are removed — these are endpoint-dependent and are labelled as such in
Table 3.

## Disease-state extensions

Under a T2DM-like state (insulin action halved; OGTT baseline loss rose
from 7.49 to 11.98), interior optima persisted
and shifted: potentiating insulin secretion became optimal at
u* = 0.55 rather than at maximum, and glucagon secretion
suppression retained a strong optimum (u* = 0.90).
Under a T1DM-like state (endogenous insulin secretion abolished),
suppressing glucagon secretion showed a Type II
optimum at u* = 0.80 for fasting
(L 56.06 → 6.34), i.e. partial —
not total — glucagon suppression is optimal when insulin is absent
(Figure 8).

## Exploratory HPT extension

An exploratory 3-ODE HPT-axis model (minimal, not fitted to clinical
data) showed a qualitatively similar interior optimum for thyroid-output
inhibition under a T4 infusion challenge (u* = 0.45;
details in Supplementary Information). We regard this as cross-axis,
hypothesis-generating corroboration only — exploratory evidence that the
phenomenon may not be unique to glucose regulation.

# Discussion

What was shown: in a previously validated whole-body
glucose–insulin–glucagon model, a subset (4 of 50) of
intervention–challenge pairs exhibits true interior optima — partial
modulation outperforms both the unperturbed baseline and maximal
modulation — spanning insulin secretion, insulin signalling and glucagon
secretion, both directions of modulation, multiple challenges, and
insulin-resistant/-deficient contexts.

Why it happens: local endocrine action can improve one failure mode
while worsening the countervailing one through feedback. A larger
insulin excursion clears glucose faster but drives deeper reactive
hypoglycaemia; suppressing the loop harder over-commits the system,
so an interior point balances the two — a Braess-like tension between
local action and global performance [1,2]. The interior optimum is the
empirical result; the Braess-like regime is our interpretation.

Why it matters: local efficacy and whole-system homeostatic utility can
be non-monotonically related. This complements earlier optimality
arguments that glucose control must trade rapid clearance against
insulin sparing [10]: rather than optimality forcing a discrete
(bistable) control regime, our results show it can also place the
optimum at an intermediate modulation strength within a continuous
efficacy convention. Maximum hormonal action is not always
equivalent to optimal homeostasis; systems tuned near an interior
optimum will respond to up-modulation with worsening in at least one
direction, a testable prediction for other axes and for patient-level
models.

Several limitations qualify the finding. The model is parameterised on a
single reference subject; the IVGTT reactive hypoglycaemia it produces
(nadir ≈ 40 mg/dL) is more severe than typical clinical FSIGT responses,
so the absolute position of u* for IVGTT is model-dependent even though
the existence of an interior optimum is not. The composite loss encodes
a particular set of homeostatic priorities (hypoglycaemia weighted
heaviest): classification is accordingly weight-dependent (46 %
of perturbations preserved Type II/II*), the OGTT optimum is
endpoint-dependent rather than Pareto-supported, and we report both
honestly via the weight-independent analysis. The HPT extension is
exploratory and unfitted. We claim no clinical dose inference, no
universal Braess behaviour, no general superiority of partial agonists
or partial modulation — the results are mechanistic and
hypothesis-generating.

# Declarations

**Data and code availability.** All code, frozen upstream model files
(SHA-256 ledger), results, figures and this pipeline are public at
github.com/bougtoir/endocrine-maximum-not-optimum; the full analysis
regenerates with `python scripts/run_all.py`.

**AI disclosure.** An AI assistant (Devin, Cognition AI) was used for code
implementation, simulation orchestration and drafting support; the human
author directed the work and takes full responsibility for content.
No AI is an author.

**Author contributions, funding, competing interests.** T.O.: conception,
analysis, writing. Funding: none declared. The author declares no
competing interests.

# References

1. Braess D. Über ein Paradoxon aus der Verkehrsplanung.
   Unternehmensforschung 1968;12:258–268.
2. Donovan GM. Biological version of Braess' paradox arising from
   perturbed homeostasis. Phys Rev E 2018;98:062406.
3. Garzilli I, Itzkovitz S. Design principles of the paradoxical feedback
   between pancreatic alpha and beta cells. Sci Rep 2018;8:11334.
4. Calabrese EJ, Baldwin LA. Hormesis: U-shaped dose responses and their
   centrality in toxicology. Trends Pharmacol Sci 2001;22:285–291.
5. Panunzi S, Pompa M, Borri A, Piemonte V, De Gaetano A. A revised
   Sorensen model: simulating glycemic and insulinemic response to oral
   and intravenous glucose loads. PLoS ONE 2020;15:e0237215.
6. Sorensen JT. A physiologic model of glucose metabolism in man and its
   use to design and assess improved insulin therapies for diabetes.
   PhD thesis, MIT, 1985.
7. Bergman RN, Ider YZ, Bowden CR, Cobelli C. Quantitative estimation of
   insulin sensitivity. Am J Physiol 1979;236:E667–E677.
8. Onishi T. yoshika: a Python package for pharmacokinetic–pharmacodynamic
   simulation of local anesthetics. Array 2026;31:101106.
9. Onishi T. When medicine repays physics: a pharmacokinetic toolkit for
   chaotic three-body scattering. Chaos Solitons Fractals 2026;212:119159.
10. Wang G. Optimal homeostasis necessitates bistable control.
    J R Soc Interface 2012;9:2723–2734.
