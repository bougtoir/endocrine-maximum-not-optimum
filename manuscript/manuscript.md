---
title: "Maximum hormonal action is not optimal: interior optima of endocrine feedback efficacy in a validated glucose–insulin–glucagon model"
short_title: "Maximum is not optimum"
word_count: 214
---

# Abstract

Endocrine feedback loops are usually interpreted as needing maximal
responsiveness to defend homeostasis. We tested whether maximum hormonal
action is in fact optimal, using a validated 22-compartment
glucose–insulin–glucagon model (revised Sorensen model) and a uniform
intervention convention u in [0,1] scaling hormone action efficacy or
secretion in either direction. Ten interventions (insulin and glucagon
signalling and secretion, potentiation and inhibition) were swept across
five challenges (fasting, intravenous and oral glucose tolerance tests,
insulin tolerance test, continuous insulin infusion) and scored with a
composite homeostatic loss combining hypo-/hyperglycaemic burden,
variability, recovery dynamics and endocrine exposure. 7 of 50
intervention–challenge combinations showed strict interior optima
(Type II, L(u*) < L(0) and < L(1)), most prominently partial suppression
of insulin secretion under IVGTT (u* = 0.74, loss 221.07 →
44.37 vs 82.44 at u = 1), arising because limiting the insulin
excursion prevents reactive hypoglycaemia while retaining enough action
to clear the load. Findings were robust to ±2-fold loss-weight
perturbations and grid refinement, persisted in insulin-resistant and
insulin-deficient states, and a qualitatively similar interior optimum
appeared in a minimal HPT-axis model (thyroid suppression u* =
0.45). These results show that endocrine feedback systems can
occupy Braess-like regimes in which maximal action is suboptimal.

# Keywords

glucose homeostasis; insulin; glucagon; mathematical model; dose-response;
feedback; Braess paradox; homeostatic regulation

# Introduction

A foundational principle of endocrinology is that homeostatic systems are
defended by maximally effective feedback: pancreatic β-cells release
insulin to suppress post-prandial hyperglycaemia, α-cells release
glucagon to avert hypoglycaemia, and each limb of the loop is assumed to
perform best when operating at full strength. Yet network theory has long
recognised that maximal local capacity can be globally counterproductive —
most famously in Braess' paradox, where adding capacity to a traffic
network degrades overall flow [1], and in its biological analogue where
perturbation of a homeostatic network can produce paradoxical behaviour
[2]. Within glucose regulation specifically, the islet α/β circuit is
itself "paradoxical": insulin suppresses glucagon secretion while
glucagon stimulates insulin secretion, a design shown to damp glucose
overshoot [3].

Whether maximum endocrine *action* is optimal at the whole-organism level
has not, to our knowledge, been tested in a validated quantitative model.
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
(CC-BY), ported from the upstream reference implementation (MATLAB;
iasi-cnr/A-Revised-Sorensen-Model, commit 1ad94954) to Python 3. The model
integrates the IV-infusion variant (Sorensen) and the oral-absorption
variant (BioSorSimo) into one 26-state system with a gastrointestinal
transit chain, pancreatic insulin secretion (potentiator/inhibitor/labile
pool), insulin-dependent peripheral glucose uptake (PGU) and hepatic
glucose production/utilisation (HGP/HGU), and glucagon secretion and
action on HGP with a 65-min delay cascade. Integration used LSODA
(rtol = 1e-7, atol = 1e-9). The basal initial condition is the model's
steady state (drift < 0.03 mg/dL over 630 min), and the port was validated
against the upstream OGTT dataset distributed with the model
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
for 150 min). Fifteen endpoints were computed per run on the post-challenge
window: hypo-/hyperglycaemic burdens (thresholds 70 and 140 mg/dL),
|G − 90| deviation, glucose AUC, SD and successive-difference RMSD, peak,
nadir, recovery time, undershoot, and insulin/glucagon exposure. The
composite loss L(u) is a weighted sum of normalised endpoints (weights and
normalisation scales documented in the repository), emphasising
hypoglycaemic burden most strongly. Responses were classified: Type 0 (no
benefit), Type I (monotone benefit, optimum at maximum), Type II (strict
interior optimum beating both ends — the primary hypothesis), Type II*
(interior optimum beating baseline but not the maximum) and Type III
(plateau). u = 0.05 grid spacing was used with local refinement to
0.01 resolution around optima.

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
T1DM-like state (endogenous secretion abolished). An exploratory
3-ODE HPT-axis model (TSH secretion with Hill feedback by T3, T4 and T3
pools) tested generality. All analyses regenerate via
`python scripts/run_all.py`; 16 unit tests cover model integrity, the
u = 0 identity, intervention semantics and the classifier.

# Results

## Landscape of modulation responses

Figure 3 shows the composite loss L(u) for all 50
intervention–challenge combinations. Three regimes dominate. In the
fasting state every intervention leaves L essentially unchanged until
ablation destabilises homeostasis (Type 0/III). Under IVGTT and IVITT the
insulin axis is strongly non-monotone; under the more physiological OGTT,
several glucagon-axis interventions have shallow interior optima.

**Strict interior optima (Type II) were found in 7 of 50
combinations**, with a further 3 Type II* partial optima (Table 2).
The strongest result is partial suppression of insulin secretion under
IVGTT: u* = 0.74, with L falling from 221.07 at baseline to
44.37, while full ablation (u = 1) gives 82.44 — worse than
the optimum but still better than baseline, i.e. the dose-response has a
genuine interior minimum (Figure 4A). Global inhibition of insulin
action showed a parallel optimum at u* = 0.70 (L = 47.24).
Under CIVII, modest potentiation of insulin secretion was optimal
(u* = 0.52; L = 3.78 vs 27.72 at maximum),
showing the phenomenon is not restricted to inhibitory interventions.

## Mechanism

The IVGTT interior optimum arises from the trade-off between the insulin
excursion needed to clear the load and the reactive hypoglycaemia it
produces. At baseline the 0.5 g/kg bolus drives a secretion spike (peak
1349 mU/L) followed by a nadir of 40 mg/dL; at
u* the insulin peak is roughly a quarter as high (298 mU/L),
the nadir rises to 77 mg/dL, and peak glucose increases only
modestly (Figure 5). At u = 1,
secretion is abolished, hypoglycaemia disappears but glucose never
returns to target — the optimum interior point balances both failure
modes. Under OGTT the glucagon-axis optima (u* = 0.03 for
signalling inhibition, 0.91 for secretion potentiation) are
shallower and driven mainly by reduced glycaemic variability, consistent
with the islet's paradoxical feedback design [3].

## Robustness and controls

Across all weight perturbations (each term family scaled ×0.5/×2 or
zeroed), the interior-optimum classification of the headline cases was
preserved in 93 % of perturbations, reverting only when the
glucose-band terms themselves were removed (which removes the phenotype
by construction) or when the optimum is shallow and the classification
threshold is raised to 5 % (Figure 7; results/robustness/). Grid and
solver checks confirmed classification stability; refined optima differed
from coarse-grid estimates by ≤ 0.05. Pareto analysis (Figure 6) shows
the interior points dominate on the hypoglycaemia–hyperglycaemia plane
for the IVGTT cases: u* is simultaneously better on both axes than the
u = 0 baseline.

## Disease-state extensions

Under a T2DM-like state (insulin action halved; OGTT baseline loss rose
from 6.81 to 12.19), interior optima persisted
and shifted: potentiating insulin secretion became optimal at
u* = 0.45 rather than at maximum, and glucagon secretion
suppression retained a strong optimum (u* = 0.85).
Under a T1DM-like state (no
endogenous secretion), suppressing glucagon secretion showed a Type II
optimum at u* = 0.80 for fasting
(L 58.22 → 7.04), i.e. partial —
not total — glucagon suppression is optimal when insulin is absent
(Figure 8).

## Exploratory HPT extension

In the minimal HPT model challenged with a 60-min T4 infusion, thyroid
output *inhibition* exhibited a Type II interior optimum at
u* = 0.45 (L 17.93 → 2.71),
while feedback potentiation improved monotonically (Type I) and thyroid
potentiation gave no benefit (Type 0). This single-axis corroboration is
hypothesis-generating only.

# Discussion

We demonstrate, in a validated whole-body glucose–insulin–glucagon model,
that maximal endocrine action is frequently not optimal: strict interior
optima exist in 7 of 50 intervention–challenge pairs, span
secretion and signalling, potentiation and inhibition, and persist under
disease states and across loss-weighting schemes. The mechanism is a
Braess-like tension [1,2]: pushing one limb of the loop harder
over-commits the system to that direction, worsening the countervailing
failure mode (here, reactive hypoglycaemia) faster than it improves the
intended one. Moderate modulation can therefore dominate both extremes —
the signature of an interior optimum rather than a dose plateau.

Several limitations qualify the finding. The model is parameterised on a
single reference subject; the IVGTT reactive hypoglycaemia it produces
(nadir ≈ 40 mg/dL) is more severe than typical clinical FSIGT responses,
so the absolute position of u* for IVGTT is model-dependent even though
the existence of an interior optimum is robust. The composite loss
embeds explicit clinical preferences (hypoglycaemia weighted heaviest);
cases whose interior optimum is driven by variability revert to Type 0
when variability terms are removed, and we report those dependencies
honestly. The HPT extension is exploratory, not a fitted clinical model.
We make no claims about clinical doses, do not assert universal Braess
behaviour, and do not claim superiority of partial agonists — the results
are mechanistic and hypothesis-generating.

These results suggest a general design principle for endocrine feedback:
systems tuned near an interior optimum will respond to up-modulation with
worsening in at least one direction, which is testable in other axes and
in patient-level models.

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
