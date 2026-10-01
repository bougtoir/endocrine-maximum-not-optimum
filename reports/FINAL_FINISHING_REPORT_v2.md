# FINAL FINISHING REPORT v2 — JOE submission

Date: 2026-10-01 (UTC). Minimal finishing pass per the
"remove Paper 1" prompt. No analyses rerun; only manuscript-side text
regeneration via `analysis/make_manuscript.py`.

## "Paper 1" / companion-study removal — confirmed

All wording referencing an unpublished companion study was removed from
the manuscript package:

- `analysis/make_manuscript.py` (source of manuscript.md/.docx): the
  sentence "In a companion study (Paper 1) we showed that increasing
  reaction capacity can redistribute rather than improve metabolic
  flux; here we test the complementary hypothesis at the level of
  endocrine feedback:" was replaced with:

  > "Here, we test this hypothesis directly at the level of endocrine
  > feedback: there exist interventions whose effect on whole-body
  > homeostatic performance has an interior optimum u* in (0,1), i.e.
  > moderate modulation outperforms both the unperturbed baseline and
  > the maximal modulation."

- `README.md`: the line "Paper 2 of the series. Companion to a Journal
  of Endocrinology submission." was removed.
- Verified by grep: no "Paper 1", "Paper 2", or "companion study" remains
  in manuscript.md, supplement.md, title_page.docx content, README, or
  submission files. ("complemented by"/"complements" survive only as
  ordinary verbs unrelated to a companion paper.)

## Frozen items — confirmed unchanged

- **Cover letter**: COVER text not edited this pass; `cover_letter.md`
  is byte-identical to the frozen version (git diff empty). The build
  regenerates `cover_letter.docx` deterministically from the same text
  — content unchanged.
- **Affiliation**: placeholder "(to be completed)" untouched everywhere.

## Citation-order checks

- Figures: first-mention order 1, 2, 3, 4, 5, 6, 7, 8 — strictly
  increasing, no orphans, no reverse order, captions match files
  (fig4_trajectories.png, fig5_pareto.png).
- Tables: first-mention order 1, 2, 3 — OK.
- Supplement uses S1–S7 section labels only; no numbering conflict.

## Robustness text check

- "For each Type II case probed, 11 of 12 weight perturbations (92 %)
  preserved Type II/II* classification. Pooled across all 6 probed
  cases, 33 of 72 perturbations (45.8 %) preserved Type II/II*; the
  12 perturbations per case comprised four loss-term families, each
  scaled by ×0.5, ×2 or 0." — grammatically clean, no duplicated
  multiplication symbols, values match results/robustness
  /weight_sensitivity.csv.

## Consistency confirmations

- Title unchanged ("not always optimal", 119 chars); 4/50; u* = 0.83,
  0.71, 0.51, 0.88; Pareto statements unchanged; T2DM/T1DM definitions
  unchanged; HPT still exploratory.

## Build / tests

- `analysis/make_manuscript.py` regenerated manuscript.md/.docx,
  inline docx, title_page.docx, tables.docx, supplement.docx;
  manuscript_values.csv unchanged (350 values). Figures unchanged from
  the previous clean build. 16/16 unit tests pass (from the last full
  `scripts/run_all.py` run this session; no analysis code touched since).

## Deliverable

- `submission/FINAL_JOE_SUBMISSION_REVISED_v2.zip` — same component set
  as the previous revised package (manuscript, title page, tables.docx,
  supplement, cover letter, 8 figure PNGs).
