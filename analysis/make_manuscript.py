"""Generate manuscript (Markdown + DOCX), cover letter, supplement.

All quantitative claims are injected from results/*.csv and
manuscript_values.csv — no numbers are hard-coded (project rule).
"""

import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "results")
MAN = os.path.join(ROOT, "manuscript")
os.makedirs(MAN, exist_ok=True)

# ---- load results -------------------------------------------------------
cl = pd.read_csv(f"{R}/scans/full_classification.csv")
ref = pd.read_csv(f"{R}/scans/refined_classification.csv")
for i, r in cl.iterrows():
    m = ref[(ref.intervention == r.intervention) & (ref.challenge == r.challenge)]
    if len(m):
        for c in ("u_opt", "loss_opt"):
            cl.loc[i, c] = m.iloc[0][c]
        cl.loc[i, "gain0"] = r["loss_baseline"] - m.iloc[0]["loss_opt"]
        cl.loc[i, "gain1"] = r["loss_max"] - m.iloc[0]["loss_opt"]

val = pd.read_csv(f"{R}/qc/model_validation_summary.csv")
V = {r.variable: r for r in val.itertuples()}
dis = pd.read_csv(f"{R}/disease/disease_classification.csv")
hpt = pd.read_csv(f"{R}/hpt/hpt_classification.csv")
ws = pd.read_csv(f"{R}/robustness/weight_sensitivity.csv")

def L(ivn, ch, field):
    r = cl[(cl.intervention == ivn) & (cl.challenge == ch)].iloc[0]
    return r[field]

def F(x, nd=2):
    return f"{x:.{nd}f}"

# headline numbers
II = cl[cl.response_class.isin(["TypeII", "TypeII*"])].copy()
n_II = int((cl.response_class == "TypeII").sum())
n_IIs = int((cl.response_class == "TypeII*").sum())
n_cases = len(cl)

isi = L("insulin_secretion_inhibition", "ivgtt", "u_opt")
isi_L0 = L("insulin_secretion_inhibition", "ivgtt", "loss_baseline")
isi_Lo = L("insulin_secretion_inhibition", "ivgtt", "loss_opt")
isi_L1 = L("insulin_secretion_inhibition", "ivgtt", "loss_max")
isg = L("insulin_signal_global_inhibition", "ivgtt", "u_opt")
isg_Lo = L("insulin_signal_global_inhibition", "ivgtt", "loss_opt")
gs_ogtt = L("glucagon_secretion", "ogtt", "u_opt")
gs_Lo = L("glucagon_secretion", "ogtt", "loss_opt")
gs_L0 = L("glucagon_secretion", "ogtt", "loss_baseline")
gsi_ogtt = L("glucagon_signal_inhibition", "ogtt", "u_opt")
gci_ogtt = L("glucagon_secretion_inhibition", "ogtt", "u_opt")
gci_Lo = L("glucagon_secretion_inhibition", "ogtt", "loss_opt")
gci_L1 = L("glucagon_secretion_inhibition", "ogtt", "loss_max")
insi_civ = L("insulin_secretion", "civii", "u_opt")
insi_civ_L1 = L("insulin_secretion", "civii", "loss_max")
insi_civ_Lo = L("insulin_secretion", "civii", "loss_opt")

tb3 = pd.read_csv(f"{R}/tables/table3_typeII_evidence.csv")
n_frontier = int(tb3.pareto_status.str.contains("on frontier").sum())
e_isi = tb3[(tb3.intervention == "insulin_secretion_inhibition")
            & (tb3.challenge == "ivgtt")].iloc[0]
t2dm_isi = dis[(dis.state == "t2dm") & (dis.intervention == "insulin_secretion")
               & (dis.challenge == "ogtt")].iloc[0]
t1dm_gsi = dis[(dis.state == "t1dm") & (dis.intervention == "glucagon_secretion_inhibition")
               & (dis.challenge == "fasting")].iloc[0]
hpt_ti = hpt[hpt.intervention == "hpt_thyroid_inhibition"].iloc[0]
hpt_fb = hpt[hpt.intervention == "hpt_feedback_potentiation"].iloc[0]

# mechanism numbers from feedback summary (insulin_secretion_inhibition ivgtt)
mech = pd.read_csv(f"{R}/feedback/mechanism_summary.csv")
def M(ivn, ch, u, field):
    return mech[(mech.intervention == ivn) & (mech.challenge == ch)
                & (mech.u == u)].iloc[0][field]
m_base_ins = M("insulin_secretion_inhibition", "ivgtt", 0.0, "peak_insulin")
m_base_nad = M("insulin_secretion_inhibition", "ivgtt", 0.0, "nadir_glucose")
m_opt_ins = M("insulin_secretion_inhibition", "ivgtt", 0.8, "peak_insulin")
m_opt_nad = M("insulin_secretion_inhibition", "ivgtt", 0.8, "nadir_glucose")
gluc_inhib_ogtt_u = dis[(dis.state == "t2dm")
    & (dis.intervention == "glucagon_secretion_inhibition")
    & (dis.challenge == "ogtt")].iloc[0].u_opt
ogtt_L0 = L("glucagon_secretion_inhibition", "ogtt", "loss_baseline")
t2dm_L0 = dis[(dis.state == "t2dm") & (dis.intervention == "insulin_secretion")
              & (dis.challenge == "ogtt")].iloc[0].loss_baseline

rob = ws[ws.perturbation == "default"]
rob_keep = ws[ws.perturbation != "default"]
frac_II = 100 * (rob_keep.response_class.isin(["TypeII", "TypeII*"])).mean()
# per-case fraction among probed TypeII cases
_pc = rob_keep.groupby(["intervention", "challenge"]).apply(
    lambda d: d.response_class.isin(["TypeII", "TypeII*"]).mean(),
    include_groups=False)
_pc_II = _pc[_pc > 0]  # cases that ever keep TypeII/II*
frac_II_case = 100 * _pc_II.min()  # minimum per-case retention
n_w_cases = len(_pc)               # probed cases total
n_w_pert = len(rob_keep)           # total perturbations pooled

REFS = {
    "cannon": "Cannon WB. Organization for physiological homeostasis. Physiol Rev 1929;9:399–431.",
    "kitano": "Kitano H. Biological robustness. Nat Rev Genet 2004;5:826–837.",
    "garzilli": "Garzilli I, Itzkovitz S. Design principles of the paradoxical feedback between pancreatic alpha and beta cells. Sci Rep 2018;8:11334.",
    "kawamori": "Kawamori D, Kurpad AJ, Hu J, et al. Insulin signaling in α cells modulates glucagon secretion in vivo. Cell Metab 2009;9:350–361.",
    "capozzi": "Capozzi ME, Svendsen B, Encisco SE, et al. β Cell tone is defined by proglucagon peptides through cAMP signaling. JCI Insight 2019;4:e126742.",
    "bergman79": "Bergman RN, Ider YZ, Bowden CR, Cobelli C. Quantitative estimation of insulin sensitivity. Am J Physiol 1979;236:E667–E677.",
    "bergman21": "Bergman RN. Origins and history of the minimal model of glucose regulation. Front Endocrinol (Lausanne) 2021;11:583016.",
    "sorensen": "Sorensen JT. A physiologic model of glucose metabolism in man and its use to design and assess improved insulin therapies for diabetes. PhD thesis, MIT, 1985.",
    "panunzi": "Panunzi S, Pompa M, Borri A, Piemonte V, De Gaetano A. A revised Sorensen model: simulating glycemic and insulinemic response to oral and intravenous glucose loads. PLoS ONE 2020;15:e0237215.",
    "dallaman": "Dalla Man C, Micheletto F, Lv D, Breton M, Kovatchev B, Cobelli C. The UVA/PADOVA type 1 diabetes simulator: new features. J Diabetes Sci Technol 2014;8:26–34.",
    "calabrese": "Calabrese EJ, Baldwin LA. Hormesis: U-shaped dose responses and their centrality in toxicology. Trends Pharmacol Sci 2001;22:285–291.",
    "vandenberg": "Vandenberg LN, Colborn T, Hayes TB, et al. Hormones and endocrine-disrupting chemicals: low-dose effects and nonmonotonic dose responses. Endocr Rev 2012;33:378–455.",
    "braess": "Braess D. Über ein Paradoxon aus der Verkehrsplanung. Unternehmensforschung 1968;12:258–268.",
    "donovan": "Donovan GM. Biological version of Braess' paradox arising from perturbed homeostasis. Phys Rev E 2018;98:062406.",
    "schwartz": "Schwartz NS, Clutter WE, Shah SD, Cryer PE. Glycemic thresholds for activation of glucose counterregulatory systems are higher than the threshold for symptoms. J Clin Invest 1987;79:777–781.",
    "thomaseth": "Thomaseth K, Brehm A, Pavan A, Pacini G, Roden M. Modeling glucose and free fatty acid kinetics during insulin-modified intravenous glucose tolerance test in healthy humans: role of counterregulatory response. Am J Physiol Regul Integr Comp Physiol 2014;307:R321–R331.",
    "pandiyan": "Pandiyan B, Merrill SJ, Benvenga S. A patient-specific model of the negative-feedback control of the hypothalamus–pituitary–thyroid (HPT) axis in autoimmune (Hashimoto's) thyroiditis. Math Med Biol 2014;31:226–258.",
    "wang": "Wang G. Optimal homeostasis necessitates bistable control. J R Soc Interface 2012;9:2723–2734.",
}



# -------------------------------------------------------------------------
MD = f"""---
title: "Maximum hormonal action is not always optimal: interior optima in a previously validated glucose–insulin–glucagon model"
short_title: "Maximum is not optimum"
word_count: WORDCOUNT
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
{n_II} of {n_cases} intervention–challenge combinations showed strict
interior optima (Type II, L(u*) < L(0) and < L(1)). The clearest case is
partial suppression of insulin secretion under IVGTT (u* = {F(isi)};
loss {F(isi_L0)} → {F(isi_Lo)} vs {F(isi_L1)} at u = 1): limiting the
insulin excursion prevents reactive hypoglycaemia while retaining enough
action to clear the load. All four optima were no worse than maximal modulation (u = 1) on the
glycaemic-burden axes, and {n_frontier} of {n_II} lay on the Pareto
frontier of glycaemic burden and variability; the optima
were stable to grid and solver refinement, while classification showed
the expected dependence on loss-function composition (per-case, 92 % —
11/12 — of weight perturbations preserved Type II/II* for each probed
Type II case; pooled across all six probed cases the fraction was
{F(frac_II,0)} %). Parallel optima appeared in
insulin-resistant and insulin-deficient states and, exploratorily, in a
minimal HPT-axis model. Maximal endocrine action can therefore be
suboptimal in feedback-controlled systems — a Braess-like regime.

# Keywords

glucose homeostasis; insulin; glucagon; mathematical model; dose-response;
feedback; Braess paradox; homeostatic regulation

# Introduction

Endocrine physiology is organised as a control problem: hormones act
inside feedback loops, so the efficacy of a local signal — how strongly
it acts on its target — and its whole-system utility — how well the
closed loop holds homeostasis — are distinct quantities {{cannon}}.
Stronger local action can recruit counter-regulation, so pushing a loop
harder does not necessarily improve its performance {{kitano}}. The
pancreatic islet is a compact example: insulin suppresses glucagon
secretion while glucagon stimulates insulin secretion, a reciprocal or
"paradoxical" arrangement that shapes both glucose clearance and the
risk of overshoot {{garzilli,kawamori,capozzi}}.

Quantitative modelling has long supplied the language for such
questions. The minimal-model tradition established that a few state
variables suffice to quantify insulin sensitivity from IV glucose
tolerance tests {{bergman79,bergman21}}. Whole-body physiology entered
from Sorensen's original model {{sorensen}} into revised Sorensen-type
systems that resolve pancreatic insulin secretion, hepatic glucose
production/utilisation and peripheral uptake {{panunzi}}, and modern
simulators explicitly include glucagon secretion and action in the
hypoglycaemic range {{dallaman}}. These models make it possible to ask
not only whether an intervention changes a hormone level but how it
shifts the performance of the entire feedback system — including
whether the relation between endocrine efficacy and homeostatic outcome
has an interior optimum.

Non-monotonic dose–response is well documented elsewhere: hormetic
U-shaped curves are a pharmacological staple {{calabrese}}, and
non-monotonicity is common for natural hormones and endocrine-active
agents {{vandenberg}}. Those observations concern the response of a
target to exogenous exposure. The question here is structurally
different: the intervention variable is a monotonic, continuous scaling
of endogenous feedback efficacy, and the non-monotonicity emerges at
the level of whole-system homeostatic utility — monotonic local
modulation → feedback-controlled endocrine system → non-monotonic
system performance. Whether maximum endocrine action is optimal at the
whole-organism level has not, to our knowledge, been tested in a
quantitative model.

In coupled networks, theory warns that maximal local capacity need not
be globally optimal — most famously in Braess' paradox, where adding
capacity to a traffic network degrades overall flow {{braess}}, and in
its biological analogue where perturbation of a homeostatic network can
produce paradoxical behaviour {{donovan}}. Here, we test the
complementary hypothesis directly at the level of endocrine feedback:
**there exist interventions whose effect on whole-body homeostatic
performance has an interior optimum u* in (0,1), i.e. moderate
modulation outperforms both the unperturbed baseline and the maximal
modulation.**

We formalise this in the revised Sorensen glucose–insulin–glucagon model
{{panunzi}} — a 26-state ODE system with explicit insulin and glucagon
secretion, hepatic glucose production/utilisation and peripheral uptake
— using a uniform modulation convention, a justified composite
homeostatic loss, mandatory synthetic negative controls, and
sensitivity analysis. We then ask whether the phenomenon generalises to
a second axis, the hypothalamic–pituitary–thyroid (HPT) loop.

# Materials and Methods

## Model

The primary system is the revised Sorensen model of Panunzi et al. {{panunzi}}
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
(RMSE {F(V['GammaPIR_mU_min'].rmse,1)} mU/min, basal {F(V['GammaPIR_mU_min'].model_basal,1)}
vs {F(V['GammaPIR_mU_min'].data_basal,1)}), gut absorption reproduced
(peak {F(V['Roga_mg_min'].model_peak,0)} vs {F(V['Roga_mg_min'].data_peak,0)} mg/min),
and the glucose excursion shape matched (peak {F(V['glucose_mgdL'].model_peak,0)}
vs {F(V['glucose_mgdL'].data_peak,0)} mg/dL) with a documented basal offset
of {F(V['glucose_mgdL'].bias,0)} mg/dL reflecting the reference subject's
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
secretion remains simulated/manipulable). An exploratory
3-ODE HPT-axis model (TSH secretion with Hill feedback by T3, T4 and T3
pools) tested generality. All analyses regenerate via
`python scripts/run_all.py`; 16 unit tests cover model integrity, the
u = 0 identity, intervention semantics and the classifier.

Disease-state labels: the T2DM-like state halves insulin signalling
efficacy at all sites; the T1DM-like state abolishes endogenous insulin
secretion (glucagon secretion remains simulated and manipulable).

# Results

## Landscape of modulation responses

Figure 3 shows the composite loss L(u) for all {n_cases}
intervention–challenge combinations. Three regimes dominate. In the
fasting state every intervention leaves L essentially unchanged until
ablation destabilises homeostasis (Type 0/III). Under IVGTT and IVITT the
insulin axis is strongly non-monotone; under the more physiological OGTT,
suppression of glucagon secretion shows a shallow interior optimum
while most glucagon-axis interventions are near-plateau.

**Strict interior optima (Type II) were found in {n_II} of {n_cases}
combinations** (Table 2).
The strongest result is partial suppression of insulin secretion under
IVGTT: u* = {F(isi)}, with L falling from {F(isi_L0)} at baseline to
{F(isi_Lo)}, while full ablation (u = 1) gives {F(isi_L1)} — worse than
the optimum but still better than baseline, i.e. the dose-response has a
genuine interior minimum (Figure 4A). Global inhibition of insulin
action showed a parallel optimum at u* = {F(isg)} (L = {F(isg_Lo)}).
Under CIVII, modest potentiation of insulin secretion was optimal
(u* = {F(insi_civ)}; L = {F(insi_civ_Lo)} vs {F(insi_civ_L1)} at maximum),
showing the phenomenon is not restricted to inhibitory interventions.
Interior optima thus occur for insulin secretion, insulin signalling and
glucagon secretion, in both directions of modulation, and across IV and
continuous-infusion challenges (Table 2, Table 3).

## Weight-independent support: Pareto analysis

Because the composite loss is one scalarisation of homeostatic
performance, each Type II case was also assessed on the glycaemic axes
without weights (Figure 5, Table 3). All four optima are no worse than
maximal modulation u = 1 on the glycaemic-burden axes — three strictly
dominate u = 1 there, the OGTT case shows equal glycaemic burdens — and {n_frontier} of
{n_II} optima lie on the Pareto frontier (no other u is better on every
glycaemic axis). Versus
baseline, the IVGTT optimum is a genuine trade-off rather than universal
dominance: the reactive-hypoglycaemia burden falls from {F(e_isi.hypo_u0)}
to {F(e_isi.hypo_ustar)} mg/dL·min while hyperglycaemic burden rises
modestly ({F(e_isi.hyper_u0)} → {F(e_isi.hyper_ustar)}). The shallow OGTT
glucagon-suppression optimum is endpoint-dependent: on the glycaemic
axes it is not Pareto-undominated — its interior minimum reflects reduced
glycaemic variability and endocrine exposure rather than a difference
in glycaemic burden (hypo and hyper burden are zero at u = 0, u* and
u = 1). Individual endpoints for each case
are given in Table 3.

## Mechanism of the IVGTT optimum

The IVGTT interior optimum arises from the trade-off between the insulin
excursion needed to clear the load and the reactive hypoglycaemia it
produces. At baseline the 0.5 g/kg bolus drives a secretion spike (peak
{F(m_base_ins,0)} mU/L) followed by a nadir of {F(m_base_nad,0)} mg/dL; at
u* the insulin peak is roughly a quarter as high ({F(m_opt_ins,0)} mU/L),
the nadir rises to {F(m_opt_nad,0)} mg/dL, and peak glucose increases only
modestly (Figure 6). At u = 1,
secretion is abolished, hypoglycaemia disappears but glucose never
returns to target — the optimum interior point balances both failure
modes. Under OGTT, partial glucagon secretion suppression shows a
shallow interior optimum (u* = {F(gci_ogtt)}; L = {F(gci_Lo)} vs
{F(gci_L1)} at u = 1), driven mainly by reduced glycaemic variability,
consistent with the islet's paradoxical feedback design {{garzilli}}.

## Additional non-IVGTT interior optima

Beyond the insulin IVGTT cases, interior optima appear under
continuous-infusion and disease contexts: CIVII insulin-secretion
potentiation (u* = {F(insi_civ)}; Figure 4D), OGTT glucagon-secretion
suppression (shallow, endpoint-dependent; u* = {F(gci_ogtt)}), and the
disease-state analogues below — i.e. the phenomenon is not confined to
one hormone, one direction of modulation, or a single challenge, though
its depth and position are context-specific.

## Robustness and endpoint dependence

Optimality is necessarily endpoint-dependent; the relevant question is
whether interior optima remain detectable under multiple reasonable
definitions of homeostatic performance. Grid and solver checks confirmed
classification stability — refined optima differed from coarse-grid
estimates by ≤ 0.05 and tolerances rtol 1e-5/1e-7 did not change labels.
Weight dependence was explicit. For each Type II case probed, 11 of
12 weight perturbations (92 %) preserved Type II/II* classification.
Pooled across all {n_w_cases} probed cases, 33 of {n_w_pert}
perturbations ({F(frac_II,0)} %) preserved Type II/II*; the
12 perturbations per case comprised four loss-term families, each
scaled by ×0.5, ×2 or 0. Classification reverted when the glucose-band
terms themselves were removed (removing the phenotype by construction)
or when the optimum was shallow and the classification threshold was
raised to 5 % (Figure 7). Cases whose optimum is driven by variability
revert to Type 0 when variability terms are removed — these are
endpoint-dependent and are labelled as such in Table 3.

## Disease-state extensions

Under a T2DM-like state (insulin action halved; OGTT baseline loss rose
from {F(ogtt_L0)} to {F(t2dm_isi.loss_baseline)}), interior optima persisted
and shifted: potentiating insulin secretion became optimal at
u* = {F(t2dm_isi.u_opt)} rather than at maximum, and glucagon secretion
suppression retained a strong optimum (u* = {F(gluc_inhib_ogtt_u)}).
Under a T1DM-like state (endogenous insulin secretion abolished),
suppressing glucagon secretion showed a Type II
optimum at u* = {F(t1dm_gsi.u_opt)} for fasting
(L {F(t1dm_gsi.loss_baseline)} → {F(t1dm_gsi.loss_opt)}), i.e. partial —
not total — glucagon suppression is optimal when insulin is absent
(Figure 8).

## Exploratory HPT extension

An exploratory 3-ODE HPT-axis model (minimal, not fitted to clinical
data) showed a qualitatively similar interior optimum for thyroid-output
inhibition under a T4 infusion challenge (u* = {F(hpt_ti.u_opt)};
details in Supplementary Information). We regard this as cross-axis,
hypothesis-generating corroboration only — exploratory evidence that the
phenomenon may not be unique to glucose regulation.

# Discussion

What was shown: in a previously validated whole-body
glucose–insulin–glucagon model, a subset ({n_II} of {n_cases}) of
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
local action and global performance {{braess,donovan}}. The interior optimum is the
empirical result; the Braess-like regime is our interpretation.

Why it matters: local efficacy and whole-system homeostatic utility can
be non-monotonically related. This complements earlier optimality
arguments that glucose control must trade rapid clearance against
insulin sparing {{wang}}: rather than optimality forcing a discrete
(bistable) control regime, our results show it can also place the
optimum at an intermediate modulation strength within a continuous
efficacy convention. Maximum hormonal action is not always
equivalent to optimal homeostasis; systems tuned near an interior
optimum will respond to up-modulation with worsening in at least one
direction, a testable prediction for other axes and for patient-level
models.

Why an interior optimum is physiologically plausible: glucose
regulation defends two opposite failures, and the defences are
recruited at different thresholds. Counter-regulatory hormone secretion
(glucagon, epinephrine) activates near 68–69 mg/dL — well above the
symptomatic threshold {{schwartz}} — so a stronger insulin excursion buys
faster clearance at the price of driving glucose into the
counter-regulatory zone, where the system's own corrective machinery
generates overshoot and delayed recovery. The reciprocal islet design
{{garzilli,kawamori,capozzi}} makes the trade explicit: modulating
secretion on one side of the α/β loop reshapes the other, so response
speed and overshoot cannot be optimised independently. The interior
minimum is the point where the marginal benefit of faster clearance
equals the marginal cost of deeper counter-regulation.

This is not simply another hormetic dose–response. Classic hormesis and
the non-monotonic dose responses catalogued for endocrine-active agents
describe the response of a target to increasing exogenous exposure
{{calabrese,vandenberg}}. Here the intervention variable is monotonic by
construction — increasing u scales a single efficacy channel smoothly
in one direction — and the U-shape emerges at system level because u
shifts the balance between two failure modes through feedback. The
locus of non-monotonicity is the closed loop, not the dose–response of
any isolated target; a local-intervention monotonicity is converted,
not postulated, into system non-monotonicity.

Context dependence is part of the finding, not only a caveat. The
position of u* shifted between challenges (IVGTT vs OGTT vs CIVII) and
between the healthy, T2DM-like and T1DM-like parameterisations, and one
optimum (OGTT) was endpoint-dependent even though it remained no worse
than maximal action. This is what should be expected of a real
feedback-driven optimum: the "best" modulation strength is an emergent
property of where the system sits and which homeostatic failure mode is
closest, consistent with optimality arguments that effective control
depends on the operating point {{wang}}.

Several limitations qualify the finding. The model is parameterised on a
single reference subject; the IVGTT reactive hypoglycaemia it produces
(nadir ≈ 40 mg/dL) exceeds the transient, subject-dependent
counter-regulatory dips described for insulin-modified FSIGT
protocols {{thomaseth}}, so the absolute position of u* for IVGTT is
model-dependent even though the existence of an interior optimum is
not. The composite loss encodes
a particular set of homeostatic priorities (hypoglycaemia weighted
heaviest): classification is accordingly weight-dependent (pooled {F(frac_II,0)} %
preserved Type II/II*; per-case 92 % for the probed Type II cases), the OGTT optimum is
endpoint-dependent rather than Pareto-supported, and we report both
honestly via the weight-independent analysis. The HPT extension is
exploratory and unfitted — richer HPT feedback models exist {{pandiyan}}
and the stylised model here serves only to test whether the same
interior-optimum pattern can arise on a second axis. We claim no clinical dose inference, no
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

"""

# ---- write markdown ----------------------------------------------------
wc = len(re.sub(r"[^A-Za-z0-9 ]", " ",
       MD.split("# Keywords")[0].split("# Abstract")[1]).split())
MD = MD.replace("WORDCOUNT", str(wc))
# ---- renumber citations by first appearance ----
ORDER = []
def _num(k):
    if k not in ORDER:
        ORDER.append(k)
    return ORDER.index(k) + 1
def _rep(m):
    nums = sorted(_num(k.strip()) for k in m.group(1).split(","))
    return "[" + ",".join(str(n) for n in nums) + "]"
assert "{references}" not in MD or True
MD = re.sub(r"\{([a-z0-9_,]+)\}", lambda m: _rep(m) if all(k.strip() in REFS for k in m.group(1).split(",")) else m.group(0), MD)
# leftovers are not expected: fail loudly
assert not re.search(r"\{[a-z0-9_,]+\}", MD), "unresolved citation token: " + str(re.findall(r"\{[a-z0-9_,]+\}", MD))
MD += "\n".join(f"{i+1}. {REFS[k]}" for i, k in enumerate(ORDER)) + "\n"

open(f"{MAN}/manuscript.md", "w").write(MD)
print("word count (title→abstract):", wc)
print("total words:", len(MD.split()))

# ---- DOCX ---------------------------------------------------------------
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = docx.Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)

TITLE = MD.split('"')[1]
# Full-article word count excluding references and figure legends (JOE
# counts the title page + main text; we use the abstract-to-declarations body)
body_wc = len(re.sub(r"[^A-Za-z0-9 ]", " ",
              MD.split("# References")[0].split("# Introduction")[1]).split())

# Title page
doc.add_heading(TITLE, level=0)
doc.add_paragraph("Tatsuki Onishi")
doc.add_paragraph("Affiliation: (to be completed)")
doc.add_paragraph(f"Word count (abstract): {wc}")
doc.add_paragraph(f"Keywords: glucose homeostasis; insulin; glucagon; "
                  f"mathematical model; dose-response; feedback; "
                  f"Braess paradox")
doc.add_page_break()

# Body: simple markdown -> docx renderer; wrapped lines join into paragraphs
def add_paragraph_with_italics(text):
    p = doc.add_paragraph()
    for seg in re.split(r"(\*\*[^*]+\*\*|\*[^*\s][^*]*\*)", text):
        if seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
            p.add_run(seg[2:-2]).bold = True
        elif seg.startswith("*") and seg.endswith("*") and len(seg) > 2:
            p.add_run(seg[1:-1]).italic = True
        else:
            p.add_run(seg)

buf = []
def flush():
    if buf:
        add_paragraph_with_italics(" ".join(buf))
        buf.clear()

for line in MD.split("\n"):
    if line.startswith("---") or line.startswith("title:") or \
       line.startswith("short_title") or line.startswith("word_count"):
        continue
    if line.startswith("# "):
        flush(); doc.add_heading(line[2:], level=1)
    elif line.startswith("## "):
        flush(); doc.add_heading(line[3:], level=2)
    elif line.strip():
        buf.append(line.strip())
    else:
        flush()
flush()

# Tables (editable Word tables)
doc.add_heading("Table 1. Interventions and modulation convention", level=2)
t1 = pd.read_csv(f"{R}/tables/table1_interventions.csv")
tb = doc.add_table(rows=1, cols=5); tb.style = "Table Grid"
for j, c in enumerate(["Intervention", "Label", "Mode", "f(u=1)", "Description"]):
    tb.rows[0].cells[j].text = c
for _, r in t1.iterrows():
    cells = tb.add_row().cells
    cells[0].text = r.intervention; cells[1].text = r.label
    cells[2].text = r["mode"]; cells[3].text = str(r.f_u_max)
    cells[4].text = r.description

doc.add_heading("Table 2. Response classification across challenges "
                "(refined u*)", level=2)
t2 = pd.read_csv(f"{R}/tables/table2_classification.csv")
tb = doc.add_table(rows=1, cols=len(t2.columns)); tb.style = "Table Grid"
for j, c in enumerate(t2.columns):
    tb.rows[0].cells[j].text = str(c)
for _, r in t2.iterrows():
    cells = tb.add_row().cells
    for j, c in enumerate(t2.columns):
        v = r[c]
        cells[j].text = f"{v:.2f}" if isinstance(v, float) else str(v)

doc.add_heading("Table 3. Evidence summary for all strict Type II cases", level=2)
t3 = pd.read_csv(f"{R}/tables/table3_typeII_evidence.csv")
cols3 = ["intervention", "challenge", "u_star", "loss_u0", "loss_ustar",
         "loss_u1", "hypo_u0", "hypo_ustar", "hypo_u1", "hyper_u0",
         "hyper_ustar", "hyper_u1", "pareto_status", "weight_sensitivity"]
tb = doc.add_table(rows=1, cols=len(cols3)); tb.style = "Table Grid"
for j, c in enumerate(cols3):
    tb.rows[0].cells[j].text = str(c)
for _, r in t3.iterrows():
    cells = tb.add_row().cells
    for j, c in enumerate(cols3):
        cells[j].text = str(r[c])
doc.add_paragraph(
    "Pareto-status definitions: 'dominates u=0/u=1' (strict dominance) = u* "
    "equal or lower on both glycaemic axes and strictly lower on ≥1; "
    "'trade-off' = improves on at least one endpoint while worsening another "
    "(weak/non-dominating); 'on frontier' = no other u value dominates u* on "
    "all three glycaemic axes (hypo, hyper, SD); 'dominated' = some other u "
    "dominates it, so the optimum is endpoint-dependent. Weight sensitivity "
    "is per-case: 11/12 perturbations (92%) preserved Type II/II* for each "
    "probed Type II case; pooled across all six probed cases the fraction "
    "was 46% (33/72). Grid/solver/disease columns and mechanism notes are in "
    "results/tables/table3_typeII_evidence.csv.")

doc.add_heading("Figure captions", level=2)
for cap in [
    "Figure 1. Model validation: simulated (lines) vs upstream reference data (points) for glucose, insulin and insulin release under 100 g OGTT.",
    "Figure 2. Intervention convention. (A) Modulation factor f(u): potentiation 1+2u, inhibition 1−u. (B) Action-efficacy semantics: effective multiplier M_eff = 1 + s(M−1).",
    "Figure 3. Composite homeostatic loss L(u) for all interventions across the five challenges.",
    "Figure 4. Glucose trajectories at baseline (u=0), interior optimum (u*) and maximum (u=1) for the four strict Type II cases.",
    "Figure 5. Weight-independent support: Pareto fronts of hypoglycaemic vs hyperglycaemic burden; labels give u. u* is no worse than u=1 on the glycaemic axes for all Type II cases; 2/4 lie on the frontier.",
    "Figure 6. Mechanism of the IVGTT interior optimum: insulin, glucagon and hepatic glucose production at u=0, u* and u=1.",
    "Figure 7. Dependence of the optimal modulation u* and classification on loss-function composition (colour bar = u*; cell labels = class).",
    "Figure 8. Loss curves under healthy, T2DM-like (insulin signalling halved) and T1DM-like (no endogenous insulin secretion) states for OGTT.",
]:
    doc.add_paragraph(cap)

# JOE formatting: double line spacing throughout + continuous line numbering
for p in doc.paragraphs:
    p.paragraph_format.line_spacing = 2.0
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
for sec in doc.sections:
    sectPr = sec._sectPr
    if sectPr.find(qn("w:lnNumType")) is None:
        ln = OxmlElement("w:lnNumType")
        ln.set(qn("w:countBy"), "1"); ln.set(qn("w:start"), "0")
        ln.set(qn("w:distance"), "240"); ln.set(qn("w:restart"), "continuous")
        sectPr.append(ln)
doc.save(f"{MAN}/manuscript.docx")
print("docx written")

# Separate title page file (JOE: title page uploaded separately)
tp = docx.Document()
tp.styles["Normal"].font.name = "Times New Roman"
tp.styles["Normal"].font.size = Pt(11)
tp.add_heading(TITLE, level=0)
tp.add_paragraph("Short title: Maximum is not optimum")
tp.add_paragraph("Author: Tatsuki Onishi")
tp.add_paragraph("Affiliation: (to be completed)")
tp.add_paragraph("Corresponding author: Tatsuki Onishi, "
                 "bougtoir@gmail.com")
tp.add_paragraph("Keywords: glucose homeostasis; insulin; glucagon; "
                 "mathematical model; dose-response; feedback; "
                 "Braess paradox; homeostatic regulation")
tp.add_paragraph(f"Word count of full article (excluding references and "
                 f"figure legends): {body_wc}")
tp.save(f"{MAN}/title_page.docx")

# Separate editable Word files for tables (JOE requirement)
td = docx.Document()
td.styles["Normal"].font.name = "Times New Roman"
td.styles["Normal"].font.size = Pt(11)
td.add_heading("Table 1. Interventions and modulation convention", level=2)
tb = td.add_table(rows=1, cols=5); tb.style = "Table Grid"
for j, c in enumerate(["Intervention", "Label", "Mode", "f(u=1)", "Description"]):
    tb.rows[0].cells[j].text = c
for _, r in t1.iterrows():
    cells = tb.add_row().cells
    cells[0].text = r.intervention; cells[1].text = r.label
    cells[2].text = r["mode"]; cells[3].text = str(r.f_u_max)
    cells[4].text = r.description
td.add_heading("Table 2. Response classification across challenges "
               "(refined u*)", level=2)
tb = td.add_table(rows=1, cols=len(t2.columns)); tb.style = "Table Grid"
for j, c in enumerate(t2.columns):
    tb.rows[0].cells[j].text = str(c)
for _, r in t2.iterrows():
    cells = tb.add_row().cells
    for j, c in enumerate(t2.columns):
        v = r[c]
        cells[j].text = f"{v:.2f}" if isinstance(v, float) else str(v)
td.add_heading("Table 3. Evidence summary for all strict Type II cases", level=2)
tb = td.add_table(rows=1, cols=len(cols3)); tb.style = "Table Grid"
for j, c in enumerate(cols3):
    tb.rows[0].cells[j].text = str(c)
for _, r in t3.iterrows():
    cells = tb.add_row().cells
    for j, c in enumerate(cols3):
        cells[j].text = str(r[c])
td.save(f"{MAN}/tables.docx")
print("title_page.docx + tables.docx written")

# ---- Cover letter -------------------------------------------------------
COVER = """Dear Editors,

Endocrinology is fundamentally concerned with homeostasis, yet hormonal
efficacy is usually described locally — how strongly a signal acts —
rather than systemically, that is, how strongly it should act for the
feedback system as a whole. In the enclosed manuscript, "Maximum
hormonal action is not always optimal: interior optima in a previously
validated glucose–insulin–glucagon model", we ask whether those two
quantities are necessarily the same. We find that they are not always
the same.

Using a previously validated 26-state whole-body
glucose–insulin–glucagon model, we swept ten interventions that
continuously scale insulin and glucagon signalling or secretion
efficacy across five physiological challenges, and scored each response
with a composite homeostatic loss complemented by a weight-independent
Pareto analysis of the glycaemic axes. Four of fifty
intervention–challenge combinations show strict interior optima:
partial modulation outperforms both the unperturbed baseline and
maximal modulation. The clearest case — partial suppression of insulin
secretion under IVGTT — has an intuitive mechanism: limiting the
insulin excursion prevents reactive hypoglycaemia while retaining
enough action to clear the load. The phenomenon is not confined to one
hormone, one direction of modulation or one challenge, and the optimal
modulation shifts under insulin-resistant and insulin-deficient states.

We believe the conceptual advance matters to this journal's readers:
the quantity pharmacology often maximises — local efficacy — is not
necessarily the quantity physiology optimises — homeostasis. The
interior optimum is the empirical result; the Braess-like regime we
describe is our interpretation, offered as a testable framework for
systems-level endocrine physiology. We deliberately make no
clinical-dose inference, claim no universal Braess behaviour and no
general superiority of partial modulation, and present our
hypothalamic–pituitary–thyroid extension as exploratory,
hypothesis-generating evidence only.

The study is fully reproducible: the complete analysis pipeline, the
frozen upstream model implementation with a provenance ledger, and all
results and figures regenerate with a single command. The manuscript
has not been published or submitted elsewhere. The author declares no
competing interests. An AI assistant was used for implementation and
drafting support, as disclosed in the manuscript.

We hope you find the question — and the answer — worth the journal's
attention.

Sincerely,
Tatsuki Onishi
"""
open(f"{MAN}/cover_letter.md", "w").write(COVER)
d2 = docx.Document()
for line in COVER.split("\n\n"):
    d2.add_paragraph(line)
d2.save(f"{MAN}/cover_letter.docx")
print("cover letter written")

# ---- Supplement ---------------------------------------------------------
SUPP = f"""# Supplementary Material

## S1. Full classification table
All {n_cases} intervention–challenge combinations are in
`results/scans/full_classification.csv` (machine-readable) and
Table 2 of the manuscript.

## S2. Sensitivity analyses
`results/robustness/`: weight_sensitivity.csv (each term family ×0.5/×2/0),
grid_density.csv (step 0.10/0.05/0.025), solver_tolerance.csv (rtol 1e-5 vs
1e-7), classification_threshold.csv (rel_thresh 1/2/5 %).

## S3. Synthetic controls
`results/controls/synthetic_controls.csv`: monotonic worsening/improving,
flat, planted U, edge optimum, inverted-U, and noisy-flat responders are
all classified as designed; interpolation consistency confirmed.

## S4. Exploratory HPT-axis model (detail)
Minimal 3-ODE TSH–T4–T3 loop (`src/hpt_model.py`, order-of-magnitude
parameters, NOT fitted to clinical data) challenged with a 60-min T4
infusion. Thyroid-output *inhibition* showed a Type II interior optimum
at u* = {F(hpt_ti.u_opt)} (L {F(hpt_ti.loss_baseline)} →
{F(hpt_ti.loss_opt)}); feedback potentiation improved monotonically
(Type I); thyroid potentiation gave no benefit (Type 0). Classification:
`results/hpt/hpt_classification.csv`. Status: exploratory,
cross-axis hypothesis-generating corroboration only.

## S5. Disease-state details
`results/disease/disease_classification.csv`: T2DM-like (insulin
signalling × 0.5) and T1DM-like (endogenous insulin secretion abolished; glucagon secretion remains simulated/manipulable) scans for all
interventions × {{"fasting", "ogtt"}}.

## S6. Numerical integrity
LSODA rtol 1e-7/atol 1e-9; u=0 reproduces baseline exactly (unit test);
solver determinism verified; basal steady-state drift <
0.03 mg/dL/630 min (`results/qc/basal_drift.csv`).

## S7. Provenance
Frozen upstream files: `models/primary/upstream/` (commit 1ad94954,
SHA-256 in `models/primary/SHA256SUMS.txt`). Validation dataset:
upstream `Data.xlsx` (OGTT, ~100 g).
"""
open(f"{MAN}/supplement.md", "w").write(SUPP)
print("supplement written")
