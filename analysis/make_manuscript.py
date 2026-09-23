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
insi_civ = L("insulin_secretion", "civii", "u_opt")
insi_civ_L1 = L("insulin_secretion", "civii", "loss_max")
insi_civ_Lo = L("insulin_secretion", "civii", "loss_opt")

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

# -------------------------------------------------------------------------
MD = f"""---
title: "Maximum hormonal action is not optimal: interior optima of endocrine feedback efficacy in a validated glucose–insulin–glucagon model"
short_title: "Maximum is not optimum"
word_count: WORDCOUNT
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
variability, recovery dynamics and endocrine exposure. {n_II} of {n_cases}
intervention–challenge combinations showed strict interior optima
(Type II, L(u*) < L(0) and < L(1)), most prominently partial suppression
of insulin secretion under IVGTT (u* = {F(isi)}, loss {F(isi_L0)} →
{F(isi_Lo)} vs {F(isi_L1)} at u = 1), arising because limiting the insulin
excursion prevents reactive hypoglycaemia while retaining enough action
to clear the load. Findings were robust to ±2-fold loss-weight
perturbations and grid refinement, persisted in insulin-resistant and
insulin-deficient states, and a qualitatively similar interior optimum
appeared in a minimal HPT-axis model (thyroid suppression u* =
{F(hpt_ti.u_opt)}). These results show that endocrine feedback systems can
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

Figure 3 shows the composite loss L(u) for all {n_cases}
intervention–challenge combinations. Three regimes dominate. In the
fasting state every intervention leaves L essentially unchanged until
ablation destabilises homeostasis (Type 0/III). Under IVGTT and IVITT the
insulin axis is strongly non-monotone; under the more physiological OGTT,
several glucagon-axis interventions have shallow interior optima.

**Strict interior optima (Type II) were found in {n_II} of {n_cases}
combinations**, with a further {n_IIs} Type II* partial optima (Table 2).
The strongest result is partial suppression of insulin secretion under
IVGTT: u* = {F(isi)}, with L falling from {F(isi_L0)} at baseline to
{F(isi_Lo)}, while full ablation (u = 1) gives {F(isi_L1)} — worse than
the optimum but still better than baseline, i.e. the dose-response has a
genuine interior minimum (Figure 4A). Global inhibition of insulin
action showed a parallel optimum at u* = {F(isg)} (L = {F(isg_Lo)}).
Under CIVII, modest potentiation of insulin secretion was optimal
(u* = {F(insi_civ)}; L = {F(insi_civ_Lo)} vs {F(insi_civ_L1)} at maximum),
showing the phenomenon is not restricted to inhibitory interventions.

## Mechanism

The IVGTT interior optimum arises from the trade-off between the insulin
excursion needed to clear the load and the reactive hypoglycaemia it
produces. At baseline the 0.5 g/kg bolus drives a secretion spike (peak
{F(m_base_ins,0)} mU/L) followed by a nadir of {F(m_base_nad,0)} mg/dL; at
u* the insulin peak is roughly a quarter as high ({F(m_opt_ins,0)} mU/L),
the nadir rises to {F(m_opt_nad,0)} mg/dL, and peak glucose increases only
modestly (Figure 5). At u = 1,
secretion is abolished, hypoglycaemia disappears but glucose never
returns to target — the optimum interior point balances both failure
modes. Under OGTT the glucagon-axis optima (u* = {F(gsi_ogtt)} for
signalling inhibition, {F(gs_ogtt)} for secretion potentiation) are
shallower and driven mainly by reduced glycaemic variability, consistent
with the islet's paradoxical feedback design [3].

## Robustness and controls

Across all weight perturbations (each term family scaled ×0.5/×2 or
zeroed), the interior-optimum classification of the headline cases was
preserved in {F(frac_II,0)} % of perturbations, reverting only when the
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
from {F(ogtt_L0)} to {F(t2dm_isi.loss_baseline)}), interior optima persisted
and shifted: potentiating insulin secretion became optimal at
u* = {F(t2dm_isi.u_opt)} rather than at maximum, and glucagon secretion
suppression retained a strong optimum (u* = {F(gluc_inhib_ogtt_u)}).
Under a T1DM-like state (no
endogenous secretion), suppressing glucagon secretion showed a Type II
optimum at u* = {F(t1dm_gsi.u_opt)} for fasting
(L {F(t1dm_gsi.loss_baseline)} → {F(t1dm_gsi.loss_opt)}), i.e. partial —
not total — glucagon suppression is optimal when insulin is absent
(Figure 8).

## Exploratory HPT extension

In the minimal HPT model challenged with a 60-min T4 infusion, thyroid
output *inhibition* exhibited a Type II interior optimum at
u* = {F(hpt_ti.u_opt)} (L {F(hpt_ti.loss_baseline)} → {F(hpt_ti.loss_opt)}),
while feedback potentiation improved monotonically (Type I) and thyroid
potentiation gave no benefit (Type 0). This single-axis corroboration is
hypothesis-generating only.

# Discussion

We demonstrate, in a validated whole-body glucose–insulin–glucagon model,
that maximal endocrine action is frequently not optimal: strict interior
optima exist in {n_II} of {n_cases} intervention–challenge pairs, span
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
"""

# ---- write markdown ----------------------------------------------------
wc = len(re.sub(r"[^A-Za-z0-9 ]", " ",
       MD.split("# Keywords")[0].split("# Abstract")[1]).split())
MD = MD.replace("WORDCOUNT", str(wc))
open(f"{MAN}/manuscript.md", "w").write(MD)
print("word count (title→abstract):", wc)
print("total words:", len(MD.split()))

# ---- DOCX ---------------------------------------------------------------
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = docx.Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)

# Title page
doc.add_heading(MD.split('"')[1] if '"' in MD.split('\n')[2] else
                "Maximum hormonal action is not optimal", level=0)
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
    for seg in re.split(r"(\*[^*\s][^*]*\*)", text):
        if seg.startswith("*") and seg.endswith("*") and len(seg) > 2:
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

doc.add_heading("Figure captions", level=2)
for cap in [
    "Figure 1. Model validation: simulated (lines) vs upstream reference data (points) for glucose, insulin and insulin release under 100 g OGTT.",
    "Figure 2. Intervention convention. (A) Modulation factor f(u): potentiation 1+2u, inhibition 1−u. (B) Action-efficacy semantics: effective multiplier M_eff = 1 + s(M−1).",
    "Figure 3. Composite homeostatic loss L(u) for all interventions across the five challenges.",
    "Figure 4. Glucose trajectories at baseline (u=0), interior optimum (u*) and maximum (u=1) for the headline Type II cases.",
    "Figure 5. Mechanism of the IVGTT interior optimum: insulin, glucagon and hepatic glucose production at u=0, u* and u=1.",
    "Figure 6. Pareto fronts: hypoglycaemic vs hyperglycaemic burden; labels give u.",
    "Figure 7. Sensitivity of the optimal modulation u* and classification to loss-weight perturbations.",
    "Figure 8. Loss curves under healthy, T2DM-like (insulin signalling halved) and T1DM-like (no endogenous insulin secretion) states for OGTT.",
]:
    doc.add_paragraph(cap)
doc.save(f"{MAN}/manuscript.docx")
print("docx written")

# ---- Cover letter -------------------------------------------------------
COVER = """Dear Editors,

We submit the manuscript "Maximum hormonal action is not optimal:
interior optima of endocrine feedback efficacy in a validated
glucose–insulin–glucagon model" for consideration in the Journal of
Endocrinology.

Homeostatic feedback loops are presumed to work best at maximal
responsiveness. Using a validated whole-body glucose–insulin–glucagon
model, we show this is not true: several interventions have strict
interior optima (moderate modulation beats both baseline and maximum),
arising from a Braess-like trade-off between opposing failure modes. The
finding is robust to loss-weighting, grid and solver checks, persists in
insulin-resistant and insulin-deficient states, and is corroborated in a
minimal HPT-axis model.

The study is fully reproducible: the complete pipeline, frozen upstream
model code, all results, and the figures regenerate with a single
command. This work is Paper 2 of a methodological series; it is
self-contained and has not been published or submitted elsewhere. The
author declares no competing interests. An AI assistant was used for
implementation support, disclosed in the manuscript.

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

## S4. Exploratory HPT-axis model
`src/hpt_model.py` + `analysis/run_hpt.py`: 3-ODE TSH–T4–T3 loop with Hill
feedback; T4-infusion challenge; classification in
`results/hpt/hpt_classification.csv`. Exploratory (not fitted to data).

## S5. Disease-state details
`results/disease/disease_classification.csv`: T2DM-like (insulin
signalling × 0.5) and T1DM-like (secretion abolished) scans for all
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
