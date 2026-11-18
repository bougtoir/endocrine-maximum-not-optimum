# C3 — Parameter provenance and ranges (Stage 1 only)

| factor | values | provenance | range type |
|---|---|---|---|
| insulin-action delay `tauInsu` | ×0.5, 0.75, 1, 1.5, 2 (reference 25 min) | Sorensen 1985 (hepatic insulin-effect time constant); Panunzi 2020 Appendix A1 | generic exploratory, not literature-bounded |
| potentiator rate `KappaPotnPtgt` | ×0.5, 1, 2 (reference 0.0169775 min⁻¹, OGTT refit) | BioSorSimo oral refit (upstream V01.01.45) | generic exploratory |
| basal plasma glucose | 82.4 (model reference), 90 mg/dL | 82.4 = upstream single basal state × 0.925; 90 = Sorensen thesis CIVII basal (Saccà 1979), close to IVITT 91 (Gerich) | model-credible (both used by the model's authors) |
| oral glucose dose | 50, 75, 100 g | 100 g = v3 protocol and BioSorSimo data; 75 g = standard clinical OGTT | protocol alternatives |

No virtual-cohort distribution was constructed. Nothing in C3 should be read as describing a human population.
