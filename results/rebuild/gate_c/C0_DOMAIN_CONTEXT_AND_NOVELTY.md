# C0 — Domain context and novelty (limited reconnaissance)

**How citations were checked.** Every citation below was verified against a Crossref record (raw JSON in `data/raw/literature/crossref_gate_c/`) or against the frozen primary PDFs/XML in the repository. Where a match is uncertain, the entry says so.

| source | verified record | relevance |
|---|---|---|
| Sorensen JT. PhD thesis, MIT 1985 | `models/primary/upstream/Sorensen_phd.pdf` | Model origin. For each protocol it gives the basal state and validation data source: IVITT, Gerich et al., n = 15; CIVII 0.25/0.4 mU/kg/min, Saccà et al. 1979, n = 5/6. It describes the CIVII *hypoglycaemic steady state* as the balance of insulin action against counterregulation. |
| Panunzi S, et al. PLoS One 2020;15:e0237215 | `data/raw/literature/panunzi2020_pone.0237215.*` | Corrected revised model. Initial conditions are inputs. Plasma = 0.925·GPV, blood = 0.84·GPV. Separate oral-refit secretion parameters (BioSorSimo). |
| Garzilli I, Itzkovitz S. Sci Rep 2018;8. doi:10.1038/s41598-018-29084-4 | Crossref | Design principles of the "paradoxical" α–β feedback. A minimal-model rationale for non-intuitive hormone interactions. This is the closest prior art for claims that more hormone action is not always better. |
| Wang G. J R Soc Interface 2012;9:2723–2734. doi:10.1098/rsif.2012.0244 | Crossref | "Optimal homeostasis necessitates bistable control": optimality and control structure in glucose homeostasis. Prior art for optimal-control framing. |
| Saccà L, et al. Diabetes 1979;28:533–536. doi:10.2337/diabetes.28.6.533 | Crossref | Glucose-dependent effects of insulin and counterregulatory hormones on glucose production. **Unverified** whether this is the thesis's CIVII data source. |
| Gerich J, et al. Am J Physiol 1979;236:E380 (thesis cites "1980"). doi:10.1152/ajpendo.1979.236.4.e380 | Crossref | Hormonal mechanisms of recovery from insulin-induced hypoglycaemia. **Unverified** match to the thesis IVITT data. |

## What the field already knows (relevant to the candidate claims)

These points are textbook physiology or control theory. They were not re-derived here.

1. **Glycaemic risk is asymmetric.** Insulin lowers hyperglycaemia at the cost of hypoglycaemia risk, so any dose has an intermediate "best" setting under a weighted risk. This is the logic behind glycaemic targets and insulin titration.
2. **Delayed negative feedback limits useful gain.** Above a delay-dependent gain the response overshoots or undershoots. This is standard in feedback control and appears in glucose–insulin delay models (e.g. the IVGTT delay models by Panunzi/De Gaetano cited in Panunzi 2020).
3. **Endogenous insulin secretion is suppressed during exogenous insulin infusion,** and counterregulation (glucagon, then catecholamines) limits the fall in glucose. The CIVII hypoglycaemic plateau is this balance (Sorensen thesis).
4. **α–β paracrine and endocrine interactions can produce counter-intuitive responses** (Garzilli & Itzkovitz 2018).

## Novelty assessment

- **Case (a)** reproduces item 2 inside the Sorensen model. **Case (b)** reproduces items 1 and 3. **Case (c)** is a protocol artifact (C2).
- None of the three is a novel mechanistic prediction.
- The only incremental, falsifiable statement we could specify is model-specific and conditional: in the revised Sorensen model under a 100 g OGTT from a low basal state, the critical secretory gain falls with insulin-action delay. It is a known control result, it fails under model-credible alternative starting states (C3), and it is not distinguishable from item 2.
