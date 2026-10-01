# FINAL FINISHING REPORT — JOE submission

Date: 2026-10-01 (UTC). Pass type: finishing only — no re-analysis, no
framing changes. Pipeline rerun in full; all outputs regenerated.

## Files changed

- `analysis/make_manuscript.py` — new title (JOE 120-char limit); title
  page extracted to a separate `title_page.docx`; double line spacing +
  continuous line numbering added to `manuscript.docx`; separate editable
  `tables.docx` generated; cover letter title updated.
- `manuscript/manuscript.md`, `manuscript.docx`,
  `manuscript_inline.docx`, `title_page.docx`, `tables.docx`,
  `cover_letter.{md,docx}` — regenerated.
- `README.md` — headline updated to the new title.
- `reports/JOE_COMPLIANCE_CHECKLIST.md` — re-verified against current
  guidelines.
- `submission/FINAL_JOE_SUBMISSION/` + `submission/FINAL_JOE_SUBMISSION.zip`
  — clean submission set (manuscript, title page, tables.docx, supplement,
  cover letter, 8 figure PNGs; no drafts/caches/CSVs).

## Exact corrections made

- **Title shortened to 119 characters** (JOE limit 120): "Maximum hormonal
  action is not always optimal: interior optima in a previously validated
  glucose–insulin–glucagon model". "not always optimal" and "previously
  validated" preserved per earlier revision requirements.
- Title page now a separate Word file including short title, keywords
  (8, min 4) and the full-article word count excluding references/legends
  (~2,742 words), as required.
- Manuscript docx now double-spaced with continuous line numbering.
- Tables additionally provided as a separate editable `tables.docx`.

## Prior-art / novelty wording

- "to our knowledge" **retained** in the Introduction ("has not, to our
  knowledge, been tested in a quantitative model"). Re-checked against
  prior art: exogenous insulin/glucagon optimal control exists
  (e.g. meal-bolus optimisation for T1D), but continuous modulation of
  *endogenous* feedback efficacy and interior optima of it were not found
  in the literature; the claim scope is unchanged and no "first" claim
  is made.
- Overstrong-wording audit: no unqualified "robust", "frequently",
  "universally", "proves", "optimal dose", "partial agonists are
  superior", or "formal Braess equivalence" remains; "validated" is only
  used as "previously validated" model with the port caveat.

## Abstract

- Final abstract word count: **243** (limit 250), single unstructured
  paragraph — unchanged, verified correct (4/50, Pareto wording, 92%/46%
  denominators, no unqualified "robust", calibrated conclusion).

## Numerical confirmations (regenerated from source, not hardcoded)

- 4/50 strict Type II cases; u* = 0.83, 0.71, 0.51, 0.88; HPT u* = 0.45.
- 92% = 11/12 weight perturbations preserving Type II/II* **per probed
  Type II case**; 46% = 33/72 **pooled across all six probed cases** —
  both stated with denominators in Abstract/Results/Discussion/Table 3.
- Pareto: all four optima no worse than u=1 on glycaemic-burden axes;
  three strictly dominate u=1; 2/4 on the frontier; OGTT
  glucagon-suppression optimum is endpoint-dependent (equal burdens).
- T1DM-like: endogenous insulin secretion abolished; glucagon secretion
  remains simulated/manipulable.
- IVGTT limitation: nadir ≈ 40 mg/dL stated as more severe than typical
  clinical FSIGT; u* position flagged model-dependent.
- Title uses "not always optimal" everywhere (manuscript, cover letter,
  README, title page).

## Quality gate

- `python scripts/run_all.py`: all 12 steps completed; 16/16 unit tests
  pass; manuscript_values.csv, figures, tables, supplement, cover letter
  regenerated (no stale files).
- Journal compliance checklist: all items OK (see
  reports/JOE_COMPLIANCE_CHECKLIST.md).

## Deliverable

- `submission/FINAL_JOE_SUBMISSION.zip`
