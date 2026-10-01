# MANUSCRIPT LITERATURE REINFORCEMENT REPORT — v2

Scope: manuscript-only literature deepening + complete reference renumbering by first appearance.
No analyses rerun for content; results, figures, tables, supplement, cover letter, title page, affiliation untouched.

## References
- Added (9): Cannon 1929; Kitano 2004; Kawamori 2009; Capozzi 2019; Bergman 2021;
  Dalla Man 2014; Vandenberg 2012; Schwartz 1987; Thomaseth 2014; Pandiyan 2014.
- Removed (2): Onishi Array 2026, Onishi CSF 2026 — were listed but never cited (orphans).
- Kept: Braess, Donovan, Garzilli, Calabrese, Panunzi, Sorensen, Bergman 1979, Wang.
- Final count: **18 references** (within JOE ≤60 limit).
- Verification: title/journal/year/volume/pages or article number checked against publisher pages
  (JCI, Cell Metab, Endocr Rev, AJP, JDS&T, Front Endocrinol, Math Med Biol, Physiol Rev,
  Nat Rev Genet, J Clin Invest); see `results/literature/literature_context_matrix.csv` and
  `literature_context_notes.md`.

## Sections expanded
- **Introduction** — rebuilt to 5 paragraphs (~+400 words): (1) efficacy vs whole-system utility
  framing (Cannon, Kitano, islet reciprocal loop: Garzilli+Kawamori+Capozzi); (2) quantitative
  modelling lineage (Bergman×2, Sorensen, Panunzi, Dalla Man); (3) distinction from classic
  non-monotonic dose–response (Calabrese, Vandenberg) — monotonic local intervention →
  emergent system non-monotonicity; (4) Braess/Donovan gap + hypothesis (unchanged bold statement);
  (5) existing formalisation paragraph (kept).
- **Discussion** — added two analytical paragraphs (~+450 words):
  (A) physiological plausibility: counter-regulation thresholds (Schwartz), reciprocal islet
  control (Kawamori, Capozzi, Garzilli), speed-vs-overshoot trade-off;
  (B) explicit contrast with hormesis/NMDR — local monotonicity by construction vs emergent
  system-level non-monotonicity; plus a context-dependence paragraph (u* shifts across
  challenges and disease states; Wang).
- **Limitations** — IVGTT nadir now benchmarked against Thomaseth 2014 wording
  ("transient, subject-dependent counter-regulatory dips") rather than an invented range;
  HPT limitation now cites Pandiyan 2014 (richer HPT models exist).

## Novelty positioning
- "to our knowledge ... not been tested in a quantitative model" retained; now explicitly
  bounded: the tested object is endogenous feedback efficacy scaling, distinguished from
  exogenous dose–response literature. No "first" claim added.

## IVGTT citation status
- RESOLVED: Thomaseth et al. 2014 (Am J Physiol Regul Integr Comp Physiol 307:R321–R331)
  documents transient, insulin-sensitivity-dependent counter-regulatory hypoglycaemia in IM-FSIGT.

## HPT references status
- RESOLVED: Pandiyan, Merrill & Benvenga 2014 (Math Med Biol 31:226–258) cited as a richer
  quantitative HPT feedback model; our stylised extension remains labelled exploratory/unfitted.

## Renumbering
- Implemented as an automated first-appearance renumber pass in `analysis/make_manuscript.py`:
  citations are written as `{key}` tokens and numbered at build time by first appearance,
  so rule compliance is structural, not manual.
- Audit: `reports/FINAL_REFERENCE_ORDER_AUDIT.md` — PASS (strict order 1–18, contiguous,
  all entries cited, no orphans, no duplicates; math interval `[0,1]` excluded from matching).

## Figure/table status
- Figure first-citation order unchanged: 1→2→3→4→5→6→4→7→8 (Fig 4 legitimately cited twice).
- Table order unchanged: 1→2→3. No renumbering, no orphans.

## Other files
- `manuscript/title_page.docx` word count updated automatically (2403→2931) — the only
  cross-file change beyond manuscript.docx/.md/manuscript_inline.docx.
- Cover letter: byte-identical content (verified by unzipping and diffing document.xml).
- Supplement, tables.docx: unchanged (tables.docx restored byte-identical).

## Results integrity
- 4/50 Type II; u* = 0.83/0.71/0.51/0.88; 92% per-case / 46% pooled denominators;
  disease shifts (T2DM 0.55, T1DM 0.80); HPT u* = 0.45 — all unchanged, verified against
  regenerated results CSVs. run_all.py full pipeline green; 16/16 unit tests pass.
- Abstract still 243 words; body word count 3425 (<5000). No clinical-dose, universal-Braess,
  or superiority claims introduced.
